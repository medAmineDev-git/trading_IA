"""
Technical Indicators Module
Computes RSI, MACD, Bollinger Bands, and other features for ML model
"""

import pandas as pd
import numpy as np


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


def add_all_indicators(df):
    """
    Add all technical indicators to dataframe
    
    Args:
        df: pandas DataFrame with OHLCV data (must have 'Close' column)
    
    Returns:
        pandas DataFrame with added indicator columns
    """
    df = df.copy()
    
    # RSI
    df['RSI'] = calculate_rsi(df['Close'], period=14)
    
    # MACD
    df['MACD'], df['MACD_Signal'], df['MACD_Hist'] = calculate_macd(df['Close'])
    
    # Bollinger Bands
    df['BB_Upper'], df['BB_Middle'], df['BB_Lower'] = calculate_bollinger_bands(df['Close'])
    
    # Price return percentage
    df['Price_Return'] = df['Close'].pct_change() * 100
    
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
        'BB_Upper', 
        'BB_Middle', 
        'BB_Lower',
        'Price_Return'
    ]
    
    X = df[feature_columns].values
    y = df['Target'].values
    
    return X, y
