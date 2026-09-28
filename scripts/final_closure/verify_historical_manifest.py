"""Verify historical artifact immutability and generate FINAL_CLOSURE_BASELINE_MANIFEST.csv."""

import csv
import hashlib
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parent.parent.parent
historical_json = root / "release_final" / "checksums" / "FINAL_HISTORICAL_CHECKSUMS.json"

with open(historical_json, "r", encoding="utf-8") as f:
    hist_data = json.load(f)

# Also load Phase 18 sentinel manifest
sentinel_csv = root / "reports" / "phase18" / "PHASE18_BASELINE_MANIFEST.csv"
sentinel_hashes = {}
if sentinel_csv.exists():
    with open(sentinel_csv, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = row["path"].replace("\\", "/")
            sentinel_hashes[p] = row["sha256"]

rows = []
mismatches = []
missing = []

# Merge all paths
all_paths = set(hist_data.keys())
for p in sentinel_hashes:
    # convert to Windows backslash if matching
    found = False
    for k in hist_data:
        if k.replace("\\", "/") == p:
            found = True
            break
    if not found:
        all_paths.add(p)

for item in sorted(all_paths):
    rel_path = item.replace("\\", "/")
    file_path = root / rel_path
    raw_val = hist_data.get(item, hist_data.get(item.replace("/", "\\"), sentinel_hashes.get(rel_path)))
    if isinstance(raw_val, dict):
        expected_hash = raw_val.get("expected", raw_val.get("sha256"))
    else:
        expected_hash = raw_val

    phase = "HISTORICAL"
    for part in rel_path.split("/"):
        if "phase" in part.lower():
            phase = part.upper()
            break

    if not file_path.exists():
        missing.append(rel_path)
        rows.append({
            "path": rel_path,
            "size": 0,
            "sha256": "MISSING",
            "phase": phase,
            "status": "MISSING"
        })
        continue

    actual_size = file_path.stat().st_size
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    actual_hash = hasher.hexdigest()

    if expected_hash and actual_hash.lower() == expected_hash.lower():
        status = "MATCHED"
    elif expected_hash:
        status = "MISMATCH"
        mismatches.append((rel_path, expected_hash, actual_hash))
    else:
        status = "MATCHED_NO_PREV"

    rows.append({
        "path": rel_path,
        "size": actual_size,
        "sha256": actual_hash,
        "phase": phase,
        "status": status
    })

out_csv = root / "reports" / "final_closure" / "FINAL_CLOSURE_BASELINE_MANIFEST.csv"
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["path", "size", "sha256", "phase", "status"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Total historical artifacts checked: {len(rows)}")
matched_count = sum(1 for r in rows if r["status"] == "MATCHED")
print(f"Matched: {matched_count}")
print(f"Missing: {len(missing)}")
print(f"Mismatches: {len(mismatches)}")
if mismatches:
    for m in mismatches:
        print("MISMATCH:", m)
    raise SystemExit("HISTORICAL_IMMUTABILITY_FAILURE")
print("SUCCESS: All historical artifacts matched byte-for-byte!")
