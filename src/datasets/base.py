"""Abstract Base Dataset Adapter for scientific image ingestion."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

from src.datasets.registry import DatasetRegistryEntry
from src.ingestion.manifest import ManifestRecord
from src.ingestion.reader import ScientificImageReader, SUPPORTED_EXTENSIONS
from src.utils.logging import AuditErrorCollector, get_logger


class BaseDatasetAdapter(ABC):
    """Abstract base class defining standardized ingestion protocol for any scientific dataset."""

    def __init__(
        self,
        entry: DatasetRegistryEntry,
        root_dir: Optional[str | Path] = None,
        error_collector: Optional[AuditErrorCollector] = None,
    ) -> None:
        self.entry = entry
        self.dataset_id = entry.dataset_id
        self.root_dir = Path(root_dir) if root_dir else Path(entry.local_path)
        self.error_collector = error_collector or AuditErrorCollector()
        self.logger = get_logger(f"adapter.{self.dataset_id}")

    @abstractmethod
    def locate_files(self) -> List[Path]:
        """Locate raw image files in the dataset's directory structure."""
        pass

    @abstractmethod
    def read_labels(self) -> Dict[str, Any]:
        """Extract available ground truth labels from dataset-specific files (e.g. CSVs, annotations)."""
        pass

    @abstractmethod
    def read_metadata(self) -> Dict[str, Any]:
        """Extract raw acquisition metadata from spreadsheets, headers, or metadata files."""
        pass

    def discover_images(self) -> List[Path]:
        """Discover valid and supported image files under the dataset directory."""
        if not self.root_dir.exists():
            self.logger.warning("Dataset root directory does not exist: %s", self.root_dir)
            return []

        all_candidates = self.locate_files()
        supported = [p for p in all_candidates if p.suffix.lower() in SUPPORTED_EXTENSIONS]
        unsupported = [p for p in all_candidates if p.suffix.lower() not in SUPPORTED_EXTENSIONS]

        for p in unsupported:
            self.error_collector.record_error(
                dataset_id=self.dataset_id,
                file_path=str(p),
                operation="discover_images",
                exception=f"Unsupported image file extension: {p.suffix}",
            )

        return supported

    @abstractmethod
    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Process discovered images, parse metadata/labels, and generate standardized manifest records."""
        pass

    def report_missing_information(self) -> Dict[str, Any]:
        """Report missing labels, metadata fields, or unreadable files."""
        return {
            "dataset_id": self.dataset_id,
            "has_metadata": self.entry.metadata_available,
            "has_labels": self.entry.labels_available,
            "error_count": self.error_collector.error_count(),
            "errors": self.error_collector.to_dict(),
        }
