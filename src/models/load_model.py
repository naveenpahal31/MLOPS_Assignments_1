"""
Model loading and inference script.

Provides functions to load saved models and make predictions.
"""

import sys
from pathlib import Path
import pickle
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.data.preprocessing import HeartDiseasePreprocessor, get_feature_names, prepare_features_target

# Define paths
MODELS_DIR = PROJECT_ROOT / "models"


class ModelLoader:
    """Class to load and use trained models for inference."""

    def __init__(self, model_name="random_forest", model_dir=None):
        """
        Initialize model loader.
        
        Args:
            model_name: Name of the model ('random_forest' or 'logistic_regression')
            model_dir: Directory containing models (default: PROJECT_ROOT/models)
        """
        self.model_dir = model_dir or MODELS_DIR
        self.model_name = model_name.lower().replace(' ', '_')
        self.model = None
        self.preprocessor = None
        self.model_info = None

    def load_latest_model(self):
        """Load the most recent model of the specified type."""
        # Find all model files matching the pattern
        pattern = f"{self.model_name}_*.pkl"
        model_files = list(self.model_dir.glob(pattern))
        
        if not model_files:
            raise FileNotFoundError(
                f"No {self.model_name} model found in {self.model_dir}"
            )
        
        # Get the latest model file
        latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
        return self.load_model(latest_model)

    def load_model(self, model_path=None):
        """
        Load model and preprocessor.
        
        Args:
            model_path: Path to model file (if None, loads latest)
        """
        if model_path is None:
            return self.load_latest_model()
        
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load model
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        # Load preprocessor (look for matching preprocessor file)
        preprocessor_pattern = "preprocessor_*.pkl"
        preprocessor_files = list(self.model_dir.glob(preprocessor_pattern))

        if not preprocessor_files:
            raise FileNotFoundError(f"No preprocessor found in {self.model_dir}")

        # Get preprocessor with similar timestamp
        model_timestamp = model_path.stem.split('_')[-1]
        matching_preprocessor = None

        for pp_file in preprocessor_files:
            if model_timestamp in pp_file.stem:
                matching_preprocessor = pp_file
                break

        if matching_preprocessor is None:
            # Use latest preprocessor
            matching_preprocessor = max(preprocessor_files, key=lambda p: p.stat().st_mtime)

        self.preprocessor = HeartDiseasePreprocessor.load(matching_preprocessor)

        # Load model info if available
        summary_pattern = "training_summary_*.json"
        summary_files = list(self.model_dir.glob(summary_pattern))
        if summary_files:
            latest_summary = max(summary_files, key=lambda p: p.stat().st_mtime)
            with open(latest_summary, 'r', encoding='utf-8') as f:
                summary = json.load(f)
                # Try to find model info
                for model_key in summary.get('models', {}):
                    if self.model_name in model_key.lower().replace(' ', '_'):
                        self.model_info = summary['models'][model_key]
                        break

        print(f"Loaded model from: {model_path}")
        print(f"Loaded preprocessor from: {matching_preprocessor}")

        return self
    
    def predict(self, X, return_proba=False):
        """
        Make predictions using the loaded model.
        
        Args:
            X: Feature matrix (DataFrame or array)
            return_proba: If True, return probabilities instead of predictions
            
        Returns:
            Predictions or probabilities
        """
        if self.model is None or self.preprocessor is None:
            raise ValueError("Model and preprocessor must be loaded first!")

        # Convert to DataFrame if needed
        if isinstance(X, np.ndarray):
            feature_names = get_feature_names()
            if X.shape[1] == len(feature_names):
                X = pd.DataFrame(X, columns=feature_names)
            else:
                X = pd.DataFrame(X)
        elif isinstance(X, dict):
            X = pd.DataFrame([X])

        # Preprocess
        X_scaled = self.preprocessor.transform(X)

        # Predict
        if return_proba:
            return self.model.predict_proba(X_scaled)
        return self.model.predict(X_scaled)
    
    def predict_single(self, **kwargs):
        """
        Make prediction for a single sample using keyword arguments.
        
        Args:
            **kwargs: Feature values as keyword arguments
            
        Returns:
            Dictionary with prediction, probability, and confidence
        """
        # Get feature names
        feature_names = get_feature_names()
        
        # Create DataFrame from kwargs
        sample = pd.DataFrame([{name: kwargs.get(name, np.nan) for name in feature_names}])
        
        # Predict
        prediction = self.predict(sample)[0]
        probabilities = self.predict(sample, return_proba=True)[0]
        
        return {
            'prediction': int(prediction),
            'prediction_label': 'Disease Present' if prediction == 1 else 'No Disease',
            'probability': float(probabilities[1]),
            'confidence': float(max(probabilities))
        }


def load_best_model(model_dir=None):
    """
    Load the best model (Random Forest by default).
    
    Args:
        model_dir: Directory containing models
        
    Returns:
        ModelLoader instance
    """
    loader = ModelLoader(model_name="random_forest", model_dir=model_dir)
    loader.load_latest_model()
    return loader


def _evaluate_on_test_data(loader):
    """Evaluate model on test data."""
    data_path = PROJECT_ROOT / "data" / "processed" / "heart_disease_processed.csv"
    if not data_path.exists():
        print("Test data not found. Run preprocess_data.py first.")
        return

    df = pd.read_csv(data_path)
    X, y = prepare_features_target(df)
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    predictions = loader.predict(X_test)
    probabilities = loader.predict(X_test, return_proba=True)[:, 1]

    accuracy = accuracy_score(y_test, predictions)
    roc_auc = roc_auc_score(y_test, probabilities)

    print(f"Test Accuracy: {accuracy:.4f}")
    print(f"Test ROC-AUC: {roc_auc:.4f}")


def main():
    """Example usage of model loader."""
    print("=" * 60)
    print("Model Loader - Example Usage")
    print("=" * 60)

    # Load model
    loader = load_best_model()

    # Example: Predict for a single sample
    print("\nExample Prediction:")
    print("-" * 60)

    sample = {
        'age': 63,
        'sex': 1,
        'cp': 1,
        'trestbps': 145,
        'chol': 233,
        'fbs': 1,
        'restecg': 2,
        'thalach': 150,
        'exang': 0,
        'oldpeak': 2.3,
        'slope': 3,
        'ca': 0,
        'thal': 6
    }

    result = loader.predict_single(**sample)
    print(f"Sample: {sample}")
    print(f"\nPrediction: {result['prediction_label']}")
    print(f"Probability: {result['probability']:.4f}")
    print(f"Confidence: {result['confidence']:.4f}")

    # Load test data and evaluate
    print("\n" + "=" * 60)
    print("Evaluating on Test Data")
    print("=" * 60)

    _evaluate_on_test_data(loader)


if __name__ == "__main__":
    main()
