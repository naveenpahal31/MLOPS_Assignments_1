# Reproducibility Guide

This document explains how to ensure full reproducibility of model training and inference.

## Random Seeds

All random operations use a fixed seed (`RANDOM_SEED = 42`) to ensure reproducibility:
- Python's `random` module
- NumPy random operations
- Scikit-learn model training (via `random_state` parameter)

## Model Packaging

### Saved Artifacts

When training completes, the following artifacts are saved:

1. **Model Files** (`models/*.pkl`):
   - `logistic_regression_<timestamp>.pkl` - Trained Logistic Regression model
   - `random_forest_<timestamp>.pkl` - Trained Random Forest model

2. **Preprocessor** (`models/preprocessor_<timestamp>.pkl`):
   - Fitted `HeartDiseasePreprocessor` with scaler and imputer

3. **Training Summary** (`models/training_summary_<timestamp>.json`):
   - Metrics, parameters, and confusion matrices

### Model Formats

- **Primary Format**: Pickle (`.pkl`) - Native Python serialization
- **Alternative**: Can be exported to MLflow format using `train_with_mlflow.py`

## Reproducing Training

### Method 1: Using reproduce_training.py

```bash
python scripts/reproduce_training.py
```

This script:
- Sets all random seeds
- Uses the same data preprocessing pipeline
- Trains models with identical parameters
- Saves models with timestamps

### Method 2: Manual Reproduction

1. Set environment variable:
   ```bash
   export PYTHONHASHSEED=42
   ```

2. Run training:
   ```bash
   python src/models/train.py
   ```

3. Verify results match previous runs

## Loading Models for Inference

### Using ModelLoader Class

```python
from src.models.load_model import load_best_model

# Load the latest Random Forest model
loader = load_best_model()

# Make single prediction
result = loader.predict_single(
    age=63, sex=1, cp=1, trestbps=145, chol=233,
    fbs=1, restecg=2, thalach=150, exang=0,
    oldpeak=2.3, slope=3, ca=0, thal=6
)

print(result['prediction_label'])  # 'Disease Present' or 'No Disease'
print(result['probability'])       # Probability of disease
```

### Batch Predictions

```python
import pandas as pd
from src.models.load_model import load_best_model

loader = load_best_model()

# Load your data
X = pd.read_csv('data/processed/X_features.csv')

# Make predictions
predictions = loader.predict(X)
probabilities = loader.predict(X, return_proba=True)
```

## Environment Setup

### Using requirements.txt (pip)

```bash
pip install -r requirements.txt
```

### Using environment.yml (conda)

```bash
conda env create -f environment.yml
conda activate mlops-heart-disease
```

## Testing Reproducibility

### Test Model Inference

```bash
python scripts/test_model_inference.py
```

This script verifies:
- Models can be loaded successfully
- Single predictions work correctly
- Batch predictions match expected metrics
- Preprocessor works consistently

### Verify Training Reproducibility

1. Run training twice:
   ```bash
   python scripts/reproduce_training.py
   # Wait for completion
   python scripts/reproduce_training.py
   ```

2. Compare model files:
   - Check that metrics in `training_summary_*.json` match
   - Verify confusion matrices are identical

## Preprocessing Pipeline

The preprocessing pipeline is fully reproducible:

1. **Data Cleaning** (`src/data/preprocessing.py::clean_data`):
   - Handles missing values (marked as -9.0 or '?')
   - Converts target to binary
   - Ensures numeric types

2. **Feature Preprocessing** (`HeartDiseasePreprocessor`):
   - Missing value imputation (median strategy)
   - Standard scaling (zero mean, unit variance)
   - Both fitted on training data only

3. **Consistent Application**:
   - Same preprocessor used for training and inference
   - Preprocessor saved with model for deployment

## Version Control

To ensure reproducibility across environments:

1. **Pin Dependencies**: All package versions are specified in `requirements.txt`
2. **Python Version**: Recommended Python 3.9+ (specified in `environment.yml`)
3. **Random Seeds**: Fixed seed (42) used throughout
4. **Data Versioning**: Raw data files are tracked (or download script provided)

## Troubleshooting

### Different Results on Different Runs

1. Check random seed is set:
   ```python
   import random
   import numpy as np
   random.seed(42)
   np.random.seed(42)
   ```

2. Verify Python version matches (check `environment.yml`)

3. Ensure all dependencies match `requirements.txt` versions

### Model Loading Errors

1. Verify model file exists in `models/` directory
2. Check preprocessor file exists (matching timestamp)
3. Ensure feature names match expected format

### Preprocessing Inconsistencies

1. Verify preprocessor was fitted on training data
2. Check that same preprocessor is used for inference
3. Ensure no data leakage (test data not used in fitting)

## Best Practices

1. **Always use reproduce_training.py** for training
2. **Save preprocessor with model** (automatically done)
3. **Test models after loading** using `test_model_inference.py`
4. **Document any changes** to preprocessing or model parameters
5. **Version your models** using timestamps or version numbers


