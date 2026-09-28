"""Dataset adapter for High-Chromium Cast Iron (HCCI) SEM Dataset."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from src.datasets.base import BaseDatasetAdapter
from src.datasets.registry import DatasetRegistryEntry
from src.ingestion.manifest import ManifestRecord
from src.ingestion.reader import ScientificImageReader, compute_sha256
from src.metadata.normalizer import MetadataNormalizer
from src.utils.logging import AuditErrorCollector


class HCCIDatasetAdapter(BaseDatasetAdapter):
    """Adapter for HCCI SEM Dataset.

    Extracts acquisition variations from Metadata_All_Samples.xlsx and parses
    Classes.txt annotations.
    """

    def __init__(
        self,
        entry: DatasetRegistryEntry,
        root_dir: Optional[str | Path] = None,
        error_collector: Optional[AuditErrorCollector] = None,
    ) -> None:
        super().__init__(entry, root_dir, error_collector)
        self.metadata_df: Optional[pd.DataFrame] = None
        self.classes_info: Dict[str, Any] = {}

    def locate_files(self) -> List[Path]:
        """Locate image files under Images/ or root directory."""
        candidates: List[Path] = []
        img_dir = self.root_dir / "Images"
        search_dir = img_dir if img_dir.is_dir() else self.root_dir

        for ext in ("*.png", "*.tif", "*.tiff", "*.jpg", "*.jpeg"):
            candidates.extend(search_dir.glob(ext))
        # Exclude MacOS metadata artifacts
        candidates = [p for p in candidates if not p.name.startswith("._")]
        return sorted(candidates)

    def read_metadata(self) -> Dict[str, Any]:
        """Read and index Metadata_All_Samples.xlsx by sample/file name."""
        meta_file = self.root_dir / "Metadata_All_Samples.xlsx"
        if not meta_file.is_file():
            # Check for alternative casing
            found = list(self.root_dir.glob("*metadata*.xlsx"))
            if found:
                meta_file = found[0]
            else:
                self.logger.warning("Metadata_All_Samples.xlsx not found in %s", self.root_dir)
                return {}

        try:
            df = pd.read_excel(meta_file)
            self.metadata_df = df
            # Map by stringified File Name column
            indexed: Dict[str, Any] = {}
            for _, row in df.iterrows():
                fname_key = str(row.get("File Name", "")).strip()
                if fname_key.endswith(".0"):
                    fname_key = fname_key[:-2]
                indexed[fname_key] = row.to_dict()
            return indexed
        except Exception as e:
            self.error_collector.record_error(
                dataset_id=self.dataset_id,
                file_path=str(meta_file),
                operation="read_metadata",
                exception=str(e),
            )
            return {}

    def read_labels(self) -> Dict[str, Any]:
        """Read Classes.txt for phase color palette information."""
        cls_file = self.root_dir / "Classes.txt"
        if not cls_file.is_file():
            return {}
        try:
            with open(cls_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.classes_info = {"raw_palette": content}
            return self.classes_info
        except Exception as e:
            self.error_collector.record_error(
                dataset_id=self.dataset_id,
                file_path=str(cls_file),
                operation="read_labels",
                exception=str(e),
            )
            return {}

    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Ingest HCCI images, bind metadata, and emit ManifestRecord objects."""
        image_paths = self.discover_images()
        if limit and limit > 0:
            image_paths = image_paths[:limit]
        metadata_map = self.read_metadata()
        self.read_labels()

        records: List[ManifestRecord] = []
        for path in image_paths:
            try:
                # Key matching
                stem = path.stem.strip()
                row_meta = metadata_map.get(stem, {})

                # Dynamic normalization
                if row_meta:
                    container = MetadataNormalizer.normalize_hcci_row(row_meta)
                else:
                    container = MetadataNormalizer.normalize_generic(modality="SEM")

                norm = container.normalized
                sample_str = str(norm.sample) if norm.sample else stem
                state_str = str(norm.sample_state) if norm.sample_state else "Unknown"

                # Audit image data
                audit_res = ScientificImageReader.audit_image(path)

                # Grouping to prevent leakage
                group_id = f"sample_{sample_str}_{state_str}"
                acquisition_id = f"{norm.microscope}_{norm.detector}_{norm.accelerating_voltage_kv}kV_{norm.magnification}x"

                try:
                    rel_path = str(path.relative_to(self.root_dir))
                except ValueError:
                    rel_path = path.name

                rec = ManifestRecord(
                    dataset_id=self.dataset_id,
                    sample_id=sample_str,
                    image_id=f"hcci_{stem}",
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
                    split=None,  # Do not fabricate splits
                    label=state_str,
                    source_label=state_str,
                    group_id=group_id,
                    specimen_id=sample_str,
                    roi_id=f"roi_{stem}",
                    acquisition_id=acquisition_id,
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
