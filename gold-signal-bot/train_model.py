"""
Train Model Script
Trains a RandomForestClassifier on Gold (XAUUSD) historical data
"""

import yfinance as yf
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
import config


def fetch_training_data(ticker, period, interval):
    """
    Fetch historical Gold data for training
    
    Args:
        ticker: Yahoo Finance ticker (default 'XAUUSD=X')
        period: Data period (default '2y' for 2 years)
        interval: Data interval (default '1h')
    
    Returns:
        pandas DataFrame with OHLCV data
    """
    print(f"📊 Fetching historical data for {ticker}...")
    print(f"   Period: {period}, Interval: {interval}")
    
    gold = yf.Ticker(ticker)
    df = gold.history(period=period, interval=interval)
    
    if df.empty:
        print("❌ No data retrieved. Check ticker symbol and parameters.")
        return None
    
    print(f"✅ Retrieved {len(df)} candles")
    return df


def train_model(X_train, y_train, *, n_estimators, random_state, max_depth, min_samples_split):
    """
    Train RandomForestClassifier
    
    Args:
        X_train: Training features
        y_train: Training labels
        n_estimators: Number of trees (default 100)
        random_state: Random state for reproducibility
    
    Returns:
        Trained model
    """
    print(f"\n🤖 Training RandomForestClassifier...")
    print(f"   Training samples: {len(X_train)}")
    print(f"   Features: {X_train.shape[1]}")
    print(f"   Number of trees: {n_estimators}")
    
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        class_weight='balanced_subsample'
    )
    
    model.fit(X_train, y_train)
    
    print("✅ Model training complete!")
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
    
    return {
        'accuracy': accuracy,
        'test_samples': len(y_test),
        'train_samples': len(model.estimators_)
    }


def main():
    """Main training pipeline"""
    
    print("=" * 60)
    print("ML GOLD SIGNAL BOT - MODEL TRAINING")
    print("=" * 60)
    
    # Step 1: Fetch data
    df = fetch_training_data(ticker=config.TICKER, period=config.TRAINING_PERIOD, interval=config.INTERVAL)
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
        'Ticker': config.TICKER,
        'Interval': config.INTERVAL,
        'Period': config.TRAINING_PERIOD,
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
