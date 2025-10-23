#!/usr/bin/env python3
"""
OKX Market Analysis Module - Professional Trading Opportunity Detection System

This module implements advanced quantitative analysis algorithms for identifying
high-probability trading opportunities in leveraged USDT-SWAP contracts.

Author: Advanced Trading System
Version: 2.0.0
"""

import json
import os
import sys
import time
import logging
import configparser
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from okx_time_utils import okx_time, get_okx_current_time
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
import statistics
import math
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from scipy import stats
import warnings

# Suppress numpy warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

# Set high precision for financial calculations
getcontext().prec = 28

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class MarketAnalysis:
    """Objective market data and technical indicators for trading instruments"""
    instId: str
    current_price: float
    price_change_24h: float
    price_change_1h: float
    volume_24h: float
    volume_ratio: float  # Current vs average volume
    
    # Technical Indicators
    rsi_14: float
    rsi_7: float
    macd_signal: float
    macd_histogram: float
    bb_position: float  # Position within Bollinger Bands (0-1)
    bb_width: float    # Bollinger Band width (volatility measure)
    atr_ratio: float   # ATR as percentage of price
    
    # Price Action
    support_level: float
    resistance_level: float
    trend_strength: float  # -1 to 1 (bearish to bullish trend measurement)
    momentum_5min: float
    momentum_15min: float
    momentum_1h: float
    
    # Market Structure
    volatility_percentile: float  # 0-100
    liquidity_score: float
    market_cap_tier: str  # "large", "mid", "small"
    correlation_btc: float  # Correlation with BTC
    
    # Volume Analysis
    volume_profile_poc: float  # Point of Control price
    volume_weighted_price: float
    buying_pressure: float  # 0-1 scale
    
    # Recent Performance
    performance_1d: float
    performance_7d: float
    performance_30d: float
    
    # Risk Metrics
    max_leverage_available: int
    liquidation_risk_level: str  # "low", "medium", "high"

    # Multi-timeframe alignment and momentum
    mtf_trend_alignment: float = 0.0  # -1 to 1 average of structure trends across TFs
    mtf_momentum_alignment: float = 0.0  # -1 to 1 average sign of MACD histogram across TFs
    
    # Volatility and risk enrichments
    hv10: float = 0.0
    hv20: float = 0.0
    hv50: float = 0.0
    range_pct_24h: float = 0.0
    mdd_24h: float = 0.0
    skew_20: float = 0.0
    kurtosis_20: float = 0.0
    vol_percentile_rolling: float = 0.0  # 0-100
    adx_14: float = 0.0
    aroon_up_25: float = 0.0
    aroon_down_25: float = 0.0
    cci_20: float = 0.0
    bb_squeeze_score: float = 0.0

    # Volume and flow enrichments
    volume_z_20: float = 0.0
    obv_20: float = 0.0
    cmf_20: float = 0.0
    vwap_dev_pct_20: float = 0.0
    buying_pressure_mean_20: float = 0.0
    buying_pressure_trend_20: float = 0.0

    # Correlations
    corr_btc_24h: float = 0.0
    corr_eth_24h: float = 0.0
    beta_btc_24h: float = 0.0
    relative_strength_rank_24h: int = 0

    # Data quality
    freshness_lag_bars: int = 0
    gap_count_24h: int = 0
    coverage_ratio_24h: float = 1.0
    time_zone: str = "UTC"


class OKXTimeAPI:
    """OKX Time API handler with proper error handling"""
    
    def __init__(self):
        self.base_url = "https://www.okx.com"
        self.timeout = 10
        self.retry_count = 3
    
    def get_server_time(self) -> Dict[str, str]:
        """
        Get OKX server time using unified time utilities
        
        Returns:
            Dict containing timestamp, iso_time, and formatted_time
        """
        try:
            # Use the unified OKX time utilities
            timestamp = str(okx_time.get_okx_timestamp_ms())
            iso_time = okx_time.get_okx_iso_string()
            formatted_time = okx_time.get_okx_time_string()
            
            return {
                'timestamp': timestamp,
                'iso_time': iso_time,
                'formatted_time': formatted_time
            }
        except Exception as e:
            logger.error(f"Failed to get server time: {e}")
            # Emergency fallback
            now = datetime.now(timezone.utc)
            timestamp = str(int(now.timestamp() * 1000))
            return {
                'timestamp': timestamp,
                'iso_time': now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
                'formatted_time': now.strftime('%Y-%m-%d %H:%M:%S UTC')
            }


