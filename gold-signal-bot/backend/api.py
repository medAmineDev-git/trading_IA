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
import hashlib

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
last_backtest_results = {} # Store last backtest for manual saving

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
STRATEGIES_FILE = os.path.join(DATA_DIR, 'strategies.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def save_strategy(strategy):
    """Save a strategy to the JSON history file"""
    strategies = []
    if os.path.exists(STRATEGIES_FILE):
        try:
            with open(STRATEGIES_FILE, 'r') as f:
                strategies = json.load(f)
        except:
            strategies = []
    
    # Check if this strategy already exists (for updates)
    existing_idx = -1
    for i, s in enumerate(strategies):
        if s.get('id') == strategy.get('id'):
            existing_idx = i
            break
    
    if existing_idx >= 0:
        strategies[existing_idx] = strategy
    else:
        strategies.append(strategy)
    
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


def sync_config(params):
    """Update global config with custom parameters"""
    print(f"\n⚙️ Syncing configuration with params: {params.keys()}")
    
    if 'indicators' in params:
        ind = params['indicators']
        config.RSI_PERIOD = int(ind.get('rsi_period', config.RSI_PERIOD))
        config.MACD_FAST = int(ind.get('macd_fast', config.MACD_FAST))
        config.MACD_SLOW = int(ind.get('macd_slow', config.MACD_SLOW))
        config.MACD_SIGNAL = int(ind.get('macd_signal', config.MACD_SIGNAL))
        config.BB_PERIOD = int(ind.get('bb_period', config.BB_PERIOD))
        config.BB_STD_DEV = float(ind.get('bb_std_dev', config.BB_STD_DEV))
        config.ATR_PERIOD = int(ind.get('atr_period', config.ATR_PERIOD))
        config.EMA_FAST = int(ind.get('ema_fast', config.EMA_FAST))
        config.EMA_SLOW = int(ind.get('ema_slow', config.EMA_SLOW))
        print(f"   Indicators updated: RSI={config.RSI_PERIOD}, MACD={config.MACD_FAST}/{config.MACD_SLOW}/{config.MACD_SIGNAL}")

    if 'risk' in params:
        risk = params['risk']
        config.STOP_LOSS_PERCENT = float(risk.get('stop_loss_percent', config.STOP_LOSS_PERCENT))
        config.TAKE_PROFIT_PERCENT = float(risk.get('take_profit_percent', config.TAKE_PROFIT_PERCENT))
        config.PROB_THRESHOLD = float(risk.get('prob_threshold', config.PROB_THRESHOLD))
        config.USE_ATR_STOPS = bool(risk.get('use_atr_stops', config.USE_ATR_STOPS))
        config.USE_TREND_FILTER = bool(risk.get('use_trend_filter', config.USE_TREND_FILTER))
        config.USE_VOLATILITY_FILTER = bool(risk.get('use_volatility_filter', config.USE_VOLATILITY_FILTER))
        config.ATR_FILTER_MIN = float(risk.get('atr_filter_min', config.ATR_FILTER_MIN))
        config.ATR_FILTER_MAX = float(risk.get('atr_filter_max', config.ATR_FILTER_MAX))
        print(f"   Risk updated: SL={config.STOP_LOSS_PERCENT}, TP={config.TAKE_PROFIT_PERCENT}, Prob={config.PROB_THRESHOLD}")

    if 'model' in params:
        model = params['model']
        config.MODEL_TYPE = model.get('model_type', config.MODEL_TYPE)
        config.N_ESTIMATORS = int(model.get('n_estimators', config.N_ESTIMATORS))
        config.MAX_DEPTH = int(model.get('max_depth', config.MAX_DEPTH))
        config.MIN_SAMPLES_SPLIT = int(model.get('min_samples_split', config.MIN_SAMPLES_SPLIT))
        print(f"   Model updated: Type={config.MODEL_TYPE}, Estimators={config.N_ESTIMATORS}")

    if 'data' in params:
        data = params['data']
        if 'csv_path' in data and data['csv_path']:
            # Handle both absolute and relative paths
            csv_path = data['csv_path']
            if not os.path.isabs(csv_path):
                # Join with project root (config.BASE_DIR)
                config.MT5_CSV_PATH = os.path.join(config.BASE_DIR, csv_path)
            else:
                config.MT5_CSV_PATH = csv_path
        if 'training_period' in data:
            config.TRAINING_PERIOD = data['training_period']
        print(f"   Data updated: CSV={config.MT5_CSV_PATH}, Period={config.TRAINING_PERIOD}")


def run_training_job(job_id, params):
    """Run training in background thread"""
    try:
        update_job_status(job_id, JobStatus.RUNNING, 10, 'Updating configuration...')
        
        # Update config with custom parameters
        sync_config(params)
        
        update_job_status(job_id, JobStatus.RUNNING, 30, 'Starting training...')
        
        # Capture training output
        from io import StringIO
        import contextlib
        
        output_buffer = StringIO()
        
        # Run training (this will print to console)
        def progress_callback(msg, progress):
            update_job_status(job_id, JobStatus.RUNNING, progress, msg)
            
        with contextlib.redirect_stdout(output_buffer):
            train_main(status_callback=progress_callback)
        
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
        update_job_status(job_id, JobStatus.RUNNING, 10, 'Updating configuration...')
        
        # Update config if needed
        sync_config(params)
        
        initial_balance = float(params.get('initial_capital', 10000))
        if 'period_days' in params:
            config.BACKTEST_PERIOD_DAYS = int(params['period_days'])
        
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
        # Prepare for processing
        pip_value = initial_balance / 10000.0 
        
        # Calculate metrics
        closed_trades = [t for t in backtester.trades if t['status'] == 'Closed']
        open_trades = [t for t in backtester.trades if t['status'] == 'Open']
        winning_trades = [t for t in closed_trades if t['pips'] and t['pips'] > 0]
        losing_trades = [t for t in closed_trades if t['pips'] and t['pips'] < 0]
        
        total_pips = sum(t['pips'] for t in closed_trades if t['pips'])
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
        avg_win = sum(t['pips'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pips'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Calculate Profit Factor
        gross_profit = sum(t['pips'] for t in winning_trades)
        gross_loss = abs(sum(t['pips'] for t in losing_trades))
        
        if gross_loss > 0:
            profit_factor = gross_profit / gross_loss
        else:
            profit_factor = float('inf') if gross_profit > 0 else 0.0
        
        avg_win_money = sum(t['pips'] * pip_value for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss_money = sum(t['pips'] * pip_value for t in losing_trades) / len(losing_trades) if losing_trades else 0

        equity_curve = []
        drawdown_curve = [] # NEW: Track drawdown over time
        current_balance = initial_balance
        equity_curve.append({
            'timestamp': 'Start',
            'balance': current_balance,
            'pips': 0
        })
        
        monthly_profits = {} # month_str -> total_profit_money
        
        total_profit_money = 0
        cumulative_pips = 0
        
        # Max Drawdown tracking
        peak_balance = initial_balance
        max_drawdown_amount = 0.0
        max_drawdown_percent = 0.0
        
        
        # Calculate daily returns for Max Daily Drawdown
        daily_closing_balances = {}
        
        # Helper to get the best timestamp for P&L tracking (Closing time)
        def get_pl_timestamp(t):
            return t.get('close_timestamp') or t['timestamp']

        for trade in sorted(closed_trades, key=get_pl_timestamp):
            if trade['pips'] is not None:
                profit_money = trade['pips'] * pip_value
                current_balance += profit_money
                total_profit_money += profit_money
                cumulative_pips += trade['pips']
                
                # Drawdown Calculation
                dd_percent = 0.0
                if current_balance > peak_balance:
                    peak_balance = current_balance
                else:
                    drawdown = peak_balance - current_balance
                    max_drawdown_amount = max(max_drawdown_amount, drawdown)
                    if peak_balance > 0:
                        dd_percent = (drawdown / peak_balance) * 100
                        max_drawdown_percent = max(max_drawdown_percent, dd_percent)
                
                ts = get_pl_timestamp(trade)
                
                # Update daily closing balance (latest trade on that day wins)
                daily_closing_balances[ts.date()] = current_balance

                month_key = ts.strftime('%Y-%m') if hasattr(ts, 'strftime') else str(ts)[:7]
                monthly_profits[month_key] = monthly_profits.get(month_key, 0) + profit_money
                
                equity_curve.append({
                    'timestamp': ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
                    'balance': round(current_balance, 2),
                    'pips': round(cumulative_pips, 2) 
                })
                
                drawdown_curve.append({
                    'timestamp': ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
                    'drawdown': round(dd_percent, 2)
                })
                
                # Update the trade record in trades_data with the calculated profit_money
                trade['profit_money'] = round(profit_money, 2)

        # Calculate Daily Performance (Profit, Count, Percent)
        daily_perf_data = {}
        sorted_days = sorted(daily_closing_balances.keys())
        prev_running_balance = initial_balance
        
        for day in sorted_days:
            close_bal = daily_closing_balances[day]
            profit_today = close_bal - prev_running_balance
            
            # Use INITIAL BALANCE as divisor for Daily ROI (to match user expectations)
            # If he prefers compounded, it would be divided by prev_running_balance
            percent_today = (profit_today / initial_balance) * 100
            
            # Count trades for this day based on get_pl_timestamp
            trades_today = [t for t in closed_trades if get_pl_timestamp(t).date() == day]
            
            daily_perf_data[day.isoformat()] = {
                'profit': round(profit_today, 2),
                'percent': round(percent_today, 2),
                'count': len(trades_today)
            }
            prev_running_balance = close_bal

        # Build final trades data for response (now that profit_money is calculated)
        trades_data = []
        for trade in backtester.trades:
            # Use same timestamp logic for status consistency if possible
            close_ts = trade.get('close_timestamp')
            trades_data.append({
                'timestamp': trade['timestamp'].isoformat() if hasattr(trade['timestamp'], 'isoformat') else str(trade['timestamp']),
                'type': trade['type'],
                'entry_price': float(trade['entry_price']),
                'sl': float(trade['sl']),
                'tp': float(trade['tp']),
                'close_price': float(trade['close_price']) if trade['close_price'] else None,
                'close_timestamp': close_ts.isoformat() if close_ts and hasattr(close_ts, 'isoformat') else str(close_ts) if close_ts else None,
                'close_reason': trade['close_reason'],
                'pips': float(trade['pips']) if trade['pips'] else None,
                'profit_money': float(trade['profit_money']) if 'profit_money' in trade else 0.0,
                'status': trade['status'],
                'confidence': float(trade['confidence'])
            })

        # Calculate Max Daily Drawdown (Worst Daily Return %)
        worst_daily_return_percent = 0.0
        for day_data in daily_perf_data.values():
            if day_data['percent'] < worst_daily_return_percent:
                worst_daily_return_percent = day_data['percent']

        # Convert monthly profits to percentages
        monthly_perf = []
        for month in sorted(monthly_profits.keys()):
            percent_gain = (monthly_profits[month] / initial_balance) * 100
            monthly_perf.append({
                'month': month,
                'percent': round(percent_gain, 2),
                'profit': round(monthly_profits[month], 2)
            })
            
        result = {
            'trades': trades_data,
            'metrics': {
                'initial_balance': initial_balance,
                'final_balance': round(current_balance, 2),
                'total_profit_money': round(total_profit_money, 2),
                'total_pips': round(total_pips, 2),
                'total_trades': len(backtester.trades),
                'closed_trades': len(closed_trades),
                'open_trades': len(open_trades),
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': round(win_rate, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'profit_factor': round(profit_factor, 2) if profit_factor != float('inf') else 999.99,
                'avg_win_money': round(avg_win_money, 2),
                'avg_loss_money': round(avg_loss_money, 2),
                'period_days': config.BACKTEST_PERIOD_DAYS,
                'max_drawdown_amount': round(max_drawdown_amount, 2),
                'max_drawdown_percent': round(max_drawdown_percent, 2),
                'max_daily_drawdown_percent': round(worst_daily_return_percent, 2)
            },
            'equity_curve': equity_curve,
            'drawdown_curve': drawdown_curve,
            'monthly_performance': monthly_perf,
            'daily_performance': daily_perf_data,
            'output': output_buffer.getvalue(),
            'timestamp': datetime.now().isoformat()
        }
        
        update_job_status(job_id, JobStatus.COMPLETED, 100, 'Backtest completed successfully!', result)
        
        # Store backtest results globally for manual saving
        # We don't save automatically anymore
        global last_backtest_results
        last_backtest_results = result
        
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
            'use_trend_filter': config.USE_TREND_FILTER,
            'use_volatility_filter': config.USE_VOLATILITY_FILTER,
            'atr_filter_min': config.ATR_FILTER_MIN,
            'atr_filter_max': config.ATR_FILTER_MAX
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


# ==================== AUTH ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
        
    users = load_users()
    if email in users:
        return jsonify({'error': 'User already exists'}), 400
        
    # Mock salt and hash
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    user_id = str(uuid.uuid4())
    users[email] = {
        'id': user_id,
        'email': email,
        'password': hashed_password,
        'created_at': datetime.now().isoformat()
    }
    
    save_users(users)
    return jsonify({
        'message': 'User registered successfully',
        'user': {'id': user_id, 'email': email, 'token': f"mock-token-{user_id}"}
    }), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    users = load_users()
    user = users.get(email)
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    if user['password'] != hashed_password:
        return jsonify({'error': 'Invalid credentials'}), 401
        
    return jsonify({
        'message': 'Login successful',
        'user': {'id': user['id'], 'email': email, 'token': f"mock-token-{user['id']}"}
    })


# ==================== STRATEGY MANAGEMENT ====================

@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get all PUBLIC (published) strategies"""
    if not os.path.exists(STRATEGIES_FILE):
        return jsonify([])
    
    try:
        with open(STRATEGIES_FILE, 'r') as f:
            strategies = json.load(f)
        
        # Filter only published ones
        published = [s for s in strategies if s.get('is_published', False)]
        return jsonify(published[::-1]) # Return newest first
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/my-strategies', methods=['GET'])
def get_my_strategies():
    """Get strategies for a specific user"""
    user_id = request.headers.get('Authorization', '').replace('Bearer mock-token-', '')
    
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    if not os.path.exists(STRATEGIES_FILE):
        return jsonify([])
        
    try:
        with open(STRATEGIES_FILE, 'r') as f:
            strategies = json.load(f)
        
        my_strategies = [s for s in strategies if s.get('owner_id') == user_id]
        return jsonify(my_strategies[::-1])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategies/save', methods=['POST'])
def save_personal_strategy():
    """Manually save a strategy from the last backtest"""
    user_id = request.headers.get('Authorization', '').replace('Bearer mock-token-', '')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
        
    data = request.get_json()
    strategy_name = data.get('name')
    
    if not strategy_name:
        return jsonify({'error': 'Strategy name required'}), 400
        
    if not last_training_info or not last_backtest_results:
        return jsonify({'error': 'No recent backtest results to save'}), 400
        
    strategy = {
        'id': str(uuid.uuid4()),
        'name': strategy_name,
        'owner_id': user_id,
        'is_published': False,
        'training': last_training_info,
        'backtest': last_backtest_results,
        'created_at': datetime.now().isoformat()
    }
    
    save_strategy(strategy)
    return jsonify({"status": "success", "strategy": strategy})

@app.route('/api/strategies/publish', methods=['POST'])
def publish_strategy():
    user_id = request.headers.get('Authorization', '').replace('Bearer mock-token-', '')
    data = request.get_json()
    strategy_id = data.get('strategy_id')
    
    strategies = []
    if os.path.exists(STRATEGIES_FILE):
        with open(STRATEGIES_FILE, 'r') as f:
            strategies = json.load(f)
            
    found = False
    for s in strategies:
        if s.get('id') == strategy_id and s.get('owner_id') == user_id:
            s['is_published'] = not s.get('is_published', False)
            found = True
            break
            
    if found:
        # Sort and save
        with open(STRATEGIES_FILE, 'w') as f:
            json.dump(strategies, f, indent=4)
        return jsonify({"status": "success", "is_published": s['is_published']})
        
    return jsonify({"error": "Strategy not found or unauthorized"}), 404

@app.route('/api/strategies/remove', methods=['DELETE'])
def remove_strategy():
    user_id = request.headers.get('Authorization', '').replace('Bearer mock-token-', '')
    strategy_id = request.args.get('strategy_id')
    
    strategies = []
    if os.path.exists(STRATEGIES_FILE):
        with open(STRATEGIES_FILE, 'r') as f:
            strategies = json.load(f)
            
    new_strategies = [s for s in strategies if not (s.get('id') == strategy_id and s.get('owner_id') == user_id)]
    
    if len(new_strategies) < len(strategies):
        with open(STRATEGIES_FILE, 'w') as f:
            json.dump(new_strategies, f, indent=4)
        return jsonify({"status": "success"})
        
    return jsonify({"error": "Strategy not found or unauthorized"}), 404


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
