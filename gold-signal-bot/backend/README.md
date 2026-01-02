# Backend API

Flask REST API for Gold Signal Bot dashboard.

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python api.py
```

Server will start on `http://127.0.0.1:5000`

## API Endpoints

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
