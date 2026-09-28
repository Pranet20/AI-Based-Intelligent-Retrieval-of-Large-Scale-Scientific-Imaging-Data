"""Dataset adapter for atomagined: Synthetic HAADF-STEM Retrieval Benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import h5py

from src.datasets.base import BaseDatasetAdapter
from src.datasets.registry import DatasetRegistryEntry
from src.ingestion.manifest import ManifestRecord
from src.ingestion.reader import ScientificImageReader
from src.metadata.normalizer import MetadataNormalizer
from src.utils.logging import AuditErrorCollector


class AtomaginedAdapter(BaseDatasetAdapter):
    """Adapter for the synthetic atomic-resolution HAADF-STEM 'atomagined' retrieval benchmark.

    Preserves target/choice query-gallery pairing structure and HDF5 attributes.
    """

    def __init__(
        self,
        entry: DatasetRegistryEntry,
        root_dir: Optional[str | Path] = None,
        error_collector: Optional[AuditErrorCollector] = None,
    ) -> None:
        super().__init__(entry, root_dir, error_collector)
        self.retrieval_pairs: List[Dict[str, Any]] = []

    def locate_files(self) -> List[Path]:
        """Locate image files (HDF5 or exported PNG/TIFF) under targets/ and choices/."""
        candidates: List[Path] = []
        for ext in ("*.h5", "*.hdf5", "*.png", "*.tif", "*.tiff"):
            candidates.extend(self.root_dir.rglob(ext))
        candidates = [p for p in candidates if not p.name.startswith("._")]
        return sorted(candidates)

    def read_metadata(self) -> Dict[str, Any]:
        """Extract HDF5 attributes if HDF5 format is present."""
        attrs_map: Dict[str, Any] = {}
        for h5_path in self.root_dir.rglob("*.h*5"):
            try:
                with h5py.File(h5_path, "r") as hf:
                    attrs_map[h5_path.stem] = {k: str(v) for k, v in hf.attrs.items()}
            except Exception as e:
                self.error_collector.record_error(
                    dataset_id=self.dataset_id,
                    file_path=str(h5_path),
                    operation="read_hdf5_attrs",
                    exception=str(e),
                )
        return attrs_map

    def read_labels(self) -> Dict[str, Any]:
        """Preserve target/choice pair mapping."""
        pairs_file = self.root_dir / "retrieval_benchmark.json"
        if pairs_file.is_file():
            try:
                with open(pairs_file, "r", encoding="utf-8") as f:
                    self.retrieval_pairs = json.load(f)
            except Exception as e:
                self.error_collector.record_error(
                    dataset_id=self.dataset_id,
                    file_path=str(pairs_file),
                    operation="read_retrieval_benchmark",
                    exception=str(e),
                )
        return {"retrieval_pairs_count": len(self.retrieval_pairs)}

    def build_manifest_records(self, limit: Optional[int] = None) -> List[ManifestRecord]:
        """Build manifest preserving retrieval role (target vs choice) and structure IDs."""
        image_paths = self.discover_images()
        if limit and limit > 0:
            image_paths = image_paths[:limit]
        h5_attrs = self.read_metadata()

        records: List[ManifestRecord] = []
        for path in image_paths:
            try:
                stem = path.stem
                is_target = "target" in path.name.lower() or "targets" in [p.lower() for p in path.parts]
                is_choice = "choice" in path.name.lower() or "choices" in [p.lower() for p in path.parts]
                role_type = "target_query" if is_target else ("choice_gallery" if is_choice else "benchmark_image")

                # Structure ID parsing (atomagined filename typically encodes crystal structure ID)
                parts = stem.split("_")
                structure_id = parts[0] if parts else stem

                raw_meta = {
                    "synthetic": True,
                    "simulation_type": "multislice_HAADF_STEM",
                    "retrieval_role": role_type,
                    "structure_id": structure_id,
                    "hdf5_attrs": h5_attrs.get(stem, {}),
                }

                container = MetadataNormalizer.normalize_generic(
                    raw_dict=raw_meta,
                    modality="HAADF-STEM_synthetic",
                )
                audit_res = ScientificImageReader.audit_image(path)

                try:
                    rel_path = str(path.relative_to(self.root_dir))
                except ValueError:
                    rel_path = path.name

                rec = ManifestRecord(
                    dataset_id=self.dataset_id,
                    sample_id=structure_id,
                    image_id=f"atomagined_{stem}",
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
                    modality="HAADF-STEM_synthetic",
                    split=role_type,
                    label=structure_id,
                    source_label=structure_id,
                    group_id=f"struct_{structure_id}",
                    specimen_id=structure_id,
                    roi_id=None,
                    acquisition_id=f"sim_{role_type}",
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

    def export_benchmark_definition(self, output_path: str | Path) -> None:
        """Export dedicated target-choice benchmark pairing file for Phase 3+ retrieval experiments."""
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump({
                "benchmark_name": "atomagined_retrieval_benchmark",
                "doi": self.entry.doi,
                "retrieval_pairs": self.retrieval_pairs,
            }, f, indent=2)
