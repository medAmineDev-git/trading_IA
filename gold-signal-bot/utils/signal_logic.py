"""
Signal Logic Module
Generates trading signals based on ML predictions
"""

import os
import csv
from datetime import datetime


def generate_signal(current_prediction, previous_prediction, current_price, 
                   sl_percent=0.01, tp_percent=0.02):
    """
    Generate trading signal based on prediction changes
    
    Args:
        current_prediction: Current model prediction (0 or 1)
        previous_prediction: Previous model prediction (0 or 1)
        current_price: Current market price
        sl_percent: Stop loss percentage (default 0.01 = 1%)
        tp_percent: Take profit percentage (default 0.02 = 2%)
    
    Returns:
        dict: Signal information
    """
    signal = {
        'type': 'HOLD',
        'price': current_price,
        'sl': None,
        'tp': None,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # BUY SIGNAL: previous = 0 (bearish) and current = 1 (bullish)
    if previous_prediction == 0 and current_prediction == 1:
        signal['type'] = 'BUY'
        signal['sl'] = round(current_price * (1 - sl_percent), 2)
        signal['tp'] = round(current_price * (1 + tp_percent), 2)
    
    # SELL SIGNAL: previous = 1 (bullish) and current = 0 (bearish)
    elif previous_prediction == 1 and current_prediction == 0:
        signal['type'] = 'SELL'
        signal['sl'] = round(current_price * (1 + sl_percent), 2)
        signal['tp'] = round(current_price * (1 - tp_percent), 2)
    
    return signal


def format_signal_output(signal):
    """
    Format signal for console output
    
    Args:
        signal: Signal dictionary
    
    Returns:
        str: Formatted signal string
    """
    if signal['type'] == 'BUY':
        return f"📈 BUY SIGNAL — Price: {signal['price']:.2f} | SL: {signal['sl']:.2f} | TP: {signal['tp']:.2f}"
    
    elif signal['type'] == 'SELL':
        return f"📉 SELL SIGNAL — Price: {signal['price']:.2f} | SL: {signal['sl']:.2f} | TP: {signal['tp']:.2f}"
    
    else:  # HOLD
        return "⏳ HOLD — No new signal at this time."


def save_signal_to_csv(signal, csv_path='data/signals.csv'):
    """
    Save signal to CSV file
    
    Args:
        signal: Signal dictionary
        csv_path: Path to CSV file (default 'data/signals.csv')
    """
    # Ensure data directory exists
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    # Check if file exists to write header
    file_exists = os.path.isfile(csv_path)
    
    with open(csv_path, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'type', 'price', 'sl', 'tp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(signal)
    
    print(f"💾 Signal saved to {csv_path}")


def calculate_custom_sltp(signal_type, entry_price, sl_pct=0.01, tp_pct=0.02):
    """
    Calculate custom SL/TP with user-defined percentages
    
    Args:
        signal_type: 'BUY' or 'SELL'
        entry_price: Entry price
        sl_pct: Stop loss percentage (default 0.01 = 1%)
        tp_pct: Take profit percentage (default 0.02 = 2%)
    
    Returns:
        tuple: (stop_loss, take_profit)
    """
    if signal_type == 'BUY':
        sl = round(entry_price * (1 - sl_pct), 2)
        tp = round(entry_price * (1 + tp_pct), 2)
    elif signal_type == 'SELL':
        sl = round(entry_price * (1 + sl_pct), 2)
        tp = round(entry_price * (1 - tp_pct), 2)
    else:
        return None, None
    
    return sl, tp
