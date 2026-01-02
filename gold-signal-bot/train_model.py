"""
Train Model Script
Trains a RandomForestClassifier on Gold (XAUUSD) historical data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

# Import custom utilities
from utils.indicators import add_all_indicators, prepare_features
from utils.model_loader import save_model, save_training_metadata
from utils.av_fetch import fetch_fx_history, period_to_days
from utils.mt5_fetch import load_csv_data
import config


def fetch_training_data(ticker, period, interval):
    """
    Fetch historical Gold data for training.
    Returns tuple: (df, effective_period, used_ticker, used_interval)
    """
    data_source = getattr(config, "DATA_SOURCE", "").lower()
    
    # MT5 CSV mode
    if data_source == "mt5_csv":
        csv_path = getattr(config, "MT5_CSV_PATH", "data/mt5_history.csv")
        symbol = getattr(config, "MT5_SYMBOL", "XAUUSD")
        timeframe = getattr(config, "MT5_TIMEFRAME", "H4")
        
        print(f"📊 Loading historical data from MT5 CSV...")
        print(f"   Symbol: {symbol}, Timeframe: {timeframe}")
        print(f"   CSV Path: {csv_path}")
        
        df = load_csv_data(csv_path)
        if df is not None and not df.empty:
            effective_period = f"{len(df)} bars"
            print(f"✅ Loaded {len(df)} candles")
            return df, effective_period, symbol, timeframe
        print("❌ Failed to load MT5 CSV. Run 'python export_mt5_data.py' first.")
        return None, "0d", symbol, timeframe
    
    # Alpha Vantage mode
    if data_source == "alphavantage":
        days = period_to_days(period)
        effective_period = f"{days}d" if days else str(period)
        print(f"📊 Fetching historical data for {ticker} from Alpha Vantage...")
        print(f"   Period: {effective_period}, Interval: 1d")
        df = fetch_fx_history(days)
        if not df.empty:
            print(f"✅ Retrieved {len(df)} candles (ticker={ticker}, interval=1d)")
            return df, effective_period, ticker, "1d"
        print("❌ No data retrieved from Alpha Vantage. Aborting.")
        return None, effective_period, ticker, "1d"

    # Unsupported data source
    print(f"❌ Unsupported DATA_SOURCE: {data_source}. Use 'mt5_csv' or 'alphavantage'.")
    return None, period, ticker, interval


def train_model(X_train, y_train, *, model_type, n_estimators, random_state, max_depth, min_samples_split):
    """
    Train specified model type
    
    Args:
        X_train: Training features
        y_train: Training labels
        model_type: 'rf', 'xgboost', or 'lightgbm'
        n_estimators: Number of trees
        random_state: Random state
        max_depth: Maximum depth
        min_samples_split: Minimum samples to split
    
    Returns:
        Trained model
    """
    print(f"\n🤖 Training {model_type.upper()} model...")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Features: {X_train.shape[1]}")
    
    if model_type == 'xgboost':
        from xgboost import XGBClassifier
        model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.05,
            random_state=random_state,
            n_jobs=-1,
            verbosity=0
        )
    elif model_type == 'lightgbm':
        from lightgbm import LGBMClassifier
        model = LGBMClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=0.05,
            random_state=random_state,
            n_jobs=-1,
            importance_type='gain'
        )
    else: # Default to RandomForest
        model = RandomForestClassifier(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            class_weight='balanced_subsample'
        )
    
    model.fit(X_train, y_train)
    
    print(f"✅ {model_type.upper()} Model training complete!")
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evaluate model performance
    
    Args:
        model: Trained model
        X_test: Test features
        y_test: Test labels
    
    Returns:
        dict: Evaluation metrics
    """
    print("\n📈 Evaluating model performance...")
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*50}")
    print("MODEL EVALUATION RESULTS")
    print(f"{'='*50}")
    print(f"Test Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Down (0)', 'Up (1)']))
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    print(f"{'='*50}\n")
    
    # Safe access to number of estimators (trees)
    num_estimators = 0
    if hasattr(model, 'estimators_'):
        num_estimators = len(model.estimators_)
    elif hasattr(model, 'n_estimators'):
        num_estimators = model.n_estimators
    
    return {
        'accuracy': accuracy,
        'test_samples': len(y_test),
        'train_samples': num_estimators
    }


def main():
    """Main training pipeline"""
    
    print("=" * 60)
    print("ML GOLD SIGNAL BOT - MODEL TRAINING")
    print("=" * 60)
    
    # Step 1: Fetch data
    df, effective_period, used_ticker, used_interval = fetch_training_data(ticker=config.TICKER, period=config.TRAINING_PERIOD, interval=config.INTERVAL)
    if df is None:
        return
    
    # Step 2: Add technical indicators
    print("\n🔧 Computing technical indicators...")
    df_with_indicators = add_all_indicators(df)
    print(f"✅ Indicators computed. Total samples: {len(df_with_indicators)}")
    
    # Step 3: Prepare features
    print("\n🎯 Preparing features for training...")
    X, y = prepare_features(df_with_indicators)
    print(f"✅ Feature matrix shape: {X.shape}")
    print(f"✅ Target distribution: Up={sum(y)}, Down={len(y)-sum(y)}")
    
    # Step 4: Time-series split (no shuffling)
    # Use 80% for training, 20% for testing
    split_index = int(len(X) * 0.8)
    X_train, X_test = X[:split_index], X[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]
    
    print(f"\n✂️ Train/Test Split (Time-Series):")
    print(f"   Training: {len(X_train)} samples")
    print(f"   Testing: {len(X_test)} samples")
    
    # Step 5: Train model
    model = train_model(
        X_train,
        y_train,
        model_type=config.MODEL_TYPE,
        n_estimators=config.N_ESTIMATORS,
        random_state=config.RANDOM_STATE,
        max_depth=config.MAX_DEPTH,
        min_samples_split=config.MIN_SAMPLES_SPLIT
    )
    
    # Step 6: Evaluate model
    metrics = evaluate_model(model, X_test, y_test)
    
    # Step 7: Save model
    print("\n💾 Saving model...")
    save_model(model, model_dir='models', model_name='gold_signal_model.pkl')
    
    # Step 8: Save metadata
    metadata = {
        'Accuracy': f"{metrics['accuracy']:.4f}",
        'Training Samples': metrics['test_samples'],
        'Test Samples': len(X_test),
        'Features': X.shape[1],
        'Ticker': used_ticker,
        'Interval': used_interval,
        'Period': effective_period,
        'Model Type': config.MODEL_TYPE,
        'N_Estimators': config.N_ESTIMATORS,
        'Max_Depth': config.MAX_DEPTH,
        'Min_Samples_Split': config.MIN_SAMPLES_SPLIT,
        'Prob_Threshold': config.PROB_THRESHOLD
    }
    save_training_metadata(metadata, model_dir='models')
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("You can now run 'signal_bot.py' to generate signals.")
    print("=" * 60)


if __name__ == "__main__":
    main()
