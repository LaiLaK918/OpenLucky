#!/usr/bin/env python3
"""
OKX Market Data Synchronization Script
Functionality: Fetch historical data + WebSocket real-time updates = Always keep local data up-to-date
Data Structure: Save different amounts of candlestick data based on timeframes
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class AsyncRateLimiter:
    """Lightweight token bucket rate limiter (coroutine-safe)"""
    def __init__(self, max_requests: int, period_seconds: float):
        self.max_requests = max_requests
        self.period = period_seconds
        self.timestamps = collections.deque()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            # Clean up expired timestamps
            while self.timestamps and now - self.timestamps[0] > self.period:
                self.timestamps.popleft()
            if len(self.timestamps) >= self.max_requests:
                sleep_time = self.period - (now - self.timestamps[0]) + 0.01
                await asyncio.sleep(max(0.0, sleep_time))
            # Record current request
            self.timestamps.append(time.monotonic())

class OKXMarketSync:
    def __init__(self):
        self.rest_url = "https://www.okx.com"
        self.ws_url = "wss://ws.okx.com:8443/ws/v5/business"
        self.market_data = {}
        self.save_interval = 60  # Save every 1 minute
        self.data_dir = "data"  # Data directory
        self.summary_file = "data/summary.json"  # Summary file
        self.instruments_file = "instruments.json"  # Product basic info file
        self.instruments_cache_hours = 24  # Cache product info for 24 hours
        # REST concurrency and rate limiting (OKX docs: about 40 requests/2 seconds)
        self.rest_concurrency = 8
        self._rest_sem = None  # Will be initialized in event loop
        # Consistency refresh throttling
        self.last_refresh = {}
        # Allowed periods for auto-backfill in consistency check (avoid frequent refresh of 1W/1M)
        self.consistency_allowed_bars = {"5m", "15m", "1H", "4H", "1D"}
        # Global rate limiter: max 18 per second
        self.rate_limiter = AsyncRateLimiter(max_requests=18, period_seconds=1.0)
        
        # Candlestick retention quantity configuration
        self.candle_limits = {
            "5m": 288,   # 24 hours
            "15m": 192,  # 48 hours
            "1H": 168,   # 7 days
            "4H": 180,   # 30 days
            "1D": 90,    # 3 months
            "1W": 52,    # 1 year
            "1M": 12     # 1 year
        }
        
        # Timeframe mapping (WebSocket uses lowercase, REST API uses uppercase)
        self.timeframe_map = {
            "5m": "5m",
            "15m": "15m",
            "1H": "1h",
            "4H": "4h",
            "1D": "1d",
            "1W": "1w",
            "1M": "1M"
        }

        # Milliseconds corresponding to each timeframe (for data freshness judgment)
        self.timeframe_ms = {
            "5m": 5 * 60 * 1000,
            "15m": 15 * 60 * 1000,
            "1H": 60 * 60 * 1000,
            "4H": 4 * 60 * 60 * 1000,
            "1D": 24 * 60 * 60 * 1000,
            "1W": 7 * 24 * 60 * 60 * 1000,
            "1M": 30 * 24 * 60 * 60 * 1000  # Approximate value
        }
        
    async def start(self):
        """Main startup function"""
        logger.info("Starting OKX Market Sync...")
        
        try:
            # Initialize concurrency semaphore
            self._rest_sem = asyncio.Semaphore(self.rest_concurrency)
            # 0. Create data directory
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 1. Update product basic info (if needed)
            await self.update_instruments_info()
            
            # 2. Get list of products to synchronize
            instruments = await self.get_instruments()
            logger.info(f"Found {len(instruments)} USDT-SWAP instruments")
            
            # 3. Load existing data (if exists)
            self.load_existing_data()
            
            # 4. Get historical candlestick data
            await self.fetch_all_history(instruments)
            logger.info("Historical data loaded")
            
            # 5. Save initial data
            self.save_all_data()
            
            # 6. Start WebSocket, data consistency patrol and periodic saving
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
        """Load existing data files"""
        if not os.path.exists(self.data_dir):
            return
        
        # Read summary file to get product list
        if os.path.exists(self.summary_file):
            try:
                with open(self.summary_file, 'r') as f:
                    summary = json.load(f)
                    instruments = summary.get('instruments', [])
                    
                    # Load data file for each product
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
        """Update product basic info (24-hour cache)"""
        # Check if update is needed
        if os.path.exists(self.instruments_file):
            file_time = os.path.getmtime(self.instruments_file)
            current_time = time.time()
            age_hours = (current_time - file_time) / 3600
            
            if age_hours < self.instruments_cache_hours:
                logger.info(f"Instruments info is fresh ({age_hours:.1f}h old), skipping update")
                return
        
        logger.info("Updating instruments info...")
        
        # Get basic info for all SWAP products from API
        async with aiohttp.ClientSession() as session:
            url = f"{self.rest_url}/api/v5/public/instruments?instType=SWAP"
            async with session.get(url) as resp:
                data = await resp.json()
                if data['code'] != '0':
                    logger.error(f"Failed to get instruments info: {data}")
                    return
                
                all_instruments = data['data']
        
        # Filter basic info for USDT contracts
        usdt_instruments = {}
        for inst in all_instruments:
            if (inst.get('instType') == 'SWAP' and 
                inst.get('settleCcy') == 'USDT' and 
                inst.get('state') == 'live'):
                usdt_instruments[inst['instId']] = inst
        
        # Save to file - use standard JSON format, each instrument ID as top-level key
        # Atomic write
        temp_file = f"{self.instruments_file}.tmp"
        with open(temp_file, 'w') as f:
            json.dump(usdt_instruments, f, indent=2, ensure_ascii=False)
        
        os.replace(temp_file, self.instruments_file)
        
        logger.info(f"Updated instruments info: {len(usdt_instruments)} USDT-SWAP instruments")
    
    async def get_instruments(self):
        """Get list of all USDT perpetual contract IDs"""
        # Read from local instruments.json file
        if not os.path.exists(self.instruments_file):
            logger.error(f"Instruments file {self.instruments_file} not found")
            return []
        
        try:
            with open(self.instruments_file, 'r') as f:
                instruments = json.load(f)
            
            # Get all instrument IDs directly (now top-level keys)
            usdt_swaps = list(instruments.keys())
            
            # Return all USDT-SWAP product IDs
            logger.info(f"Total USDT-SWAP instruments found: {len(usdt_swaps)}")
            return usdt_swaps
            
        except Exception as e:
            logger.error(f"Error reading instruments file: {e}")
            return []
    
    async def fetch_all_history(self, instruments):
        """Get historical candlesticks for all products (concurrent + rate limited)"""
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
        """WebSocket loop"""
        reconnect_delay = 1
        
        while True:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    logger.info("WebSocket connected")
                    reconnect_delay = 1  # Reset delay
                    
                    # Subscribe to candlestick data in batches (avoid exceeding 64KB limit)
                    # Each subscription is about 50 bytes, 64KB ≈ 1300 subscriptions
                    # 7 timeframes, so max 1300/7 ≈ 185 products per batch
                    # Use smaller batches for safety
                    batch_size = 15  # 15 products per batch = 105 subscriptions
                    timeframes = list(self.timeframe_map.items())
                    
                    for i in range(0, len(instruments), batch_size):
                        batch_instruments = instruments[i:i+batch_size]
                        
                        sub_msg = {
                            "op": "subscribe",
                            "args": []
                        }
                        
                        # Add all timeframe subscriptions for current batch of products
                        for inst_id in batch_instruments:
                            for tf, ws_tf in timeframes:
                                sub_msg["args"].append({
                                    "channel": f"candle{ws_tf}",
                                    "instId": inst_id
                                })
                        
                        logger.info(f"Subscribing batch {i//batch_size + 1}: {len(batch_instruments)} instruments, {len(sub_msg['args'])} subscriptions")
                        await ws.send(json.dumps(sub_msg))
                        await asyncio.sleep(1)  # Give server more time to process
                    
                    logger.info(f"Subscribed to {len(instruments)} instruments")
                    
                    # Start heartbeat task
                    heartbeat_task = asyncio.create_task(self.heartbeat_loop(ws))
                    
                    try:
                        # Receive data
                        async for message in ws:
                            try:
                                # Handle pong response
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
                        # Cancel heartbeat task
                        heartbeat_task.cancel()
                        try:
                            await heartbeat_task
                        except asyncio.CancelledError:
                            pass
                            
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(reconnect_delay)
                reconnect_delay = min(reconnect_delay * 2, 60)  # Exponential backoff, max 60 seconds
    
    async def heartbeat_loop(self, ws):
        """Heartbeat loop - send ping every 25 seconds"""
        try:
            while True:
                await asyncio.sleep(25)  # Send every 25 seconds (safe value under 30 seconds)
                await ws.send('ping')
                logger.debug("Sent ping")
        except asyncio.CancelledError:
            logger.debug("Heartbeat task cancelled")
            raise
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            raise
    
    def update_candle(self, msg):
        """Update candlestick data"""
        arg = msg['arg']
        channel = arg.get('channel', '')
        inst_id = arg.get('instId', '')
        
        if not inst_id or 'candle' not in channel:
            return
        
        # Extract time period
        ws_bar = channel.replace('candle', '')
        
        # Find corresponding standard timeframe
        bar = None
        for tf, ws_tf in self.timeframe_map.items():
            if ws_tf == ws_bar:
                bar = tf
                break
        
        if not bar or bar not in self.candle_limits:
            return
        
        # Ensure data structure exists
        if inst_id not in self.market_data:
            self.market_data[inst_id] = {}
        if bar not in self.market_data[inst_id]:
            self.market_data[inst_id][bar] = {
                "latest_ts": 0,
                "candles": []
            }
        
        # Update data
        new_candles = msg['data']
        bar_data = self.market_data[inst_id][bar]
        
        for new_candle in new_candles:
            ts = int(new_candle[0])
            
            # Update latest timestamp
            if ts > bar_data["latest_ts"]:
                bar_data["latest_ts"] = ts
            
            # Check if update is needed
            updated = False
            for i, candle in enumerate(bar_data["candles"]):
                if int(candle[0]) == ts:
                    bar_data["candles"][i] = new_candle
                    updated = True
                    break
            
            # If it's a new candlestick, add to the beginning
            if not updated:
                bar_data["candles"].insert(0, new_candle)
                # Maintain limited quantity
                limit = self.candle_limits[bar]
                bar_data["candles"] = bar_data["candles"][:limit]

    async def consistency_loop(self, instruments):
        """Data consistency patrol and auto-backfill: ensure all timeframes are gap-free, up-to-date and meet length standards"""
        # Patrol interval (seconds)
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
                            # Only perform auto-backfill for allowed periods
                            if bar not in self.consistency_allowed_bars:
                                continue
                            if self._need_refresh_or_backfill(inst_id, bar):
                                refresh_tasks.append(self._refresh_recent_candles(session, inst_id, bar, limit))
                    if refresh_tasks:
                        await asyncio.gather(*refresh_tasks)
            except Exception as e:
                logger.warning(f"Consistency loop warning: {e}")
            # Wait for next round
            await asyncio.sleep(interval_seconds)

    def _need_refresh_or_backfill(self, inst_id: str, bar: str) -> bool:
        """Determine if this product/period needs refresh (insufficient length/too old/gaps exist)"""
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
            # Too old
            now_ms = int(time.time() * 1000)
            if latest_ts == 0 or (now_ms - latest_ts) > bar_ms * 3:
                return True
            # Gaps: check time intervals of recent candlesticks
            check_n = min(50, len(candles) - 1)
            for i in range(check_n):
                try:
                    ts_curr = int(candles[i][0])
                    ts_next = int(candles[i + 1][0])
                except Exception:
                    return True
                gap = ts_curr - ts_next
                # Allow small jitter due to matching delays, threshold 1.5 bars
                if gap > int(bar_ms * 1.5):
                    return True
            return False
        except Exception:
            return True

    async def _refresh_recent_candles(self, session: aiohttp.ClientSession, inst_id: str, bar: str, limit: int):
        """Use REST to refresh recent candlesticks for this product/period, fix gaps and staleness"""
        url = f"{self.rest_url}/api/v5/market/candles"
        params = {'instId': inst_id, 'bar': bar, 'limit': str(min(limit, 300))}
        try:
            await self.rate_limiter.acquire()
            async with self._rest_sem:
                async with session.get(url, params=params) as resp:
                    data = await resp.json()
            if data.get('code') == '0' and data.get('data'):
                candles = data['data']
                # Overwrite
                if inst_id not in self.market_data:
                    self.market_data[inst_id] = {}
                if bar not in self.market_data[inst_id]:
                    self.market_data[inst_id][bar] = {"latest_ts": 0, "candles": []}
                self.market_data[inst_id][bar]["candles"] = candles
                self.market_data[inst_id][bar]["latest_ts"] = int(candles[0][0]) if candles else 0
                logger.info(f"Refreshed {bar} candles for {inst_id} (consistency)")
                # Mark throttle time
                self.last_refresh.setdefault(inst_id, {})[bar] = int(time.time() * 1000)
            else:
                logger.warning(f"Failed to refresh {inst_id} {bar}: {data}")
        except Exception as e:
            logger.warning(f"Refresh error for {inst_id} {bar}: {e}")
    
    async def save_loop(self):
        """Periodically save data"""
        while True:
            await asyncio.sleep(self.save_interval)
            self.save_all_data()
            logger.info(f"Data saved - {len(self.market_data)} instruments")
    
    def save_all_data(self):
        """Save all data to separate files"""
        current_time = datetime.now().isoformat()
        
        # Save summary file
        summary = {
            'update_time': current_time,
            'instrument_count': len(self.market_data),
            'instruments': list(self.market_data.keys())
        }
        
        # Atomic write summary file
        temp_summary = f"{self.summary_file}.tmp"
        with open(temp_summary, 'w') as f:
            json.dump(summary, f, separators=(',', ':'))
        os.replace(temp_summary, self.summary_file)
        
        # Save data file for each product
        for inst_id, inst_data in self.market_data.items():
            self.save_instrument_data(inst_id, inst_data, current_time)
    
    def save_instrument_data(self, inst_id, inst_data, update_time):
        """Save data for a single product"""
        output = {
            'update_time': update_time,
            'instrument': inst_id,
            'data': inst_data
        }
        
        # Atomic write product data file
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