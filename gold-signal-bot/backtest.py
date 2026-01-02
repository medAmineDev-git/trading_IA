"""
Backtest Module - Test strategy on historical data and calculate pip results
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

import config
from utils.indicators import add_all_indicators, prepare_features
from utils.model_loader import load_model
from utils.av_fetch import fetch_fx_history
from utils.mt5_fetch import load_csv_data
import os


class GoldBacktester:
    """Backtester for Gold Signal Bot"""
    
    def __init__(self, days=None, model_path=config.MODEL_PATH):
        """
        Initialize backtester
        
        Args:
            days: Number of days to backtest (default from config.BACKTEST_PERIOD_DAYS)
            model_path: Path to trained model
        """
        if days is None:
            days = config.BACKTEST_PERIOD_DAYS
        self.days = days
        self.model_path = model_path
        self.model = load_model(model_path)
        self.trades = []
        self.ticker = config.TICKER
        self.interval = config.INTERVAL
        self.used_ticker = self.ticker
        self.used_interval = self.interval
        
        if self.model is None:
            raise Exception("Model not found. Please run train_model.py first.")
    
    def fetch_data(self):
        """Fetch historical data for backtest period"""
        data_source = getattr(config, "DATA_SOURCE", "").lower()
        
        # MT5 CSV mode
        if data_source == "mt5_csv":
            csv_path = getattr(config, "MT5_CSV_PATH", "data/mt5_history.csv")
            symbol = getattr(config, "MT5_SYMBOL", "XAUUSD")
            timeframe = getattr(config, "MT5_TIMEFRAME", "H4")
            
            print(f"\n📊 Loading {self.days} days from MT5 CSV for backtest...")
            print(f"   Symbol: {symbol}, Timeframe: {timeframe}")
            
            data = load_csv_data(csv_path, days=self.days)
            if data is not None and not data.empty:
                self.used_ticker = symbol
                self.used_interval = timeframe
                print(f"✅ Loaded {len(data)} candles")
                return data
            print("❌ Failed to load MT5 CSV. Run 'python export_mt5_data.py' first.")
            return None
        
        # Alpha Vantage mode
        if data_source == "alphavantage":
            print(f"\n📊 Fetching {self.days} days of historical data from Alpha Vantage...")
            data = fetch_fx_history(self.days)
            if not data.empty:
                self.used_ticker = config.TICKER
                self.used_interval = "1d"
                print(f"✅ Downloaded {len(data)} candles (ticker={self.used_ticker}, interval={self.used_interval})")
                return data
            print("❌ No data retrieved from Alpha Vantage. Aborting (spot-only setup).")
            return None

        print(f"❌ Unsupported DATA_SOURCE: {data_source}. Use 'mt5_csv' or 'alphavantage'.")
        return None
    
    def run_backtest(self):
        """Run backtest on historical data"""
        data = self.fetch_data()
        if data is None:
            return
        
        print(f"\n🔄 Running backtest on {self.days} days of data...")

        # Debug: show columns to diagnose missing OHLCV fields
        print(f"   Data columns: {list(data.columns)}")
        print(f"   Using ticker={self.used_ticker}, interval={self.used_interval}")
        
        # Add indicators
        data_with_indicators = add_all_indicators(data)
        
        if len(data_with_indicators) == 0:
            print("❌ Not enough data to compute indicators")
            return
        
        # Prepare features
        X, _ = prepare_features(data_with_indicators)
        
        # Make predictions with probabilities
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        # Create results dataframe
        results_df = data_with_indicators.copy()
        results_df['Prediction'] = predictions
        results_df['Prob_Up'] = probabilities[:, 1]
        results_df['Prob_Down'] = probabilities[:, 0]
        results_df['Prev_Prediction'] = results_df['Prediction'].shift(1)
        
        # Track trades and filters
        prev_prediction = None
        confidence_rejects = 0
        macd_rejects = 0
        signals_generated = 0
        
        print(f"\n🎯 Generating signals...")
        
        for idx in range(len(results_df)):
            timestamp = results_df.index[idx]
            self._current_timestamp = timestamp  # Store for exit tracking
            current_price = float(results_df['Close'].iloc[idx])
            curr_pred = int(results_df['Prediction'].iloc[idx])
            prev_pred = results_df['Prev_Prediction'].iloc[idx]
            prob_up = float(results_df['Prob_Up'].iloc[idx])
            prob_down = float(results_df['Prob_Down'].iloc[idx])
            confidence = float(max(prob_up, prob_down))
            
            # Skip first row (no previous prediction)
            if pd.isna(prev_pred):
                continue
            
            prev_pred = int(prev_pred)
            latest_row = results_df.iloc[idx]
            macd_val = float(latest_row['MACD'])
            macd_sig = float(latest_row['MACD_Signal'])
            rsi_val = float(latest_row['RSI'])
            atr_val = float(latest_row['ATR'])
            ema_slow = float(latest_row['EMA_Slow'])
            
            # Trend filter: only trade with EMA200 trend
            use_trend_filter = getattr(config, 'USE_TREND_FILTER', False)
            trend_ok_buy = (current_price > ema_slow) if use_trend_filter else True
            trend_ok_sell = (current_price < ema_slow) if use_trend_filter else True
            
            macd_ok_buy = bool((macd_val > macd_sig) and (rsi_val > config.RSI_BUY_MIN) and trend_ok_buy)
            macd_ok_sell = bool((macd_val < macd_sig) and (rsi_val < config.RSI_SELL_MAX) and trend_ok_sell)
            
            # Confidence gate
            if confidence < float(config.PROB_THRESHOLD):
                confidence_rejects += 1
                self._check_trade_exits(current_price, idx)
                continue
            
            # BUY signal: previous = 0, current = 1
            if (prev_pred == 0) and (curr_pred == 1) and macd_ok_buy:
                # Use ATR-based stops if enabled
                use_atr = getattr(config, 'USE_ATR_STOPS', False)
                if use_atr and atr_val > 0:
                    atr_stop_mult = getattr(config, 'ATR_STOP_MULTIPLIER', 2.0)
                    atr_tp_mult = getattr(config, 'ATR_TP_MULTIPLIER', 10)
                    sl = round(current_price - (atr_val * atr_stop_mult), 2)
                    tp = round(current_price + (atr_val * atr_tp_mult), 2)
                else:
                    sl = round(current_price * (1 - config.STOP_LOSS_PERCENT), 2)
                    tp = round(current_price * (1 + config.TAKE_PROFIT_PERCENT), 2)
                
                self.trades.append({
                    'timestamp': timestamp,
                    'type': 'BUY',
                    'entry_price': current_price,
                    'sl': sl,
                    'tp': tp,
                    'close_price': None,
                    'close_timestamp': None,
                    'close_reason': None,
                    'pips': None,
                    'status': 'Open',
                    'confidence': confidence
                })
                signals_generated += 1
            
            # SELL signal: previous = 1, current = 0
            elif (prev_pred == 1) and (curr_pred == 0) and macd_ok_sell:
                # Use ATR-based stops if enabled
                use_atr = getattr(config, 'USE_ATR_STOPS', False)
                if use_atr and atr_val > 0:
                    atr_stop_mult = getattr(config, 'ATR_STOP_MULTIPLIER', 2.0)
                    atr_tp_mult = getattr(config, 'ATR_TP_MULTIPLIER', 5.0)
                    sl = round(current_price + (atr_val * atr_stop_mult), 2)
                    tp = round(current_price - (atr_val * atr_tp_mult), 2)
                else:
                    sl = round(current_price * (1 + config.STOP_LOSS_PERCENT), 2)
                    tp = round(current_price * (1 - config.TAKE_PROFIT_PERCENT), 2)
                
                self.trades.append({
                    'timestamp': timestamp,
                    'type': 'SELL',
                    'entry_price': current_price,
                    'sl': sl,
                    'tp': tp,
                    'close_price': None,
                    'close_timestamp': None,
                    'close_reason': None,
                    'pips': None,
                    'status': 'Open',
                    'confidence': confidence
                })
                signals_generated += 1
            else:
                # MACD/RSI gate failed
                macd_rejects += 1
            
            # Check if any open trades hit SL or TP
            self._check_trade_exits(current_price, idx)
        
        self._print_results(signals_generated, confidence_rejects, macd_rejects)
    
    def _check_trade_exits(self, current_price, idx):
        """Check if open trades hit SL or TP"""
        # Get current timestamp from results_df if available
        current_timestamp = None
        if hasattr(self, '_current_timestamp'):
            current_timestamp = self._current_timestamp
        
        for trade in self.trades:
            if trade['status'] == 'Open':
                if trade['type'] == 'BUY':
                    # Check SL
                    if current_price <= trade['sl']:
                        trade['close_price'] = trade['sl']
                        trade['close_timestamp'] = current_timestamp
                        trade['close_reason'] = 'SL_HIT'
                        # For Gold: pips = price_diff * 10 (each 0.1 = 1 pip)
                        trade['pips'] = (trade['sl'] - trade['entry_price']) * 10
                        trade['status'] = 'Closed'
                    # Check TP
                    elif current_price >= trade['tp']:
                        trade['close_price'] = trade['tp']
                        trade['close_timestamp'] = current_timestamp
                        trade['close_reason'] = 'TP_HIT'
                        trade['pips'] = (trade['tp'] - trade['entry_price']) * 10
                        trade['status'] = 'Closed'
                
                elif trade['type'] == 'SELL':
                    # Check SL
                    if current_price >= trade['sl']:
                        trade['close_price'] = trade['sl']
                        trade['close_timestamp'] = current_timestamp
                        trade['close_reason'] = 'SL_HIT'
                        trade['pips'] = (trade['entry_price'] - trade['sl']) * 10
                        trade['status'] = 'Closed'
                    # Check TP
                    elif current_price <= trade['tp']:
                        trade['close_price'] = trade['tp']
                        trade['close_timestamp'] = current_timestamp
                        trade['close_reason'] = 'TP_HIT'
                        trade['pips'] = (trade['entry_price'] - trade['tp']) * 10
                        trade['status'] = 'Closed'
    
    def _print_results(self, signals_generated, confidence_rejects, macd_rejects):
        """Print backtest results with monthly breakdown"""
        lines = []
        lines.append("\n" + "="*70)
        lines.append("BACKTEST RESULTS - GOLD SIGNAL BOT")
        lines.append("="*70)
        lines.append(f"\nFilter stats: signals={signals_generated}, confidence rejects={confidence_rejects}, macd/rsi rejects={macd_rejects}")
        
        if not self.trades:
            lines.append("❌ No trades generated during backtest period")
            print("\n".join(lines))
            return
        
        closed_trades = [t for t in self.trades if t['status'] == 'Closed']
        open_trades = [t for t in self.trades if t['status'] == 'Open']
        
        lines.append("\n📊 TRADE SUMMARY:")
        lines.append(f"   Total Signals: {len(self.trades)}")
        lines.append(f"   Closed Trades: {len(closed_trades)}")
        lines.append(f"   Open Trades: {len(open_trades)}")
        
        # Overall metrics
        if closed_trades:
            pips_list = [t['pips'] for t in closed_trades if t['pips'] is not None]
            if pips_list:
                total_pips = sum(pips_list)
                winning_trades = len([p for p in pips_list if p > 0])
                losing_trades = len([p for p in pips_list if p < 0])
                win_rate = (winning_trades / len(pips_list) * 100) if pips_list else 0
                lines.append("\n💰 P&L METRICS (Total):")
                lines.append(f"   Total Pips: {total_pips:.2f}")
                lines.append(f"   Winning Trades: {winning_trades} ✅")
                lines.append(f"   Losing Trades: {losing_trades} ❌")
                lines.append(f"   Win Rate: {win_rate:.2f}%")
                if winning_trades > 0:
                    avg_win = np.mean([p for p in pips_list if p > 0])
                    lines.append(f"   Avg Win: {avg_win:.2f} pips")
                if losing_trades > 0:
                    avg_loss = np.mean([p for p in pips_list if p < 0])
                    lines.append(f"   Avg Loss: {avg_loss:.2f} pips")
                if winning_trades > 0 and losing_trades > 0:
                    avg_win = np.mean([p for p in pips_list if p > 0])
                    avg_loss = abs(np.mean([p for p in pips_list if p < 0]))
                    profit_factor = avg_win * winning_trades / (avg_loss * losing_trades)
                    lines.append(f"   Profit Factor: {profit_factor:.2f}")
        
        # Monthly breakdown (by close timestamp)
        if closed_trades:
            month_buckets = {}
            for t in closed_trades:
                ts = t['timestamp']
                month_key = ts.strftime('%Y-%m') if hasattr(ts, 'strftime') else str(ts)[:7]
                month_buckets.setdefault(month_key, []).append(t)
            lines.append("\n📅 MONTHLY P&L (by close date):")
            for month in sorted(month_buckets.keys()):
                trades = month_buckets[month]
                pips = [tr['pips'] for tr in trades if tr['pips'] is not None]
                total_pips = sum(pips) if pips else 0.0
                wins = len([p for p in pips if p > 0])
                losses = len([p for p in pips if p < 0])
                win_rate = (wins / len(pips) * 100) if pips else 0
                if wins > 0 and losses > 0:
                    avg_win = np.mean([p for p in pips if p > 0])
                    avg_loss = abs(np.mean([p for p in pips if p < 0]))
                    profit_factor = avg_win * wins / (avg_loss * losses)
                else:
                    profit_factor = float('inf') if wins > 0 else 0.0
                lines.append(f"   {month}: Total Pips={total_pips:.2f} | Trades={len(pips)} (✅{wins} wins, ❌{losses} losses) | WinRate={win_rate:.1f}% | ProfitFactor={profit_factor:.2f}")
        
        # Detailed closed trades
        if closed_trades:
            tz_offset = pd.Timedelta(hours=getattr(config, 'TIMEZONE_OFFSET_HOURS', 0))
            lines.append("\n📋 CLOSED TRADE DETAILS:")
            lines.append("-"*70)
            for i, trade in enumerate(closed_trades, 1):
                pips_emoji = "✅" if trade['pips'] > 0 else "❌"
                lines.append(f"\nTrade #{i} | {trade['type']:4s} | Pips: {trade['pips']:7.2f} {pips_emoji}")
                entry_time = trade['timestamp'] + tz_offset
                lines.append(f"  Entry: {trade['entry_price']:.2f} @ {entry_time}")
                exit_time = trade.get('close_timestamp', None)
                if exit_time:
                    exit_time = exit_time + tz_offset
                else:
                    exit_time = 'N/A'
                lines.append(f"  Exit:  {trade['close_price']:.2f} @ {exit_time} ({trade['close_reason']})")
                lines.append(f"  SL: {trade['sl']:.2f} | TP: {trade['tp']:.2f}")
        
        lines.append("\n" + "="*70)
        output_text = "\n".join(lines)
        print(output_text)
        os.makedirs(config.DATA_DIR, exist_ok=True)
        report_path = os.path.join(config.DATA_DIR, "backtest_report.txt")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"\n📝 Backtest report saved to: {report_path}")


def main():
    """Run backtest"""
    print("\n" + "="*70)
    print("🚀 ML GOLD SIGNAL BOT - BACKTEST")
    print("="*70)
    
    try:
        # Backtest period from config
        backtester = GoldBacktester()
        backtester.run_backtest()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure the model is trained first: python train_model.py")


if __name__ == "__main__":
    main()
