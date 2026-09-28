"""Dataset adapter for the SEM Nanoscience Benchmark Dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.datasets.base import BaseDatasetAdapter
from src.datasets.registry import DatasetRegistryEntry
from src.ingestion.manifest import ManifestRecord
from src.ingestion.reader import ScientificImageReader
from src.metadata.normalizer import MetadataNormalizer
from src.utils.logging import AuditErrorCollector


class SemNanoscienceAdapter(BaseDatasetAdapter):
    """Adapter for 'The First Annotated Set of SEM Images for Nanoscience'.

    Explicitly records that images are JPEG-compressed and lack instrument metadata tags.
    """

    def __init__(
        self,
        entry: DatasetRegistryEntry,
        root_dir: Optional[str | Path] = None,
        error_collector: Optional[AuditErrorCollector] = None,
    ) -> None:
        super().__init__(entry, root_dir, error_collector)
        self.labels_map: Dict[str, str] = {}

    def locate_files(self) -> List[Path]:
        """Locate JPEG image files recursively."""
        candidates = list(self.root_dir.rglob("*.jpg")) + list(self.root_dir.rglob("*.jpeg"))
        candidates = [p for p in candidates if not p.name.startswith("._")]
        return sorted(candidates)

    def read_labels(self) -> Dict[str, Any]:
        """Read category directory names or CSV annotations if present."""
        lbl_file = self.root_dir / "labels.csv"
        if lbl_file.is_file():
            try:
                df = pd.read_csv(lbl_file)
                mapping = {}
                for _, row in df.iterrows():
                    mapping[str(row.iloc[0]).strip()] = str(row.iloc[1]).strip()
                self.labels_map = mapping
                return mapping
            except Exception as e:
                self.error_collector.record_error(
                    dataset_id=self.dataset_id,
                    file_path=str(lbl_file),
                    operation="read_labels",
                    exception=str(e),
                )
        return {}

    def read_metadata(self) -> Dict[str, Any]:
        """Explicitly record the absence of instrument TIFF tags in the JPEG dataset."""
        return {
            "limitation_note": "Dataset contains lossy JPEG files; instrument TIFF metadata tags were omitted by the original publisher."
        }

    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Ingest SEM Nanoscience images."""
        image_paths = self.discover_images()
        if limit and limit > 0:
            image_paths = image_paths[:limit]
        labels_map = self.read_labels()
        meta_note = self.read_metadata()

        records: List[ManifestRecord] = []
        for path in image_paths:
            try:
                # If subdirectories represent categories, capture as label
                parent_dir = path.parent.name
                lbl = labels_map.get(path.name, parent_dir if parent_dir != self.root_dir.name else None)

                container = MetadataNormalizer.normalize_generic(raw_dict=meta_note, modality="SEM")
                audit_res = ScientificImageReader.audit_image(path)

                try:
                    rel_path = str(path.relative_to(self.root_dir))
                except ValueError:
                    rel_path = path.name

                rec = ManifestRecord(
                    dataset_id=self.dataset_id,
                    sample_id=path.stem,
                    image_id=f"sem_nano_{path.stem}",
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
                    split=None,
                    label=lbl,
                    source_label=lbl,
                    group_id=lbl,
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
