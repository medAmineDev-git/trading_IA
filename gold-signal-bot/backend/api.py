"""
Flask API for Gold Signal Bot
Provides REST endpoints for training models and running backtests
"""

import os
import sys
import json
import uuid
import threading
from datetime import datetime
from telegram_service import telegram_service
from live_manager import live_manager
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import traceback

# Add parent directory to path to import project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from train_model import main as train_main
from backtest import GoldBacktester

app = Flask(__name__)
CORS(app)  # Enable CORS for Angular dev server

# In-memory storage for jobs (use Redis in production)
jobs = {}
job_results = {}
last_training_info = {} # Store the params of the last successful training

STRATEGIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'strategies.json')

def save_strategy(strategy):
    """Save a strategy to the JSON history file"""
    strategies = []
    if os.path.exists(STRATEGIES_FILE):
        try:
            with open(STRATEGIES_FILE, 'r') as f:
                strategies = json.load(f)
        except:
            strategies = []
    
    strategies.append(strategy)
    # Sort by win rate or profit if needed, but for now just reverse chronological
    
    os.makedirs(os.path.dirname(STRATEGIES_FILE), exist_ok=True)
    with open(STRATEGIES_FILE, 'w') as f:
        json.dump(strategies, f, indent=4)


class JobStatus:
    PENDING = 'pending'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'


def update_job_status(job_id, status, progress=0, message='', result=None):
    """Update job status and store result"""
    jobs[job_id] = {
        'status': status,
        'progress': progress,
        'message': message,
        'updated_at': datetime.now().isoformat()
    }
    if result:
        job_results[job_id] = result


def run_training_job(job_id, params):
    """Run training in background thread"""
    try:
        update_job_status(job_id, JobStatus.RUNNING, 10, 'Updating configuration...')
        
        # Update config with custom parameters
        if 'indicators' in params:
            ind = params['indicators']
            config.RSI_PERIOD = ind.get('rsi_period', config.RSI_PERIOD)
            config.MACD_FAST = ind.get('macd_fast', config.MACD_FAST)
            config.MACD_SLOW = ind.get('macd_slow', config.MACD_SLOW)
            config.MACD_SIGNAL = ind.get('macd_signal', config.MACD_SIGNAL)
            config.BB_PERIOD = ind.get('bb_period', config.BB_PERIOD)
            config.BB_STD_DEV = ind.get('bb_std_dev', config.BB_STD_DEV)
            config.ATR_PERIOD = ind.get('atr_period', config.ATR_PERIOD)
            config.EMA_FAST = ind.get('ema_fast', config.EMA_FAST)
            config.EMA_SLOW = ind.get('ema_slow', config.EMA_SLOW)
        
        if 'risk' in params:
            risk = params['risk']
            config.STOP_LOSS_PERCENT = risk.get('stop_loss_percent', config.STOP_LOSS_PERCENT)
            config.TAKE_PROFIT_PERCENT = risk.get('take_profit_percent', config.TAKE_PROFIT_PERCENT)
            config.PROB_THRESHOLD = risk.get('prob_threshold', config.PROB_THRESHOLD)
            config.USE_ATR_STOPS = risk.get('use_atr_stops', config.USE_ATR_STOPS)
            config.USE_TREND_FILTER = risk.get('use_trend_filter', config.USE_TREND_FILTER)
        
        if 'model' in params:
            model = params['model']
            config.MODEL_TYPE = model.get('model_type', config.MODEL_TYPE)
            config.N_ESTIMATORS = model.get('n_estimators', config.N_ESTIMATORS)
            config.MAX_DEPTH = model.get('max_depth', config.MAX_DEPTH)
            config.MIN_SAMPLES_SPLIT = model.get('min_samples_split', config.MIN_SAMPLES_SPLIT)
        
        if 'data' in params:
            data = params['data']
            if 'csv_path' in data:
                config.MT5_CSV_PATH = data['csv_path']
            if 'training_period' in data:
                config.TRAINING_PERIOD = data['training_period']
        
        update_job_status(job_id, JobStatus.RUNNING, 30, 'Starting training...')
        
        # Capture training output
        from io import StringIO
        import contextlib
        
        output_buffer = StringIO()
        
        # Run training (this will print to console)
        with contextlib.redirect_stdout(output_buffer):
            train_main()
        
        update_job_status(job_id, JobStatus.RUNNING, 90, 'Training complete, saving results...')
        
        # Read training metadata
        metadata_path = os.path.join(config.MODEL_DIR, 'training_metadata.txt')
        metadata = {}
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.strip().split(':', 1)
                        metadata[key.strip()] = value.strip()
        
        result = {
            'metadata': metadata,
            'output': output_buffer.getvalue(),
            'model_path': config.MODEL_PATH,
            'timestamp': datetime.now().isoformat()
        }
        
        update_job_status(job_id, JobStatus.COMPLETED, 100, 'Training completed successfully!', result)
        
        # Store for next backtest
        global last_training_info
        last_training_info = {
            'params': params,
            'metadata': metadata,
            'timestamp': result['timestamp']
        }
        
    except Exception as e:
        error_msg = f"Training failed: {str(e)}\n{traceback.format_exc()}"
        update_job_status(job_id, JobStatus.FAILED, 0, error_msg)


