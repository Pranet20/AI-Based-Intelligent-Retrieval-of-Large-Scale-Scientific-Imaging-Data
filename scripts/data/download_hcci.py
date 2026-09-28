"""Deterministic Dataset Acquisition Script for HCCI SEM Dataset.

Dataset: High-Chromium Cast Iron SEM Dataset
Source: Zenodo
DOI: 10.5281/zenodo.21931379
URL: https://zenodo.org/records/21931379
Expected Archive: 'HCCI Dataset .zip'
Expected Physical Files: 774 TIFF microscopy images + Metadata_All_Samples.xlsx + Classes.txt
Target Directory: data/raw/hcci/
License: UNKNOWN_VERIFY_SOURCE_TERMS (Direct acquisition from Zenodo required)
"""

import sys
import os
import zipfile
from pathlib import Path

ZENODO_RECORD_URL = "https://zenodo.org/records/21931379"
TARGET_DIR = Path("data/raw/hcci")
ARCHIVE_NAME = "HCCI Dataset .zip"


def verify_or_extract():
    print(f"=== HCCI Dataset Acquisition & Verification ===")
    print(f"Source: {ZENODO_RECORD_URL}")
    print(f"Target Directory: {TARGET_DIR}")
    
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if physical files already unpacked
    tiff_files = list(TARGET_DIR.glob("**/*.tif")) + list(TARGET_DIR.glob("**/*.tiff"))
    if len(tiff_files) == 774:
        print(f"[OK] 774 physical TIFF images verified in {TARGET_DIR}.")
        return 0
    elif len(tiff_files) > 0:
        print(f"[WARN] Found {len(tiff_files)} TIFF images (expected 774).")
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
        tiff_files = list(TARGET_DIR.glob("**/*.tif")) + list(TARGET_DIR.glob("**/*.tiff"))
        print(f"[INFO] Extracted {len(tiff_files)} TIFF images.")
        if len(tiff_files) == 774:
            print("[SUCCESS] HCCI acquisition verified (774/774 physical images).")
            return 0
        else:
            print(f"[WARN] Expected 774 images, found {len(tiff_files)}.")
            return 1
    else:
        print("\n[ACTION REQUIRED] Automated redistribution of raw HCCI imagery is restricted.")
        print(f"1. Please visit the official Zenodo deposition record: {ZENODO_RECORD_URL}")
        print(f"2. Download '{ARCHIVE_NAME}' (approx. 4.0 GB).")
        print(f"3. Place '{ARCHIVE_NAME}' in the project root or in '{TARGET_DIR}/'.")
        print(f"4. Re-run: python scripts/data/download_hcci.py\n")
        return 2


if __name__ == "__main__":
    sys.exit(verify_or_extract())
