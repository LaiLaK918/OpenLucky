#!/usr/bin/env python3
"""
OKX 市场数据同步脚本
功能：获取历史数据 + WebSocket 实时更新 = 始终保持最新的本地数据
数据结构：按时间框架保存不同数量的K线数据
"""

import asyncio
import aiohttp
import websockets
import json
import time
import os
from datetime import datetime
import logging
import random
import collections

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AsyncRateLimiter:
    """轻量级令牌桶速率限制器（协程安全）"""
    def __init__(self, max_requests: int, period_seconds: float):
        self.max_requests = max_requests
        self.period = period_seconds
        self.timestamps = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            # 清理过期时间戳
            while self.timestamps and now - self.timestamps[0] > self.period:
                self.timestamps.popleft()
            if len(self.timestamps) >= self.max_requests:
                sleep_time = self.period - (now - self.timestamps[0]) + 0.01
                await asyncio.sleep(max(0.0, sleep_time))
            # 记录当前请求
            self.timestamps.append(time.monotonic())

class OKXMarketSync:
    def __init__(self):
        self.rest_url = "https://www.okx.com"
        self.ws_url = "wss://ws.okx.com:8443/ws/v5/business"
        self.market_data = {}
        self.save_interval = 60  # 1分钟保存一次
        self.data_dir = "data"  # 数据目录
        self.summary_file = "data/summary.json"  # 概要文件
        self.instruments_file = "instruments.json"  # 产品基础信息文件
        self.instruments_cache_hours = 24  # 产品信息缓存24小时
        # REST并发与速率限制（OKX 文档：约40请求/2秒）
        self.rest_concurrency = 8
        self._rest_sem = None  # 将在事件循环中初始化
        # 一致性刷新节流
        self.last_refresh = {}
        # 允许在一致性巡检中自动回补的周期（避免1W/1M频繁刷）
        self.consistency_allowed_bars = {"5m", "15m", "1H", "4H", "1D"}
        # 全局速率限制器：每秒最多18次
        self.rate_limiter = AsyncRateLimiter(max_requests=18, period_seconds=1.0)
        
        # K线保留数量配置
        self.candle_limits = {
            "5m": 288,   # 24小时
            "15m": 192,  # 48小时
            "1H": 168,   # 7天
            "4H": 180,   # 30天
            "1D": 90,    # 3个月
            "1W": 52,    # 1年
            "1M": 12     # 1年
        }
        
        # 时间框架映射（WebSocket用小写，REST API用大写）
        self.timeframe_map = {
            "5m": "5m",
            "15m": "15m",
            "1H": "1h",
            "4H": "4h",
            "1D": "1d",
            "1W": "1w",
            "1M": "1M"
        }

        # 各时间框架对应毫秒数（用于数据新鲜度判断）
        self.timeframe_ms = {
            "5m": 5 * 60 * 1000,
            "15m": 15 * 60 * 1000,
            "1H": 60 * 60 * 1000,
            "4H": 4 * 60 * 60 * 1000,
            "1D": 24 * 60 * 60 * 1000,
            "1W": 7 * 24 * 60 * 60 * 1000,
            "1M": 30 * 24 * 60 * 60 * 1000  # 近似值
        }
        
    async def start(self):
        """主启动函数"""
        logger.info("Starting OKX Market Sync...")
        
        try:
            # 初始化并发信号量
            self._rest_sem = asyncio.Semaphore(self.rest_concurrency)
            # 0. 创建数据目录
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 1. 更新产品基础信息（如果需要）
            await self.update_instruments_info()
            
            # 2. 获取要同步的产品列表
            instruments = await self.get_instruments()
            logger.info(f"Found {len(instruments)} USDT-SWAP instruments")
            
            # 3. 加载已有数据（如果存在）
            self.load_existing_data()
            
            # 4. 获取历史K线数据
            await self.fetch_all_history(instruments)
            logger.info("Historical data loaded")
            
            # 5. 保存初始数据
            self.save_all_data()
            
            # 6. 启动WebSocket、数据一致性巡检与定期保存
            await asyncio.gather(
                self.websocket_loop(instruments),
                self.consistency_loop(instruments),
                self.save_loop()
            )
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
    
    def load_existing_data(self):
        """加载已存在的数据文件"""
        if not os.path.exists(self.data_dir):
            return
        
        # 读取概要文件获取产品列表
        if os.path.exists(self.summary_file):
            try:
                with open(self.summary_file, 'r') as f:
                    summary = json.load(f)
                    instruments = summary.get('instruments', [])
                    
                    # 加载每个产品的数据文件
                    for inst_id in instruments:
                        data_file = f"{self.data_dir}/{inst_id}.json"
                        if os.path.exists(data_file):
                            try:
                                with open(data_file, 'r') as f:
                                    inst_data = json.load(f)
                                    self.market_data[inst_id] = inst_data.get('data', {})
                            except Exception as e:
                                logger.warning(f"Failed to load data for {inst_id}: {e}")
                    
                    logger.info(f"Loaded existing data for {len(self.market_data)} instruments")
            except Exception as e:
                logger.warning(f"Failed to load summary file: {e}")
    
    async def update_instruments_info(self):
        """更新产品基础信息（24小时缓存）"""
        # 检查是否需要更新
        if os.path.exists(self.instruments_file):
            file_time = os.path.getmtime(self.instruments_file)
            current_time = time.time()
            age_hours = (current_time - file_time) / 3600
            
            if age_hours < self.instruments_cache_hours:
                logger.info(f"Instruments info is fresh ({age_hours:.1f}h old), skipping update")
                return
        
        logger.info("Updating instruments info...")
        
        # 从API获取所有SWAP产品的基础信息
        async with aiohttp.ClientSession() as session:
            url = f"{self.rest_url}/api/v5/public/instruments?instType=SWAP"
            async with session.get(url) as resp:
                data = await resp.json()
                if data['code'] != '0':
                    logger.error(f"Failed to get instruments info: {data}")
                    return
                
                all_instruments = data['data']
        
        # 筛选USDT合约的基础信息
        usdt_instruments = {}
        for inst in all_instruments:
            if (inst.get('instType') == 'SWAP' and 
                inst.get('settleCcy') == 'USDT' and 
                inst.get('state') == 'live'):
                usdt_instruments[inst['instId']] = inst
        
        # 保存到文件 - 使用标准JSON格式，每个instrument ID作为顶级key
        # 原子写入
        temp_file = f"{self.instruments_file}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(usdt_instruments, f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, self.instruments_file)
        
        logger.info(f"Updated instruments info: {len(usdt_instruments)} USDT-SWAP instruments")
    
    async def get_instruments(self):
        """获取所有USDT永续合约ID列表"""
        # 从本地instruments.json文件读取
        if not os.path.exists(self.instruments_file):
            logger.error(f"Instruments file {self.instruments_file} not found")
            return []
        
        try:
            with open(self.instruments_file, 'r') as f:
                instruments = json.load(f)
            
            # 直接获取所有instrument ID（现在是顶级key）
            usdt_swaps = list(instruments.keys())
            
            # 返回所有 USDT-SWAP 产品ID
            logger.info(f"Total USDT-SWAP instruments found: {len(usdt_swaps)}")
            return usdt_swaps
            
        except Exception as e:
            logger.error(f"Error reading instruments file: {e}")
            return []
    
    async def fetch_all_history(self, instruments):
        """获取所有产品的历史K线（并发+限速）"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            now_ms = int(time.time() * 1000)
            for inst_id in instruments:
                if inst_id not in self.market_data:
                    self.market_data[inst_id] = {}
                for bar, limit in self.candle_limits.items():
                    if bar not in self.market_data[inst_id]:
                        self.market_data[inst_id][bar] = {"latest_ts": 0, "candles": []}
                    existing = self.market_data[inst_id][bar]
                    latest_ts = int(existing.get("latest_ts", 0) or 0)
                    bar_ms = self.timeframe_ms.get(bar, 0)
                    need_refresh = (
                        len(existing["candles"]) < (limit // 2)
                        or latest_ts == 0
                        or (bar_ms > 0 and (now_ms - latest_ts) > bar_ms * 3)
                    )
                    if need_refresh:
                        tasks.append(self._fetch_and_store(session, inst_id, bar, limit))
            if tasks:
                await asyncio.gather(*tasks)

    async def _fetch_and_store(self, session: aiohttp.ClientSession, inst_id: str, bar: str, limit: int):
        url = f"{self.rest_url}/api/v5/market/candles"
        params = {'instId': inst_id, 'bar': bar, 'limit': str(min(limit, 300))}
        try:
            await self.rate_limiter.acquire()
            async with self._rest_sem:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
            if data.get('code') == '0' and data.get('data'):
                candles = data['data']
                self.market_data.setdefault(inst_id, {}).setdefault(bar, {"latest_ts": 0, "candles": []})
                self.market_data[inst_id][bar]["candles"] = candles
                self.market_data[inst_id][bar]["latest_ts"] = int(candles[0][0]) if candles else 0
                logger.info(f"Fetched {len(candles)} {bar} candles for {inst_id}")
            else:
                logger.warning(f"No data for {inst_id} {bar}: {data}")
        except Exception as e:
            logger.error(f"Error fetching {inst_id} {bar}: {e}")
    
    async def websocket_loop(self, instruments):
        """WebSocket循环"""
        reconnect_delay = 1
        
        while True:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    logger.info("WebSocket connected")
                    reconnect_delay = 1  # 重置延迟
                    
                    # 分批订阅K线数据（避免超过64KB限制）
                    # 每个订阅约50字节，64KB ≈ 1300个订阅
                    # 7个时间框架，所以每批最多 1300/7 ≈ 185 个产品
                    # 为安全起见，使用更小的批次
                    batch_size = 15  # 每批15个产品 = 105个订阅
                    timeframes = list(self.timeframe_map.items())
                    
                    for i in range(0, len(instruments), batch_size):
                        batch_instruments = instruments[i:i+batch_size]
                        
                        sub_msg = {
                            "op": "subscribe",
                            "args": []
                        }
                        
                        # 为当前批次的产品添加所有时间框架订阅
                        for inst_id in batch_instruments:
                            for tf, ws_tf in timeframes:
                                sub_msg["args"].append({
                                    "channel": f"candle{ws_tf}",
                                    "instId": inst_id
                                })
                        
                        logger.info(f"Subscribing batch {i//batch_size + 1}: {len(batch_instruments)} instruments, {len(sub_msg['args'])} subscriptions")
                        await ws.send(json.dumps(sub_msg))
                        await asyncio.sleep(1)  # 给服务器更多时间处理
                    
                    logger.info(f"Subscribed to {len(instruments)} instruments")
                    
                    # 启动心跳任务
                    heartbeat_task = asyncio.create_task(self.heartbeat_loop(ws))
                    
                    try:
                        # 接收数据
                        async for message in ws:
                            try:
                                # 处理 pong 响应
                                if message == 'pong':
                                    continue
                                
                                data = json.loads(message)
                                if 'data' in data and 'arg' in data:
                                    self.update_candle(data)
                            except json.JSONDecodeError:
                                pass
                            except Exception as e:
                                logger.error(f"Error processing message: {e}")
                    finally:
                        # 取消心跳任务
                        heartbeat_task.cancel()
                        try:
                            await heartbeat_task
                        except asyncio.CancelledError:
                            pass
                            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60)  # 指数退避，最多60秒
    
    async def heartbeat_loop(self, ws):
        """心跳循环 - 每25秒发送一次ping"""
        try:
            while True:
                await asyncio.sleep(25)  # 每25秒发送一次（小于30秒的安全值）
                await ws.send('ping')
                logger.debug("Sent ping")
        except asyncio.CancelledError:
            logger.debug("Heartbeat task cancelled")
            raise
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            raise
    
    def update_candle(self, msg):
        """更新K线数据"""
        arg = msg['arg']
        channel = arg.get('channel', '')
        inst_id = arg.get('instId', '')
        
        if not inst_id or 'candle' not in channel:
            return
        
        # 提取时间周期
        ws_bar = channel.replace('candle', '')
        
        # 找到对应的标准时间框架
        bar = None
        for tf, ws_tf in self.timeframe_map.items():
            if ws_tf == ws_bar:
                bar = tf
                break
        
        if not bar or bar not in self.candle_limits:
            return
        
        # 确保数据结构存在
        if inst_id not in self.market_data:
            self.market_data[inst_id] = {}
        if bar not in self.market_data[inst_id]:
            self.market_data[inst_id][bar] = {
                "latest_ts": 0,
                "candles": []
            }
        
        # 更新数据
        new_candles = msg['data']
        bar_data = self.market_data[inst_id][bar]
        
        for new_candle in new_candles:
            ts = int(new_candle[0])
            
            # 更新最新时间戳
            if ts > bar_data["latest_ts"]:
                bar_data["latest_ts"] = ts
            
            # 查找是否需要更新
            updated = False
            for i, candle in enumerate(bar_data["candles"]):
                if int(candle[0]) == ts:
                    bar_data["candles"][i] = new_candle
                    updated = True
                    break
            
            # 如果是新K线，添加到开头
            if not updated:
                bar_data["candles"].insert(0, new_candle)
                # 保持限定数量
                limit = self.candle_limits[bar]
                bar_data["candles"] = bar_data["candles"][:limit]

    async def consistency_loop(self, instruments):
        """数据一致性巡检与自动回补：确保各时间框架无断层、最新且长度达标"""
        # 巡检周期（秒）
        interval_seconds = 180
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    refresh_tasks = []
                    for inst_id in instruments:
                        if inst_id not in self.market_data:
                            continue
                        for bar, limit in self.candle_limits.items():
                            if bar not in self.market_data[inst_id]:
                                continue
                            # 只对允许的周期执行自动回补
                            if bar not in self.consistency_allowed_bars:
                                continue
                            if self._need_refresh_or_backfill(inst_id, bar):
                                refresh_tasks.append(self._refresh_recent_candles(session, inst_id, bar, limit))
                    if refresh_tasks:
                        await asyncio.gather(*refresh_tasks)
            except Exception as e:
                logger.warning(f"Consistency loop warning: {e}")
            # 等待下轮
            await asyncio.sleep(interval_seconds)

    def _need_refresh_or_backfill(self, inst_id: str, bar: str) -> bool:
        """判断该产品该周期是否需要刷新（长度不足/过旧/存在断层）"""
        try:
            bar_ms = self.timeframe_ms.get(bar, 0)
            if bar_ms <= 0:
                return False
            data = self.market_data.get(inst_id, {}).get(bar, {})
            candles = data.get("candles", [])
            latest_ts = int(data.get("latest_ts", 0) or 0)
            limit = self.candle_limits.get(bar, 0)
            if not candles or len(candles) < max(10, limit // 3):
                return True
            # 过旧
            now_ms = int(time.time() * 1000)
            if latest_ts == 0 or (now_ms - latest_ts) > bar_ms * 3:
                return True
            # 断层：检查最近若干根时间间隔
            check_n = min(50, len(candles) - 1)
            for i in range(check_n):
                try:
                    ts_curr = int(candles[i][0])
                    ts_next = int(candles[i + 1][0])
                except Exception:
                    return True
                gap = ts_curr - ts_next
                # 允许因撮合延迟产生的小抖动，阈值1.5个bar
                if gap > int(bar_ms * 1.5):
                    return True
            return False
        except Exception:
            return True

    async def _refresh_recent_candles(self, session: aiohttp.ClientSession, inst_id: str, bar: str, limit: int):
        """用REST刷新该产品该周期的最近K线，修复断层与过旧问题"""
        url = f"{self.rest_url}/api/v5/market/candles"
        params = {'instId': inst_id, 'bar': bar, 'limit': str(min(limit, 300))}
        try:
            await self.rate_limiter.acquire()
            async with self._rest_sem:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
            if data.get('code') == '0' and data.get('data'):
                candles = data['data']
                # 覆盖写入
                if inst_id not in self.market_data:
                    self.market_data[inst_id] = {}
                if bar not in self.market_data[inst_id]:
                    self.market_data[inst_id][bar] = {"latest_ts": 0, "candles": []}
                self.market_data[inst_id][bar]["candles"] = candles
                self.market_data[inst_id][bar]["latest_ts"] = int(candles[0][0]) if candles else 0
                logger.info(f"Refreshed {bar} candles for {inst_id} (consistency)")
                # 标记节流时间
                self.last_refresh.setdefault(inst_id, {})[bar] = int(time.time() * 1000)
            else:
                logger.warning(f"Failed to refresh {inst_id} {bar}: {data}")
        except Exception as e:
            logger.warning(f"Refresh error for {inst_id} {bar}: {e}")
    
    async def save_loop(self):
        """定期保存数据"""
        while True:
            await asyncio.sleep(self.save_interval)
            self.save_all_data()
            logger.info(f"Data saved - {len(self.market_data)} instruments")
    
    def save_all_data(self):
        """保存所有数据到分文件"""
        current_time = datetime.now().isoformat()
        
        # 保存概要文件
        summary = {
            'update_time': current_time,
            'instrument_count': len(self.market_data),
            'instruments': list(self.market_data.keys())
        }
        
        # 原子写入概要文件
        temp_summary = f"{self.summary_file}.tmp"
        with open(temp_summary, 'w') as f:
            json.dump(summary, f, separators=(',', ':'))
        os.replace(temp_summary, self.summary_file)
        
        # 保存每个产品的数据文件
        for inst_id, inst_data in self.market_data.items():
            self.save_instrument_data(inst_id, inst_data, current_time)
    
    def save_instrument_data(self, inst_id, inst_data, update_time):
        """保存单个产品的数据"""
        output = {
            'update_time': update_time,
            'instrument': inst_id,
            'data': inst_data
        }
        
        # 原子写入产品数据文件
        data_file = f"{self.data_dir}/{inst_id}.json"
        temp_file = f"{data_file}.tmp"
        
        with open(temp_file, 'w') as f:
            json.dump(output, f, separators=(',', ':'))
        
        os.replace(temp_file, data_file)

if __name__ == "__main__":
    sync = OKXMarketSync()
    try:
        asyncio.run(sync.start())
    except KeyboardInterrupt:
        logger.info("Stopped by user")