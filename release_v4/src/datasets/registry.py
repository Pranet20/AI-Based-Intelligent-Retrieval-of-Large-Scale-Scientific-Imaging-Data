"""Machine-readable dataset registry and metadata validator."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field
import yaml


class DatasetRegistryEntry(BaseModel):
    """Specification of an enrolled dataset in the research platform."""

    model_config = ConfigDict(extra="allow")

    dataset_id: str
    name: str
    source_url: str
    doi: str
    version: str
    license: str = "UNKNOWN_VERIFY_SOURCE_TERMS"
    license_status: str = "UNKNOWN_VERIFY_SOURCE_TERMS"
    repository_license: Optional[str] = None
    dataset_license: str = "UNKNOWN_VERIFY_SOURCE_TERMS"
    commercial_use: str = "UNKNOWN"
    redistribution_allowed: str = "UNKNOWN"
    access_notes: str
    approximate_image_count: int
    modality: str
    domain: str
    role: str
    metadata_available: bool
    labels_available: bool
    retrieval_labels_available: bool
    intended_use: str
    citation: str
    archive_size_if_known: Optional[str] = None
    local_path: str
    enabled: bool = True
    acquisition_status: str = "NOT_YET_DOWNLOADED"
    dataset_family: Optional[str] = None
    dataset_variant: Optional[str] = None
    variants_available: Optional[Dict[str, Any]] = None


class DatasetRegistry:
    """Loads and queries the central dataset registry."""

    def __init__(self, config_path: str | Path = "configs/datasets.yaml") -> None:
        self.config_path = Path(config_path)
        self.entries: Dict[str, DatasetRegistryEntry] = {}
        self.load()

    def load(self) -> None:
        """Load datasets from YAML configuration."""
        if not self.config_path.is_file():
            raise FileNotFoundError(f"Dataset registry config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        raw_datasets = raw.get("datasets", {})
        for ds_id, data in raw_datasets.items():
            self.entries[ds_id] = DatasetRegistryEntry(**data)

    def get(self, dataset_id: str) -> DatasetRegistryEntry:
        if dataset_id not in self.entries:
            raise KeyError(f"Dataset ID '{dataset_id}' not found in registry.")
        return self.entries[dataset_id]

    def list_all(self, enabled_only: bool = False) -> List[DatasetRegistryEntry]:
        if enabled_only:
            return [e for e in self.entries.values() if e.enabled]
        return list(self.entries.values())

    def validate_all(self) -> List[str]:
        """Validate consistency of all registered datasets. Returns list of notices/issues."""
        issues = []
        for ds_id, entry in self.entries.items():
            if "UNKNOWN" in entry.license_status:
                issues.append(f"[{ds_id}] License status is '{entry.license_status}' - source terms require verification.")
            if not entry.source_url:
                issues.append(f"[{ds_id}] Missing source_url.")
            if not entry.doi:
                issues.append(f"[{ds_id}] Missing DOI.")
        return issues
