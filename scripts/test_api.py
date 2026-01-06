#!/usr/bin/env python3
"""
Script to test the FastAPI application endpoints.
"""

import sys
import json
import requests
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

API_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Health check passed: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_root():
    """Test root endpoint."""
    print("\nTesting / endpoint...")
    try:
        response = requests.get(f"{API_URL}/", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Root endpoint: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Root endpoint failed: {e}")
        return False


def test_predict():
    """Test prediction endpoint."""
    print("\nTesting /predict endpoint...")
    
    # Load test request
    test_file = PROJECT_ROOT / "test_request.json"
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
    else:
        # Default test data
        test_data = {
            "age": 63,
            "sex": 1,
            "cp": 1,
            "trestbps": 145,
            "chol": 233,
            "fbs": 1,
            "restecg": 2,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 3,
            "ca": 0,
            "thal": 6
        }
    
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ Prediction successful:")
        print(f"  Prediction: {result['prediction_label']}")
        print(f"  Probability: {result['probability']:.4f}")
        print(f"  Confidence: {result['confidence']:.4f}")
        return True
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                print(f"  Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"  Error response: {e.response.text}")
        return False


def test_model_info():
    """Test model info endpoint."""
    print("\nTesting /model/info endpoint...")
    try:
        response = requests.get(f"{API_URL}/model/info", timeout=5)
        response.raise_for_status()
        data = response.json()
        print(f"✓ Model info: {json.dumps(data, indent=2)}")
        return True
    except Exception as e:
        print(f"✗ Model info failed: {e}")
        return False


def test_batch_predict():
    """Test batch prediction endpoint."""
    print("\nTesting /predict/batch endpoint...")
    
    test_data = [
        {
            "age": 63,
            "sex": 1,
            "cp": 1,
            "trestbps": 145,
            "chol": 233,
            "fbs": 1,
            "restecg": 2,
            "thalach": 150,
            "exang": 0,
            "oldpeak": 2.3,
            "slope": 3,
            "ca": 0,
            "thal": 6
        },
        {
            "age": 37,
            "sex": 1,
            "cp": 2,
            "trestbps": 130,
            "chol": 250,
            "fbs": 0,
            "restecg": 0,
            "thalach": 187,
            "exang": 0,
            "oldpeak": 3.5,
            "slope": 1,
            "ca": 0,
            "thal": 3
        }
    ]
    
    try:
        response = requests.post(
            f"{API_URL}/predict/batch",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ Batch prediction successful:")
        print(f"  Number of predictions: {result['count']}")
        for i, pred in enumerate(result['predictions']):
            print(f"  Sample {i+1}: {pred['prediction_label']} "
                  f"(probability: {pred['probability']:.4f})")
        return True
    except Exception as e:
        print(f"✗ Batch prediction failed: {e}")
        return False


def main():
    """Run all API tests."""
    print("=" * 60)
    print("Testing Heart Disease Prediction API")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print("=" * 60)
    
    # Wait for API to be ready
    print("\nWaiting for API to be ready...")
    import time
    for i in range(30):
        try:
            requests.get(f"{API_URL}/health", timeout=2)
            print("✓ API is ready!")
            break
        except:
            if i == 29:
                print("✗ API failed to start. Make sure the server is running.")
                print("  Run: python scripts/run_api_local.py")
                return
            time.sleep(1)
    
    # Run tests
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Root Endpoint", test_root()))
    results.append(("Model Info", test_model_info()))
    results.append(("Single Prediction", test_predict()))
    results.append(("Batch Prediction", test_batch_predict()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("All tests passed! ✓")
        return 0
    else:
        print("Some tests failed. ✗")
        return 1


if __name__ == "__main__":
    sys.exit(main())

