"""
Gold Signal Bot - Main Runtime
Generates BUY/SELL signals for Gold (XAUUSD) using ML predictions
NO AUTO-TRADING - Signal Generation Only
"""

import yfinance as yf
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Import custom utilities
from utils.indicators import add_all_indicators, prepare_features
from utils.model_loader import load_model
from utils.signal_logic import generate_signal, format_signal_output, save_signal_to_csv
import config


class GoldSignalBot:
    """ML-based signal generator for Gold (XAUUSD)"""
    
    def __init__(self, ticker=config.TICKER, interval=config.INTERVAL, model_path=config.MODEL_PATH):
        """Initialize the signal bot"""
        self.ticker = ticker
        self.interval = interval
        self.model_path = model_path
        self.model = None
        self.previous_prediction = None
        
        # SL/TP settings (can be customized)
        self.sl_percent = config.STOP_LOSS_PERCENT
        self.tp_percent = config.TAKE_PROFIT_PERCENT
        self.prob_threshold = config.PROB_THRESHOLD
        self.rsi_buy_min = config.RSI_BUY_MIN
        self.rsi_sell_max = config.RSI_SELL_MAX
        
    def load_trained_model(self):
        """Load the trained ML model"""
        print("🤖 Loading trained model...")
        self.model = load_model(self.model_path)
        
        if self.model is None:
            raise Exception("Failed to load model. Please run train_model.py first.")
        
        return True
    
    def fetch_latest_data(self, lookback_period='5d'):
        """
        Fetch latest market data
        
        Args:
            lookback_period: How much historical data to fetch (default '5d')
        
        Returns:
            pandas DataFrame with latest data
        """
        try:
            gold = yf.Ticker(self.ticker)
            df = gold.history(period=lookback_period, interval=self.interval)
            
            if df.empty:
                print("⚠️ No data retrieved from Yahoo Finance")
                return None
            
            return df
        
        except Exception as e:
            print(f"❌ Error fetching data: {e}")
            return None
    
    def make_prediction(self, df):
        """Make prediction on latest data with confidence and indicator filters"""
        try:
            # Add indicators
            df_with_indicators = add_all_indicators(df)
            
            if len(df_with_indicators) == 0:
                print("⚠️ Not enough data to compute indicators")
                return None, None, None
            
            # Prepare features
            X, _ = prepare_features(df_with_indicators)
            
            # Get latest feature vector
            latest_features = X[-1].reshape(1, -1)
            latest_row = df_with_indicators.iloc[-1]
            
            # Probabilistic prediction
            proba = self.model.predict_proba(latest_features)[0]
            prob_down, prob_up = float(proba[0]), float(proba[1])
            prediction = 1 if prob_up >= prob_down else 0
            confidence = max(prob_up, prob_down)
            
            # Indicator filters (MACD + RSI gate)
            macd_ok_buy = latest_row['MACD'] > latest_row['MACD_Signal'] and latest_row['RSI'] > self.rsi_buy_min
            macd_ok_sell = latest_row['MACD'] < latest_row['MACD_Signal'] and latest_row['RSI'] < self.rsi_sell_max
            
            # Confidence gate
            if confidence < self.prob_threshold:
                return None, latest_row['Close'], confidence
            
            # Directional filters
            if prediction == 1 and not macd_ok_buy:
                return None, latest_row['Close'], confidence
            if prediction == 0 and not macd_ok_sell:
                return None, latest_row['Close'], confidence
            
            current_price = float(latest_row['Close'])
            return prediction, current_price, confidence
        
        except Exception as e:
            print(f"❌ Error making prediction: {e}")
            return None, None, None
    
    def process_signal(self, prediction, current_price):
        """
        Process prediction and generate signal
        
        Args:
            prediction: Model prediction (0 or 1)
            current_price: Current market price
        
        Returns:
            dict: Signal information
        """
        # First run - initialize previous prediction
        if self.previous_prediction is None:
            self.previous_prediction = prediction
            return {
                'type': 'HOLD',
                'price': current_price,
                'sl': None,
                'tp': None,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # Generate signal based on prediction change
        signal = generate_signal(
            current_prediction=prediction,
            previous_prediction=self.previous_prediction,
            current_price=current_price,
            sl_percent=self.sl_percent,
            tp_percent=self.tp_percent
        )
        
        # Update previous prediction only when we acted
        self.previous_prediction = prediction
        
        return signal
    
    def run_once(self):
        """Run one iteration of the bot"""
        print("\n" + "=" * 70)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Analyzing {self.ticker}...")
        print("=" * 70)
        
        # Fetch latest data
        df = self.fetch_latest_data(lookback_period='5d')
        
        if df is None:
            print("⚠️ Skipping this cycle due to data fetch error")
            return
        
        # Make prediction
        prediction, current_price, confidence = self.make_prediction(df)
        
        if prediction is None:
            print(f"⚠️ Skipping this cycle (filters or low confidence). Confidence: {confidence if confidence is not None else 'N/A'}")
            return
        
        print(f"📊 Current Price: ${current_price:.2f}")
        print(f"🔮 ML Prediction: {'UP (1)' if prediction == 1 else 'DOWN (0)'} | Confidence: {confidence:.2f}")
        
        # Process signal
        signal = self.process_signal(prediction, current_price)
        
        # Display signal
        print(f"\n{format_signal_output(signal)}")
        
        # Save signal if not HOLD
        if signal['type'] != 'HOLD':
            save_signal_to_csv(signal)
        
        print("=" * 70)
    
    def run_continuous(self, check_interval_minutes=None):
        """
        Run bot continuously with time-based checks
        
        Args:
            check_interval_minutes: Minutes between checks (default: auto-detect from interval)
        """
        # Auto-detect interval if not specified
        if check_interval_minutes is None:
            interval_map = {
                '1m': 1,
                '5m': 5,
                '15m': 15,
                '30m': 30,
                '1h': 60,
                '2h': 120,
                '4h': 240,
                '1d': 1440
            }
            check_interval_minutes = interval_map.get(self.interval, 60)
        
        print("\n" + "=" * 70)
        print("🚀 ML GOLD SIGNAL BOT - RUNNING")
        print("=" * 70)
        print(f"📈 Ticker: {self.ticker}")
        print(f"⏱️  Interval: {self.interval}")
        print(f"🔄 Check every: {check_interval_minutes} minutes")
        print(f"🛑 Stop Loss: {self.sl_percent*100:.1f}%")
        print(f"🎯 Take Profit: {self.tp_percent*100:.1f}%")
        print("=" * 70)
        print("\n⚠️  WARNING: This bot generates signals only - NO AUTO-TRADING")
        print("💡 Press Ctrl+C to stop the bot\n")
        
        try:
            while True:
                self.run_once()
                
                # Wait for next candle
                wait_seconds = check_interval_minutes * 60
                print(f"\n⏳ Waiting {check_interval_minutes} minutes for next candle...")
                print(f"   Next check at: {(datetime.now() + timedelta(seconds=wait_seconds)).strftime('%Y-%m-%d %H:%M:%S')}")
                
                time.sleep(wait_seconds)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Bot stopped by user")
            print("✅ Shutdown complete")


def main():
    """Main entry point"""
    
    try:
        # Initialize bot
        bot = GoldSignalBot()
        
        # Load model
        bot.load_trained_model()
        
        # Run bot continuously
        bot.run_continuous()
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        print("Please check your configuration and try again.")


if __name__ == "__main__":
    main()
