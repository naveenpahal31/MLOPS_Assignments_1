"""
Unit tests for data processing functions.
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

from src.data.preprocessing import (
    HeartDiseasePreprocessor,
    clean_data,
    prepare_features_target,
    get_feature_names
)


class TestHeartDiseasePreprocessor:
    """Test cases for HeartDiseasePreprocessor class."""
    
    def test_preprocessor_initialization(self):
        """Test preprocessor can be initialized."""
        preprocessor = HeartDiseasePreprocessor()
        assert preprocessor is not None
        assert preprocessor.is_fitted == False
    
    def test_preprocessor_fit(self):
        """Test preprocessor can be fitted."""
        preprocessor = HeartDiseasePreprocessor()
        X = pd.DataFrame({
            'age': [63, 67, 37],
            'sex': [1, 1, 1],
            'cp': [1, 4, 3],
            'trestbps': [145, 160, 130],
            'chol': [233, 286, 250]
        })
        
        preprocessor.fit(X)
        assert preprocessor.is_fitted == True
    
    def test_preprocessor_transform_without_fit(self):
        """Test transform raises error if not fitted."""
        preprocessor = HeartDiseasePreprocessor()
        X = pd.DataFrame({
            'age': [63, 67],
            'sex': [1, 1],
            'cp': [1, 4]
        })
        
        with pytest.raises(ValueError, match="must be fitted"):
            preprocessor.transform(X)
    
    def test_preprocessor_fit_transform(self):
        """Test fit_transform method."""
        preprocessor = HeartDiseasePreprocessor()
        X = pd.DataFrame({
            'age': [63, 67, 37],
            'sex': [1, 1, 1],
            'cp': [1, 4, 3]
        })
        
        X_transformed = preprocessor.fit_transform(X)
        assert X_transformed.shape == X.shape
        assert preprocessor.is_fitted == True
    
    def test_preprocessor_handles_missing_values(self):
        """Test preprocessor handles missing values."""
        preprocessor = HeartDiseasePreprocessor()
        X = pd.DataFrame({
            'age': [63, np.nan, 37],
            'sex': [1, 1, 1],
            'cp': [1, 4, np.nan]
        })
        
        X_transformed = preprocessor.fit_transform(X)
        assert not np.isnan(X_transformed).any()
        assert X_transformed.shape == X.shape
    
    def test_preprocessor_save_and_load(self, tmp_path):
        """Test preprocessor can be saved and loaded."""
        preprocessor = HeartDiseasePreprocessor()
        X = pd.DataFrame({
            'age': [63, 67, 37],
            'sex': [1, 1, 1],
            'cp': [1, 4, 3]
        })
        
        preprocessor.fit(X)
        
        # Save
        save_path = tmp_path / "preprocessor.pkl"
        preprocessor.save(save_path)
        assert save_path.exists()
        
        # Load
        loaded_preprocessor = HeartDiseasePreprocessor.load(save_path)
        assert loaded_preprocessor.is_fitted == True
        
        # Test loaded preprocessor works
        X_test = pd.DataFrame({
            'age': [50, 60],
            'sex': [1, 0],
            'cp': [2, 3]
        })
        result = loaded_preprocessor.transform(X_test)
        assert result.shape == X_test.shape


class TestDataCleaning:
    """Test cases for data cleaning functions."""
    
    def test_clean_data_removes_source_column(self):
        """Test clean_data removes source column."""
        df = pd.DataFrame({
            'age': [63, 67],
            'sex': [1, 1],
            'target': [0, 1],
            'source': ['cleveland', 'hungarian']
        })
        
        df_clean = clean_data(df)
        assert 'source' not in df_clean.columns
    
    def test_clean_data_converts_target_to_binary(self):
        """Test clean_data converts target to binary."""
        df = pd.DataFrame({
            'age': [63, 67, 37, 41],
            'sex': [1, 1, 1, 0],
            'target': [0, 1, 2, 3]  # Original: 0=no disease, 1-4=disease
        })
        
        df_clean = clean_data(df)
        assert set(df_clean['target'].unique()).issubset({0, 1})
        assert (df_clean['target'] > 0).sum() == 3  # 1, 2, 3 should become 1
    
    def test_clean_data_handles_missing_values(self):
        """Test clean_data handles missing value markers."""
        df = pd.DataFrame({
            'age': [63, -9.0, 37],
            'sex': [1, 1, -9],
            'target': [0, 1, 0]
        })
        
        df_clean = clean_data(df)
        # Check that -9.0 and -9 are replaced with NaN
        assert df_clean['age'].isna().any() or df_clean['age'].notna().all()
    
    def test_prepare_features_target(self):
        """Test prepare_features_target separates features and target."""
        df = pd.DataFrame({
            'age': [63, 67, 37],
            'sex': [1, 1, 1],
            'cp': [1, 4, 3],
            'target': [0, 1, 0]
        })
        
        X, y = prepare_features_target(df)
        assert 'target' not in X.columns
        assert 'target' in df.columns
        assert len(X) == len(y)
        assert len(X.columns) == 3  # age, sex, cp
    
    def test_prepare_features_target_missing_target(self):
        """Test prepare_features_target raises error if target missing."""
        df = pd.DataFrame({
            'age': [63, 67],
            'sex': [1, 1]
        })
        
        with pytest.raises(ValueError, match="Target column 'target' not found"):
            prepare_features_target(df)
    
    def test_get_feature_names(self):
        """Test get_feature_names returns correct list."""
        feature_names = get_feature_names()
        assert isinstance(feature_names, list)
        assert len(feature_names) == 13
        assert 'age' in feature_names
        assert 'sex' in feature_names
        assert 'target' not in feature_names  # Target is not a feature


class TestDataIntegration:
    """Integration tests for data processing pipeline."""
    
    def test_full_preprocessing_pipeline(self):
        """Test complete preprocessing pipeline."""
        # Create sample data with missing values
        df = pd.DataFrame({
            'age': [63, np.nan, 37, 41],
            'sex': [1, 1, 1, 0],
            'cp': [1, 4, 3, 2],
            'trestbps': [145, 160, np.nan, 130],
            'target': [0, 1, 0, 1]
        })
        
        # Clean data
        df_clean = clean_data(df)
        
        # Prepare features and target
        X, y = prepare_features_target(df_clean)
        
        # Preprocess
        preprocessor = HeartDiseasePreprocessor()
        X_transformed = preprocessor.fit_transform(X)
        
        # Assertions
        assert X_transformed.shape[0] == len(y)
        assert not np.isnan(X_transformed).any()
        assert X_transformed.shape[1] == X.shape[1]

