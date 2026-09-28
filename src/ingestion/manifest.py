"""Dataset manifest builder supporting Parquet and CSV export."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


MANIFEST_COLUMNS = [
    "dataset_id",
    "sample_id",
    "image_id",
    "relative_path",
    "absolute_path_if_local_only",
    "filename",
    "extension",
    "file_size_bytes",
    "sha256",
    "width",
    "height",
    "channels",
    "bit_depth",
    "dtype",
    "format",
    "color_mode",
    "modality",
    "split",
    "label",
    "source_label",
    "group_id",
    "specimen_id",
    "roi_id",
    "acquisition_id",
    "metadata_json",
    "quality_status",
    "quality_score",
    "duplicate_group_id",
    "near_duplicate_group_id",
]


@dataclass
class ManifestRecord:
    """Normalized manifest record for a single scientific image."""

    dataset_id: str
    sample_id: Optional[str] = None
    image_id: str = ""
    relative_path: str = ""
    absolute_path_if_local_only: Optional[str] = None
    filename: str = ""
    extension: str = ""
    file_size_bytes: int = 0
    sha256: str = ""
    width: Optional[int] = None
    height: Optional[int] = None
    channels: Optional[int] = None
    bit_depth: Optional[int] = None
    dtype: Optional[str] = None
    format: Optional[str] = None
    color_mode: Optional[str] = None
    modality: Optional[str] = None
    split: Optional[str] = None
    label: Optional[str] = None
    source_label: Optional[str] = None
    group_id: Optional[str] = None
    specimen_id: Optional[str] = None
    roi_id: Optional[str] = None
    acquisition_id: Optional[str] = None
    metadata_json: Optional[str] = None
    quality_status: Optional[str] = None
    quality_score: Optional[float] = None
    duplicate_group_id: Optional[str] = None
    near_duplicate_group_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        return d


class ManifestManager:
    """Manages collection, validation, and serialization of dataset manifests."""

    @staticmethod
    def records_to_dataframe(records: List[ManifestRecord | Dict[str, Any]]) -> pd.DataFrame:
        """Convert a list of manifest records into a standardized DataFrame."""
        dict_records = []
        for r in records:
            if isinstance(r, ManifestRecord):
                dict_records.append(r.to_dict())
            elif isinstance(r, dict):
                dict_records.append(r)
            else:
                raise TypeError(f"Unsupported record type: {type(r)}")

        df = pd.DataFrame(dict_records)
        # Ensure all standard columns exist
        for col in MANIFEST_COLUMNS:
            if col not in df.columns:
                df[col] = None
        # Order columns strictly
        return df[MANIFEST_COLUMNS]

    @classmethod
    def save_manifest(
        cls,
        records: List[ManifestRecord | Dict[str, Any]],
        output_prefix: str | Path,
    ) -> Dict[str, str]:
        """Save manifest as both Parquet and CSV files.

        Returns paths of saved files.
        """
        prefix = Path(output_prefix)
        prefix.parent.mkdir(parents=True, exist_ok=True)
        parquet_path = prefix.with_suffix(".parquet")
        csv_path = prefix.with_suffix(".csv")

        df = cls.records_to_dataframe(records)

        # Write Parquet
        df.to_parquet(parquet_path, engine="pyarrow", index=False)

        # Write CSV
        df.to_csv(csv_path, index=False, encoding="utf-8")

        return {
            "parquet": str(parquet_path.resolve()),
            "csv": str(csv_path.resolve()),
            "count": str(len(df)),
        }

    @classmethod
    def load_manifest(cls, manifest_path: str | Path) -> pd.DataFrame:
        """Load manifest from Parquet or CSV."""
        p = Path(manifest_path)
        if not p.is_file():
            raise FileNotFoundError(f"Manifest not found: {p}")
        if p.suffix == ".parquet":
            return pd.read_parquet(p)
        elif p.suffix == ".csv":
            return pd.read_csv(p)
        else:
            raise ValueError(f"Unsupported manifest file extension: {p.suffix}")
