# MLflow Guide - Running Experiments and Viewing Results

This guide explains how to run MLflow training and view experiment results locally.

## Prerequisites

### 1. Install MLflow

```bash
pip install mlflow matplotlib seaborn
```

Or using conda:
```bash
conda install -c conda-forge mlflow
```

### 2. Ensure Data is Processed

```bash
python scripts/preprocess_data.py
```

## Running MLflow Training

### Method 1: Using the Training Script Directly

```bash
python src/models/train_with_mlflow.py
```

This will:
- Load and preprocess the data
- Train Logistic Regression and Random Forest models
- Log all parameters, metrics, and artifacts to MLflow
- Save confusion matrix plots
- Log classification reports

### Method 2: Using the Helper Script (Linux/Mac)

```bash
chmod +x scripts/run_mlflow_training.sh
./scripts/run_mlflow_training.sh
```

## Viewing Results in MLflow UI

### Start MLflow UI

After training, start the MLflow UI:

```bash
mlflow ui --backend-store-uri file://$(pwd)/mlruns --port 5000
```

Or use the helper script:

```bash
chmod +x scripts/start_mlflow_ui.sh
./scripts/start_mlflow_ui.sh
```

### Access the UI

Open your browser and navigate to:
```
http://localhost:5000
```

## What You'll See in MLflow UI

### 1. Experiments List
- View all experiments
- See experiment names and metadata
- Filter and search experiments

### 2. Runs Overview
- List of all training runs
- Quick comparison of metrics
- Run status and duration

### 3. Run Details
For each run, you can view:

**Parameters:**
- Model hyperparameters
- Training configuration
- Data information

**Metrics:**
- Accuracy
- Precision
- Recall
- ROC-AUC
- Cross-validation scores

**Artifacts:**
- Saved models
- Confusion matrix plots
- Classification reports
- Feature importance (for Random Forest)

**Code:**
- Source code used for the run
- Git commit information (if available)

### 4. Model Comparison
- Compare multiple runs side-by-side
- Visualize metric differences
- Select best model based on metrics

## Example Workflow

### Step 1: Run Training
```bash
cd /Users/a0k04ou/Desktop/MLOPs
python src/models/train_with_mlflow.py
```

Expected output:
```
============================================================
Heart Disease Model Training with MLflow
============================================================
Loaded data: (920, 14)
...
Logistic Regression - ROC-AUC: 0.8940
Random Forest - ROC-AUC: 0.9202
...
Training complete! View results in MLflow UI:
  mlflow ui --backend-store-uri file:///path/to/mlruns
============================================================
```

### Step 2: Start MLflow UI
```bash
mlflow ui --backend-store-uri file://$(pwd)/mlruns --port 5000
```

### Step 3: View Results
1. Open browser: http://localhost:5000
2. Click on "heart_disease_prediction" experiment
3. View runs for Logistic Regression and Random Forest
4. Compare metrics and select best model

## Understanding the Logged Information

### Parameters Logged
- `random_state`: 42
- `max_iter`: 1000 (Logistic Regression)
- `n_estimators`: 100 (Random Forest)
- `max_depth`: 10 (Random Forest)
- `train_samples`: Number of training samples
- `test_samples`: Number of test samples
- `n_features`: Number of features

### Metrics Logged
- `accuracy`: Overall accuracy
- `precision`: Precision score
- `recall`: Recall score
- `roc_auc`: ROC-AUC score
- `cv_roc_auc_mean`: Mean cross-validation ROC-AUC
- `cv_roc_auc_std`: Standard deviation of CV ROC-AUC

### Artifacts Logged
- `model/`: Saved scikit-learn model (can be loaded for inference)
- `confusion_matrix_*.png`: Confusion matrix visualization
- `classification_report.json`: Detailed classification metrics
- `feature_importance.json`: Feature importance (Random Forest only)

## Loading Models from MLflow

You can load models logged to MLflow:

```python
import mlflow
import mlflow.sklearn

# Set tracking URI
mlflow.set_tracking_uri("file:///path/to/mlruns")

# Load a specific run's model
run_id = "your-run-id-here"
model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

# Use the model
predictions = model.predict(X_test)
```

## Troubleshooting

### MLflow UI Not Starting

1. **Check if port 5000 is available:**
   ```bash
   lsof -i :5000
   ```
   If occupied, use a different port:
   ```bash
   mlflow ui --backend-store-uri file://$(pwd)/mlruns --port 5001
   ```

2. **Check if mlruns directory exists:**
   ```bash
   ls -la mlruns/
   ```
   If empty, run training first.

### No Experiments Showing

- Ensure you've run `train_with_mlflow.py` successfully
- Check that `mlruns/` directory contains experiment data
- Verify MLflow tracking URI matches the directory path

### Permission Errors

If you get permission errors:
```bash
chmod -R 755 mlruns/
```

## Best Practices

1. **Run multiple experiments** with different hyperparameters
2. **Tag important runs** for easy identification
3. **Compare models** using the MLflow UI comparison feature
4. **Export best model** for production deployment
5. **Document experiments** with notes in MLflow UI

## Next Steps

After viewing results in MLflow:
- Select the best model based on metrics
- Export the model for deployment
- Use the model in Phase 6 (Containerization)
- Set up automated model registry (advanced)


