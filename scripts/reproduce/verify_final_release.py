#!/usr/bin/env python3
"""
Verify Release Final Checksums (Read-Only)
===========================================
Reads release_final/checksums/SHA256SUMS.txt and verifies the SHA-256
hash of each file on disk under release_final/ without modifying any files.
"""

import sys
import hashlib
from pathlib import Path


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    root = Path(__file__).resolve().parent.parent.parent
    release_dir = root / "release_final"
    checksum_file = release_dir / "checksums" / "SHA256SUMS.txt"

    if not checksum_file.is_file():
        print(f"ERROR: Checksum file not found: {checksum_file}")
        sys.exit(1)

    print(f"Verifying release_final against {checksum_file}...")

    total = 0
    passed = 0
    missing = 0
    mismatched = 0

    with open(checksum_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(maxsplit=1)
            if len(parts) != 2:
                print(f"Line {line_num}: invalid format: {line}")
                continue

            expected_hash, rel_path = parts[0], parts[1].strip()
            file_path = release_dir / rel_path
            total += 1

            if not file_path.is_file():
                print(f"MISSING: {rel_path}")
                missing += 1
                continue

            actual_hash = compute_sha256(file_path)
            if actual_hash == expected_hash:
                passed += 1
            else:
                print(f"MISMATCH: {rel_path} (expected {expected_hash[:10]}..., got {actual_hash[:10]}...)")
                mismatched += 1

    print("-" * 60)
    print(f"Total checked: {total}")
    print(f"Passed:        {passed}")
    print(f"Missing:       {missing}")
    print(f"Mismatched:    {mismatched}")
    print("-" * 60)

    if missing == 0 and mismatched == 0 and total > 0:
        print("PASS: All release files verified successfully.")
        sys.exit(0)
    else:
        print("FAIL: Checksum verification failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
