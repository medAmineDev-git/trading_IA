# 🤖 ML Gold Signal Bot

A Python-based machine learning application that generates trading signals for **Gold (XAUUSD)** using technical analysis and Random Forest classification.

⚠️ **IMPORTANT: This bot generates signals only — NO AUTO-TRADING**

---

## 📋 Features

- ✅ Analyzes Gold (XAUUSD) market data
- ✅ Uses Machine Learning (RandomForestClassifier) for predictions
- ✅ Computes technical indicators (RSI, MACD, Bollinger Bands)
- ✅ Generates BUY/SELL signals with Stop Loss and Take Profit levels
- ✅ Saves all signals to CSV file
- ✅ Time-series aware training (no data shuffling)
- ✅ Configurable timeframes (1h default)
- ✅ No broker connection — analysis only

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas numpy scikit-learn yfinance joblib
```

### 2. Train the Model

```bash
python train_model.py
```

This will:
- Fetch 2 years of Gold historical data
- Compute technical indicators
- Train a RandomForestClassifier
- Save the model to `models/gold_signal_model.pkl`
- Display accuracy metrics

### 3. Run the Signal Bot

```bash
python signal_bot.py
```

The bot will:
- Load the trained model
- Fetch latest Gold data every hour
- Generate BUY/SELL/HOLD signals
- Display signals with SL/TP levels
- Save signals to `data/signals.csv`

---

## 📂 Project Structure

```
gold-signal-bot/
│
├── data/                       # Data storage
│   └── signals.csv            # Generated signals log
│
├── models/                     # Trained models
│   ├── gold_signal_model.pkl  # ML model
│   └── training_metadata.txt  # Training info
│
├── utils/                      # Utility modules
│   ├── __init__.py
│   ├── indicators.py          # Technical indicators
│   ├── model_loader.py        # Model save/load
│   └── signal_logic.py        # Signal generation
│
├── train_model.py             # Training script
├── signal_bot.py              # Main runtime
└── README.md                  # Documentation
```

---

## 📊 Technical Indicators

The bot computes the following features:

| Indicator | Parameters | Description |
|-----------|-----------|-------------|
| **RSI** | Period: 14 | Relative Strength Index |
| **MACD** | Fast: 12, Slow: 26, Signal: 9 | Moving Average Convergence Divergence |
| **Bollinger Bands** | Period: 20, Std: 2 | Upper and Lower bands |
| **Price Return** | — | Percentage change |

---

## 🎯 Signal Logic

The bot generates signals based on **prediction changes**:

| Condition | Signal | Action |
|-----------|--------|--------|
| Previous = 0 (Down) → Current = 1 (Up) | **BUY** | Enter long position |
| Previous = 1 (Up) → Current = 0 (Down) | **SELL** | Enter short position |
| No change | **HOLD** | No action |

### Stop Loss & Take Profit

**BUY Signal:**
- SL = Entry Price × 0.99 (1% below)
- TP = Entry Price × 1.02 (2% above)

**SELL Signal:**
- SL = Entry Price × 1.01 (1% above)
- TP = Entry Price × 0.98 (2% below)

---

## 🖥️ Output Examples

### BUY Signal
```
📈 BUY SIGNAL — Price: 1923.50 | SL: 1904.26 | TP: 1961.97
```

### SELL Signal
```
📉 SELL SIGNAL — Price: 1923.50 | SL: 1942.73 | TP: 1885.03
```

### HOLD
```
⏳ HOLD — No new signal at this time.
```

---

## ⚙️ Configuration

You can customize settings in `signal_bot.py`:

```python
# In main() function
TICKER = 'XAUUSD=X'              # Gold ticker
INTERVAL = '1h'                   # Timeframe (1m, 5m, 15m, 30m, 1h, 4h, 1d)
STOP_LOSS_PERCENT = 0.01          # 1% SL
TAKE_PROFIT_PERCENT = 0.02        # 2% TP
```

### Available Intervals

- `1m` — 1 minute
- `5m` — 5 minutes
- `15m` — 15 minutes
- `30m` — 30 minutes
- `1h` — 1 hour (default)
- `2h` — 2 hours
- `4h` — 4 hours
- `1d` — 1 day

---

## 📈 Training Details

### Model
- **Algorithm**: RandomForestClassifier
- **Trees**: 100
- **Max Depth**: 10
- **Min Samples Split**: 5

### Data
- **Source**: Yahoo Finance (`yfinance`)
- **Period**: 2 years (default)
- **Split**: 80% training, 20% testing
- **Method**: Time-series split (no shuffling)

### Retraining

To retrain with fresh data:

```bash
python train_model.py
```

---

## 📝 CSV Signal Log

All signals are saved to `data/signals.csv`:

| timestamp | type | price | sl | tp |
|-----------|------|-------|----|----|
| 2026-01-01 14:00:00 | BUY | 1923.50 | 1904.26 | 1961.97 |
| 2026-01-01 18:00:00 | SELL | 1935.20 | 1954.55 | 1896.49 |

---

## 🛑 Stopping the Bot

Press `Ctrl+C` to stop the bot gracefully.

```
🛑 Bot stopped by user
✅ Shutdown complete
```

---

## ⚠️ Disclaimer

**This software is for educational and informational purposes only.**

- This bot **does NOT place trades automatically**
- This bot **does NOT connect to any broker or exchange**
- Trading financial instruments carries risk
- Past performance does not guarantee future results
- Use signals at your own discretion
- Always conduct your own analysis before trading

---

## 🔧 Troubleshooting

### Model Not Found Error

```
❌ Model not found at: models/gold_signal_model.pkl
```

**Solution**: Run `python train_model.py` first to create the model.

### Data Fetch Error

```
⚠️ No data retrieved from Yahoo Finance
```

**Solutions**:
- Check internet connection
- Verify ticker symbol is correct
- Try a different interval
- Yahoo Finance may have rate limits

### Module Import Error

```
ModuleNotFoundError: No module named 'yfinance'
```

**Solution**: Install missing dependencies:

```bash
pip install pandas numpy scikit-learn yfinance joblib
```

---

## 📚 Dependencies

- **pandas** — Data manipulation
- **numpy** — Numerical operations
- **scikit-learn** — Machine learning
- **yfinance** — Market data
- **joblib** — Model serialization

---

## 🤝 Contributing

Feel free to:
- Report bugs
- Suggest features
- Submit improvements
- Share your results

---

## 📄 License

This project is open-source and available for educational use.

---

## 📧 Support

For issues or questions, please open an issue in the project repository.

---

**Happy Signal Trading! 📈📉**
