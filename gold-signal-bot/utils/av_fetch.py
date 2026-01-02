"""
Alpha Vantage fetch utilities for spot gold (XAU/USD).
"""

import pandas as pd
from datetime import datetime, timedelta
from alpha_vantage.foreignexchange import ForeignExchange
import config


def period_to_days(period: str) -> int:
    """Convert a period string like '5y' or '730d' to days."""
    if isinstance(period, (int, float)):
        return int(period)
    if not isinstance(period, str):
        return 0
    p = period.strip().lower()
    try:
        if p.endswith('y'):
            return int(float(p[:-1]) * 365)
        if p.endswith('d'):
            return int(float(p[:-1]))
    except ValueError:
        return 0
    return 0


def fetch_fx_history(days: int) -> pd.DataFrame:
    """Fetch daily XAU/USD history from Alpha Vantage and clip to N days."""
    fx = ForeignExchange(key=config.ALPHAVANTAGE_API_KEY, output_format='pandas')
    try:
        df, _ = fx.get_currency_exchange_daily(
            from_symbol='XAU',
            to_symbol='USD',
            outputsize='full'
        )
    except Exception as e:
        print(f"❌ Alpha Vantage fetch error: {e}")
        return pd.DataFrame()

    # Rename to standard OHLC
    df = df.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close'
    })
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    if days > 0:
        cutoff = datetime.utcnow() - timedelta(days=days)
        df = df[df.index >= cutoff]

    # Alpha Vantage does not provide volume for FX; fill Volume with zeros to keep schema stable
    if 'Volume' not in df.columns:
        df['Volume'] = 0

    return df
