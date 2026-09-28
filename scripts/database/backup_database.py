"""Database Backup Utility with Checksum Verification.

Supports SQLite and PostgreSQL backups.
Produces timestamped backup archive and SHA-256 integrity manifest.
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

# Add project root and backend to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))

from app.core.config import settings


def backup_database(output_dir: Path = None):
    if output_dir is None:
        output_dir = PROJECT_ROOT / "platform" / "storage" / "backups"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_url = settings.DATABASE_URL

    print(f"[{timestamp}] Initiating Database Backup...")
    print(f"Target URL: {db_url.split('@')[-1] if '@' in db_url else db_url}")

    if db_url.startswith("sqlite"):
        sqlite_path = db_url.replace("sqlite:///", "")
        src_file = Path(sqlite_path)
        if not src_file.is_absolute():
            src_file = PROJECT_ROOT / "platform" / "backend" / src_file
            if not src_file.exists():
                src_file = PROJECT_ROOT / "platform" / "storage" / "scidata_platform.db"

        if not src_file.exists():
            print(f"[ERROR] Source SQLite file not found: {src_file}")
            return None

        dst_file = output_dir / f"db_backup_{timestamp}.sqlite"
        shutil.copy2(src_file, dst_file)
        
        # Calculate SHA-256
        with open(dst_file, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        manifest = {
            "backup_type": "sqlite",
            "timestamp": timestamp,
            "source_file": str(src_file),
            "backup_file": str(dst_file.name),
            "size_bytes": dst_file.stat().st_size,
            "sha256": file_hash,
            "status": "COMPLETED"
        }

    else:
        # PostgreSQL pg_dump
        dst_file = output_dir / f"pg_backup_{timestamp}.sql"
        cmd = ["pg_dump", db_url, "-f", str(dst_file)]
        try:
            subprocess.run(cmd, check=True)
            with open(dst_file, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            manifest = {
                "backup_type": "postgresql",
                "timestamp": timestamp,
                "backup_file": str(dst_file.name),
                "size_bytes": dst_file.stat().st_size,
                "sha256": file_hash,
                "status": "COMPLETED"
            }
        except Exception as e:
            print(f"[ERROR] pg_dump failed: {e}")
            return None

    manifest_path = output_dir / f"backup_manifest_{timestamp}.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"[SUCCESS] Database backup saved: {dst_file}")
    print(f"[SUCCESS] Manifest generated: {manifest_path} (SHA-256: {file_hash[:16]}...)")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Backup platform database")
    parser.add_argument("--out", type=str, default=None, help="Output directory")
    args = parser.parse_args()
    backup_database(Path(args.out) if args.out else None)
