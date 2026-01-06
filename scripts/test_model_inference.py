"""
Test model inference script.

Verifies that saved models can be loaded and used for inference correctly.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

from src.models.load_model import load_best_model, ModelLoader
from src.data.preprocessing import prepare_features_target
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score


def test_model_loading():
    """Test that models can be loaded successfully."""
    print("=" * 60)
    print("Test 1: Model Loading")
    print("=" * 60)
    
    try:
        loader = load_best_model()
        print("✅ Model loaded successfully")
        print(f"   Model type: {type(loader.model).__name__}")
        print(f"   Preprocessor loaded: {loader.preprocessor is not None}")
        return loader
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        return None


def test_single_prediction(loader):
    """Test single prediction."""
    print("\n" + "=" * 60)
    print("Test 2: Single Prediction")
    print("=" * 60)
    
    if loader is None:
        print("❌ Skipping: Model not loaded")
        return False
    
    try:
        # Test sample
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
        
        print("✅ Single prediction successful")
        print(f"   Input: {sample}")
        print(f"   Prediction: {result['prediction_label']}")
        print(f"   Probability: {result['probability']:.4f}")
        print(f"   Confidence: {result['confidence']:.4f}")
        
        # Validate output
        assert result['prediction'] in [0, 1], "Prediction must be 0 or 1"
        assert 0 <= result['probability'] <= 1, "Probability must be between 0 and 1"
        assert 0 <= result['confidence'] <= 1, "Confidence must be between 0 and 1"
        
        return True
    except Exception as e:
        print(f"❌ Single prediction failed: {e}")
        return False


def test_batch_prediction(loader):
    """Test batch prediction on test data."""
    print("\n" + "=" * 60)
    print("Test 3: Batch Prediction on Test Data")
    print("=" * 60)
    
    if loader is None:
        print("❌ Skipping: Model not loaded")
        return False
    
    try:
        # Load test data
        data_path = PROJECT_ROOT / "data" / "processed" / "heart_disease_processed.csv"
        if not data_path.exists():
            print("⚠️  Test data not found. Run preprocess_data.py first.")
            return False
        
        df = pd.read_csv(data_path)
        X, y = prepare_features_target(df)
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Make predictions
        predictions = loader.predict(X_test)
        probabilities = loader.predict(X_test, return_proba=True)[:, 1]
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, predictions)
        roc_auc = roc_auc_score(y_test, probabilities)
        
        print("✅ Batch prediction successful")
        print(f"   Test samples: {len(X_test)}")
        print(f"   Accuracy: {accuracy:.4f}")
        print(f"   ROC-AUC: {roc_auc:.4f}")
        
        # Validate metrics
        assert accuracy > 0.5, "Accuracy should be better than random"
        assert roc_auc > 0.5, "ROC-AUC should be better than random"
        
        return True
    except Exception as e:
        print(f"❌ Batch prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preprocessor_consistency(loader):
    """Test that preprocessor works consistently."""
    print("\n" + "=" * 60)
    print("Test 4: Preprocessor Consistency")
    print("=" * 60)
    
    if loader is None:
        print("❌ Skipping: Model not loaded")
        return False
    
    try:
        # Create sample data
        sample_data = pd.DataFrame({
            'age': [63, 67, 37],
            'sex': [1, 1, 1],
            'cp': [1, 4, 3],
            'trestbps': [145, 160, 130],
            'chol': [233, 286, 250],
            'fbs': [1, 0, 0],
            'restecg': [2, 2, 0],
            'thalach': [150, 108, 187],
            'exang': [0, 1, 0],
            'oldpeak': [2.3, 1.5, 3.5],
            'slope': [3, 2, 3],
            'ca': [0, 3, 0],
            'thal': [6, 3, 3]
        })
        
        # Transform
        transformed = loader.preprocessor.transform(sample_data)
        
        print("✅ Preprocessor consistency test passed")
        print(f"   Input shape: {sample_data.shape}")
        print(f"   Output shape: {transformed.shape}")
        print(f"   Output type: {type(transformed)}")
        
        # Validate
        assert transformed.shape[0] == sample_data.shape[0], "Row count should match"
        assert transformed.shape[1] == sample_data.shape[1], "Column count should match"
        assert not np.isnan(transformed).any(), "No NaN values should be present"
        
        return True
    except Exception as e:
        print(f"❌ Preprocessor consistency test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Model Inference Tests")
    print("=" * 60)
    
    results = []
    
    # Test 1: Model loading
    loader = test_model_loading()
    results.append(("Model Loading", loader is not None))
    
    if loader:
        # Test 2: Single prediction
        results.append(("Single Prediction", test_single_prediction(loader)))
        
        # Test 3: Batch prediction
        results.append(("Batch Prediction", test_batch_prediction(loader)))
        
        # Test 4: Preprocessor consistency
        results.append(("Preprocessor Consistency", test_preprocessor_consistency(loader)))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Models are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


