"""Deterministic Dataset Acquisition Script for cigRockSEM Dataset.

Dataset: cigRockSEM
Source: Zenodo
DOI: 10.5281/zenodo.14988631
URL: https://zenodo.org/records/14988631
Expected Physical Files: ~1,500 geological SEM micrographs
Target Directory: data/raw/cigrocksem/
License: UNKNOWN_VERIFY_SOURCE_TERMS
"""

import sys
from pathlib import Path

ZENODO_URL = "https://zenodo.org/records/14988631"
TARGET_DIR = Path("data/raw/cigrocksem")


def main():
    print("=== cigRockSEM Geological Microstructure Acquisition ===")
    print(f"Zenodo Deposition Record: {ZENODO_URL}")
    print(f"Target Directory: {TARGET_DIR}")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    images = list(TARGET_DIR.glob("**/*.tif")) + list(TARGET_DIR.glob("**/*.png"))
    if len(images) >= 1500:
        print(f"[OK] Found {len(images)} images in {TARGET_DIR}.")
        return 0

    print("\n[ACQUISITION PROCEDURE]")
    print(f"1. Open Zenodo record: {ZENODO_URL}")
    print("2. Download the rock microstructure image archive.")
    print(f"3. Unpack into '{TARGET_DIR}/'.")
    print("4. Validate using: python scripts/validation/validate_datasets.py --dataset cigrocksem")
    return 0


if __name__ == "__main__":
    sys.exit(main())
