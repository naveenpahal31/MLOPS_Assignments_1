"""
Model training script with MLflow tracking.

Trains models and logs experiments to MLflow.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, 
    roc_auc_score, confusion_matrix, classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns

from src.data.preprocessing import HeartDiseasePreprocessor, prepare_features_target

# Define paths
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MLFLOW_DIR = PROJECT_ROOT / "mlruns"

# Set MLflow tracking URI
mlflow.set_tracking_uri(f"file://{MLFLOW_DIR.absolute()}")
mlflow.set_experiment("heart_disease_prediction")


def load_data():
    """Load processed data."""
    data_path = DATA_PROCESSED_DIR / "heart_disease_processed.csv"
    
    if not data_path.exists():
        msg = f"Processed data not found at {data_path}. Run preprocess_data.py first!"
        raise FileNotFoundError(msg)
    
    df = pd.read_csv(data_path)
    print(f"Loaded data: {df.shape}")
    return df


def plot_confusion_matrix(y_true, y_pred, model_name):
    """Create and save confusion matrix plot."""
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['No Disease', 'Disease'],
                yticklabels=['No Disease', 'Disease'])
    plt.title(f'Confusion Matrix - {model_name}')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    
    # Save plot
    model_name_safe = model_name.replace(' ', '_')
    plot_path = PROJECT_ROOT / "mlruns" / "plots" / f"confusion_matrix_{model_name_safe}.png"
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(plot_path)
    plt.close()
    
    return str(plot_path)


def train_logistic_regression(X_train, y_train, X_test, y_test, preprocessor):
    """Train Logistic Regression with MLflow tracking."""
    
    X_train_scaled = preprocessor.transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)
    
    with mlflow.start_run(run_name="Logistic_Regression"):
        # Hyperparameters
        params = {
            'random_state': 42,
            'max_iter': 1000,
            'solver': 'lbfgs'
        }
        
        # Log parameters
        mlflow.log_params(params)
        
        # Train model
        model = LogisticRegression(**params)
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='roc_auc')
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("roc_auc", roc_auc)
        mlflow.log_metric("cv_roc_auc_mean", cv_scores.mean())
        mlflow.log_metric("cv_roc_auc_std", cv_scores.std())
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log confusion matrix plot
        plot_path = plot_confusion_matrix(y_test, y_pred, "Logistic Regression")
        mlflow.log_artifact(plot_path)
        
        # Log classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        mlflow.log_dict(report, "classification_report.json")
        
        print(f"\nLogistic Regression - ROC-AUC: {roc_auc:.4f}")
        
        return model, {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'roc_auc': roc_auc
        }


def train_random_forest(X_train, y_train, X_test, y_test, preprocessor):
    """Train Random Forest with MLflow tracking."""
    
    X_train_scaled = preprocessor.transform(X_train)
    X_test_scaled = preprocessor.transform(X_test)
    
    with mlflow.start_run(run_name="Random_Forest"):
        # Hyperparameters
        params = {
            'n_estimators': 100,
            'max_depth': 10,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42,
            'n_jobs': -1
        }
        
        # Log parameters
        mlflow.log_params(params)
        
        # Train model
        model = RandomForestClassifier(**params)
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        
        # Cross-validation
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv, scoring='roc_auc')
        
        # Log metrics
        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("precision", precision)
        mlflow.log_metric("recall", recall)
        mlflow.log_metric("roc_auc", roc_auc)
        mlflow.log_metric("cv_roc_auc_mean", cv_scores.mean())
        mlflow.log_metric("cv_roc_auc_std", cv_scores.std())
        
        # Log feature importance
        feature_importance = dict(zip(
            X_train.columns,
            model.feature_importances_
        ))
        mlflow.log_dict(feature_importance, "feature_importance.json")
        
        # Log model
        mlflow.sklearn.log_model(model, "model")
        
        # Log confusion matrix plot
        plot_path = plot_confusion_matrix(y_test, y_pred, "Random Forest")
        mlflow.log_artifact(plot_path)
        
        # Log classification report
        report = classification_report(y_test, y_pred, output_dict=True)
        mlflow.log_dict(report, "classification_report.json")
        
        print(f"\nRandom Forest - ROC-AUC: {roc_auc:.4f}")
        
        return model, {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'roc_auc': roc_auc
        }


def main():
    """Main training function with MLflow."""
    print("=" * 60)
    print("Heart Disease Model Training with MLflow")
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
    
    # Log data info
    with mlflow.start_run(run_name="Data_Info"):
        mlflow.log_param("train_samples", len(X_train))
        mlflow.log_param("test_samples", len(X_test))
        mlflow.log_param("n_features", X_train.shape[1])
        mlflow.log_param("class_balance", f"{y_train.value_counts().to_dict()}")
    
    # Train models
    print("\n" + "=" * 60)
    print("Training Models")
    print("=" * 60)
    
    _, lr_metrics = train_logistic_regression(X_train, y_train, X_test, y_test, preprocessor)
    _, rf_metrics = train_random_forest(X_train, y_train, X_test, y_test, preprocessor)
    
    # Compare models
    print("\n" + "=" * 60)
    print("Model Comparison")
    print("=" * 60)
    print(f"Logistic Regression - ROC-AUC: {lr_metrics['roc_auc']:.4f}")
    print(f"Random Forest - ROC-AUC: {rf_metrics['roc_auc']:.4f}")
    
    if rf_metrics['roc_auc'] > lr_metrics['roc_auc']:
        print("\nBest Model: Random Forest")
    else:
        print("\nBest Model: Logistic Regression")
    
    print("\n" + "=" * 60)
    print("Training complete! View results in MLflow UI:")
    print(f"  mlflow ui --backend-store-uri file://{MLFLOW_DIR.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()

