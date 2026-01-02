import threading
import time
import joblib
import pandas as pd
import os
from telegram_service import telegram_service

class LiveManager:
    def __init__(self):
        self.active_strategies = {} # strategy_id -> thread
        self.is_running = True
        self.lock = threading.Lock()
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.strategies_file = os.path.join(self.data_dir, "strategies.json")

    def start_monitoring(self, strategy_id, strategy_data):
        """Start a background thread to monitor a specific strategy."""
        with self.lock:
            if strategy_id in self.active_strategies:
                return
            
            thread = threading.Thread(target=self._monitor_loop, args=(strategy_id, strategy_data))
            thread.daemon = True
            self.active_strategies[strategy_id] = thread
            thread.start()

    def _monitor_loop(self, strategy_id, strategy_data):
        print(f"📡 Started monitoring strategy: {strategy_id}")
        
        # Load model
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "gold_signal_model.pkl")
        try:
            model = joblib.load(model_path)
        except Exception as e:
            print(f"❌ Failed to load model for {strategy_id}: {e}")
            return

        while self.is_running:
            try:
                # 1. Fetch live data (simulated for now or using a helper)
                # In a real app, this would call MT5 or yfinance
                print(f"🔍 Monitoring {strategy_id}...")
                
                # 2. Preprocess & Predict
                # (Logic would go here to match feature engineering in train_model.py)
                
                # 3. If signal generated, broadcast
                # signal = {"signal": "BUY", "price": 2045.5, "sl": 2038.2, "tp": 2060.0, "confidence": 85}
                # telegram_service.send_signal(strategy_id, signal)
                
            except Exception as e:
                print(f"⚠️ Error in monitoring loop for {strategy_id}: {e}")
            
            time.sleep(3600) # Poll every hour

    def stop_monitoring(self, strategy_id):
        with self.lock:
            if strategy_id in self.active_strategies:
                # In a real app, you'd have a more graceful stop
                del self.active_strategies[strategy_id]

live_manager = LiveManager()
