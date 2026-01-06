"""
Data download script for Heart Disease UCI Dataset.

This script downloads the dataset from UCI ML Repository or uses local data.
"""

import pandas as pd
from pathlib import Path

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
HEART_DISEASE_DIR = PROJECT_ROOT / "heart+disease"

# Column names for the 14 features used in the dataset
COLUMN_NAMES = [
    "age",           # 1. age
    "sex",           # 2. sex (1=male, 0=female)
    "cp",            # 3. chest pain type (1-4)
    "trestbps",      # 4. resting blood pressure
    "chol",          # 5. serum cholesterol
    "fbs",           # 6. fasting blood sugar > 120 (1=true, 0=false)
    "restecg",       # 7. resting electrocardiographic results
    "thalach",       # 8. maximum heart rate achieved
    "exang",         # 9. exercise induced angina (1=yes, 0=no)
    "oldpeak",       # 10. ST depression induced by exercise
    "slope",         # 11. slope of peak exercise ST segment
    "ca",            # 12. number of major vessels colored by flourosopy
    "thal",          # 13. thalassemia (3=normal, 6=fixed, 7=reversible)
    "target"         # 14. target variable (0=no disease, 1-4=disease)
]


def download_from_uci():
    """
    Download dataset from UCI ML Repository.
    Note: This is a placeholder - actual download would require network access.
    """
    print("Note: For actual download, use the UCI ML Repository URL:")
    print("https://archive.ics.uci.edu/ml/datasets/heart+disease")
    print("\nUsing local data files instead...")


def load_local_data():
    """Load data from local heart+disease directory."""
    data_files = {
        "cleveland": HEART_DISEASE_DIR / "processed.cleveland.data",
        "hungarian": HEART_DISEASE_DIR / "processed.hungarian.data",
        "switzerland": HEART_DISEASE_DIR / "processed.switzerland.data",
        "va": HEART_DISEASE_DIR / "processed.va.data"
    }
    
    all_dataframes = []

    for name, file_path in data_files.items():
        if file_path.exists():
            print(f"Loading {name} data from {file_path}...")
            try:
                df = pd.read_csv(
                    file_path,
                    header=None,
                    names=COLUMN_NAMES,
                    na_values=["?", -9.0, -9]
                )
                df["source"] = name
                all_dataframes.append(df)
                print(f"  Loaded {len(df)} rows")
            except Exception as e:
                print(f"  Error loading {name}: {e}")
        else:
            print(f"  File not found: {file_path}")
    
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"\nTotal combined dataset: {len(combined_df)} rows, {len(combined_df.columns)} columns")
        return combined_df
    else:
        raise FileNotFoundError("No data files found!")


def save_raw_data(df):
    """Save raw data to data/raw directory."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_RAW_DIR / "heart_disease_raw.csv"
    df.to_csv(output_path, index=False)
    print(f"\nRaw data saved to: {output_path}")
    return output_path


def main():
    """Main function to download and save data."""
    print("=" * 60)
    print("Heart Disease Dataset Download Script")
    print("=" * 60)
    
    # Try to download from UCI (placeholder)
    download_from_uci()
    
    # Load local data
    df = load_local_data()
    
    # Save raw data
    save_raw_data(df)
    
    print("\n" + "=" * 60)
    print("Data download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
