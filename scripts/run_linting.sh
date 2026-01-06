#!/bin/bash
# Script to run linting checks locally

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "Running Linting Checks"
echo "============================================================"

# Check and install flake8
if ! python -c "import flake8" 2>/dev/null; then
    echo "Installing flake8..."
    pip install flake8
fi

# Check and install pylint
if ! python -c "import pylint" 2>/dev/null; then
    echo "Installing pylint..."
    pip install pylint
fi

echo ""
echo "Running flake8..."
flake8 src/ scripts/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src/ scripts/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=100 --statistics

echo ""
echo "Running pylint..."
pylint src/ scripts/ --exit-zero --rcfile=.pylintrc || true

echo ""
echo "============================================================"
echo "Linting completed!"
echo "============================================================"

