# 🚀 Gold Signal Bot - Full Stack Dashboard

Complete backtesting platform for Gold (XAUUSD) trading strategies with ML-powered signal generation.

## 📋 Project Structure

```
gold-signal-bot/
├── backend/                    # Flask REST API
│   ├── api.py                 # Main API server
│   ├── requirements.txt       # Python dependencies
│   └── README.md
├── frontend/                   # Angular 20 Dashboard
│   ├── src/                   # Source code
│   ├── package.json           # Node dependencies
│   └── README.md
├── data/                       # Historical CSV data
├── models/                     # Trained ML models
├── utils/                      # Python utilities
├── train_model.py             # Training script
├── backtest.py                # Backtesting script
├── config.py                  # Configuration
└── README.md                  # This file
```

## 🎯 Features

### Backend (Python + Flask)

- ✅ REST API for model training and backtesting
- ✅ Real-time progress tracking with job status
- ✅ Random Forest ML model
- ✅ Technical indicators (RSI, MACD, BB, ATR, EMA)
- ✅ Configurable risk management
- ✅ Historical data processing

### Frontend (Angular 20)

- ✅ Modern Material Design UI
- ✅ Interactive parameter configuration
- ✅ Real-time training progress
- ✅ Backtest execution and monitoring
- ✅ Results visualization with charts
- ✅ Trade history table
- ✅ CSV export functionality

## 🚀 Quick Start

### 1. Install Backend Dependencies

```bash
# Install Python packages
pip install -r requirements.txt

# Install API-specific packages
cd backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Backend API

```bash
# From project root
cd backend
python api.py
```

Server will start on `http://127.0.0.1:5000`

### 4. Start the Frontend Dashboard

```bash
# In a new terminal
cd frontend
npm start
```

Dashboard will be available at `http://localhost:4200`

### 5. Open Your Browser

Navigate to `http://localhost:4200` and start using the dashboard!

## 📊 Usage Workflow

### Step 1: Configure Parameters

1. Open the **Parameters** tab
2. Adjust technical indicators (RSI, MACD, etc.)
3. Set risk management (Stop Loss, Take Profit)
4. Configure model hyperparameters
5. Select data source (CSV file)

### Step 2: Train Model

1. Go to the **Training** tab
2. Review your configuration summary
3. Click **"Start Training"**
4. Monitor real-time progress
5. View training results (accuracy, metrics)

### Step 3: Run Backtest

1. Navigate to the **Backtest** tab
2. Set backtest period (days)
3. Click **"Start Backtest"**
4. Watch progress updates
5. See quick results summary

### Step 4: Analyze Results

1. Switch to the **Results** tab
2. View equity curve chart
3. Analyze trade history table
4. Review detailed statistics
5. Export results to CSV

## 🔧 Configuration

### Backend Configuration (`config.py`)

```python
# Data Source
DATA_SOURCE = 'mt5_csv'
MT5_CSV_PATH = 'data/XAUUSD_1D.csv'

# Model Settings
N_ESTIMATORS = 300
MAX_DEPTH = 6
PROB_THRESHOLD = 0.50

# Risk Management
STOP_LOSS_PERCENT = 0.005  # 0.5%
TAKE_PROFIT_PERCENT = 0.01  # 1%
```

### Frontend API URL (`frontend/src/app/core/services/api.service.ts`)

```typescript
private baseUrl = 'http://127.0.0.1:5000/api';
```

## 📡 API Endpoints

### Configuration

- `GET /api/health` - Health check
- `GET /api/config` - Get current configuration
- `GET /api/data-files` - List available CSV files

### Training

- `POST /api/train` - Start training job
- `GET /api/train/status/<job_id>` - Get training status
- `GET /api/train/results/<job_id>` - Get training results

### Backtesting

- `POST /api/backtest` - Start backtest job
- `GET /api/backtest/status/<job_id>` - Get backtest status
- `GET /api/backtest/results/<job_id>` - Get backtest results

## 🎨 Screenshots

### Parameters Configuration

Configure all indicators, risk settings, and model hyperparameters through an intuitive form interface.

### Training Progress

Real-time progress tracking with status updates and completion metrics.

### Backtest Results

Interactive charts showing equity curve and comprehensive trade statistics.

## 🧪 Testing

### Backend API Test

```bash
# Test health endpoint
curl http://127.0.0.1:5000/api/health

# Expected response:
# {"status": "ok", "timestamp": "2026-01-02T12:00:00"}
```

### Frontend Development

```bash
cd frontend
npm test
```

## 📦 Dependencies

### Backend

- Flask 3.0.0
- Flask-CORS 4.0.0
- pandas
- numpy
- scikit-learn
- joblib

### Frontend

- Angular 20
- Angular Material 20
- Chart.js 4.4
- ng2-charts 6.0
- RxJS 7.8

## 🐛 Troubleshooting

### Backend Not Starting

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:

```bash
pip install flask flask-cors
```

### Frontend Build Errors

**Error**: `Cannot find module '@angular/core'`

**Solution**:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### API Connection Failed

**Error**: "Failed to load configuration"

**Solution**:

1. Ensure backend is running on port 5000
2. Check CORS is enabled
3. Verify firewall settings

### Chart Not Displaying

**Solution**:

```bash
cd frontend
npm install chart.js ng2-charts
```

## 🔐 Security Notes

- This is a development setup - **DO NOT** expose to the internet
- Backend runs without authentication - for local use only
- Add authentication/authorization for production use
- Use environment variables for sensitive configuration

## 📈 Performance Tips

1. **Training**: Use smaller datasets for faster training during development
2. **Backtesting**: Limit period to 1-2 years for quicker results
3. **Frontend**: Enable production mode for better performance
4. **API**: Consider Redis for job storage in production

## 🚀 Production Deployment

### Backend

```bash
# Use production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.api:app
```

### Frontend

```bash
cd frontend
npm run build
# Serve dist/ folder with nginx or similar
```

## 📝 Future Enhancements

- [ ] User authentication
- [ ] Multiple strategy comparison
- [ ] Real-time trading signals
- [ ] Email/SMS notifications
- [ ] Advanced charting (candlesticks, indicators overlay)
- [ ] Walk-forward optimization
- [ ] Monte Carlo simulation
- [ ] Portfolio management

## 🤝 Contributing

1. Configure parameters
2. Train your model
3. Run backtests
4. Analyze results
5. Iterate and improve!

## ⚠️ Disclaimer

This software is for **educational and research purposes only**.

- Does NOT place real trades
- Does NOT connect to brokers
- Past performance does NOT guarantee future results
- Trading carries significant risk
- Always do your own research

## 📄 License

Open-source for educational use.

---

## 🎓 Learning Resources

- **Machine Learning**: scikit-learn documentation
- **Technical Analysis**: TA-Lib, pandas-ta
- **Angular**: Angular.io official docs
- **Flask**: Flask documentation

---

**Built with ❤️ for algorithmic trading enthusiasts**

**Happy Backtesting! 📈📉**
