"""Deterministic Dataset Acquisition Script for atomagined HAADF-STEM Benchmark.

Dataset: atomagined
Source: Materials Data Facility / GitHub
DOI: 10.18126/szeq-yde5
URL: https://github.com/MaterialEyes/atomagined
Expected Micrographs: ~16,000 synthetic HAADF-STEM images + HDF5 simulation parameters
Target Directory: data/raw/atomagined/
License: Repository MIT; MDF dataset terms require confirmation
"""

import sys
from pathlib import Path

MDF_URL = "https://doi.org/10.18126/szeq-yde5"
GITHUB_URL = "https://github.com/MaterialEyes/atomagined"
TARGET_DIR = Path("data/raw/atomagined")


def main():
    print("=== atomagined HAADF-STEM Benchmark Acquisition ===")
    print(f"Materials Data Facility DOI: {MDF_URL}")
    print(f"Code Repository: {GITHUB_URL}")
    print(f"Target Directory: {TARGET_DIR}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    h5_files = list(TARGET_DIR.glob("**/*.h5")) + list(TARGET_DIR.glob("**/*.hdf5"))
    if h5_files:
        print(f"[OK] Found {len(h5_files)} HDF5 simulation benchmark files.")
        return 0

    print("\n[ACQUISITION PROCEDURE]")
    print(f"1. Access the dataset on the Materials Data Facility via Globus or HTTP: {MDF_URL}")
    print("2. Download the simulation HDF5 packages and crystal structure metadata.")
    print(f"3. Place files in '{TARGET_DIR}/'.")
    print("4. Validate dataset schema using: python scripts/validation/validate_datasets.py --dataset atomagined")
    return 0


if __name__ == "__main__":
    sys.exit(main())