def run_backtest_job(job_id, params):
    """Run backtest in background thread"""
    try:
        update_job_status(job_id, JobStatus.RUNNING, 10, 'Initializing backtest...')
        
        # Update config if needed
        if 'period_days' in params:
            config.BACKTEST_PERIOD_DAYS = params['period_days']
        
        update_job_status(job_id, JobStatus.RUNNING, 30, 'Loading model and data...')
        
        # Create backtester
        backtester = GoldBacktester(days=config.BACKTEST_PERIOD_DAYS)
        
        update_job_status(job_id, JobStatus.RUNNING, 50, 'Running backtest...')
        
        # Capture output
        from io import StringIO
        import contextlib
        
        output_buffer = StringIO()
        
        with contextlib.redirect_stdout(output_buffer):
            backtester.run_backtest()
        
        update_job_status(job_id, JobStatus.RUNNING, 90, 'Processing results...')
        
        # Extract results
        trades_data = []
        for trade in backtester.trades:
            trades_data.append({
                'timestamp': trade['timestamp'].isoformat() if hasattr(trade['timestamp'], 'isoformat') else str(trade['timestamp']),
                'type': trade['type'],
                'entry_price': float(trade['entry_price']),
                'sl': float(trade['sl']),
                'tp': float(trade['tp']),
                'close_price': float(trade['close_price']) if trade['close_price'] else None,
                'close_timestamp': trade['close_timestamp'].isoformat() if trade['close_timestamp'] and hasattr(trade['close_timestamp'], 'isoformat') else str(trade['close_timestamp']) if trade['close_timestamp'] else None,
                'close_reason': trade['close_reason'],
                'pips': float(trade['pips']) if trade['pips'] else None,
                'status': trade['status'],
                'confidence': float(trade['confidence'])
            })
        
        # Calculate metrics
        closed_trades = [t for t in backtester.trades if t['status'] == 'Closed']
        winning_trades = [t for t in closed_trades if t['pips'] and t['pips'] > 0]
        losing_trades = [t for t in closed_trades if t['pips'] and t['pips'] < 0]
        
        total_pips = sum(t['pips'] for t in closed_trades if t['pips'])
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        avg_win = sum(t['pips'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pips'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Calculate equity curve
        equity_curve = []
        cumulative_pips = 0
        for trade in sorted(closed_trades, key=lambda x: x['timestamp']):
            if trade['pips'] is not None:
                cumulative_pips += trade['pips']
                equity_curve.append({
                    'timestamp': trade['timestamp'].isoformat() if hasattr(trade['timestamp'], 'isoformat') else str(trade['timestamp']),
                    'pips': cumulative_pips
                })
        
        result = {
            'trades': trades_data,
            'metrics': {
                'total_pips': round(total_pips, 2),
                'total_trades': len(backtester.trades),
                'closed_trades': len(closed_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': round(win_rate, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'profit_factor': round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0
            },
            'equity_curve': equity_curve,
            'output': output_buffer.getvalue(),
            'timestamp': datetime.now().isoformat()
        }
        
        update_job_status(job_id, JobStatus.COMPLETED, 100, 'Backtest completed successfully!', result)
        
        # If we have training info, save this as a complete strategy
        if last_training_info:
            strategy = {
                'id': str(uuid.uuid4()),
                'name': f"Strategy {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                'training': last_training_info,
                'backtest': {
                    'metrics': result['metrics'],
                    'timestamp': result['timestamp']
                }
            }
            save_strategy(strategy)
        
    except Exception as e:
        error_msg = f"Backtest failed: {str(e)}\n{traceback.format_exc()}"
        update_job_status(job_id, JobStatus.FAILED, 0, error_msg)


# ==================== API ENDPOINTS ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    config_data = {
        'indicators': {
            'rsi_period': config.RSI_PERIOD,
            'macd_fast': config.MACD_FAST,
            'macd_slow': config.MACD_SLOW,
            'macd_signal': config.MACD_SIGNAL,
            'bb_period': config.BB_PERIOD,
            'bb_std_dev': config.BB_STD_DEV,
            'atr_period': config.ATR_PERIOD,
            'ema_fast': config.EMA_FAST,
            'ema_slow': config.EMA_SLOW
        },
        'risk': {
            'stop_loss_percent': config.STOP_LOSS_PERCENT,
            'take_profit_percent': config.TAKE_PROFIT_PERCENT,
            'prob_threshold': config.PROB_THRESHOLD,
            'use_atr_stops': config.USE_ATR_STOPS,
            'use_trend_filter': config.USE_TREND_FILTER
        },
        'model': {
            'n_estimators': config.N_ESTIMATORS,
            'max_depth': config.MAX_DEPTH,
            'min_samples_split': config.MIN_SAMPLES_SPLIT
        },
        'data': {
            'ticker': config.TICKER,
            'interval': config.INTERVAL,
            'training_period': config.TRAINING_PERIOD,
            'mt5_csv_path': config.MT5_CSV_PATH
        }
    }
    return jsonify(config_data)


@app.route('/api/data-files', methods=['GET'])
def get_data_files():
    """List available CSV files in data directory"""
    # Get the parent directory (project root) since we're running from backend/
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data')
    
    if not os.path.exists(data_dir):
        return jsonify({'files': []})
    
    csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    files_with_info = []
    
    for filename in csv_files:
        filepath = os.path.join(data_dir, filename)
        stat = os.stat(filepath)
        files_with_info.append({
            'name': filename,
            'path': filepath,
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
        })
    
    return jsonify({'files': files_with_info})


@app.route('/api/train', methods=['POST'])
def start_training():
    """Start model training with custom parameters"""
    try:
        params = request.get_json()
        job_id = str(uuid.uuid4())
        
        # Initialize job
        update_job_status(job_id, JobStatus.PENDING, 0, 'Training job queued')
        
        # Start training in background thread
        thread = threading.Thread(target=run_training_job, args=(job_id, params))
        thread.daemon = True
        thread.start()
        
        return jsonify({'job_id': job_id, 'status': 'started'}), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/train/status/<job_id>', methods=['GET'])
def get_training_status(job_id):
    """Get training job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])


@app.route('/api/train/results/<job_id>', methods=['GET'])
def get_training_results(job_id):
    """Get training results"""
    if job_id not in job_results:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify(job_results[job_id])


@app.route('/api/backtest', methods=['POST'])
def start_backtest():
    """Start backtest with parameters"""
    try:
        params = request.get_json()
        job_id = str(uuid.uuid4())
        
        # Initialize job
        update_job_status(job_id, JobStatus.PENDING, 0, 'Backtest job queued')
        
        # Start backtest in background thread
        thread = threading.Thread(target=run_backtest_job, args=(job_id, params))
        thread.daemon = True
        thread.start()
        
        return jsonify({'job_id': job_id, 'status': 'started'}), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/backtest/status/<job_id>', methods=['GET'])
def get_backtest_status(job_id):
    """Get backtest job status"""
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(jobs[job_id])


@app.route('/api/backtest/results/<job_id>', methods=['GET'])
def get_backtest_results(job_id):
    """Get backtest results"""
    if job_id not in job_results:
        return jsonify({'error': 'Results not found'}), 404
    
    return jsonify(job_results[job_id])


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all saved strategies from history"""
    if not os.path.exists(STRATEGIES_FILE):
        return jsonify([])
    
    try:
        with open(STRATEGIES_FILE, 'r') as f:
            strategies = json.load(f)
        return jsonify(strategies[::-1]) # Return newest first
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/strategies/<strategy_id>/toggle-live', methods=['POST'])
def toggle_strategy_live(strategy_id):
    strategies = []
    if os.path.exists(STRATEGIES_FILE):
        with open(STRATEGIES_FILE, 'r') as f:
            strategies = json.load(f)
    
    found = False
    for s in strategies:
        # We need a way to identify strategies. Let's assume they have a 'id' or use timestamp.
        # For now, let's use the timestamp as ID if 'id' field isn't there.
        s_id = s.get('id') or s.get('backtest', {}).get('timestamp')
        if s_id == strategy_id:
            s['is_live'] = not s.get('is_live', False)
            found = True
            
            if s['is_live']:
                live_manager.start_monitoring(strategy_id, s)
            else:
                live_manager.stop_monitoring(strategy_id)
            break
    
    if found:
        with open(STRATEGIES_FILE, 'w') as f:
            json.dump(strategies, f, indent=4)
        return jsonify({"status": "success", "is_live": s['is_live']})
    
    return jsonify({"error": "Strategy not found"}), 404

@app.route('/api/strategies/telegram-link/<strategy_id>', methods=['GET'])
def get_telegram_link(strategy_id):
    # In a real app, this would be your bot username
    bot_username = os.environ.get("TELEGRAM_BOT_USERNAME", "FundedLabBot")
    link = f"https://t.me/{bot_username}?start={strategy_id}"
    return jsonify({"link": link})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 FundedLab API Server")
    print("=" * 60)
    print(f"Server starting on http://127.0.0.1:5000")
    print(f"CORS enabled for Angular dev server")
    print(f"Data directory: {config.DATA_DIR}")
    print(f"Model directory: {config.MODEL_DIR}")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
