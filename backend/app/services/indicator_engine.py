"""
Indicator Engine - Computes technical indicators using pandas and pandas_ta
"""
import pandas as pd
import pandas_ta as ta
from typing import Dict, Optional


def compute_pivot(previous_day_ohlc: Dict[str, float]) -> Dict[str, float]:
    """
    Compute pivot points from previous day's OHLC.
    Returns: pivot, R1, R2, S1, S2
    """
    high = previous_day_ohlc.get('high', 0)
    low = previous_day_ohlc.get('low', 0)
    close = previous_day_ohlc.get('close', 0)
    
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    r2 = pivot + (high - low)
    s1 = 2 * pivot - high
    s2 = pivot - (high - low)
    
    return {
        'pivot': pivot,
        'r1': r1,
        'r2': r2,
        's1': s1,
        's2': s2
    }


def compute_rsi(series: pd.Series, length: int = 14) -> float:
    """
    Compute RSI (Relative Strength Index).
    Returns the last RSI value.
    """
    rsi = ta.rsi(series, length=length)
    if rsi is not None and len(rsi) > 0:
        return float(rsi.iloc[-1])
    return 50.0  # Default neutral value


def compute_stochastic(
    high_series: pd.Series,
    low_series: pd.Series,
    close_series: pd.Series,
    k: int = 14,
    d: int = 3
) -> Dict[str, float]:
    """
    Compute Stochastic Oscillator (%K and %D).
    Returns dict with 'k' and 'd' values.
    """
    stoch = ta.stoch(high_series, low_series, close_series, k=k, d=d)
    if stoch is not None and len(stoch) > 0:
        last_row = stoch.iloc[-1]
        # Try different possible column names for pandas-ta compatibility
        k_col = None
        d_col = None
        for col in stoch.columns:
            if 'STOCHk' in col.upper() or 'K_' in col.upper():
                k_col = col
            if 'STOCHd' in col.upper() or 'D_' in col.upper():
                d_col = col
        
        k_value = float(last_row[k_col]) if k_col and k_col in last_row else 50.0
        d_value = float(last_row[d_col]) if d_col and d_col in last_row else 50.0
        
        return {
            'k': k_value,
            'd': d_value
        }
    return {'k': 50.0, 'd': 50.0}


def compute_ma(
    series: pd.Series,
    window: int,
    ma_type: str = 'sma'
) -> float:
    """
    Compute Moving Average (SMA or EMA).
    Returns the last MA value.
    """
    if ma_type.lower() == 'ema':
        ma = ta.ema(series, length=window)
    else:
        ma = ta.sma(series, length=window)
    
    if ma is not None and len(ma) > 0:
        return float(ma.iloc[-1])
    return float(series.iloc[-1]) if len(series) > 0 else 0.0


class IndicatorCache:
    """
    Cache for storing recent indicator values per symbol.
    """
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self.cache: Dict[str, Dict] = {}
    
    def get(self, symbol: str, indicator: str) -> Optional[float]:
        if symbol in self.cache and indicator in self.cache[symbol]:
            return self.cache[symbol][indicator]
        return None
    
    def set(self, symbol: str, indicator: str, value: float):
        if symbol not in self.cache:
            self.cache[symbol] = {}
        self.cache[symbol][indicator] = value
    
    def clear(self, symbol: Optional[str] = None):
        if symbol:
            if symbol in self.cache:
                del self.cache[symbol]
        else:
            self.cache.clear()

