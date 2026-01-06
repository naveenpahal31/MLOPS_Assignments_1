#!/bin/bash
# Script to start MLflow UI for viewing experiment results

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

MLFLOW_DIR="$PROJECT_ROOT/mlruns"

echo "============================================================"
echo "Starting MLflow UI"
echo "============================================================"

# Check if MLflow is installed
if ! python -c "import mlflow" 2>/dev/null; then
    echo "❌ MLflow is not installed."
    echo "Please install it first: pip install mlflow"
    exit 1
fi

# Check if mlruns directory exists
if [ ! -d "$MLFLOW_DIR" ]; then
    echo "❌ No MLflow runs found in $MLFLOW_DIR"
    echo "Please run training first: python src/models/train_with_mlflow.py"
    exit 1
fi

echo "MLflow tracking URI: file://$MLFLOW_DIR"
echo ""
echo "MLflow UI will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo "============================================================"

mlflow ui --backend-store-uri "file://$MLFLOW_DIR" --port 5000


