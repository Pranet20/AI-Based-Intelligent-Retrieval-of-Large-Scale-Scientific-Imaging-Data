"""Dataset adapter for MicroAl-Dataset: Multi-Modal Materials Microscopy Extension."""

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


class MicroAlAdapter(BaseDatasetAdapter):
    """Adapter for MicroAl-Dataset containing Optical, SEM, and TEM subsets.

    Explicitly records subset-specific access authorizations and imaging modality.
    """

    def locate_files(self) -> List[Path]:
        """Locate image files across OM, SEM, and TEM subfolders."""
        candidates: List[Path] = []
        for ext in ("*.tif", "*.tiff", "*.png", "*.jpg", "*.jpeg"):
            candidates.extend(self.root_dir.rglob(ext))
        candidates = [p for p in candidates if not p.name.startswith("._")]
        return sorted(candidates)

    def read_labels(self) -> Dict[str, Any]:
        """Read alloy grade or microstructural phase labels if present."""
        return {}

    def read_metadata(self) -> Dict[str, Any]:
        """Record subset licensing notice and multi-modality structure."""
        return {
            "access_notice": "Inspect repository licenses per-subset prior to external redistribution.",
            "supported_modalities": ["optical", "SEM", "TEM"],
        }

    def _infer_modality(self, path: Path) -> str:
        """Infer modality from directory hierarchy or filename."""
        p_str = str(path).lower()
        if "tem" in p_str:
            return "TEM"
        elif "sem" in p_str:
            return "SEM"
        elif "om" in p_str or "optical" in p_str:
            return "Optical"
        return "Microscopy_Unknown"

    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Ingest MicroAl images."""
        image_paths = self.discover_images()
        if limit and limit > 0:
            image_paths = image_paths[:limit]
        raw_meta = self.read_metadata()

        records: List[ManifestRecord] = []
        for path in image_paths:
            try:
                modality = self._infer_modality(path)
                item_meta = dict(raw_meta)
                item_meta["inferred_modality"] = modality

                container = MetadataNormalizer.normalize_generic(
                    raw_dict=item_meta,
                    modality=modality,
                )
                audit_res = ScientificImageReader.audit_image(path)

                try:
                    rel_path = str(path.relative_to(self.root_dir))
                except ValueError:
                    rel_path = path.name

                rec = ManifestRecord(
                    dataset_id=self.dataset_id,
                    sample_id=path.stem,
                    image_id=f"microal_{path.stem}",
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
                    modality=modality,
                    split="extension_modality",
                    label=None,
                    source_label=None,
                    group_id=modality,
                    specimen_id=None,
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
