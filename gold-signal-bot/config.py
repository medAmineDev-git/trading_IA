"""
Config Module - Configuration settings for Gold Signal Bot
"""

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Market Settings
DATA_SOURCE = 'mt5_csv'        # 'alphavantage', 'yahoo', 'mt5_csv', or 'mt5_live'
ALPHAVANTAGE_API_KEY = 'HKZNVPRK1KQG8DIL'
TICKER = 'XAUUSD'              # Spot gold (not used for MT5 modes)
INTERVAL = 'h4'                # Not used for MT5 CSV mode
LOOKBACK_PERIOD = '30d'        # How much historical data to fetch for live bot
YF_FALLBACK_TICKER = None      # No Yahoo fallback (stay on spot)
YF_FALLBACK_INTERVAL = None    # No fallback interval
USE_GC_F_FALLBACK = False      # Do not auto-add GC=F

# MT5 Settings
MT5_SYMBOL = 'XAUUSD'          # Your broker's symbol (XAUUSD, GOLD, etc.)
MT5_TIMEFRAME = 'D1'           # M1, M5, M15, M30, H1, H4, D1
MT5_EXPORT_DAYS = 1825         # Days to export (5 years)
MT5_CSV_PATH = os.path.join(BASE_DIR, 'data/XAUUSD_1D.csv')  # CSV file path
MT5_LIVE_BARS = 500            # Number of bars to fetch for live signals
TIMEZONE_OFFSET_HOURS = 1      # Timezone offset for display (UTC+1 = 1, UTC-5 = -5)

# AI Model Settings
MODEL_TYPE = 'rf'              # 'rf', 'xgboost', 'lightgbm', or 'ensemble'
ENSEMBLE_MODELS = ['rf', 'xgboost', 'lightgbm'] # Models used in ensemble
MODEL_PATH = os.path.join(BASE_DIR, 'models/gold_signal_model.pkl')
N_ESTIMATORS = 300             # Reduced from 1000: prevent overfitting
MAX_DEPTH = 6                  # Reduced from 12: simpler, more robust model
MIN_SAMPLES_SPLIT = 5          # Stricter splits
MIN_SAMPLES_LEAF = 5           # Reduced from 1: avoid capturing noise
RANDOM_STATE = 42              # For reproducibility
PROB_THRESHOLD = 0.50          # Min confidence to act (more trades, balanced quality)

# Trading Settings (Signal Generation)
STOP_LOSS_PERCENT = 0.005      # 0.5% Stop Loss
TAKE_PROFIT_PERCENT = 0.01    # 1.4% Take Profit
USE_ATR_STOPS = False          # Disabled: ATR too volatile at high gold prices
ATR_STOP_MULTIPLIER = 2.0      # Stop Loss = 2 × ATR
ATR_TP_MULTIPLIER = 5.0       # Take Profit = 5 × ATR
USE_TREND_FILTER = False       # Disabled: allow counter-trend trades
USE_VOLATILITY_FILTER = False  # Disabled by default
ATR_FILTER_MIN = 5.0           # Minimum ATR to trade (avoid chop)
ATR_FILTER_MAX = 50.0          # Maximum ATR to trade (avoid news spikes)
RSI_BUY_MIN = 30               # Require RSI > 30 for BUY (more lenient)
RSI_SELL_MAX = 70              # Require RSI < 70 for SELL (more lenient)
MIN_RR = 1.8                   # Minimum risk-reward ratio to accept

# Technical Indicator Settings
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD_DEV = 2
ATR_PERIOD = 14
EMA_FAST = 50
EMA_SLOW = 200

# Training Settings
TRAINING_PERIOD = '1y'         # Historical data period for training
TRAIN_TEST_SPLIT = 0.8         # 80% train, 20% test (for proper evaluation)

# Backtesting Settings
BACKTEST_PERIOD_DAYS = 350     # Number of days to backtest (~8 years)

# Data Storage
SIGNALS_CSV_PATH = os.path.join(BASE_DIR, 'data/signals.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Display Settings
DISPLAY_DECIMALS = 2           # Price decimal places
