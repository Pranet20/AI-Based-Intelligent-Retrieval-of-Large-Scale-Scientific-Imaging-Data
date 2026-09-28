"""Dataset adapter for Carinthia SEM Dataset."""

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


class CarinthiaDatasetAdapter(BaseDatasetAdapter):
    """Adapter for Carinthia SEM Dataset.

    Reads 6 verified defect classes directly from carinthia.csv.
    """

    def __init__(
        self,
        entry: DatasetRegistryEntry,
        root_dir: Optional[str | Path] = None,
        error_collector: Optional[AuditErrorCollector] = None,
    ) -> None:
        super().__init__(entry, root_dir, error_collector)
        self.labels_df: Optional[pd.DataFrame] = None

    def locate_files(self) -> List[Path]:
        """Locate image files under images/, data/images/, or root_dir."""
        candidates: List[Path] = []
        possible_dirs = [
            self.root_dir / "data" / "images",
            self.root_dir / "images",
            self.root_dir,
        ]
        search_dir = next((d for d in possible_dirs if d.is_dir()), self.root_dir)

        for ext in ("*.jpg", "*.jpeg", "*.png", "*.tif", "*.tiff"):
            candidates.extend(search_dir.glob(ext))
        candidates = [p for p in candidates if not p.name.startswith("._")]
        return sorted(candidates)

    def read_labels(self) -> Dict[str, Any]:
        """Read carinthia.csv (semicolon-delimited) and index defect labels by filename."""
        possible_csvs = [
            self.root_dir / "data" / "carinthia.csv",
            self.root_dir / "carinthia.csv",
        ]
        csv_path = next((p for p in possible_csvs if p.is_file()), None)
        if not csv_path:
            # Fallback to search
            found = list(self.root_dir.glob("*carinthia*.csv"))
            if found:
                csv_path = found[0]

        if not csv_path:
            self.logger.warning("carinthia.csv not found under %s", self.root_dir)
            return {}

        try:
            # Note: carinthia.csv uses semicolon delimiter
            df = pd.read_csv(csv_path, sep=";")
            self.labels_df = df
            label_map: Dict[str, Any] = {}
            for _, row in df.iterrows():
                fname = str(row.get("file_name", "")).strip()
                lbl = row.get("label")
                if fname:
                    label_map[fname] = {
                        "label": f"defect_class_{lbl}",
                        "source_label": str(lbl),
                    }
            return label_map
        except Exception as e:
            self.error_collector.record_error(
                dataset_id=self.dataset_id,
                file_path=str(csv_path),
                operation="read_labels",
                exception=str(e),
            )
            return {}

    def read_metadata(self) -> Dict[str, Any]:
        """Carinthia has no instrument metadata; report explicitly."""
        return {}

    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Ingest Carinthia images and generate manifest records."""
        image_paths = self.discover_images()
        if limit and limit > 0:
            image_paths = image_paths[:limit]
        labels_map = self.read_labels()

        records: List[ManifestRecord] = []
        for path in image_paths:
            try:
                fname = path.name
                lbl_info = labels_map.get(fname, {"label": None, "source_label": None})

                container = MetadataNormalizer.normalize_generic(modality="SEM")
                audit_res = ScientificImageReader.audit_image(path)

                try:
                    rel_path = str(path.relative_to(self.root_dir))
                except ValueError:
                    rel_path = path.name

                rec = ManifestRecord(
                    dataset_id=self.dataset_id,
                    sample_id=path.stem,
                    image_id=f"carinthia_{path.stem}",
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
                    label=lbl_info["label"],
                    source_label=lbl_info["source_label"],
                    group_id=lbl_info["label"],  # Class-level grouping
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
