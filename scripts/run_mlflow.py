#!/usr/bin/env python3
"""
Helper script to run MLflow training and start UI.

This script checks for MLflow installation, runs training, and provides
instructions for starting the MLflow UI.
"""

import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def check_mlflow():
    """Check if MLflow is installed."""
    try:
        import mlflow
        print(f"✅ MLflow is installed (version: {mlflow.__version__})")
        return True
    except ImportError:
        print("❌ MLflow is not installed")
        print("\nPlease install MLflow first:")
        print("  pip install mlflow matplotlib seaborn")
        print("\nOr using conda:")
        print("  conda install -c conda-forge mlflow")
        return False


def check_data():
    """Check if processed data exists."""
    data_path = PROJECT_ROOT / "data" / "processed" / "heart_disease_processed.csv"
    if data_path.exists():
        print("✅ Processed data found")
        return True
    else:
        print("❌ Processed data not found")
        print("\nPlease run preprocessing first:")
        print("  python scripts/preprocess_data.py")
        return False


def run_training():
    """Run MLflow training."""
    print("\n" + "=" * 60)
    print("Running MLflow Training")
    print("=" * 60)
    
    train_script = PROJECT_ROOT / "src" / "models" / "train_with_mlflow.py"
    
    try:
        result = subprocess.run(
            [sys.executable, str(train_script)],
            cwd=str(PROJECT_ROOT),
            check=True
        )
        print("\n✅ Training completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed with error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error running training: {e}")
        return False


def start_ui():
    """Start MLflow UI."""
    mlruns_dir = PROJECT_ROOT / "mlruns"
    
    if not mlruns_dir.exists():
        print("❌ No MLflow runs found. Please run training first.")
        return False
    
    print("\n" + "=" * 60)
    print("Starting MLflow UI")
    print("=" * 60)
    print(f"\nMLflow UI will be available at: http://localhost:5000")
    print(f"Tracking URI: file://{mlruns_dir.absolute()}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        subprocess.run(
            [
                sys.executable, "-m", "mlflow", "ui",
                "--backend-store-uri", f"file://{mlruns_dir.absolute()}",
                "--port", "5000"
            ],
            cwd=str(PROJECT_ROOT)
        )
    except KeyboardInterrupt:
        print("\n\nMLflow UI stopped.")
    except Exception as e:
        print(f"\n❌ Error starting MLflow UI: {e}")
        print("\nYou can start it manually with:")
        print(f"  mlflow ui --backend-store-uri file://{mlruns_dir.absolute()} --port 5000")


def main():
    """Main function."""
    print("=" * 60)
    print("MLflow Training and UI Helper")
    print("=" * 60)
    
    # Check prerequisites
    if not check_mlflow():
        sys.exit(1)
    
    if not check_data():
        sys.exit(1)
    
    # Ask user what to do
    print("\n" + "=" * 60)
    print("What would you like to do?")
    print("=" * 60)
    print("1. Run MLflow training only")
    print("2. Start MLflow UI only (if training already done)")
    print("3. Run training and start UI")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        run_training()
    elif choice == "2":
        start_ui()
    elif choice == "3":
        if run_training():
            print("\n" + "=" * 60)
            input("Press Enter to start MLflow UI...")
            start_ui()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice. Exiting...")


if __name__ == "__main__":
    main()


