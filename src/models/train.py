"""
Model training script.

Trains Logistic Regression and Random Forest classifiers.
"""

import sys
import random
import pickle
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import numpy as np

# Set random seeds for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, classification_report
)

from src.data.preprocessing import HeartDiseasePreprocessor, prepare_features_target

# Define paths
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(exist_ok=True)


def load_data():
    """Load processed data."""
    data_path = DATA_PROCESSED_DIR / "heart_disease_processed.csv"
    
    if not data_path.exists():
        msg = f"Processed data not found at {data_path}. Run preprocess_data.py first!"
        raise FileNotFoundError(msg)
    
    df = pd.read_csv(data_path)
    print(f"Loaded data: {df.shape}")
    return df


def train_models(X_train, y_train, X_test, y_test, preprocessor):
    """Train multiple models and return results."""
    
    # Prepare training and test data
    X_train_scaled = preprocessor.transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)
    
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    results = {}
    
    # Cross-validation setup
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, model in models.items():
        print(f"\n{'='*60}")
        print(f"Training {name}")
        print(f"{'='*60}")
        
        # Train model
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation scores
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='roc_auc')
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Store results
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'roc_auc': roc_auc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'confusion_matrix': cm.tolist(),
            'predictions': y_pred.tolist(),
            'probabilities': y_pred_proba.tolist()
        }
        
        # Print results
        print(f"\n{name} Results:")
        print(f"  Accuracy:  {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall:    {recall:.4f}")
        print(f"  ROC-AUC:   {roc_auc:.4f}")
        print(f"  CV ROC-AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
        print("\nConfusion Matrix:")
        print(cm)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
    
    return results


def save_models(results, preprocessor):
    """Save trained models and preprocessor."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for name, result in results.items():
        # Save model
        model_filename = MODELS_DIR / f"{name.lower().replace(' ', '_')}_{timestamp}.pkl"
        with open(model_filename, 'wb') as f:
            pickle.dump(result['model'], f)
        print(f"\nSaved model: {model_filename}")
    
    # Save preprocessor
    preprocessor_filename = MODELS_DIR / f"preprocessor_{timestamp}.pkl"
    preprocessor.save(preprocessor_filename)
    
    # Save results summary
    summary = {
        'timestamp': timestamp,
        'models': {
            name: {
                'accuracy': float(result['accuracy']),
                'precision': float(result['precision']),
                'recall': float(result['recall']),
                'roc_auc': float(result['roc_auc']),
                'cv_mean': float(result['cv_mean']),
                'cv_std': float(result['cv_std']),
                'confusion_matrix': result['confusion_matrix']
            }
            for name, result in results.items()
        }
    }
    
    summary_filename = MODELS_DIR / f"training_summary_{timestamp}.json"
    with open(summary_filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary: {summary_filename}")
    
    return summary


def main():
    """Main training function."""
    print("=" * 60)
    print("Heart Disease Model Training")
    print("=" * 60)
    
    # Load data
    df = load_data()
    
    # Prepare features and target
    X, y = prepare_features_target(df)
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target distribution:\n{y.value_counts()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTrain set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Initialize and fit preprocessor
    print("\nFitting preprocessor...")
    preprocessor = HeartDiseasePreprocessor()
    preprocessor.fit(X_train)
    
    # Train models
    results = train_models(X_train, y_train, X_test, y_test, preprocessor)
    
    # Save models
    summary = save_models(results, preprocessor)
    
    # Select best model
    best_model_name = max(results.keys(), key=lambda k: results[k]['roc_auc'])
    print(f"\n{'='*60}")
    print(f"Best Model: {best_model_name}")
    print(f"  ROC-AUC: {results[best_model_name]['roc_auc']:.4f}")
    print(f"{'='*60}")
    
    return results, preprocessor, summary


if __name__ == "__main__":
    main()

