"""Database Restore Utility with Checksum Verification.

Verifies backup integrity against manifest prior to restoring.
Creates a pre-restore rollback backup.
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))

from app.core.config import settings


def restore_database(backup_manifest_path: Path):
    if not backup_manifest_path.exists():
        print(f"[ERROR] Manifest not found: {backup_manifest_path}")
        return False

    with open(backup_manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    backup_dir = backup_manifest_path.parent
    backup_file = backup_dir / manifest["backup_file"]

    if not backup_file.exists():
        print(f"[ERROR] Backup file missing: {backup_file}")
        return False

    # Checksum verification
    print("[1/3] Verifying backup checksum...")
    with open(backup_file, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()

    if actual_hash != manifest["sha256"]:
        print(f"[FATAL] Checksum mismatch! Expected: {manifest['sha256']}, Got: {actual_hash}")
        return False
    print("  Checksum verified: Integrity intact.")

    db_url = settings.DATABASE_URL
    print(f"[2/3] Preparing target database ({manifest['backup_type']})...")

    if manifest["backup_type"] == "sqlite":
        sqlite_path = db_url.replace("sqlite:///", "")
        target_file = Path(sqlite_path)
        if not target_file.is_absolute():
            target_file = PROJECT_ROOT / "platform" / "storage" / "scidata_platform.db"

        # Create pre-restore safety snapshot
        if target_file.exists():
            pre_restore = target_file.with_name(f"{target_file.name}.pre_restore_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(target_file, pre_restore)
            print(f"  Safety snapshot created: {pre_restore.name}")

        shutil.copy2(backup_file, target_file)
        print(f"[3/3] SQLite database restored to: {target_file}")
        print("[SUCCESS] Restore operation completed cleanly.")
        return True

    elif manifest["backup_type"] == "postgresql":
        # psql restore
        cmd = ["psql", db_url, "-f", str(backup_file)]
        try:
            subprocess.run(cmd, check=True)
            print("[3/3] PostgreSQL database restored from dump.")
            print("[SUCCESS] Restore operation completed cleanly.")
            return True
        except Exception as e:
            print(f"[ERROR] Restore failed: {e}")
            return False

    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Restore platform database from backup")
    parser.add_argument("manifest", type=str, help="Path to backup manifest JSON")
    args = parser.parse_args()
    success = restore_database(Path(args.manifest))
    sys.exit(0 if success else 1)
