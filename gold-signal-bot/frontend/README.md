# Gold Signal Bot - Angular Dashboard

Modern Angular 20 dashboard for configuring, training, and backtesting the Gold Signal Bot ML trading strategy.

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ (for backend API)

### Installation

```bash
# Install dependencies
cd frontend
npm install
```

### Running the Application

#### 1. Start the Backend API

```bash
# In the project root directory
cd backend
python api.py
```

The API will start on `http://127.0.0.1:5000`

#### 2. Start the Angular Dev Server

```bash
# In the frontend directory
cd frontend
npm start
```

The dashboard will be available at `http://localhost:4200`

## 📋 Features

### 1. Parameters Configuration

- **Technical Indicators**: Configure RSI, MACD, Bollinger Bands, ATR, and EMA parameters
- **Risk Management**: Set stop loss, take profit, and confidence thresholds
- **Model Hyperparameters**: Adjust Random Forest settings (trees, depth, splits)
- **Data Source**: Select CSV files and training periods

### 2. Model Training

- Real-time progress tracking
- Training metrics display (accuracy, samples, features)
- Model metadata visualization
- Automatic parameter application

### 3. Backtesting

- Configurable backtest period
- Real-time progress updates
- Quick results summary
- Detailed performance metrics

### 4. Results Visualization

- **Charts**: Interactive equity curve with Chart.js
- **Trade Table**: Sortable, filterable trade history
- **Statistics**: Comprehensive performance metrics
- **Export**: Download results as CSV

## 🎨 UI Components

### Material Design

- Angular Material 20 components
- Responsive grid layouts
- Card-based interface
- Tab navigation
- Progress indicators

### Charts

- Equity curve (cumulative pips over time)
- Line charts with Chart.js
- Responsive and interactive

## 📁 Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── core/
│   │   │   ├── models/
│   │   │   │   └── models.ts              # TypeScript interfaces
│   │   │   └── services/
│   │   │       └── api.service.ts         # HTTP client service
│   │   ├── features/
│   │   │   ├── dashboard/
│   │   │   │   └── dashboard.component.ts # Main container
│   │   │   ├── parameters/
│   │   │   │   └── parameters-form.component.* # Config form
│   │   │   ├── training/
│   │   │   │   └── training-panel.component.* # Training UI
│   │   │   ├── backtesting/
│   │   │   │   └── backtest-panel.component.ts # Backtest UI
│   │   │   └── results/
│   │   │       └── results-dashboard.component.* # Results & charts
│   │   ├── app.component.ts
│   │   ├── app.config.ts
│   │   └── app.routes.ts
│   ├── styles.scss                        # Global styles
│   ├── index.html
│   └── main.ts
├── angular.json
├── package.json
└── tsconfig.json
```

## 🔧 Configuration

### API Endpoint

The API base URL is configured in `api.service.ts`:

```typescript
private baseUrl = 'http://127.0.0.1:5000/api';
```

Change this if your backend runs on a different host/port.

### Chart.js

Charts are configured in `results-dashboard.component.ts`. Customize chart options:

```typescript
equityChartOptions: ChartConfiguration["options"] = {
  // Your custom options
};
```

## 📊 API Endpoints Used

- `GET /api/config` - Load default configuration
- `GET /api/data-files` - List available CSV files
- `POST /api/train` - Start training job
- `GET /api/train/status/<job_id>` - Poll training progress
- `GET /api/train/results/<job_id>` - Get training results
- `POST /api/backtest` - Start backtest job
- `GET /api/backtest/status/<job_id>` - Poll backtest progress
- `GET /api/backtest/results/<job_id>` - Get backtest results

## 🧪 Development

### Build for Production

```bash
npm run build
```

Output will be in `dist/gold-signal-bot-dashboard/`

### Run Tests

```bash
npm test
```

### Linting

```bash
ng lint
```

## 🎯 Workflow

1. **Configure Parameters** → Adjust indicators, risk, and model settings
2. **Train Model** → Click "Start Training" and monitor progress
3. **Run Backtest** → Configure period and execute backtest
4. **View Results** → Analyze charts, trades, and statistics
5. **Export Data** → Download results as CSV for further analysis

## 🐛 Troubleshooting

### API Connection Error

**Error**: "Failed to load configuration. Is the API server running?"

**Solution**:

1. Ensure the backend API is running on port 5000
2. Check CORS is enabled in `backend/api.py`
3. Verify the API URL in `api.service.ts`

### Chart Not Rendering

**Solution**:

1. Ensure Chart.js is installed: `npm install chart.js ng2-charts`
2. Check browser console for errors
3. Verify data format matches Chart.js requirements

### Module Not Found

**Solution**:

```bash
rm -rf node_modules package-lock.json
npm install
```

## 📦 Dependencies

### Core

- Angular 20
- Angular Material 20
- RxJS 7.8

### Charts

- Chart.js 4.4
- ng2-charts 6.0

### Development

- TypeScript 5.6
- Angular CLI 20

## 🚀 Performance

- Lazy loading for feature modules
- OnPush change detection strategy
- Optimized bundle size
- Server-side polling with RxJS

## 📝 License

This project is part of the Gold Signal Bot backtesting tool.

## 🤝 Contributing

1. Configure parameters
2. Train model
3. Run backtest
4. Analyze results
5. Iterate and improve!

---

**Happy Trading! 📈📉**
