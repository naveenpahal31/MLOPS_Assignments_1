"""
Data preprocessing script.

Cleans and preprocesses the raw heart disease dataset.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

import pandas as pd
from src.data.preprocessing import clean_data, prepare_features_target

# Define paths
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main():
    """Main preprocessing function."""
    print("=" * 60)
    print("Heart Disease Data Preprocessing")
    print("=" * 60)

    # Load raw data
    raw_data_path = DATA_RAW_DIR / "heart_disease_raw.csv"

    if not raw_data_path.exists():
        print(f"Error: Raw data not found at {raw_data_path}")
        print("Please run download_data.py first!")
        return

    print(f"\nLoading raw data from {raw_data_path}...")
    df_raw = pd.read_csv(raw_data_path)
    print(f"Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")

    # Clean data
    print("\nCleaning data...")
    df_clean = clean_data(df_raw)
    print(f"After cleaning: {len(df_clean)} rows, {len(df_clean.columns)} columns")

    # Check for missing values
    missing = df_clean.isnull().sum()
    if missing.sum() > 0:
        print("\nMissing values per column:")
        print(missing[missing > 0])
    else:
        print("\nNo missing values found!")

    # Separate features and target
    print("\nPreparing features and target...")
    X, y = prepare_features_target(df_clean)
    print(f"Features shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Target distribution:\n{y.value_counts()}")

    # Save processed data
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Save full dataset
    df_clean.to_csv(DATA_PROCESSED_DIR / "heart_disease_processed.csv", index=False)
    print(f"\nProcessed data saved to: {DATA_PROCESSED_DIR / 'heart_disease_processed.csv'}")

    # Save features and target separately
    X.to_csv(DATA_PROCESSED_DIR / "X_features.csv", index=False)
    y.to_csv(DATA_PROCESSED_DIR / "y_target.csv", index=False)
    print(f"Features saved to: {DATA_PROCESSED_DIR / 'X_features.csv'}")
    print(f"Target saved to: {DATA_PROCESSED_DIR / 'y_target.csv'}")

    print("\n" + "=" * 60)
    print("Data preprocessing complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
