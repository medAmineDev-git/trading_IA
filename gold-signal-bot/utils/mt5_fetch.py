"""
MT5 Data Fetcher - Export historical data from MetaTrader 5
"""

import pandas as pd
from datetime import datetime, timedelta
import os

# Try to import MetaTrader5 (optional for CSV-only mode)
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    mt5 = None


def initialize_mt5():
    """Initialize MT5 connection"""
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 library not available. Use CSV mode or install MetaTrader5.")
        return False
    if not mt5.initialize():
        print(f"❌ MT5 initialization failed: {mt5.last_error()}")
        return False
    print("✅ MT5 connected successfully")
    return True


def export_historical_data(symbol="XAUUSD", timeframe="H4", days=730, csv_path="data/mt5_history.csv"):
    """
    Export historical data from MT5 to CSV
    
    Args:
        symbol: Trading symbol (e.g., "XAUUSD")
        timeframe: Timeframe ("M1", "M5", "M15", "M30", "H1", "H4", "D1")
        days: Number of days to fetch
        csv_path: Output CSV file path
    
    Returns:
        DataFrame with OHLCV data
    """
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 library not installed. Cannot export from MT5.")
        return None
    
    if not initialize_mt5():
        return None
    
    # Map timeframe string to MT5 constant
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    
    tf = timeframe_map.get(timeframe.upper(), mt5.TIMEFRAME_H4)
    
    print(f"\n📊 Fetching {symbol} data from MT5...")
    print(f"   Timeframe: {timeframe}")
    print(f"   Period: {days} days")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Fetch rates
    rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
    
    if rates is None or len(rates) == 0:
        print(f"❌ No data retrieved. Error: {mt5.last_error()}")
        mt5.shutdown()
        return None
    
    # Convert to DataFrame
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.rename(columns={
        'time': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'tick_volume': 'Volume'
    })
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.set_index('Date', inplace=True)
    
    # Save to CSV
    os.makedirs(os.path.dirname(csv_path) if os.path.dirname(csv_path) else '.', exist_ok=True)
    df.to_csv(csv_path)
    
    print(f"✅ Exported {len(df)} candles to {csv_path}")
    
    mt5.shutdown()
    return df


def fetch_live_data(symbol="XAUUSD", timeframe="H4", bars=500):
    """
    Fetch recent bars from MT5 for live signal generation
    
    Args:
        symbol: Trading symbol
        timeframe: Timeframe string
        bars: Number of bars to fetch
    
    Returns:
        DataFrame with recent OHLCV data
    """
    if not MT5_AVAILABLE:
        print("❌ MetaTrader5 library not installed. Cannot fetch live data.")
        return None
    
    if not initialize_mt5():
        return None
    
    timeframe_map = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }
    
    tf = timeframe_map.get(timeframe.upper(), mt5.TIMEFRAME_H4)
    
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    
    if rates is None or len(rates) == 0:
        print(f"❌ No live data. Error: {mt5.last_error()}")
        mt5.shutdown()
        return None
    
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    df = df.rename(columns={
        'time': 'Date',
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'tick_volume': 'Volume'
    })
    df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df.set_index('Date', inplace=True)
    
    mt5.shutdown()
    return df


def load_csv_data(csv_path, days=None):
    """
    Load historical data from CSV file
    
    Args:
        csv_path: Path to CSV file
        days: Optional number of recent days to load
    
    Returns:
        DataFrame with OHLCV data
    """
    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found: {csv_path}")
        return None
    
    print(f"\n📊 Loading data from CSV: {csv_path}")
    
    # Try to detect MT5 format (tab-separated, no headers)
    try:
        # First try: MT5 export format (tab-separated, no column names)
        df = pd.read_csv(csv_path, sep='\t', header=None, names=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    except Exception as e:
        # Fallback: standard CSV with headers
        try:
            df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        except Exception as e2:
            print(f"❌ Failed to parse CSV: {e2}")
            return None
    
    if df.empty:
        print("❌ CSV loaded but contains no data")
        return None
    
    if days is not None:
        cutoff = datetime.now() - timedelta(days=days)
        df = df[df.index >= cutoff]
    
    print(f"✅ Loaded {len(df)} candles")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    
    return df
