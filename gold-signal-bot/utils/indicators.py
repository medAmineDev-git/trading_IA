"""
Technical Indicators Module
Computes RSI, MACD, Bollinger Bands, and other features for ML model
"""

import pandas as pd
import numpy as np
import config


def calculate_rsi(data, period=14):
    """
    Calculate Relative Strength Index (RSI)
    
    Args:
        data: pandas Series of closing prices
        period: RSI period (default 14)
    
    Returns:
        pandas Series with RSI values
    """
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(data, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        data: pandas Series of closing prices
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line period (default 9)
    
    Returns:
        tuple: (macd, signal_line, histogram)
    """
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    histogram = macd - signal_line
    
    return macd, signal_line, histogram


def calculate_bollinger_bands(data, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    
    Args:
        data: pandas Series of closing prices
        period: Moving average period (default 20)
        std_dev: Standard deviation multiplier (default 2)
    
    Returns:
        tuple: (upper_band, middle_band, lower_band)
    """
    middle_band = data.rolling(window=period).mean()
    std = data.rolling(window=period).std()
    
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band


def calculate_atr(df, period=14):
    """Calculate Average True Range (ATR)."""
    high = df['High']
    low = df['Low']
    close = df['Close']
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr


def calculate_ema(series, period):
    """Calculate EMA for a series."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_slope(series, period=3):
    """Simple slope over last 'period' points."""
    return series.diff(periods=period) / period


def add_all_indicators(df):
    """
    Add all technical indicators to dataframe
    
    Args:
        df: pandas DataFrame with OHLCV data (must have 'Close' column)
    
    Returns:
        pandas DataFrame with added indicator columns
    """
    df = df.copy()

    # Flatten possible MultiIndex columns from yfinance (single-ticker downloads can still carry two-level columns)
    if isinstance(df.columns, pd.MultiIndex):
        # Prefer the first level (price field), fallback to joining if ambiguous
        new_cols = []
        for col in df.columns:
            if isinstance(col, tuple) and len(col) > 0:
                new_cols.append(col[0])
            else:
                new_cols.append(col)
        # If duplicates arise, append symbol suffix to keep uniqueness
        if len(set(new_cols)) < len(new_cols):
            deduped = []
            counts = {}
            for orig, base in zip(df.columns, new_cols):
                counts[base] = counts.get(base, 0) + 1
                if counts[base] > 1:
                    # append last level (symbol) if available
                    suffix = orig[-1] if isinstance(orig, tuple) and len(orig) > 1 else counts[base]
                    deduped.append(f"{base}_{suffix}")
                else:
                    deduped.append(base)
            new_cols = deduped
        df.columns = new_cols

    # Normalize column names to standard OHLCV keys (case-insensitive)
    def _normalize_ohlc_columns(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = {}
        for col in frame.columns:
            key = col.lower().strip().replace(' ', '')
            normalized[key] = col  # keep original to access

        mapping = {}
        for target, variants in {
            'Open': {'open'},
            'High': {'high'},
            'Low': {'low'},
            'Close': {'close'},
            'Adj Close': {'adjclose', 'adj_close', 'adjustedclose'},
            'Volume': {'volume'}
        }.items():
            for variant in variants:
                if variant in normalized:
                    mapping[target] = normalized[variant]
                    break

        # Rename found columns to canonical names
        frame = frame.rename(columns={v: k for k, v in mapping.items()})

        # Ensure columns are Series (not DataFrames) in case of duplicates
        for col in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']:
            if col in frame.columns:
                col_data = frame[col]
                if isinstance(col_data, pd.DataFrame):
                    frame[col] = col_data.iloc[:, 0]

        return frame

    df = _normalize_ohlc_columns(df)

    missing = [c for c in ['Close', 'High', 'Low'] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required price columns: {missing}")
    
    # RSI
    df['RSI'] = calculate_rsi(df['Close'], period=config.RSI_PERIOD if hasattr(config, 'RSI_PERIOD') else 14)

    # MACD
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(
        df['Close'], fast=config.MACD_FAST if hasattr(config, 'MACD_FAST') else 12,
        slow=config.MACD_SLOW if hasattr(config, 'MACD_SLOW') else 26,
        signal=config.MACD_SIGNAL if hasattr(config, 'MACD_SIGNAL') else 9)

    # Bollinger Bands
    bb_period = config.BB_PERIOD if hasattr(config, 'BB_PERIOD') else 20
    bb_std = config.BB_STD_DEV if hasattr(config, 'BB_STD_DEV') else 2
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = calculate_bollinger_bands(df['Close'], period=bb_period, std_dev=bb_std)
    bb_width = df['BB_Upper'] - df['BB_Lower']
    df['BB_%B'] = (df['Close'] - df['BB_Lower']) / bb_width.replace(0, np.nan)

    # ATR
    atr_period = config.ATR_PERIOD if hasattr(config, 'ATR_PERIOD') else 14
    df['ATR'] = calculate_atr(df, period=atr_period)

    # EMAs and slope
    ema_fast = calculate_ema(df['Close'], period=getattr(config, 'EMA_FAST', 50))
    ema_slow = calculate_ema(df['Close'], period=getattr(config, 'EMA_SLOW', 200))
    df['EMA_Fast'] = ema_fast
    df['EMA_Slow'] = ema_slow
    df['EMA_Slope'] = calculate_slope(ema_fast, period=3)
    df['EMA_Ratio'] = ema_fast / ema_slow

    # Price return percentage
    df['Price_Return'] = df['Close'].pct_change() * 100
    df['Return_3'] = df['Close'].pct_change(periods=3) * 100

    # Target: 1 if next bar is higher, 0 otherwise
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    # Drop NaN values
    df = df.dropna()
    
    return df


def prepare_features(df):
    """
    Prepare feature matrix (X) and target vector (y) for ML model
    
    Args:
        df: pandas DataFrame with indicators
    
    Returns:
        tuple: (X, y) - features and target
    """
    feature_columns = [
        'RSI',
        'MACD',
        'MACD_Signal',
        'MACD_Hist',
        'BB_%B',
        'ATR',
        'EMA_Fast',
        'EMA_Slow',
        'EMA_Slope',
        'EMA_Ratio',
        'Price_Return',
        'Return_3'
    ]
    
    X = df[feature_columns].values
    y = df['Target'].values
    
    return X, y
