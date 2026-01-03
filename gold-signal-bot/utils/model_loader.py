"""
Model Loader/Saver Module
Handles saving and loading of trained ML models
"""

import joblib
import os
from datetime import datetime
import config


def save_model(model, model_dir=config.MODEL_DIR, model_name='gold_signal_model.pkl'):
    """
    Save trained model to disk
    
    Args:
        model: Trained scikit-learn model
        model_dir: Directory to save model (default 'models')
        model_name: Name of model file (default 'gold_signal_model.pkl')
    
    Returns:
        str: Path to saved model
    """
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, model_name)
    
    joblib.dump(model, model_path)
    print(f"✅ Model saved to: {model_path}")
    
    return model_path


def load_model(model_path=config.MODEL_PATH):
    """
    Load trained model from disk
    
    Args:
        model_path: Path to saved model file
    
    Returns:
        Loaded scikit-learn model or None if not found
    """
    if not os.path.exists(model_path):
        print(f"❌ Model not found at: {model_path}")
        print("Please train the model first by running train_model.py")
        return None
    
    try:
        model = joblib.load(model_path)
        print(f"✅ Model loaded from: {model_path}")
        return model
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return None


def save_training_metadata(metadata, model_dir=config.MODEL_DIR):
    """
    Save training metadata (accuracy, date, etc.)
    
    Args:
        metadata: Dictionary with training information
        model_dir: Directory to save metadata
    """
    os.makedirs(model_dir, exist_ok=True)
    metadata_path = os.path.join(model_dir, 'training_metadata.txt')
    
    with open(metadata_path, 'w') as f:
        f.write(f"Training Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                import json
                value = json.dumps(value)
            f.write(f"{key}: {value}\n")
    
    print(f"✅ Training metadata saved to: {metadata_path}")
