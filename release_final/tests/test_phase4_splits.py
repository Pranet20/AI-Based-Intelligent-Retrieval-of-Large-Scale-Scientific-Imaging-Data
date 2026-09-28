"""Tests for Phase 4 leakage-safe instrument partitioning."""

import json
from pathlib import Path
import pytest
import pandas as pd

from src.adaptation.split_builder import SplitBuilder


def test_hcci_instrument_split_integrity():
    """Verify that HCCI instrument-held-out splits have zero image and acquisition leakage."""
    manifest_path = Path("data/manifests/hcci_manifest.parquet")
    if not manifest_path.is_file():
        pytest.skip("HCCI manifest not available")

    sb = SplitBuilder(hcci_manifest_path=manifest_path)
    df = sb.load_data()
    splits = sb.build_instrument_split(df)

    # 1. Total counts
    assert len(splits["train"]) == 427
    assert len(splits["val"]) == 135
    assert len(splits["test"]) == 212
    assert len(splits["train"]) + len(splits["val"]) + len(splits["test"]) == 774

    # 2. Image ID disjointness
    set_train = set(splits["train"])
    set_val = set(splits["val"])
    set_test = set(splits["test"])
    assert len(set_train & set_val) == 0
    assert len(set_train & set_test) == 0
    assert len(set_val & set_test) == 0

    # 3. Acquisition condition disjointness
    id_to_acq = dict(zip(df["image_id"], df["acquisition_id"]))
    train_acqs = {id_to_acq[i] for i in splits["train"]}
    val_acqs = {id_to_acq[i] for i in splits["val"]}
    test_acqs = {id_to_acq[i] for i in splits["test"]}

    assert len(train_acqs & val_acqs) == 0
    assert len(train_acqs & test_acqs) == 0
    assert len(val_acqs & test_acqs) == 0
    assert len(train_acqs) + len(val_acqs) + len(test_acqs) == 67

    # 4. Material class coverage
    id_to_spec = dict(zip(df["image_id"], df["specimen_id"]))
    for split_name, ids in splits.items():
        classes = {id_to_spec[i] for i in ids}
        assert classes == {"AsCast", "Q980_0h_WC", "Q980_9h_AC"}


def test_split_builder_save_and_reload(tmp_path):
    """Verify split builder serializes and reloads cleanly."""
    manifest_path = Path("data/manifests/hcci_manifest.parquet")
    if not manifest_path.is_file():
        pytest.skip("HCCI manifest not available")

    sb = SplitBuilder(hcci_manifest_path=manifest_path, output_dir=tmp_path)
    df = sb.load_data()
    splits = sb.build_instrument_split(df)
    saved_file = sb.save_splits(splits, filename="test_splits.json")

    assert saved_file.is_file()
    with open(saved_file, "r", encoding="utf-8") as f:
        reloaded = json.load(f)
    assert reloaded == splits
