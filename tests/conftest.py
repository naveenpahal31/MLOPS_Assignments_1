"""
Pytest configuration and shared fixtures.
"""

import sys
from pathlib import Path

# Add project root to path before other imports
PROJECT_ROOT = Path(__file__).parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_heart_disease_data():
    """Create sample heart disease dataset for testing."""
    return pd.DataFrame({
        'age': [63, 67, 37, 41, 56, 62, 57, 63],
        'sex': [1, 1, 1, 0, 1, 0, 0, 1],
        'cp': [1, 4, 3, 2, 2, 4, 4, 4],
        'trestbps': [145, 160, 130, 130, 120, 140, 120, 130],
        'chol': [233, 286, 250, 204, 236, 268, 354, 254],
        'fbs': [1, 0, 0, 0, 0, 0, 0, 0],
        'restecg': [2, 2, 0, 2, 0, 2, 0, 2],
        'thalach': [150, 108, 187, 172, 178, 160, 163, 147],
        'exang': [0, 1, 0, 0, 0, 0, 1, 0],
        'oldpeak': [2.3, 1.5, 3.5, 1.4, 0.8, 3.6, 0.6, 1.4],
        'slope': [3, 2, 3, 1, 1, 3, 1, 2],
        'ca': [0, 3, 0, 0, 0, 2, 0, 1],
        'thal': [6, 3, 3, 3, 3, 3, 3, 7],
        'target': [0, 1, 0, 0, 0, 1, 0, 1]
    })


@pytest.fixture
def sample_features_only():
    """Create sample features without target."""
    return pd.DataFrame({
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

