#!/bin/bash
# Script to run MLflow training and start MLflow UI

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "MLflow Training and UI Setup"
echo "============================================================"

# Check if MLflow is installed
if ! python -c "import mlflow" 2>/dev/null; then
    echo "MLflow is not installed. Installing..."
    pip install mlflow matplotlib seaborn
    echo "✅ MLflow installed"
else
    echo "✅ MLflow is already installed"
fi

# Check if data is processed
if [ ! -f "data/processed/heart_disease_processed.csv" ]; then
    echo "Processing data first..."
    python scripts/preprocess_data.py
fi

# Run MLflow training
echo ""
echo "============================================================"
echo "Running MLflow Training"
echo "============================================================"
python src/models/train_with_mlflow.py

# Start MLflow UI
echo ""
echo "============================================================"
echo "Starting MLflow UI"
echo "============================================================"
echo "MLflow UI will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "============================================================"

mlflow ui --backend-store-uri "file://$PROJECT_ROOT/mlruns" --port 5000


