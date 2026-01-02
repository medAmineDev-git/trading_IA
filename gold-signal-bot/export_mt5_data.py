"""
Export MT5 Historical Data to CSV
Run this script once to export your broker's historical data for training

Requirements:
- MetaTrader 5 must be running and logged in
- pip install MetaTrader5
"""

from utils.mt5_fetch import export_historical_data
import config


def main():
    print("=" * 60)
    print("MT5 DATA EXPORT")
    print("=" * 60)
    
    # Get MT5 settings from config
    symbol = getattr(config, 'MT5_SYMBOL', 'XAUUSD')
    timeframe = getattr(config, 'MT5_TIMEFRAME', 'H4')
    days = getattr(config, 'MT5_EXPORT_DAYS', 730)
    csv_path = getattr(config, 'MT5_CSV_PATH', 'data/mt5_history.csv')
    
    print(f"\nExporting {symbol} ({timeframe}) for last {days} days...")
    print(f"Output: {csv_path}")
    print("\n⚠️  Make sure MT5 is running and logged in!")
    
    # Export historical data
    df = export_historical_data(
        symbol=symbol,
        timeframe=timeframe,
        days=days,
        csv_path=csv_path
    )
    
    if df is not None:
        print("\n" + "=" * 60)
        print("✅ EXPORT COMPLETE!")
        print("=" * 60)
        print(f"   File: {csv_path}")
        print(f"   Rows: {len(df)}")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"\nYou can now run: python train_model.py")
    else:
        print("\n" + "=" * 60)
        print("❌ EXPORT FAILED")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Make sure MT5 terminal is running and logged in")
        print("2. Check if symbol name is correct in config.py")
        print("3. Verify you have historical data for the symbol in MT5")
        print("4. Install library: pip install MetaTrader5")


if __name__ == "__main__":
    main()