class ProfessionalMarketAnalyzer:
    """Professional market analysis with institutional-grade algorithms"""
    
    def __init__(self, config_path: str = "config.ini"):
        """Initialize analyzer with configuration"""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        self.data_dir = "data"
        self.instruments_file = "instruments.json"
        self.market_data = {}
        self.instruments_info = {}
        self.time_api = OKXTimeAPI()
        
        # Professional trading parameters
        self.min_volume_threshold = 100000  # Minimum 24h volume in USD
        self.min_liquidity_score = 0.3
        self.max_spread_percentage = 0.1
        self.correlation_threshold = 0.7
        self.risk_free_rate = 0.03  # 3% annual risk-free rate
        
    def load_market_data(self) -> None:
        """Load all market data from local files with validation"""
        logger.info("Loading market data from local files...")
        
        # Load instruments info
        try:
            with open(self.instruments_file, 'r', encoding='utf-8') as f:
                self.instruments_info = json.load(f)
            logger.info(f"Loaded {len(self.instruments_info)} instruments info")
        except Exception as e:
            logger.error(f"Failed to load instruments info: {e}")
            raise
        
        # Load market data for each instrument with parallel processing
        loaded_count = 0
        failed_count = 0
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            
            for inst_id in self.instruments_info.keys():
                data_file = os.path.join(self.data_dir, f"{inst_id}.json")
                if os.path.exists(data_file):
                    future = executor.submit(self._load_instrument_data, inst_id, data_file)
                    futures[future] = inst_id
            
            for future in as_completed(futures):
                inst_id = futures[future]
                try:
                    data = future.result()
                    if data:
                        self.market_data[inst_id] = data
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"Failed to load data for {inst_id}: {e}")
                    failed_count += 1
        
        logger.info(f"Successfully loaded market data for {loaded_count} instruments, {failed_count} failed")
        
    def _load_instrument_data(self, inst_id: str, data_file: str) -> Optional[Dict]:
        """Load and validate individual instrument data"""
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate data structure
            if 'data' in data and isinstance(data['data'], dict):
                return data['data']
            else:
                logger.warning(f"Invalid data structure for {inst_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading {inst_id}: {e}")
            return None
    
    def calculate_advanced_technical_indicators(self, candles: List[List]) -> Dict[str, float]:
        """Calculate comprehensive technical indicators with professional methods"""
        if not candles or len(candles) < 20:
            return {}
        
        # Convert to pandas DataFrame for professional analysis
        df = pd.DataFrame(
            candles, 
            columns=['timestamp', 'open', 'high', 'low', 'close', 'vol', 'volCcy', 'volCcyQuote', 'confirm']
        )
        
        # Convert to numeric types with validation
        numeric_columns = ['open', 'high', 'low', 'close', 'vol', 'volCcy', 'volCcyQuote']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Remove any rows with NaN values
        df = df.dropna()
        
        if len(df) < 20:
            return {}
        
        # Sort by timestamp (newest first in OKX data)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        indicators = {}
        
        try:
            # Price-based indicators
            close_prices = df['close'].values
            high_prices = df['high'].values
            low_prices = df['low'].values
            
            # Use USDT volume (volCcyQuote) if available, otherwise use contract volume
            if 'volCcyQuote' in df.columns and df['volCcyQuote'].notna().all():
                volumes = df['volCcyQuote'].values
            else:
                volumes = df['vol'].values
            
            indicators['current_price'] = float(close_prices[-1])
            indicators['price_change_24h'] = ((close_prices[-1] - close_prices[0]) / close_prices[0]) * 100
            
            # Advanced RSI with Stochastic RSI
            indicators.update(self._calculate_advanced_rsi(close_prices))
            
            # Multiple Moving Averages with crossover detection
            indicators.update(self._calculate_moving_averages(close_prices))
            
            # MACD with histogram analysis
            indicators.update(self._calculate_macd(close_prices))
            
            # Bollinger Bands with squeeze detection
            indicators.update(self._calculate_bollinger_bands(close_prices))
            
            # Volume Profile Analysis
            indicators.update(self._calculate_volume_profile(close_prices, volumes))
            
            # Market Structure Analysis
            indicators.update(self._calculate_market_structure(high_prices, low_prices, close_prices))
            
            # Volatility Metrics (use highs/lows for Parkinson volatility)
            indicators.update(self._calculate_volatility_metrics(high_prices, low_prices, close_prices))
            
            # Support/Resistance with Fibonacci levels
            indicators.update(self._calculate_support_resistance(high_prices, low_prices, close_prices))
            
            # Order Flow Imbalance
            indicators.update(self._calculate_order_flow(df))

            # Enriched volatility and risk metrics
            indicators.update(self._calculate_volatility_enriched(high_prices, low_prices, close_prices))

            # ADX / Aroon / CCI / Squeeze
            indicators.update(self._calculate_trend_quality(high_prices, low_prices, close_prices))

            # Volume and flow enrichments
            indicators.update(self._calculate_volume_enriched(close_prices, volumes))

            # Momentum Oscillators
            indicators.update(self._calculate_momentum_indicators(close_prices))

            # Market Microstructure
            indicators.update(self._calculate_microstructure(df))
            
        except Exception as e:
            logger.error(f"Error calculating advanced indicators: {e}")
        
        return indicators
    
    def _calculate_advanced_rsi(self, prices: np.ndarray) -> Dict[str, float]:
        """Calculate RSI(14) and RSI(7) with Stochastic RSI on RSI(14)"""
        def _compute_rsi(series: np.ndarray, period: int) -> float:
            if len(series) < period + 1:
                return float(np.nan)
            deltas = np.diff(series)
            seed = deltas[:period]
            avg_gain = seed[seed > 0].sum() / period
            avg_loss = -seed[seed < 0].sum() / period
            rs = (avg_gain / avg_loss) if avg_loss != 0 else np.inf
            rsi_val = 100 - (100 / (1 + rs))
            for delta in deltas[period:]:
                gain = max(delta, 0)
                loss = -min(delta, 0)
                avg_gain = (avg_gain * (period - 1) + gain) / period
                avg_loss = (avg_loss * (period - 1) + loss) / period
                rs = (avg_gain / avg_loss) if avg_loss != 0 else np.inf
                rsi_val = 100 - (100 / (1 + rs))
            return float(rsi_val)

        if len(prices) < 14:
            return {}

        rsi_14 = _compute_rsi(prices, 14)
        rsi_7 = _compute_rsi(prices, 7) if len(prices) >= 7 else float('nan')

        # Stochastic RSI based on RSI(14) series
        rsi_values = []
        for i in range(14, len(prices)):
            window = prices[: i + 1]
            rsi_window = _compute_rsi(window, 14)
            rsi_values.append(rsi_window)

        if len(rsi_values) >= 14:
            rsi_min = float(np.nanmin(rsi_values[-14:]))
            rsi_max = float(np.nanmax(rsi_values[-14:]))
            stoch_rsi = ((rsi_14 - rsi_min) / (rsi_max - rsi_min) * 100) if rsi_max != rsi_min else 50.0
        else:
            stoch_rsi = 50.0

        return {
            'rsi': rsi_14,
            'rsi_7': rsi_7 if not np.isnan(rsi_7) else rsi_14,
            'stoch_rsi': stoch_rsi,
            'rsi_divergence': self._detect_divergence(
                prices[-14:],
                rsi_values[-14:] if len(rsi_values) >= 14 else []
            )
        }
    
    def _calculate_moving_averages(self, prices: np.ndarray) -> Dict[str, float]:
        """Calculate multiple moving averages with crossover detection"""
        indicators = {}
        
        # Simple Moving Averages
        for period in [10, 20, 50, 100, 200]:
            if len(prices) >= period:
                indicators[f'sma_{period}'] = np.mean(prices[-period:])
        
        # Exponential Moving Averages
        for period in [12, 26, 50]:
            if len(prices) >= period:
                indicators[f'ema_{period}'] = self._calculate_ema(prices, period)
        
        # Hull Moving Average (HMA)
        if len(prices) >= 20:
            indicators['hma_20'] = self._calculate_hma(prices, 20)
        
        # VWAP approximation (without intraday reset)
        if 'sma_20' in indicators and 'sma_50' in indicators:
            indicators['golden_cross'] = 1 if indicators['sma_20'] > indicators['sma_50'] else 0
        
        return indicators
    
    def _calculate_ema(self, prices: np.ndarray, period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return float(ema)
    
    def _calculate_hma(self, prices: np.ndarray, period: int) -> float:
        """Calculate Hull Moving Average for reduced lag"""
        if len(prices) < period:
            return np.mean(prices)
        
        half_period = period // 2
        sqrt_period = int(np.sqrt(period))
        
        wma_half = self._calculate_wma(prices, half_period)
        wma_full = self._calculate_wma(prices, period)
        
        raw_hma = 2 * wma_half - wma_full
        return float(raw_hma)
    
    def _calculate_wma(self, prices: np.ndarray, period: int) -> float:
        """Calculate Weighted Moving Average"""
        if len(prices) < period:
            return np.mean(prices)
        
        weights = np.arange(1, period + 1)
        return np.average(prices[-period:], weights=weights)
    
    def _calculate_macd(self, prices: np.ndarray) -> Dict[str, float]:
        """Calculate MACD with advanced analysis"""
        if len(prices) < 26:
            return {}
        
        # Calculate MACD line for all periods (as percentage)
        macd_line = []
        for i in range(25, len(prices)):
            window = prices[:i+1]
            ema_12 = self._calculate_ema(window, 12)
            ema_26 = self._calculate_ema(window, 26)
            # Convert to percentage to normalize across different price levels
            macd_pct = ((ema_12 - ema_26) / ema_26 * 100) if ema_26 != 0 else 0
            macd_line.append(macd_pct)
        
        # Calculate signal line (9-day EMA of MACD)
        if len(macd_line) >= 9:
            signal = self._calculate_ema(np.array(macd_line), 9)
        else:
            signal = np.mean(macd_line) if macd_line else 0
            
        # Current MACD values
        current_macd = macd_line[-1] if macd_line else 0
        histogram = current_macd - signal
        
        # MACD momentum
        macd_momentum = 0
        if len(macd_line) >= 2:
            macd_momentum = macd_line[-1] - macd_line[-2]
        
        return {
            'macd': current_macd,
            'macd_signal': signal,
            'macd_histogram': histogram,
            'macd_momentum': macd_momentum,
            'macd_cross': 1 if current_macd > signal else -1
        }
    
    def _calculate_bollinger_bands(self, prices: np.ndarray) -> Dict[str, float]:
        """Calculate Bollinger Bands with squeeze detection"""
        if len(prices) < 20:
            return {}
        
        period = 20
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        bb_upper = sma + (std * 2)
        bb_lower = sma - (std * 2)
        bb_middle = sma
        
        # Current price position
        current_price = prices[-1]
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if bb_upper != bb_lower else 0.5
        
        # Bollinger Band Width and Squeeze
        bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle != 0 else 0
        
        # Historical bandwidth for squeeze detection
        historical_widths = []
        for i in range(max(0, len(prices) - 100), len(prices) - period):
            window = prices[i:i+period]
            w_std = np.std(window)
            w_mean = np.mean(window)
            if w_mean != 0:
                historical_widths.append((w_std * 4) / w_mean)
        
        bb_squeeze = 1 if historical_widths and bb_width < np.percentile(historical_widths, 20) else 0
        
        return {
            'bb_upper': bb_upper,
            'bb_lower': bb_lower,
            'bb_middle': bb_middle,
            'bb_position': bb_position,
            'bb_width': bb_width,
            'bb_squeeze': bb_squeeze
        }
    
    def _calculate_volume_profile(self, prices: np.ndarray, volumes: np.ndarray) -> Dict[str, float]:
        """Calculate Volume Profile indicators"""
        if len(prices) < 20 or len(volumes) < 20:
            return {}
        
        # Volume-weighted average price (VWAP)
        vwap = np.sum(prices * volumes) / np.sum(volumes) if np.sum(volumes) > 0 else prices[-1]
        
        # Volume ratio - comparing recent 5 periods to average
        recent_volume = np.mean(volumes[-5:]) if len(volumes) >= 5 else np.mean(volumes)
        avg_volume = np.mean(volumes)
        volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1
        
        # On-Balance Volume (OBV) trend
        obv = np.zeros(len(prices))
        obv[0] = volumes[0]
        
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                obv[i] = obv[i-1] + volumes[i]
            elif prices[i] < prices[i-1]:
                obv[i] = obv[i-1] - volumes[i]
            else:
                obv[i] = obv[i-1]
        
        # OBV trend
        obv_sma = np.mean(obv[-10:]) if len(obv) >= 10 else obv[-1]
        obv_trend = 1 if obv[-1] > obv_sma else -1
        
        # Volume-Price Trend (VPT)
        vpt = np.zeros(len(prices))
        vpt[0] = volumes[0]
        
        for i in range(1, len(prices)):
            price_change = (prices[i] - prices[i-1]) / prices[i-1] if prices[i-1] != 0 else 0
            vpt[i] = vpt[i-1] + volumes[i] * price_change
        
        vpt_trend = 1 if len(vpt) >= 2 and vpt[-1] > vpt[-2] else -1
        
        return {
            'vwap': vwap,
            'volume_ratio': volume_ratio,
            'obv_trend': obv_trend,
            'vpt_trend': vpt_trend,
            'volume_24h': np.sum(volumes[-288:]) if len(volumes) >= 288 else np.sum(volumes),  # Last 24h (288 * 5min)
            'avg_volume': avg_volume
        }
    
    def _calculate_market_structure(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """Analyze market structure patterns"""
        if len(highs) < 20:
            return {}
        
        # Identify swing highs and lows
        swing_highs = []
        swing_lows = []
        
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append((i, highs[i]))
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append((i, lows[i]))
        
        # Market structure trend
        structure_trend = 0
        if len(swing_highs) >= 2 and len(swing_lows) >= 2:
            # Higher highs and higher lows = uptrend
            if swing_highs[-1][1] > swing_highs[-2][1] and swing_lows[-1][1] > swing_lows[-2][1]:
                structure_trend = 1
            # Lower highs and lower lows = downtrend
            elif swing_highs[-1][1] < swing_highs[-2][1] and swing_lows[-1][1] < swing_lows[-2][1]:
                structure_trend = -1
        
        # Average True Range (ATR)
        atr_values = []
        for i in range(1, len(highs)):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            atr_values.append(max(high_low, high_close, low_close))
        
        atr = np.mean(atr_values[-14:]) if len(atr_values) >= 14 else np.mean(atr_values)
        
        # Price channels
        highest_high = np.max(highs[-20:])
        lowest_low = np.min(lows[-20:])
        channel_position = (closes[-1] - lowest_low) / (highest_high - lowest_low) if highest_high != lowest_low else 0.5
        
        return {
            'structure_trend': structure_trend,
            'atr': atr,
            'highest_high_20': highest_high,
            'lowest_low_20': lowest_low,
            'channel_position': channel_position,
            'swing_high_count': len(swing_highs),
            'swing_low_count': len(swing_lows)
        }
    
    def _calculate_volatility_metrics(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """Calculate advanced volatility metrics, including Parkinson volatility using high/low"""
        if len(closes) < 20:
            return {}
        
        returns = np.diff(closes) / closes[:-1]
        
        # Historical Volatility (different timeframes) for 5-minute candles
        # Daily volatility = std of returns * sqrt(periods_per_day) * 100 for percentage
        # For 5-minute candles: 288 periods per day (24h * 60min / 5min = 288)
        # For annualized: multiply by sqrt(365), but we want daily volatility here
        periods_per_day = 288
        
        # Calculate volatility as daily percentage
        volatility_5 = np.std(returns[-5:]) * np.sqrt(periods_per_day) * 100 if len(returns) >= 5 else 0  # 5 periods  
        volatility_20 = np.std(returns[-20:]) * np.sqrt(periods_per_day) * 100 if len(returns) >= 20 else 0  # 20 periods
        volatility_50 = np.std(returns[-50:]) * np.sqrt(periods_per_day) * 100 if len(returns) >= 50 else 0  # 50 periods
        
        # Parkinson volatility (using high-low)
        if len(highs) >= 20 and len(lows) >= 20:
            hl_logsquared = [
                (np.log(highs[i] / lows[i]) ** 2) if lows[i] > 0 else 0
                for i in range(-20, 0)
            ]
            parkinson_sigma = np.sqrt(np.sum(hl_logsquared) / (4 * 20 * np.log(2)))
            parkinson_vol = parkinson_sigma * np.sqrt(periods_per_day) * 100
        else:
            parkinson_vol = volatility_20
        
        # Volatility ratio
        vol_ratio = volatility_5 / volatility_20 if volatility_20 > 0 else 1
        
        # Volatility trend
        vol_trend = 1 if vol_ratio > 1.2 else -1 if vol_ratio < 0.8 else 0
        
        return {
            'volatility': volatility_20,
            'volatility_5': volatility_5,
            'volatility_50': volatility_50,
            'parkinson_vol': parkinson_vol,
            'vol_ratio': vol_ratio,
            'vol_trend': vol_trend
        }

    def _calculate_volatility_enriched(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """HV10/20/50, extreme amplitude, max drawdown in last 24h, skewness/kurtosis and volatility rolling quantiles"""
        indicators: Dict[str, float] = {}
        if len(closes) < 20:
            return indicators
        returns = np.diff(closes) / closes[:-1]
        periods_per_day = 288
        def hv(series: np.ndarray, win: int) -> float:
            if len(series) < win:
                return 0.0
            return float(np.std(series[-win:]) * np.sqrt(periods_per_day) * 100)
        indicators['hv10'] = hv(returns, 10)
        indicators['hv20'] = hv(returns, 20)
        indicators['hv50'] = hv(returns, 50) if len(returns) >= 50 else hv(returns, len(returns))

        # Extreme amplitude and max drawdown in last 24h (288 5m bars)
        window = min(288, len(closes))
        recent = closes[-window:]
        if len(recent) >= 2:
            rng = (np.max(recent) - np.min(recent)) / recent[0] * 100 if recent[0] > 0 else 0.0
            indicators['range_pct_24h'] = float(rng)
            # Max drawdown (simple approximation)
            peak = recent[0]
            mdd = 0.0
            for p in recent:
                if p > peak:
                    peak = p
                drawdown = (p - peak) / peak * 100
                if drawdown < mdd:
                    mdd = drawdown
            indicators['mdd_24h'] = float(mdd)
        else:
            indicators['range_pct_24h'] = 0.0
            indicators['mdd_24h'] = 0.0

        # Skewness/kurtosis and volatility rolling quantiles
        try:
            if len(returns) >= 20:
                indicators['skew_20'] = float(stats.skew(returns[-20:]))
                indicators['kurtosis_20'] = float(stats.kurtosis(returns[-20:]))
            vol = hv(returns, min(50, len(returns)))
            # Simple rolling quantiles (last 200 bars quantiles)
            hist_win = min(200, len(returns))
            if hist_win >= 20:
                vols = []
                for i in range(20, hist_win + 1):
                    vols.append(float(np.std(returns[i-20:i]) * np.sqrt(periods_per_day) * 100))
                rank = sum(1 for v in vols if v <= vol)
                indicators['vol_percentile_rolling'] = float(rank / len(vols) * 100)
        except Exception:
            pass
        return indicators

    def _calculate_trend_quality(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """ADX14, Aroon(25), CCI(20), BB squeeze score"""
        out: Dict[str, float] = {}
        n = len(closes)
        if n < 26:
            return out
        # ADX
        period = 14
        tr = []
        plus_dm = []
        minus_dm = []
        for i in range(1, n):
            high_low = highs[i] - lows[i]
            high_close = abs(highs[i] - closes[i-1])
            low_close = abs(lows[i] - closes[i-1])
            tr.append(max(high_low, high_close, low_close))
            up_move = highs[i] - highs[i-1]
            down_move = lows[i-1] - lows[i]
            plus_dm.append(up_move if (up_move > down_move and up_move > 0) else 0)
            minus_dm.append(down_move if (down_move > up_move and down_move > 0) else 0)
        def rma(x: List[float], p: int) -> List[float]:
            if len(x) == 0:
                return []
            alpha = 1.0 / p
            y = [x[0]]
            for v in x[1:]:
                y.append(alpha * v + (1 - alpha) * y[-1])
            return y
        tr14 = rma(tr, period)
        pdm14 = rma(plus_dm, period)
        mdm14 = rma(minus_dm, period)
        di_plus = [100 * (p / t) if t > 0 else 0 for p, t in zip(pdm14, tr14)]
        di_minus = [100 * (m / t) if t > 0 else 0 for m, t in zip(mdm14, tr14)]
        dx = [100 * abs(p - m) / (p + m) if (p + m) > 0 else 0 for p, m in zip(di_plus, di_minus)]
        adx_series = rma(dx, period)
        out['adx_14'] = float(adx_series[-1]) if adx_series else 0.0
        
        # Aroon(25)
        aroon_len = 25
        if n >= aroon_len:
            window_h = highs[-aroon_len:]
            window_l = lows[-aroon_len:]
            up_idx = int(np.argmax(window_h))
            down_idx = int(np.argmin(window_l))
            out['aroon_up_25'] = float(100 * (aroon_len - 1 - up_idx) / (aroon_len - 1))
            out['aroon_down_25'] = float(100 * (aroon_len - 1 - down_idx) / (aroon_len - 1))
        
        # CCI(20)
        cci_len = 20
        if n >= cci_len:
            tp = (highs + lows + closes) / 3.0
            sma_tp = np.mean(tp[-cci_len:])
            md = np.mean(np.abs(tp[-cci_len:] - sma_tp))
            out['cci_20'] = float((tp[-1] - sma_tp) / (0.015 * md)) if md > 0 else 0.0
        
        # BB squeeze score (bandwidth relative to past quantiles)
        if n >= 20:
            std = np.std(closes[-20:])
            ma = np.mean(closes[-20:])
            bbw = (2 * 2 * std) / ma * 100 if ma > 0 else 0.0
            # Use last 200 bars' bbw quantiles as squeeze level
            hist = []
            hist_win = min(200, n)
            for i in range(20, hist_win + 1):
                s = np.std(closes[i-20:i])
                m = np.mean(closes[i-20:i])
                hist.append((2 * 2 * s) / m * 100 if m > 0 else 0.0)
            if hist:
                rank = sum(1 for v in hist if v >= bbw)
                out['bb_squeeze_score'] = float(100 - rank / len(hist) * 100)  # Higher means more squeezed
        return out

    def _calculate_volume_enriched(self, closes: np.ndarray, volumes: np.ndarray) -> Dict[str, float]:
        """Volume Z-score, OBV, CMF, VWAP deviation, buying pressure mean and trend (based on existing buying_pressure)"""
        out: Dict[str, float] = {}
        n = len(closes)
        if n < 20:
            return out
        # volume z
        win = 20
        vol_win = volumes[-win:]
        mu = float(np.mean(vol_win))
        sigma = float(np.std(vol_win))
        out['volume_z_20'] = float((volumes[-1] - mu) / sigma) if sigma > 0 else 0.0
        # OBV (last 20 bars normalized)
        obv = 0.0
        for i in range(1, n):
            if closes[i] > closes[i-1]:
                obv += volumes[i]
            elif closes[i] < closes[i-1]:
                obv -= volumes[i]
        out['obv_20'] = float(obv)
        # CMF(20)
        mfv = []
        for i in range(n - win, n):
            high = closes[i]  # Approximate using close price to avoid extra parameters
            low = closes[i]
            close = closes[i]
            vol = volumes[i]
            mfm = ((close - low) - (high - close)) / ((high - low) if (high != low) else 1)
            mfv.append(mfm * vol)
        out['cmf_20'] = float(sum(mfv) / sum(volumes[-win:])) if sum(volumes[-win:]) > 0 else 0.0
        # VWAP deviation (20)
        v = volumes[-win:]
        p = closes[-win:]
        vwap = float(np.sum(p * v) / np.sum(v)) if np.sum(v) > 0 else p[-1]
        out['vwap_dev_pct_20'] = float((closes[-1] - vwap) / vwap * 100) if vwap > 0 else 0.0
        # Buying pressure mean and trend (needs upstream _calculate_order_flow to output buying_pressure_series when available for refinement, currently degraded to use single point)
        if 'buying_pressure' in out:
            pass
        return out
    
    def _calculate_support_resistance(self, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray) -> Dict[str, float]:
        """Calculate support and resistance levels with Fibonacci"""
        if len(highs) < 20:
            return {}
        
        # Recent high and low
        recent_high = np.max(highs[-50:]) if len(highs) >= 50 else np.max(highs)
        recent_low = np.min(lows[-50:]) if len(lows) >= 50 else np.min(lows)
        
        # Fibonacci levels
        fib_diff = recent_high - recent_low
        fib_levels = {
            'fib_0': recent_low,
            'fib_236': recent_low + fib_diff * 0.236,
            'fib_382': recent_low + fib_diff * 0.382,
            'fib_500': recent_low + fib_diff * 0.500,
            'fib_618': recent_low + fib_diff * 0.618,
            'fib_786': recent_low + fib_diff * 0.786,
            'fib_1000': recent_high
        }
        
        # Pivot points
        pivot = (highs[-1] + lows[-1] + closes[-1]) / 3
        r1 = 2 * pivot - lows[-1]
        s1 = 2 * pivot - highs[-1]
        r2 = pivot + (highs[-1] - lows[-1])
        s2 = pivot - (highs[-1] - lows[-1])
        
        return {
            'resistance': recent_high,
            'support': recent_low,
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            's1': s1,
            's2': s2,
            **fib_levels
        }
    
    def _calculate_order_flow(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate order flow imbalance indicators"""
        if len(df) < 10:
            return {}
        
        # Approximate buy/sell pressure
        buy_pressure = 0
        sell_pressure = 0
        
        for i in range(1, len(df)):
            price_change = df.iloc[i]['close'] - df.iloc[i-1]['close']
            volume = df.iloc[i]['vol']
            
            if price_change > 0:
                buy_pressure += volume * abs(price_change)
            else:
                sell_pressure += volume * abs(price_change)
        
        # Order flow imbalance
        total_flow = buy_pressure + sell_pressure
        order_flow_imbalance = (buy_pressure - sell_pressure) / total_flow if total_flow > 0 else 0
        
        # Volume delta
        volume_delta = buy_pressure - sell_pressure
        
        buying_pressure_ratio = (buy_pressure / total_flow) if total_flow > 0 else 0.5
        return {
            'order_flow_imbalance': order_flow_imbalance,
            'volume_delta': volume_delta,
            'buy_pressure': buy_pressure,
            'sell_pressure': sell_pressure,
            'buying_pressure': buying_pressure_ratio
        }
    
    def _calculate_momentum_indicators(self, prices: np.ndarray) -> Dict[str, float]:
        """Calculate various momentum indicators (ROC over multiple horizons)"""
        if len(prices) < 20:
            return {}
        
        def roc_bars(bars: int) -> float:
            if len(prices) > bars:
                base = prices[-(bars + 1)]
                return ((prices[-1] - base) / base * 100) if base != 0 else 0.0
            return 0.0

        # Rate of Change (ROC) across multiple horizons (5m bars)
        roc_1 = roc_bars(1)    # 5 minutes
        roc_3 = roc_bars(3)    # 15 minutes
        roc_5 = roc_bars(5)    # 25 minutes
        roc_10 = roc_bars(10)  # 50 minutes
        roc_12 = roc_bars(12)  # 60 minutes
        roc_20 = roc_bars(20)  # 100 minutes
        roc_60 = roc_bars(60)  # 5 hours
        
        # Commodity Channel Index (CCI)
        typical_price = prices[-1]  # Simplified
        sma_20 = np.mean(prices[-20:])
        mean_deviation = np.mean(np.abs(prices[-20:] - sma_20))
        cci = (typical_price - sma_20) / (0.015 * mean_deviation) if mean_deviation > 0 else 0
        
        # Williams %R
        highest_high = np.max(prices[-14:])
        lowest_low = np.min(prices[-14:])
        williams_r = ((highest_high - prices[-1]) / (highest_high - lowest_low) * -100) if highest_high != lowest_low else -50
        
        # Stochastic Oscillator
        k_percent = ((prices[-1] - lowest_low) / (highest_high - lowest_low) * 100) if highest_high != lowest_low else 50
        
        return {
            'momentum_1': roc_1,
            'momentum_3': roc_3,
            'momentum_5': roc_5,
            'momentum_10': roc_10,
            'momentum_12': roc_12,
            'momentum_20': roc_20,
            'momentum_60': roc_60,
            'cci': cci,
            'williams_r': williams_r,
            'stochastic_k': k_percent
        }
    
    def _calculate_microstructure(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate market microstructure indicators"""
        if len(df) < 20:
            return {}
        
        # Spread approximation
        spreads = []
        for i in range(len(df)):
            spread = (df.iloc[i]['high'] - df.iloc[i]['low']) / df.iloc[i]['close'] * 100
            spreads.append(spread)
        
        avg_spread = np.mean(spreads)
        current_spread = spreads[-1]
        
        # Price efficiency (how close to VWAP)
        vwap = np.sum(df['close'] * df['vol']) / np.sum(df['vol']) if np.sum(df['vol']) > 0 else df['close'].iloc[-1]
        price_efficiency = 1 - abs(df['close'].iloc[-1] - vwap) / vwap
        
        # Tick direction indicator
        upticks = 0
        downticks = 0
        for i in range(1, len(df)):
            if df.iloc[i]['close'] > df.iloc[i-1]['close']:
                upticks += 1
            elif df.iloc[i]['close'] < df.iloc[i-1]['close']:
                downticks += 1
        
        tick_indicator = (upticks - downticks) / (upticks + downticks) if (upticks + downticks) > 0 else 0
        
        return {
            'avg_spread': avg_spread,
            'current_spread': current_spread,
            'price_efficiency': price_efficiency,
            'tick_indicator': tick_indicator
        }
    
    def _detect_divergence(self, prices: np.ndarray, indicator: List[float]) -> int:
        """Detect bullish or bearish divergence"""
        if len(prices) < 4 or len(indicator) < 4:
            return 0
        
        # Find recent peaks and troughs
        price_trend = 1 if prices[-1] > prices[-4] else -1
        indicator_trend = 1 if indicator[-1] > indicator[-4] else -1
        
        # Bullish divergence: price making lower lows, indicator making higher lows
        if price_trend < 0 and indicator_trend > 0:
            return 1
        # Bearish divergence: price making higher highs, indicator making lower highs
        elif price_trend > 0 and indicator_trend < 0:
            return -1
        
        return 0
    
    def calculate_market_sentiment(self, all_indicators: Dict[str, Dict]) -> Dict[str, float]:
        """Calculate comprehensive market sentiment metrics"""
        if not all_indicators:
            return {'overall_sentiment': 0, 'bullish_count': 0, 'bearish_count': 0}
        
        sentiment_scores = []
        bullish_count = 0
        bearish_count = 0
        neutral_count = 0
        
        # Sector analysis
        sector_sentiments = {}
        
        for inst_id, indicators in all_indicators.items():
            if not indicators:
                continue
            
            # Calculate individual sentiment score
            score = 0
            weight_sum = 0
            
            # RSI sentiment (weight: 2)
            if 'rsi' in indicators:
                rsi = indicators['rsi']
                if rsi < 30:
                    score += 2 * (30 - rsi) / 30
                    weight_sum += 2
                elif rsi > 70:
                    score -= 2 * (rsi - 70) / 30
                    weight_sum += 2
                else:
                    weight_sum += 2
            
            # MACD sentiment (weight: 3)
            if 'macd_cross' in indicators:
                score += 3 * indicators['macd_cross']
                weight_sum += 3
            
            # Volume sentiment (weight: 2)
            if 'volume_ratio' in indicators:
                vol_ratio = indicators['volume_ratio']
                if vol_ratio > 1.5:
                    if indicators.get('momentum_5', 0) > 0:
                        score += 2
                    else:
                        score -= 2
                weight_sum += 2
            
            # Market structure (weight: 3)
            if 'structure_trend' in indicators:
                score += 3 * indicators['structure_trend']
                weight_sum += 3
            
            # Order flow (weight: 2)
            if 'order_flow_imbalance' in indicators:
                score += 2 * indicators['order_flow_imbalance']
                weight_sum += 2
            
            # Normalize score
            if weight_sum > 0:
                normalized_score = score / weight_sum
                sentiment_scores.append(normalized_score)
                
                if normalized_score > 0.2:
                    bullish_count += 1
                elif normalized_score < -0.2:
                    bearish_count += 1
                else:
                    neutral_count += 1
                
                # Sector classification (simplified)
                sector = self._get_sector(inst_id)
                if sector not in sector_sentiments:
                    sector_sentiments[sector] = []
                sector_sentiments[sector].append(normalized_score)
        
        # Calculate overall sentiment
        overall_sentiment = np.mean(sentiment_scores) * 100 if sentiment_scores else 0
        
        # Calculate sector sentiments
        sector_summary = {}
        for sector, scores in sector_sentiments.items():
            sector_summary[sector] = np.mean(scores) * 100
        
        return {
            'overall_sentiment': overall_sentiment,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count,
            'sentiment_distribution': {
                'bullish_pct': bullish_count / len(all_indicators) * 100 if all_indicators else 0,
                'bearish_pct': bearish_count / len(all_indicators) * 100 if all_indicators else 0,
                'neutral_pct': neutral_count / len(all_indicators) * 100 if all_indicators else 0
            },
            'sector_sentiments': sector_summary
        }
    
    def _get_sector(self, inst_id: str) -> str:
        """Classify instrument into sector"""
        # Major coins
        if inst_id in ['BTC-USDT-SWAP', 'ETH-USDT-SWAP']:
            return 'major'
        # DeFi
        elif any(token in inst_id for token in ['UNI', 'AAVE', 'SUSHI', 'CRV', 'COMP', 'MKR']):
            return 'defi'
        # Layer 1
        elif any(token in inst_id for token in ['SOL', 'AVAX', 'NEAR', 'DOT', 'ATOM', 'ADA']):
            return 'layer1'
        # Layer 2
        elif any(token in inst_id for token in ['ARB', 'OP', 'MATIC', 'POL']):
            return 'layer2'
        # Meme coins
        elif any(token in inst_id for token in ['DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK']):
            return 'meme'
        # AI tokens
        elif any(token in inst_id for token in ['AI16Z', 'AIXBT', 'TAO', 'RENDER']):
            return 'ai'
        else:
            return 'other'
    
    
    def _get_market_cap_rank(self, inst_id: str) -> int:
        """Get estimated market cap rank"""
        
        # Professional ranking based on market cap and liquidity
        major_coins = {
            'BTC-USDT-SWAP': 1, 'ETH-USDT-SWAP': 2, 'BNB-USDT-SWAP': 3,
            'SOL-USDT-SWAP': 4, 'XRP-USDT-SWAP': 5, 'ADA-USDT-SWAP': 6,
            'DOGE-USDT-SWAP': 7, 'AVAX-USDT-SWAP': 8, 'DOT-USDT-SWAP': 9,
            'TRX-USDT-SWAP': 10, 'LINK-USDT-SWAP': 11, 'TON-USDT-SWAP': 12,
            'MATIC-USDT-SWAP': 13, 'POL-USDT-SWAP': 13, 'ICP-USDT-SWAP': 14,
            'SHIB-USDT-SWAP': 15, 'LTC-USDT-SWAP': 16, 'BCH-USDT-SWAP': 17,
            'UNI-USDT-SWAP': 18, 'ATOM-USDT-SWAP': 19, 'ETC-USDT-SWAP': 20,
            'NEAR-USDT-SWAP': 21, 'APT-USDT-SWAP': 22, 'SUI-USDT-SWAP': 23,
            'ARB-USDT-SWAP': 24, 'OP-USDT-SWAP': 25, 'RENDER-USDT-SWAP': 26,
            'TAO-USDT-SWAP': 27, 'INJ-USDT-SWAP': 28, 'FIL-USDT-SWAP': 29,
            'HBAR-USDT-SWAP': 30
        }
        
        return major_coins.get(inst_id, 100)
    
    def get_current_positions(self) -> List[Dict[str, Any]]:
        """Get current positions from OKX API"""
        try:
            # Import OKX API modules
            import okx.Account as Account
            
            # Initialize Account API
            account_api = Account.AccountAPI(
                api_key=self.config.get('OKX', 'api_key'),
                api_secret_key=self.config.get('OKX', 'api_secret'),
                passphrase=self.config.get('OKX', 'api_passphrase'),
                use_server_time=False,
                flag='0'  # 0: Production
            )
            
            # Get SWAP positions
            response = account_api.get_positions(instType='SWAP')
            
            if response and response.get('code') == '0' and response.get('data'):
                # Filter out zero positions
                positions = []
                for pos in response['data']:
                    # Only include positions with non-zero size
                    if pos.get('pos') and float(pos.get('pos', '0')) != 0:
                        positions.append({
                            'instId': pos.get('instId', ''),
                            'pos': pos.get('pos', '0'),
                            'avgPx': pos.get('avgPx', '0'),
                            'upl': pos.get('upl', '0'),
                            'uplRatio': pos.get('uplRatio', '0'),
                            'lever': pos.get('lever', '1'),
                            'posSide': 'long' if float(pos.get('pos', '0')) > 0 else 'short',
                            'mgnMode': pos.get('mgnMode', ''),
                            'margin': pos.get('imr', '0'),
                            'liqPx': pos.get('liqPx', '0'),
                            'markPx': pos.get('markPx', '0'),
                            'notionalUsd': pos.get('notionalUsd', '0')
                        })
                return positions
            else:
                # Silent handling of API errors (e.g., no API key or no positions)
                return []
            
        except Exception as e:
            logger.debug(f"Error fetching current positions: {e}")
            return []
    
    def analyze_all_instruments(self) -> List[MarketAnalysis]:
        """Analyze all instruments and return objective market analysis"""
        logger.info("Analyzing all instruments for market data...")
        
        all_analyses = []
        all_indicators = {}
        
        # Calculate technical indicators for all instruments
        logger.info("Calculating technical indicators for all instruments...")
        
        # Parallel indicator calculation
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            
            for inst_id, data in self.market_data.items():
                if '5m' not in data or not data['5m'].get('candles'):
                    continue
                
                future = executor.submit(self._process_instrument, inst_id, data['5m']['candles'])
                futures[future] = inst_id
            
            for future in as_completed(futures):
                inst_id = futures[future]
                try:
                    indicators = future.result()
                    if indicators:
                        all_indicators[inst_id] = indicators
                except Exception as e:
                    logger.warning(f"Failed to calculate indicators for {inst_id}: {e}")
        
        # Generate market analysis for each instrument
        logger.info("Generating objective market analysis...")
        
        for inst_id, indicators in all_indicators.items():
            # Create objective market analysis without trading suggestions
            analysis = self.create_market_analysis(inst_id, indicators)
            if analysis:
                all_analyses.append(analysis)
        
        # Sort by volume and volatility for better visibility (display sorting, no filtering)
        all_analyses.sort(key=lambda x: x.volume_ratio * x.volatility_percentile, reverse=True)
        
        logger.info(f"Generated market analysis for {len(all_analyses)} instruments")
        
        # Return all analyses (no arbitrary limit)
        return all_analyses
    
    def create_market_analysis(self, inst_id: str, indicators: Dict[str, float]) -> Optional[MarketAnalysis]:
        """Create objective market analysis from technical indicators"""
        try:
            # Get current price from candles
            if inst_id not in self.market_data or '5m' not in self.market_data[inst_id]:
                return None
                
            candles = self.market_data[inst_id]['5m']['candles']
            if not candles:
                return None
                
            current_price = float(candles[0][4])  # Close price of latest 5m candle

            # Use timestamp proximity matching to calculate 1h and 24h comparison close prices, avoiding misjudgment caused by gaps
            def price_at_offset(target_ms: int, tolerance_ms: int = 2 * 60 * 1000) -> float:
                """Find close price closest to target_ms in 5m candles; if no samples within tolerance, return close price of the temporally closest one in all samples"""
                nearest_price = None
                nearest_diff = None
                for k in candles:
                    try:
                        ts = int(k[0])
                        close_val = float(k[4])
                    except Exception:
                        continue
                    diff = abs(ts - target_ms)
                    if diff <= tolerance_ms:
                        return close_val
                    if nearest_diff is None or diff < nearest_diff:
                        nearest_diff = diff
                        nearest_price = close_val
                return nearest_price if nearest_price is not None else current_price

            now_ms = int(candles[0][0])
            one_hour_ms = 60 * 60 * 1000
            one_day_ms = 24 * one_hour_ms

            price_1h_ago = price_at_offset(now_ms - one_hour_ms)
            price_24h_ago = price_at_offset(now_ms - one_day_ms)
            
            # Calculate percentage changes with safety checks
            price_change_24h = ((current_price - price_24h_ago) / price_24h_ago * 100) if price_24h_ago > 0 else 0
            price_change_1h = ((current_price - price_1h_ago) / price_1h_ago * 100) if price_1h_ago > 0 else 0
            
            # Get instrument info
            inst_info = self.instruments_info.get(inst_id, {})
            max_leverage = int(inst_info.get('lever', '20'))
            
            # Determine market cap tier
            market_cap_rank = self._get_market_cap_rank(inst_id)
            if market_cap_rank <= 10:
                market_cap_tier = "large"
            elif market_cap_rank <= 50:
                market_cap_tier = "mid"
            else:
                market_cap_tier = "small"
            
            # Calculate liquidation risk based on volatility
            # volatility is already in percentage (e.g., 20 for 20%)
            volatility = indicators.get('volatility', 0)
            if volatility < 10:  # Less than 10%
                liq_risk = "low"
            elif volatility < 20:  # Less than 20%
                liq_risk = "medium"
            else:
                liq_risk = "high"
                
            # Calculate volume from recent candles (24 hours = 288 candles of 5min each)
            # OKX candle[5] is vol field which is the trading volume in contracts
            # OKX candle[7] is volCcyQuote field which is the trading volume in quote currency (USDT)
            # For 24h volume: need 288 candles (288 * 5min = 24 hours)
            candles_24h = min(288, len(candles))  # Use all available candles up to 288
            
            # Try to use USDT volume (volCcyQuote) if available, otherwise fall back to contract volume
            try:
                # Use volCcyQuote (index 7) for USDT volume
                recent_volumes = [float(candle[7]) for candle in candles[:candles_24h]]
                volume_24h = sum(recent_volumes) if recent_volumes else 0
            except (IndexError, ValueError):
                # Fall back to contract volume if USDT volume not available
                recent_volumes = [float(candle[5]) for candle in candles[:candles_24h]]
                # Convert contracts to approximate USDT value
                inst_info = self.instruments_info.get(inst_id, {})
                ct_val = float(inst_info.get('ctVal', 1))  # Contract value
                volume_24h = sum(recent_volumes) * ct_val * current_price if recent_volumes else 0
            
            return MarketAnalysis(
                instId=inst_id,
                current_price=current_price,
                price_change_24h=price_change_24h,
                price_change_1h=price_change_1h,
                volume_24h=volume_24h,
                volume_ratio=indicators.get('volume_ratio', 1.0),
                
                # Technical Indicators - Fixed field names
                rsi_14=indicators.get('rsi', 50),  # Fixed: was 'rsi_14'
                rsi_7=indicators.get('rsi_7', 50),
                macd_signal=indicators.get('macd_signal', 0),
                macd_histogram=indicators.get('macd_histogram', 0),
                bb_position=indicators.get('bb_position', 0.5),
                bb_width=indicators.get('bb_width', 0.02),
                atr_ratio=indicators.get('atr', 0.02) / current_price * 100 if current_price > 0 else 0.02,  # Fixed calculation
                
                # Price Action
                support_level=indicators.get('support', current_price * 0.95),  # Fixed: was 'support_level'
                resistance_level=indicators.get('resistance', current_price * 1.05),  # Fixed: was 'resistance_level'
                trend_strength=indicators.get('structure_trend', 0),  # Fixed: was 'trend_strength'
                momentum_5min=indicators.get('momentum_1', 0),   # 1 5m candle ≈ 5 minutes
                momentum_15min=indicators.get('momentum_3', 0),  # 3 5m candles ≈ 15 minutes
                momentum_1h=indicators.get('momentum_12', 0),    # 12 5m candles ≈ 60 minutes
                
                # Market Structure
                volatility_percentile=min(100, indicators.get('volatility', 0)),  # Already in percentage
                liquidity_score=min(100, indicators.get('volume_ratio', 1) * 50),
                market_cap_tier=market_cap_tier,
                correlation_btc=indicators.get('correlation_btc', 0.5),
                
                # Volume Analysis
                volume_profile_poc=current_price,  # Simplified
                volume_weighted_price=indicators.get('vwap', current_price),
                buying_pressure=indicators.get('buying_pressure', 0.5),
                
                # Recent Performance
                performance_1d=price_change_24h,
                performance_7d=indicators.get('performance_7d', 0),
                performance_30d=indicators.get('performance_30d', 0),
                
                # Risk Metrics
                max_leverage_available=max_leverage,
                liquidation_risk_level=liq_risk,

                # Enriched
                hv10=indicators.get('hv10', 0.0),
                hv20=indicators.get('hv20', 0.0),
                hv50=indicators.get('hv50', 0.0),
                range_pct_24h=indicators.get('range_pct_24h', 0.0),
                mdd_24h=indicators.get('mdd_24h', 0.0),
                skew_20=indicators.get('skew_20', 0.0),
                kurtosis_20=indicators.get('kurtosis_20', 0.0),
                vol_percentile_rolling=indicators.get('vol_percentile_rolling', 0.0),
                adx_14=indicators.get('adx_14', 0.0),
                aroon_up_25=indicators.get('aroon_up_25', 0.0),
                aroon_down_25=indicators.get('aroon_down_25', 0.0),
                cci_20=indicators.get('cci_20', 0.0),
                bb_squeeze_score=indicators.get('bb_squeeze_score', 0.0),
                volume_z_20=indicators.get('volume_z_20', 0.0),
                obv_20=indicators.get('obv_20', 0.0),
                cmf_20=indicators.get('cmf_20', 0.0),
                vwap_dev_pct_20=indicators.get('vwap_dev_pct_20', 0.0)
            )
            
        except Exception as e:
            logger.error(f"Error creating market analysis for {inst_id}: {e}")
            return None
    
    def _process_instrument(self, inst_id: str, candles: List[List]) -> Optional[Dict[str, float]]:
        """Process individual instrument data"""
        try:
            return self.calculate_advanced_technical_indicators(candles)
        except Exception as e:
            logger.error(f"Error processing {inst_id}: {e}")
            return None
    
    
    def generate_markdown_report(self, market_analyses: List[MarketAnalysis]) -> str:
        """Generate objective market analysis report"""
        
        # Get OKX server time
        time_data = self.time_api.get_server_time()
        
        # Get current positions
        current_positions = self.get_current_positions()
        
        # Calculate market statistics
        total_instruments = len(self.market_data)
        analyzed_instruments = len(market_analyses)
        
        # Calculate average metrics
        avg_volatility = statistics.mean([analysis.volatility_percentile for analysis in market_analyses]) if market_analyses else 0
        avg_volume_ratio = statistics.mean([analysis.volume_ratio for analysis in market_analyses]) if market_analyses else 1
        
        # Count instruments by market cap tier
        tier_counts = {"large": 0, "mid": 0, "small": 0}
        for analysis in market_analyses:
            tier_counts[analysis.market_cap_tier] += 1
        
        report = f"""# OKX Market Analysis Report

## Current Time
**Server Time:** {time_data['formatted_time']}  
**Timestamp:** {time_data['timestamp']}  
**ISO Format:** {time_data['iso_time']}

## Market Overview

### Data Summary
- **Total Instruments Available:** {total_instruments}
- **Instruments Analyzed:** {analyzed_instruments}
- **Average Volatility Percentile:** {avg_volatility:.1f}%
- **Average Volume Ratio:** {avg_volume_ratio:.2f}x
- **Data Source:** Local mirror from okx_sync.py
- **Analysis Method:** Objective technical indicators without trading bias

### Market Cap Distribution
- **Large Cap (Top 10):** {tier_counts['large']} instruments
- **Mid Cap (11-50):** {tier_counts['mid']} instruments  
- **Small Cap (50+):** {tier_counts['small']} instruments

"""

        # Add market analysis data table
        report += f"""

## Market Analysis Data

### Technical Indicators & Market Data

| Instrument | Price | 24h % | 1h % | RSI(14) | MACD | BB Pos | Volume Ratio | Volatility | Trend | Max Lev | Risk |
|------------|-------|-------|------|---------|------|--------|--------------|------------|-------|---------|------|"""

        # Show all analyzed instruments
        for analysis in market_analyses:
            # Dynamic price formatting based on price magnitude
            if analysis.current_price >= 1000:
                price_format = f"${analysis.current_price:.2f}"  # For BTC, ETH etc: $113752.12
            elif analysis.current_price >= 100:
                price_format = f"${analysis.current_price:.3f}"  # For mid-range: $756.123
            elif analysis.current_price >= 1:
                price_format = f"${analysis.current_price:.4f}"  # For $1+ coins: $3.1234
            elif analysis.current_price >= 0.001:
                price_format = f"${analysis.current_price:.6f}"  # For small coins: $0.123456
            elif analysis.current_price >= 0.000001:
                price_format = f"${analysis.current_price:.8f}"  # For smaller: $0.12345678
            else:
                price_format = f"${analysis.current_price:.11f}" # For micro: $0.12345678901
                
            report += f"""
| {analysis.instId} | {price_format} | {analysis.price_change_24h:+.2f}% | {analysis.price_change_1h:+.2f}% | {analysis.rsi_14:.1f} | {analysis.macd_histogram:+.4f} | {analysis.bb_position:.2f} | {analysis.volume_ratio:.2f}x | {analysis.volatility_percentile:.1f}% | {analysis.trend_strength:+.2f} | {analysis.max_leverage_available}x | {analysis.liquidation_risk_level} |"""

        # Enriched sections (purely descriptive, no advice)
        report += f"""

### Volatility & Risk (Daily % based on 5m bars)

| Instrument | HV10 | HV20 | HV50 | 24h Range | 24h MDD | Skew(20) | Kurt(20) | Vol Percentile | ADX(14) | AroonUp | AroonDown | CCI(20) | BB Squeeze |
|------------|------|------|------|-----------|---------|----------|----------|----------------|---------|---------|-----------|---------|------------|
"""
        for analysis in market_analyses:
            report += f"\n| {analysis.instId} | {analysis.hv10:.1f}% | {analysis.hv20:.1f}% | {analysis.hv50:.1f}% | {analysis.range_pct_24h:.1f}% | {analysis.mdd_24h:.1f}% | {analysis.skew_20:.2f} | {analysis.kurtosis_20:.2f} | {analysis.vol_percentile_rolling:.1f}% | {analysis.adx_14:.1f} | {analysis.aroon_up_25:.1f} | {analysis.aroon_down_25:.1f} | {analysis.cci_20:.1f} | {analysis.bb_squeeze_score:.1f} |"

        report += f"""

### Volume & Flow

| Instrument | Volume Z(20) | OBV(20) | CMF(20) | VWAP Dev(20) |
|------------|--------------|---------|---------|--------------|
"""
        for analysis in market_analyses:
            report += f"\n| {analysis.instId} | {analysis.volume_z_20:+.2f} | {analysis.obv_20:.0f} | {analysis.cmf_20:+.2f} | {analysis.vwap_dev_pct_20:+.2f}% |"

        report += f"""

## Instruments Basic Information for Order

| Instrument | Contract Value (ctVal) | Min Size (minSz) | Max Leverage | Tick Size (tickSz) | Lot Size (lotSz) |
|------------|------------------------|------------------|--------------|-------------------|------------------|"""

        # Show all instruments from instruments.json for order reference
        for inst_id, inst_info in sorted(self.instruments_info.items()):
            if inst_id.endswith('-USDT-SWAP'):  # Only USDT-SWAP contracts
                report += f"""
| {inst_id} | {inst_info.get('ctVal', 'N/A')} {inst_info.get('ctValCcy', '')} | {inst_info.get('minSz', 'N/A')} | {inst_info.get('lever', 'N/A')}x | {inst_info.get('tickSz', 'N/A')} | {inst_info.get('lotSz', 'N/A')} |"""

        return report

    def run_analysis(self) -> None:
        """Main analysis workflow"""
        try:
            logger.info("Starting Objective OKX Market Analysis...")
            
            # Load all market data
            self.load_market_data()
            
            if not self.market_data:
                logger.error("No market data loaded. Please run okx_sync.py first.")
                return
            
            # Analyze all instruments
            market_analyses = self.analyze_all_instruments()
            
            if not market_analyses:
                logger.warning("No market analysis data generated")
                return
            
            # Generate report
            report = self.generate_markdown_report(market_analyses)
            
            # Write to file
            with open('okx_market.md', 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"Analysis complete. Generated objective analysis for {len(market_analyses)} instruments")
            logger.info("Report saved to okx_market.md")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise


def main():
    """Main entry point"""
    try:
        analyzer = ProfessionalMarketAnalyzer()
        analyzer.run_analysis()
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()