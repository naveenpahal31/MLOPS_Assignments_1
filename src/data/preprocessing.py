"""
Data preprocessing pipeline for Heart Disease dataset.

This module provides reusable transformers and preprocessing functions.
"""

import pickle
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


class HeartDiseasePreprocessor:
    """
    Preprocessing pipeline for Heart Disease dataset.
    Handles missing values, feature encoding, and scaling.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = SimpleImputer(strategy='median')
        self.is_fitted = False
        
    def fit(self, X):
        """Fit the preprocessor on training data."""
        # Handle missing values
        X_imputed = self.imputer.fit_transform(X)
        
        # Fit scaler
        self.scaler.fit(X_imputed)
        
        self.is_fitted = True
        return self
    
    def transform(self, X):
        """Transform data using fitted preprocessor."""
        if not self.is_fitted:
            raise ValueError("Preprocessor must be fitted before transform!")
        
        # Impute missing values
        X_imputed = self.imputer.transform(X)
        
        # Scale features
        X_scaled = self.scaler.transform(X_imputed)
        
        return X_scaled
    
    def fit_transform(self, X):
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
    
    def save(self, filepath):
        """Save preprocessor to disk."""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'scaler': self.scaler,
                'imputer': self.imputer,
                'is_fitted': self.is_fitted
            }, f)
        print(f"Preprocessor saved to {filepath}")
    
    @classmethod
    def load(cls, filepath):
        """Load preprocessor from disk."""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        
        preprocessor = cls()
        preprocessor.scaler = data['scaler']
        preprocessor.imputer = data['imputer']
        preprocessor.is_fitted = data['is_fitted']
        
        return preprocessor


def clean_data(df):
    """
    Clean the raw dataset.
    
    Args:
        df: Raw dataframe
        
    Returns:
        Cleaned dataframe
    """
    df_clean = df.copy()
    
    # Remove source column if present (not needed for modeling)
    if 'source' in df_clean.columns:
        df_clean = df_clean.drop('source', axis=1)
    
    # Convert target to binary (0 = no disease, 1 = disease present)
    # Original: 0 = no disease, 1-4 = disease
    if 'target' in df_clean.columns:
        df_clean['target'] = (df_clean['target'] > 0).astype(int)
    
    # Handle missing values - replace with NaN for easier handling
    df_clean = df_clean.replace([-9.0, -9, '?'], np.nan)
    
    # Ensure numeric columns are numeric
    if 'target' in df_clean.columns:
        numeric_cols = df_clean.columns.drop('target')
    else:
        numeric_cols = df_clean.columns
    for col in numeric_cols:
        df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    
    return df_clean


def prepare_features_target(df):
    """
    Separate features and target variable.
    
    Args:
        df: Dataframe with features and target
        
    Returns:
        X: Feature matrix
        y: Target vector
    """
    if 'target' not in df.columns:
        raise ValueError("Target column 'target' not found in dataframe")
    
    X = df.drop('target', axis=1)
    y = df['target']
    
    return X, y


def get_feature_names():
    """Get list of feature names."""
    return [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal"
    ]

