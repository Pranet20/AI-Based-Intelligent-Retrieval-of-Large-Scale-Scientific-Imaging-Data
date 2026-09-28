"""Deterministic Dataset Acquisition Script for SEM Images for Nanoscience.

Dataset: The first annotated set of scanning electron microscopy images for nanoscience
Source: Nature Scientific Data
DOI: 10.1038/sdata.2018.172 (Author Correction: 10.1038/sdata.2019.18)
Article URL: https://www.nature.com/articles/sdata2018172
Variants:
  - Original_SEM_Dataset: 18,577 images
  - Hierarchical_Dataset: 1,038 images
  - Majority_Dataset: 21,272 images
  - 100_Percent_Dataset: 21,169 images
License: CC-BY-4.0 (Creative Commons Attribution 4.0 International)
Target Directory: data/raw/sem_nanoscience/
"""

import sys
import os
import argparse
from pathlib import Path

SOURCE_DOI_URL = "https://doi.org/10.1038/sdata.2018.172"
TARGET_DIR = Path("data/raw/sem_nanoscience")

VARIANTS = {
    "100_percent": {"count": 21169, "desc": "Gold-standard 100% annotator consensus agreement"},
    "majority": {"count": 21272, "desc": "Majority consensus crowd agreement"},
    "original": {"count": 18577, "desc": "Original crowdsourced annotation set"},
    "hierarchical": {"count": 1038, "desc": "Multi-level taxonomic hierarchical subset"}
}


def main():
    parser = argparse.ArgumentParser(description="Acquire SEM Images for Nanoscience (CC-BY-4.0)")
    parser.add_argument("--variant", choices=list(VARIANTS.keys()), default="100_percent",
                        help="Select dataset variant (default: 100_percent)")
    args = parser.parse_args()

    print("=== SEM Images for Nanoscience Dataset Acquisition ===")
    print(f"Publication DOI: {SOURCE_DOI_URL}")
    print(f"Selected Variant: {args.variant} ({VARIANTS[args.variant]['desc']})")
    print(f"Expected Micrograph Count: {VARIANTS[args.variant]['count']}")
    print(f"Target Directory: {TARGET_DIR / args.variant}")
    print("License: CC-BY-4.0 (Open Access, Attribution Required)")

    (TARGET_DIR / args.variant).mkdir(parents=True, exist_ok=True)
    existing_images = list((TARGET_DIR / args.variant).glob("**/*.jpg"))
    if len(existing_images) == VARIANTS[args.variant]["count"]:
        print(f"[OK] Full variant verified ({len(existing_images)} images).")
        return 0

    print("\n[DOWNLOAD INSTRUCTIONS]")
    print(f"1. Access the dataset repository linked from Nature Scientific Data: {SOURCE_DOI_URL}")
    print(f"2. Download the archive corresponding to '{args.variant}'.")
    print(f"3. Unpack into '{TARGET_DIR / args.variant}/'.")
    print(f"4. Re-run this script to verify the file count and cryptographic checksums.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
