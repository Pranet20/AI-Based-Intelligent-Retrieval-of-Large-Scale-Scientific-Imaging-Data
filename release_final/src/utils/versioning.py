"""Dataset versioning and provenance tracking (dataset_versions.json)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.datasets.registry import DatasetRegistryEntry
from src.utils.reproducibility import compute_file_sha256


class DatasetVersionManager:
    """Manages data/manifests/dataset_versions.json for scientific tracking."""

    def __init__(self, versions_path: str | Path = "data/manifests/dataset_versions.json") -> None:
        self.versions_path = Path(versions_path)
        self.versions_path.parent.mkdir(parents=True, exist_ok=True)
        self.data: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        if self.versions_path.is_file():
            try:
                with open(self.versions_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save(self) -> None:
        with open(self.versions_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def record_version(
        self,
        entry: DatasetRegistryEntry,
        manifest_path: str | Path,
        file_count: int,
        total_size_bytes: int,
        source_checksum: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record version stamp for a dataset based on its manifest and source."""
        mp = Path(manifest_path)
        manifest_hash = compute_file_sha256(mp) if mp.is_file() else "MISSING"

        record = {
            "dataset_id": entry.dataset_id,
            "name": entry.name,
            "source": entry.source_url,
            "doi": entry.doi,
            "version": entry.version,
            "recorded_timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "file_count": file_count,
            "total_size_bytes": total_size_bytes,
            "manifest_file": str(mp.name),
            "manifest_hash": manifest_hash,
            "source_checksum_if_available": source_checksum or "NOT_AVAILABLE",
        }

        self.data[entry.dataset_id] = record
        self._save()
        return record

    def get_version(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        return self.data.get(dataset_id)
