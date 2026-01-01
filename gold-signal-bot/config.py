"""
Config Module - Configuration settings for Gold Signal Bot
"""

# Market Settings
TICKER = 'GC=F'                # Gold Futures (correct ticker for yfinance)
INTERVAL = '1h'                # Default timeframe
LOOKBACK_PERIOD = '5d'         # How much historical data to fetch

# Model Settings
MODEL_PATH = 'models/gold_signal_model.pkl'
N_ESTIMATORS = 300             # More trees for stability
MAX_DEPTH = 12                 # Limit depth to reduce overfitting
MIN_SAMPLES_SPLIT = 4          # Slightly stricter splits
RANDOM_STATE = 42              # For reproducibility
PROB_THRESHOLD = 0.50          # Min confidence to act on a prediction

# Trading Settings (Signal Generation)
STOP_LOSS_PERCENT = 0.005      # 0.5% Stop Loss
TAKE_PROFIT_PERCENT = 0.018    # 1.8% Take Profit (wider reward)
RSI_BUY_MIN = 47               # Require RSI > 47 for BUY (looser)
RSI_SELL_MAX = 53              # Require RSI < 53 for SELL (looser)

# Technical Indicator Settings
RSI_PERIOD = 14
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
BB_PERIOD = 20
BB_STD_DEV = 2

# Training Settings
TRAINING_PERIOD = '5y'         # Historical data period for training
TRAIN_TEST_SPLIT = 0.8         # 80% train, 20% test

# Backtesting Settings
BACKTEST_PERIOD_DAYS = 340     # Number of days to backtest (340 = ~11 months)

# Data Storage
SIGNALS_CSV_PATH = 'data/signals.csv'
MODEL_DIR = 'models'
DATA_DIR = 'data'

# Display Settings
DISPLAY_DECIMALS = 2           # Price decimal places
