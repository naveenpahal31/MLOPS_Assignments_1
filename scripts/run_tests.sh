#!/bin/bash
# Script to run all tests locally

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "============================================================"
echo "Running Tests"
echo "============================================================"

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "Installing pytest..."
    pip install pytest pytest-cov
fi

# Run tests
echo ""
echo "Running unit tests..."
pytest tests/ -v --tb=short

echo ""
echo "============================================================"
echo "Running with coverage..."
echo "============================================================"
pytest tests/ -v --cov=src --cov-report=term-missing

echo ""
echo "============================================================"
echo "All tests completed!"
echo "============================================================"

