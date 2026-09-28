"""Dataset adapter for cigRockSEM: Geological Microstructure Cross-Domain Validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.datasets.base import BaseDatasetAdapter
from src.datasets.registry import DatasetRegistryEntry
from src.ingestion.manifest import ManifestRecord
from src.ingestion.reader import ScientificImageReader
from src.metadata.normalizer import MetadataNormalizer
from src.utils.logging import AuditErrorCollector


class CigRockSEMAdapter(BaseDatasetAdapter):
    """Adapter for cigRockSEM dataset.

    Specifically flagged as 'cross_domain_validation' to prevent accidental inclusion
    in standard training splits.
    """

    def locate_files(self) -> List[Path]:
        """Locate SEM images of rock microstructures."""
        candidates: List[Path] = []
        for ext in ("*.tif", "*.tiff", "*.png", "*.jpg", "*.jpeg"):
            candidates.extend(self.root_dir.rglob(ext))
        candidates = [p for p in candidates if not p.name.startswith("._")]
        return sorted(candidates)

    def read_labels(self) -> Dict[str, Any]:
        """Rock microstructure classes or lithology if present."""
        return {}

    def read_metadata(self) -> Dict[str, Any]:
        return {
            "domain": "geological_microstructure",
            "cross_domain_evaluation_role": "external_generalization_test",
        }

    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Ingest cigRockSEM files with external validation tags."""
        image_paths = self.discover_images()
        if limit and limit > 0:
            image_paths = image_paths[:limit]
        raw_meta = self.read_metadata()

        records: List[ManifestRecord] = []
        for path in image_paths:
            try:
                container = MetadataNormalizer.normalize_generic(
                    raw_dict=raw_meta,
                    modality="SEM",
                )
                audit_res = ScientificImageReader.audit_image(path)

                try:
                    rel_path = str(path.relative_to(self.root_dir))
                except ValueError:
                    rel_path = path.name

                rec = ManifestRecord(
                    dataset_id=self.dataset_id,
                    sample_id=path.stem,
                    image_id=f"cigrock_{path.stem}",
                    relative_path=rel_path,
                    absolute_path_if_local_only=str(path.resolve()),
                    filename=path.name,
                    extension=path.suffix.lower(),
                    file_size_bytes=audit_res.file_size_bytes,
                    sha256=audit_res.sha256,
                    width=audit_res.width,
                    height=audit_res.height,
                    channels=audit_res.channels,
                    bit_depth=audit_res.bit_depth,
                    dtype=audit_res.dtype,
                    format=audit_res.extension.lstrip("."),
                    color_mode=audit_res.color_mode,
                    modality="SEM",
                    split="external_validation",  # Strictly labeled external validation
                    label="rock_microstructure",
                    source_label=None,
                    group_id="rock_microstructure",
                    specimen_id=path.stem,
                    roi_id=None,
                    acquisition_id=None,
                    metadata_json=json.dumps(container.to_json_dict()),
                    quality_status=None,
                    quality_score=None,
                )
                records.append(rec)
            except Exception as e:
                self.error_collector.record_error(
                    dataset_id=self.dataset_id,
                    file_path=str(path),
                    operation="build_manifest_record",
                    exception=str(e),
                )

        return records
