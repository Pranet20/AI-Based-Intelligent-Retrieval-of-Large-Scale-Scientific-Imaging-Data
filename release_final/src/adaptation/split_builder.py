"""Leakage-safe dataset splitting for Phase 4 representation adaptation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from src.utils.logging import get_logger

logger = get_logger("adaptation.split_builder")


class SplitBuilder:
    """Constructs and validates leakage-safe splits across SEM acquisition domains."""

    def __init__(
        self,
        hcci_manifest_path: str | Path = "data/manifests/hcci_manifest.parquet",
        output_dir: str | Path = "data/processed/phase4/splits",
    ) -> None:
        self.manifest_path = Path(hcci_manifest_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_data(self) -> pd.DataFrame:
        """Load manifest and extract instrument from metadata_json."""
        df = pd.read_parquet(self.manifest_path)
        sem_list = []
        for meta_str in df["metadata_json"]:
            try:
                data = json.loads(meta_str)
                sem = data.get("raw_metadata", {}).get("SEM") or data.get("normalized", {}).get("microscope")
                sem_list.append(sem)
            except Exception:
                sem_list.append(None)
        df["SEM"] = sem_list
        return df

    def build_instrument_split(
        self,
        df: Optional[pd.DataFrame] = None,
        train_instruments: Optional[List[str]] = None,
        val_instruments: Optional[List[str]] = None,
        test_instruments: Optional[List[str]] = None,
    ) -> Dict[str, List[str]]:
        """Construct leakage-safe instrument-held-out splits.

        Default partition:
          - Train: Helios NanoLab, Helios G4 PFIB CXe (427 micrographs)
          - Val:   VEGA3 XMH (135 micrographs)
          - Test:  Zeiss Gemini (212 micrographs)
        """
        if df is None:
            df = self.load_data()

        train_inst = train_instruments or ["Helios NanoLab", "Helios G4 PFIB CXe"]
        val_inst = val_instruments or ["VEGA3 XMH"]
        test_inst = test_instruments or ["Zeiss Gemini"]

        train_ids = df[df["SEM"].isin(train_inst)]["image_id"].tolist()
        val_ids = df[df["SEM"].isin(val_inst)]["image_id"].tolist()
        test_ids = df[df["SEM"].isin(test_inst)]["image_id"].tolist()

        splits = {
            "train": sorted(train_ids),
            "val": sorted(val_ids),
            "test": sorted(test_ids),
        }

        self.validate_splits(df, splits)
        return splits

    def validate_splits(self, df: pd.DataFrame, splits: Dict[str, List[str]]) -> None:
        """Validate that splits are mutually exclusive and have zero acquisition/image leakage."""
        id_to_row = {r["image_id"]: r for _, r in df.iterrows()}

        set_train = set(splits["train"])
        set_val = set(splits["val"])
        set_test = set(splits["test"])

        # 1. Total coverage & image disjointness
        assert len(set_train & set_val) == 0, "Train and Val share image IDs!"
        assert len(set_train & set_test) == 0, "Train and Test share image IDs!"
        assert len(set_val & set_test) == 0, "Val and Test share image IDs!"
        total_assigned = len(set_train) + len(set_val) + len(set_test)
        assert total_assigned == len(df), f"Expected {len(df)} images, but got {total_assigned}"

        # 2. Acquisition ID disjointness
        train_acqs = {id_to_row[img_id]["acquisition_id"] for img_id in splits["train"]}
        val_acqs = {id_to_row[img_id]["acquisition_id"] for img_id in splits["val"]}
        test_acqs = {id_to_row[img_id]["acquisition_id"] for img_id in splits["test"]}

        assert len(train_acqs & val_acqs) == 0, "Train and Val share acquisition conditions!"
        assert len(train_acqs & test_acqs) == 0, "Train and Test share acquisition conditions!"
        assert len(val_acqs & test_acqs) == 0, "Val and Test share acquisition conditions!"

        # 3. Material representation
        for split_name, ids in splits.items():
            materials = {id_to_row[img_id]["specimen_id"] for img_id in ids}
            assert len(materials) == 3, f"Split '{split_name}' does not contain all 3 material categories! Found: {materials}"

        logger.info(
            "Splits validated successfully: Train=%d (%d acqs), Val=%d (%d acqs), Test=%d (%d acqs)",
            len(splits["train"]),
            len(train_acqs),
            len(splits["val"]),
            len(val_acqs),
            len(splits["test"]),
            len(test_acqs),
        )

    def save_splits(
        self,
        splits: Dict[str, List[str]],
        filename: str = "hcci_instrument_splits.json",
    ) -> Path:
        """Save split mapping to JSON."""
        out_path = self.output_dir / filename
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(splits, f, indent=2)
        logger.info("Saved Phase 4 splits to %s", out_path)
        return out_path
