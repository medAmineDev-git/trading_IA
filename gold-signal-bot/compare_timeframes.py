"""
Compare Timeframes Script
Trains and backtests multiple timeframes to find the best performing one
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
import os
import pickle
from datetime import datetime, timedelta

warnings.filterwarnings('ignore')

import config
from utils.indicators import add_all_indicators, prepare_features
from utils.model_loader import save_model, save_training_metadata
from utils.mt5_fetch import load_csv_data


class TimeframeComparator:
    """Compare performance across multiple timeframes"""
    
    def __init__(self):
        self.results = {}
        self.timeframes = {
            '1D': 'data/XAUUSD_1D.csv',
            'H4': 'data/XAUUSD_h4.csv',
            'H1': 'data/XAUUSD_h1.csv'
        }
    
    def train_timeframe(self, timeframe_name, csv_path):
        """Train model for a specific timeframe"""
        print(f"\n{'='*70}")
        print(f"🔄 TRAINING: {timeframe_name}")
        print(f"{'='*70}")
        print(f"CSV Path: {csv_path}")
        
        # Load data
        if not os.path.exists(csv_path):
            print(f"❌ File not found: {csv_path}")
            return None
        
        df = load_csv_data(csv_path)
        if df is None or df.empty:
            print(f"❌ Failed to load {csv_path}")
            return None
        
        print(f"✅ Loaded {len(df)} candles")
        
        # Sample for speed (max 10k candles for training)
        if len(df) > 10000:
            sample_idx = np.random.choice(len(df), 10000, replace=False)
            sample_idx.sort()
            df = df.iloc[sample_idx].reset_index(drop=True)
            print(f"   Sampled to {len(df)} candles for speed")
        
        # Add indicators
        print(f"📊 Computing indicators...")
        df = add_all_indicators(df)
        
        # Prepare features
        print(f"🎯 Preparing features...")
        X, y = prepare_features(df)
        
        if X is None or len(X) == 0:
            print(f"❌ Failed to prepare features")
            return None
        
        print(f"   Features: {X.shape[1]}")
        print(f"   Samples: {len(X)}")
        print(f"   Class distribution: {np.bincount(y.astype(int))}")
        
        # Train/test split (80/20 time-series)
        split_idx = int(len(X) * 0.8)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        print(f"   Train samples: {len(X_train)}, Test samples: {len(X_test)}")
        
        # Train model
        print(f"🤖 Training RandomForest ({config.N_ESTIMATORS} trees)...")
        model = RandomForestClassifier(
            n_estimators=config.N_ESTIMATORS,
            max_depth=config.MAX_DEPTH,
            min_samples_split=config.MIN_SAMPLES_SPLIT,
            min_samples_leaf=config.MIN_SAMPLES_LEAF,
            random_state=config.RANDOM_STATE,
            class_weight='balanced',
            n_jobs=-1,
            verbose=0
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        
        print(f"📈 Training Accuracy: {train_acc:.4f}")
        print(f"📈 Test Accuracy: {test_acc:.4f}")
        
        # Save model
        model_name = f'gold_signal_model_{timeframe_name}.pkl'
        model_path = os.path.join(config.MODEL_DIR, model_name)
        os.makedirs(config.MODEL_DIR, exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"💾 Model saved: {model_path}")
        
        return {
            'model': model,
            'model_path': model_path,
            'train_acc': train_acc,
            'test_acc': test_acc,
            'df': df,
            'X_test': X_test,
            'y_test': y_test,
            'num_candles': len(df)
        }
    
    def backtest_timeframe(self, timeframe_name, model_data):
        """Backtest strategy for a specific timeframe"""
        if model_data is None:
            print(f"⚠️  Skipping backtest for {timeframe_name} (model not available)")
            return None
        
        print(f"\n{'='*70}")
        print(f"📊 BACKTEST: {timeframe_name}")
        print(f"{'='*70}")
        
        model = model_data['model']
        df = model_data['df'].copy()
        
        # Limit backtest to last 1000 candles for speed
        df = df.tail(1000).reset_index(drop=True)
        
        # Add indicators and features
        df = add_all_indicators(df)
        X, y = prepare_features(df)
        
        if X is None or len(X) == 0:
            print(f"❌ Failed to prepare features for backtest")
            return None
        
        # Get predictions
        y_pred = model.predict(X)
        y_pred_proba = model.predict_proba(X)
        
        # Add predictions to dataframe
        df['pred'] = y_pred
        df['pred_proba'] = y_pred_proba.max(axis=1)
        
        # Simulate trading (optimized)
        trades = []
        position = None
        entry_price = None
        entry_idx = None
        entry_time = None
        
        for i in range(1, len(df)):
            current_pred = df.iloc[i]['pred']
            current_proba = df.iloc[i]['pred_proba']
            current_price = df.iloc[i]['Close']
            current_time = i
            
            prev_pred = df.iloc[i-1]['pred'] if i > 0 else None
            
            # Entry signals
            if position is None and current_proba >= config.PROB_THRESHOLD:
                # BUY signal (pred=1)
                if current_pred == 1 and prev_pred == 0:
                    rsi = df.iloc[i].get('RSI', 50)
                    if rsi >= config.RSI_BUY_MIN:
                        position = 'BUY'
                        entry_price = current_price
                        entry_idx = i
                        entry_time = current_time
                
                # SELL signal (pred=0)
                elif current_pred == 0 and prev_pred == 1:
                    rsi = df.iloc[i].get('RSI', 50)
                    if rsi <= config.RSI_SELL_MAX:
                        position = 'SELL'
                        entry_price = current_price
                        entry_idx = i
                        entry_time = current_time
            
            # Exit signals
            elif position is not None:
                if position == 'BUY':
                    pips = (current_price - entry_price) * 100
                    stop_loss = entry_price * (1 - config.STOP_LOSS_PERCENT)
                    take_profit = entry_price * (1 + config.TAKE_PROFIT_PERCENT)
                    
                    # SL hit
                    if current_price <= stop_loss:
                        trades.append({
                            'Pips': -abs(config.STOP_LOSS_PERCENT * 100),
                            'Reason': 'SL'
                        })
                        position = None
                    
                    # TP hit
                    elif current_price >= take_profit:
                        trades.append({
                            'Pips': config.TAKE_PROFIT_PERCENT * 100,
                            'Reason': 'TP'
                        })
                        position = None
                    
                    # Signal reversal
                    elif current_pred == 0 and current_proba >= config.PROB_THRESHOLD:
                        trades.append({
                            'Pips': pips,
                            'Reason': 'Signal'
                        })
                        position = None
                
                elif position == 'SELL':
                    pips = (entry_price - current_price) * 100
                    stop_loss = entry_price * (1 + config.STOP_LOSS_PERCENT)
                    take_profit = entry_price * (1 - config.TAKE_PROFIT_PERCENT)
                    
                    # SL hit
                    if current_price >= stop_loss:
                        trades.append({
                            'Pips': -abs(config.STOP_LOSS_PERCENT * 100),
                            'Reason': 'SL'
                        })
                        position = None
                    
                    # TP hit
                    elif current_price <= take_profit:
                        trades.append({
                            'Pips': config.TAKE_PROFIT_PERCENT * 100,
                            'Reason': 'TP'
                        })
                        position = None
                    
                    # Signal reversal
                    elif current_pred == 1 and current_proba >= config.PROB_THRESHOLD:
                        trades.append({
                            'Pips': pips,
                            'Reason': 'Signal'
                        })
                        position = None
        
        # Calculate metrics
        if len(trades) == 0:
            print(f"⚠️  No trades generated")
            return {
                'trades': [],
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pips': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'model_path': model_data['model_path']
            }
        
        trades_df = pd.DataFrame(trades)
        
        total_trades = len(trades_df)
        winning_trades = len(trades_df[trades_df['Pips'] > 0])
        losing_trades = len(trades_df[trades_df['Pips'] < 0])
        total_pips = trades_df['Pips'].sum()
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        win_pips = trades_df[trades_df['Pips'] > 0]['Pips'].sum()
        loss_pips = abs(trades_df[trades_df['Pips'] < 0]['Pips'].sum())
        
        avg_win = (win_pips / winning_trades) if winning_trades > 0 else 0
        avg_loss = (loss_pips / losing_trades) if losing_trades > 0 else 0
        profit_factor = (win_pips / loss_pips) if loss_pips > 0 else 0
        
        print(f"✅ Total Trades: {total_trades}")
        print(f"   Winning: {winning_trades} ({win_rate:.2f}%)")
        print(f"   Losing: {losing_trades}")
        print(f"   Total Pips: {total_pips:,.2f}")
        print(f"   Avg Win: {avg_win:.2f} pips")
        print(f"   Avg Loss: {avg_loss:.2f} pips")
        print(f"   Profit Factor: {profit_factor:.2f}")
        
        return {
            'trades': trades_df,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pips': total_pips,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'model_path': model_data['model_path']
        }
    
    def run_comparison(self):
        """Run full comparison across all timeframes"""
        print(f"\n🌟 MULTI-TIMEFRAME COMPARISON 🌟")
        print(f"Timeframes: {', '.join(self.timeframes.keys())}")
        
        # Train all timeframes
        model_data = {}
        for timeframe, csv_path in self.timeframes.items():
            model_data[timeframe] = self.train_timeframe(timeframe, csv_path)
        
        # Backtest all timeframes
        backtest_results = {}
        for timeframe in self.timeframes.keys():
            backtest_results[timeframe] = self.backtest_timeframe(timeframe, model_data[timeframe])
        
        # Generate comparison report
        self.generate_report(model_data, backtest_results)
        
        return backtest_results
    
    def generate_report(self, model_data, backtest_results):
        """Generate comprehensive comparison report"""
        report_path = 'data/timeframe_comparison_report.txt'
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("MULTI-TIMEFRAME COMPARISON REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Training metrics
            f.write("TRAINING METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Timeframe':<12} {'Candles':<12} {'Train Acc':<12} {'Test Acc':<12}\n")
            f.write("-" * 80 + "\n")
            
            for timeframe, data in model_data.items():
                if data:
                    f.write(f"{timeframe:<12} {data['num_candles']:<12} "
                           f"{data['train_acc']:.4f}        {data['test_acc']:.4f}\n")
            
            f.write("\n")
            
            # Backtest metrics
            f.write("BACKTEST METRICS\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Timeframe':<12} {'Trades':<10} {'Win%':<10} {'Pips':<15} {'PF':<8}\n")
            f.write("-" * 80 + "\n")
            
            best_timeframe = None
            best_pips = -float('inf')
            
            for timeframe, results in backtest_results.items():
                if results:
                    trades = results['total_trades']
                    win_rate = results['win_rate']
                    pips = results['total_pips']
                    pf = results['profit_factor']
                    
                    f.write(f"{timeframe:<12} {trades:<10} {win_rate:>8.2f}% "
                           f"{pips:>13,.2f} {pf:>7.2f}\n")
                    
                    if pips > best_pips:
                        best_pips = pips
                        best_timeframe = timeframe
            
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write(f"🏆 BEST TIMEFRAME: {best_timeframe} (Total Pips: {best_pips:,.2f})\n")
            f.write("=" * 80 + "\n\n")
            
            # Detailed results per timeframe
            for timeframe, results in backtest_results.items():
                if results and results['total_trades'] > 0:
                    f.write(f"\n{timeframe} DETAILED RESULTS\n")
                    f.write("-" * 80 + "\n")
                    f.write(f"Total Trades: {results['total_trades']}\n")
                    f.write(f"Winning Trades: {results['winning_trades']} ({results['win_rate']:.2f}%)\n")
                    f.write(f"Losing Trades: {results['losing_trades']}\n")
                    f.write(f"Total Pips: {results['total_pips']:,.2f}\n")
                    f.write(f"Avg Win: {results['avg_win']:.2f} pips\n")
                    f.write(f"Avg Loss: {results['avg_loss']:.2f} pips\n")
                    f.write(f"Profit Factor: {results['profit_factor']:.2f}\n")
                    f.write(f"Model Path: {results['model_path']}\n")
        
        print(f"\n✅ Report saved: {report_path}")


if __name__ == '__main__':
    comparator = TimeframeComparator()
    results = comparator.run_comparison()
    
    print(f"\n✨ Comparison complete! Check 'data/timeframe_comparison_report.txt' for details.")
