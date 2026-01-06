"""
Unit tests for model training and prediction.
"""

import sys
from pathlib import Path

# Add project root to path before other imports
PROJECT_ROOT = Path(__file__).parent.parent
project_root_str = str(PROJECT_ROOT)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

# Try to import with helpful error message if it fails
try:
    from src.models.load_model import ModelLoader, load_best_model
    from src.data.preprocessing import HeartDiseasePreprocessor, prepare_features_target
except ImportError as e:
    # If import fails, print debug info for CI troubleshooting
    import os
    print(f"\n{'='*60}")
    print(f"Import Error: {e}")
    print(f"{'='*60}")
    print(f"Current directory: {os.getcwd()}")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"PROJECT_ROOT exists: {PROJECT_ROOT.exists()}")
    print(f"sys.path (first 5): {sys.path[:5]}")
    
    # Check directory and file existence
    src_dir = PROJECT_ROOT / "src"
    models_dir = src_dir / "models"
    data_dir = src_dir / "data"
    load_model_file = models_dir / "load_model.py"
    
    print(f"src directory exists: {src_dir.exists()}")
    print(f"src/models directory exists: {models_dir.exists()}")
    print(f"src/models/load_model.py exists: {load_model_file.exists()}")
    print(f"src/data directory exists: {data_dir.exists()}")
    
    # Check for specific files (check files, not just directories)
    if load_model_file.exists():
        model_files = list(models_dir.glob("*.py"))
        print(f"✓ Files in src/models: {[f.name for f in model_files]}")
    else:
        print(f"✗ src/models/load_model.py NOT found at {load_model_file}")
        # Try to list what's in src/
        if src_dir.exists():
            print(f"Contents of src/: {[p.name for p in src_dir.iterdir()]}")
        # Check if models_dir exists as a file (shouldn't happen but check)
        if models_dir.exists() and models_dir.is_file():
            print(f"⚠️  src/models exists but is a FILE, not a directory!")
    
    if data_dir.exists():
        data_files = list(data_dir.glob("*.py"))
        print(f"✓ Files in src/data: {[f.name for f in data_files]}")
    
    print(f"{'='*60}\n")
    raise

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class TestModelLoader:
    """Test cases for ModelLoader class."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        return pd.DataFrame({
            'age': [63, 67, 37, 41, 56],
            'sex': [1, 1, 1, 0, 1],
            'cp': [1, 4, 3, 2, 2],
            'trestbps': [145, 160, 130, 130, 120],
            'chol': [233, 286, 250, 204, 236],
            'fbs': [1, 0, 0, 0, 0],
            'restecg': [2, 2, 0, 2, 0],
            'thalach': [150, 108, 187, 172, 178],
            'exang': [0, 1, 0, 0, 0],
            'oldpeak': [2.3, 1.5, 3.5, 1.4, 0.8],
            'slope': [3, 2, 3, 1, 1],
            'ca': [0, 3, 0, 0, 0],
            'thal': [6, 3, 3, 3, 3],
            'target': [0, 1, 0, 0, 0]
        })
    
    def test_model_loader_initialization(self):
        """Test ModelLoader can be initialized."""
        loader = ModelLoader(model_name="random_forest")
        assert loader.model_name == "random_forest"
        assert loader.model is None
        assert loader.preprocessor is None
    
    def test_predict_single_with_mock_model(self, sample_data):
        """Test predict_single method with mocked model."""
        loader = ModelLoader(model_name="test")
        
        # Create mock model and preprocessor
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1])
        mock_model.predict_proba.return_value = np.array([[0.3, 0.7]])
        
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([[1, 2, 3]])
        
        loader.model = mock_model
        loader.preprocessor = mock_preprocessor
        
        # Test prediction
        result = loader.predict_single(
            age=63, sex=1, cp=1, trestbps=145, chol=233,
            fbs=1, restecg=2, thalach=150, exang=0,
            oldpeak=2.3, slope=3, ca=0, thal=6
        )
        
        assert result['prediction'] in [0, 1]
        assert 0 <= result['probability'] <= 1
        assert 0 <= result['confidence'] <= 1
        assert 'prediction_label' in result
    
    def test_predict_batch_with_mock_model(self, sample_data):
        """Test batch prediction with mocked model."""
        loader = ModelLoader(model_name="test")
        
        # Prepare test data first to know the size
        X, _ = prepare_features_target(sample_data)
        n_samples = len(X)
        
        # Create mock model and preprocessor
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([0, 1, 0, 1, 0][:n_samples])
        mock_model.predict_proba.return_value = np.array([
            [0.8, 0.2],
            [0.3, 0.7],
            [0.9, 0.1],
            [0.4, 0.6],
            [0.85, 0.15]
        ])[:n_samples]
        
        mock_preprocessor = MagicMock()
        mock_preprocessor.transform.return_value = np.array([
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
            [10, 11, 12],
            [13, 14, 15]
        ])[:n_samples]
        
        loader.model = mock_model
        loader.preprocessor = mock_preprocessor
        
        # Test batch prediction
        predictions = loader.predict(X)
        probabilities = loader.predict(X, return_proba=True)
        
        assert len(predictions) == len(X)
        assert probabilities.shape[0] == len(X)
        assert probabilities.shape[1] == 2  # Binary classification


class TestModelTraining:
    """Test cases for model training functionality."""
    
    @pytest.fixture
    def sample_training_data(self):
        """Create sample data for training."""
        np.random.seed(42)
        n_samples = 100
        X = pd.DataFrame({
            'age': np.random.randint(30, 80, n_samples),
            'sex': np.random.randint(0, 2, n_samples),
            'cp': np.random.randint(1, 5, n_samples),
            'trestbps': np.random.randint(90, 200, n_samples),
            'chol': np.random.randint(100, 400, n_samples),
            'fbs': np.random.randint(0, 2, n_samples),
            'restecg': np.random.randint(0, 3, n_samples),
            'thalach': np.random.randint(70, 200, n_samples),
            'exang': np.random.randint(0, 2, n_samples),
            'oldpeak': np.random.uniform(0, 6, n_samples),
            'slope': np.random.randint(1, 4, n_samples),
            'ca': np.random.randint(0, 4, n_samples),
            'thal': np.random.choice([3, 6, 7], n_samples)
        })
        y = pd.Series(np.random.randint(0, 2, n_samples))
        return X, y
    
    def test_logistic_regression_training(self, sample_training_data):
        """Test Logistic Regression can be trained."""
        X, y = sample_training_data
        
        # Preprocess
        preprocessor = HeartDiseasePreprocessor()
        X_scaled = preprocessor.fit_transform(X)
        
        # Train model
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_scaled, y)
        
        # Make predictions
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)
        
        assert len(predictions) == len(y)
        assert probabilities.shape == (len(y), 2)
        assert model.score(X_scaled, y) > 0  # Should have some accuracy
    
    def test_random_forest_training(self, sample_training_data):
        """Test Random Forest can be trained."""
        X, y = sample_training_data
        
        # Preprocess
        preprocessor = HeartDiseasePreprocessor()
        X_scaled = preprocessor.fit_transform(X)
        
        # Train model
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X_scaled, y)
        
        # Make predictions
        predictions = model.predict(X_scaled)
        probabilities = model.predict_proba(X_scaled)
        
        assert len(predictions) == len(y)
        assert probabilities.shape == (len(y), 2)
        assert model.score(X_scaled, y) > 0  # Should have some accuracy
    
    def test_model_predictions_are_binary(self, sample_training_data):
        """Test model predictions are binary (0 or 1)."""
        X, y = sample_training_data
        
        preprocessor = HeartDiseasePreprocessor()
        X_scaled = preprocessor.fit_transform(X)
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_scaled, y)
        
        predictions = model.predict(X_scaled)
        
        assert set(predictions).issubset({0, 1})
    
    def test_model_probabilities_sum_to_one(self, sample_training_data):
        """Test model probabilities sum to 1."""
        X, y = sample_training_data
        
        preprocessor = HeartDiseasePreprocessor()
        X_scaled = preprocessor.fit_transform(X)
        
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_scaled, y)
        
        probabilities = model.predict_proba(X_scaled)
        
        # Each row should sum to approximately 1
        assert np.allclose(probabilities.sum(axis=1), 1.0)


class TestModelMetrics:
    """Test cases for model evaluation metrics."""
    
    @pytest.fixture
    def sample_predictions(self):
        """Create sample predictions for testing."""
        y_true = np.array([0, 1, 0, 1, 0, 1, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.2, 0.4, 0.6, 0.8, 0.95, 0.3])
        return y_true, y_pred, y_proba
    
    def test_accuracy_calculation(self, sample_predictions):
        """Test accuracy calculation."""
        from sklearn.metrics import accuracy_score
        y_true, y_pred, _ = sample_predictions
        
        accuracy = accuracy_score(y_true, y_pred)
        assert 0 <= accuracy <= 1
        
        # Perfect predictions should have accuracy = 1
        perfect_pred = y_true.copy()
        assert accuracy_score(y_true, perfect_pred) == 1.0
    
    def test_precision_calculation(self, sample_predictions):
        """Test precision calculation."""
        from sklearn.metrics import precision_score
        y_true, y_pred, _ = sample_predictions
        
        precision = precision_score(y_true, y_pred)
        assert 0 <= precision <= 1
    
    def test_recall_calculation(self, sample_predictions):
        """Test recall calculation."""
        from sklearn.metrics import recall_score
        y_true, y_pred, _ = sample_predictions
        
        recall = recall_score(y_true, y_pred)
        assert 0 <= recall <= 1
    
    def test_roc_auc_calculation(self, sample_predictions):
        """Test ROC-AUC calculation."""
        from sklearn.metrics import roc_auc_score
        y_true, _, y_proba = sample_predictions
        
        roc_auc = roc_auc_score(y_true, y_proba)
        assert 0 <= roc_auc <= 1

