"""
Reproduce training script.

This script ensures full reproducibility by:
1. Setting random seeds
2. Using the same data preprocessing pipeline
3. Training models with identical parameters
4. Saving models and artifacts

Run this script to reproduce the exact same model training results.
"""

import sys
from pathlib import Path
import random
import numpy as np

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))

# Set random seeds for reproducibility
RANDOM_SEED = 42


def set_random_seeds(seed=RANDOM_SEED):
    """Set all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)

    # Set sklearn random state (will be used in training scripts)
    import os
    os.environ['PYTHONHASHSEED'] = str(seed)

    print(f"Random seeds set to: {seed}")


def main():
    """Main function to reproduce training."""
    print("=" * 60)
    print("Reproduce Training - Full Reproducibility")
    print("=" * 60)

    # Set random seeds
    set_random_seeds(RANDOM_SEED)

    # Import after setting seeds
    from src.models.train import main as train_main

    print("\nStarting model training with fixed random seed...")
    print(f"Random seed: {RANDOM_SEED}")
    print("-" * 60)

    # Run training
    results, preprocessor, summary = train_main()

    print("\n" + "=" * 60)
    print("Training Reproduced Successfully!")
    print("=" * 60)
    print(f"\nModels saved to: {PROJECT_ROOT / 'models'}")
    print(f"\nTo verify reproducibility, run this script multiple times")
    print("and compare the saved model files and metrics.")


if __name__ == "__main__":
    main()
