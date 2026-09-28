"""Deterministic Dataset Acquisition Script for Carinthia SEM Defect Dataset.

Dataset: Carinthia Scanning Electron Microscopy Defect Dataset
Source: Zenodo
DOI: 10.5281/zenodo.10715190
URL: https://zenodo.org/records/10715190
Expected Archive: '10715190.zip'
Expected Physical Files: 4,591 PNG images + carinthia.csv
Target Directory: data/raw/carinthia/
License: UNKNOWN_VERIFY_SOURCE_TERMS (Direct acquisition from Zenodo required)
"""

import sys
import os
import zipfile
from pathlib import Path

ZENODO_RECORD_URL = "https://zenodo.org/records/10715190"
TARGET_DIR = Path("data/raw/carinthia")
ARCHIVE_NAME = "10715190.zip"


def verify_or_extract():
    print(f"=== Carinthia Defect Dataset Acquisition & Verification ===")
    print(f"Source: {ZENODO_RECORD_URL}")
    print(f"Target Directory: {TARGET_DIR}")
    
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if physical files already unpacked
    png_files = list(TARGET_DIR.glob("**/*.png"))
    if len(png_files) == 4591:
        print(f"[OK] 4,591 physical PNG images verified in {TARGET_DIR}.")
        return 0
    elif len(png_files) > 0:
        print(f"[WARN] Found {len(png_files)} PNG images (expected 4,591).")
        return 1

    # Check for archive in workspace root or target dir
    archive_paths = [
        Path(ARCHIVE_NAME),
        Path("data") / ARCHIVE_NAME,
        TARGET_DIR / ARCHIVE_NAME
    ]
    
    found_archive = None
    for p in archive_paths:
        if p.exists():
            found_archive = p
            break
            
    if found_archive:
        print(f"[INFO] Found archive at {found_archive}. Extracting to {TARGET_DIR}...")
        with zipfile.ZipFile(found_archive, 'r') as z:
            z.extractall(TARGET_DIR)
        png_files = list(TARGET_DIR.glob("**/*.png"))
        print(f"[INFO] Extracted {len(png_files)} PNG images.")
        if len(png_files) == 4591:
            print("[SUCCESS] Carinthia acquisition verified (4,591/4,591 physical images).")
            return 0
        else:
            print(f"[WARN] Expected 4,591 images, found {len(png_files)}.")
            return 1
    else:
        print("\n[ACTION REQUIRED] Automated redistribution of raw Carinthia imagery is restricted.")
        print(f"1. Please visit the official Zenodo deposition record: {ZENODO_RECORD_URL}")
        print(f"2. Download '{ARCHIVE_NAME}' (approx. 130 MB).")
        print(f"3. Place '{ARCHIVE_NAME}' in the project root or in '{TARGET_DIR}/'.")
        print(f"4. Re-run: python scripts/data/download_carinthia.py\n")
        return 2


if __name__ == "__main__":
    sys.exit(verify_or_extract())
