"""Dataset Access and Authorization Guide for MicroAl-Dataset.

Dataset: MicroAl-Dataset
Source: GitHub (neulmc/MicroAl-Dataset)
URL: https://github.com/neulmc/MicroAl-Dataset
Target Directory: data/raw/microal/
License: ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION
Redistribution Status: RESTRICTED — PROHIBITED FROM THIRD-PARTY DISTRIBUTION
"""

import sys
from pathlib import Path

GITHUB_URL = "https://github.com/neulmc/MicroAl-Dataset"
TARGET_DIR = Path("data/raw/microal")


def main():
    print("=== MicroAl Multi-Modal Aluminum Dataset Access Guide ===")
    print(f"Repository: {GITHUB_URL}")
    print(f"Target Directory: {TARGET_DIR}")
    print("RESTRICTION NOTICE: This dataset is restricted to academic use.")
    print("Redistribution by third parties is strictly prohibited.\n")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    images = list(TARGET_DIR.glob("**/*.tif")) + list(TARGET_DIR.glob("**/*.png")) + list(TARGET_DIR.glob("**/*.jpg"))
    if len(images) >= 800:
        print(f"[OK] Found {len(images)} multi-modal micrographs in {TARGET_DIR}.")
        return 0

    print("[ACCESS INSTRUCTIONS]")
    print(f"1. Navigate to: {GITHUB_URL}")
    print("2. Review contributor access constraints in the repository documentation.")
    print("3. Contact the original dataset authors to request authorization.")
    print(f"4. Once authorized, place the micrographs in '{TARGET_DIR}/'.")
    print("5. Run: python scripts/validation/validate_datasets.py --dataset microal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
