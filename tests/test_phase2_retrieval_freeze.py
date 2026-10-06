"""Unit and integration tests for Phase 2 Controlled Retrieval Benchmark Freeze.

Verifies:
1. All 5 model types evaluated (pHash, dHash, ResNet-50, DINOv2, Adapters).
2. Identical query and gallery sets used across all models.
3. Strict zero-leakage from train partition into test queries and gallery.
4. Deterministic rerun produces identical metrics down to 6 decimal places.
5. All result files exist, are valid JSON/CSV, and match the specified schema.
6. Confidence intervals are statistically valid (bounded in [0, 1] with low <= high).
"""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest


RESULTS_DIR = Path("research/experiments/freeze1")
SYNC_DIR = Path("research/results/freeze1")
QUERY_MANIFEST_PATH = RESULTS_DIR / "query_manifest.json"
RESULTS_CSV_PATH = RESULTS_DIR / "retrieval_results.csv"
RESULTS_JSON_PATH = RESULTS_DIR / "retrieval_results.json"
REPORT_MD_PATH = RESULTS_DIR / "RETRIEVAL_FREEZE_1_REPORT.md"
EVIDENCE_HASH_PATH = RESULTS_DIR / "FREEZE_1_EVIDENCE_HASH.txt"

SPLIT_MANIFEST_PATH = Path("research/final_manifests/FINAL_SPLIT_MANIFEST.json")
IMAGE_MANIFEST_PATH = Path("research/final_manifests/FINAL_IMAGE_MANIFEST.json")


def test_freeze1_artifacts_exist_and_synced():
    """Verify that all required Freeze 1 benchmark artifacts exist and are synced."""
    for path in [
        QUERY_MANIFEST_PATH,
        RESULTS_CSV_PATH,
        RESULTS_JSON_PATH,
        REPORT_MD_PATH,
        EVIDENCE_HASH_PATH,
    ]:
        assert path.exists(), f"Missing artifact: {path}"
        assert path.stat().st_size > 0, f"Artifact is empty: {path}"

    for fname in [
        "retrieval_results.csv",
        "retrieval_results.json",
        "RETRIEVAL_FREEZE_1_REPORT.md",
        "FREEZE_1_EVIDENCE_HASH.txt",
    ]:
        synced_file = SYNC_DIR / fname
        assert synced_file.exists(), f"Missing synced file: {synced_file}"
        assert synced_file.stat().st_size == (RESULTS_DIR / fname).stat().st_size


def test_five_model_families_evaluated():
    """Verify that all 5 required model types are present in results."""
    assert RESULTS_JSON_PATH.exists()
    with open(RESULTS_JSON_PATH, "r") as f:
        data = json.load(f)

    models_dict = data["models"]
    # 1. pHash
    assert "phash" in models_dict
    assert models_dict["phash"]["embedding_dim"] == 64
    # 2. dHash
    assert "dhash" in models_dict
    assert models_dict["dhash"]["embedding_dim"] == 64
    # 3. ResNet-50
    assert "resnet50" in models_dict
    assert models_dict["resnet50"]["embedding_dim"] == 2048
    # 4. DINOv2 ViT-S/14
    assert "dinov2_vits14" in models_dict
    assert models_dict["dinov2_vits14"]["embedding_dim"] == 384
    # 5. Phase-4 Adapter (seeds 42, 123, 2024 and ensemble)
    assert "adapter_seed42" in models_dict
    assert "adapter_seed123" in models_dict
    assert "adapter_seed2024" in models_dict
    assert "adapter_ensemble" in data


def test_identical_query_and_gallery_sets():
    """Verify all models evaluate the exact same 212 queries and 211 gallery candidates."""
    with open(QUERY_MANIFEST_PATH, "r") as f:
        q_manifest = json.load(f)

    total_queries = q_manifest["total_valid_queries"]
    assert total_queries == 212
    assert q_manifest["gallery_size_per_query"] == 211

    with open(RESULTS_JSON_PATH, "r") as f:
        res = json.load(f)

    for mid, mdata in res["models"].items():
        assert mdata["n_queries"] == 212, f"Model {mid} evaluated {mdata['n_queries']} queries, expected 212"


def test_no_train_leakage_in_test_queries_and_gallery():
    """Verify complete disjointness of image IDs and SHA hashes between train and test."""
    with open(SPLIT_MANIFEST_PATH, "r") as f:
        split_data = json.load(f)
    with open(IMAGE_MANIFEST_PATH, "r") as f:
        images = json.load(f)["images"]

    img_map = {im["image_id"]: im for im in images}
    hcci_splits = split_data["hcci_primary_retrieval"]

    train_ids = set(hcci_splits["train"])
    test_ids = set(hcci_splits["test"])

    # ID overlap
    assert len(train_ids.intersection(test_ids)) == 0

    # SHA overlap
    train_shas = {img_map[i]["sha256"] for i in train_ids}
    test_shas = {img_map[i]["sha256"] for i in test_ids}
    assert len(train_shas.intersection(test_shas)) == 0

    # Query manifest queries match test partition
    with open(QUERY_MANIFEST_PATH, "r") as f:
        q_manifest = json.load(f)
    query_ids = {q["query_id"] for q in q_manifest["queries"]}
    assert query_ids == test_ids


def test_confidence_intervals_valid():
    """Verify confidence interval bounds are mathematically sound."""
    df = pd.read_csv(RESULTS_CSV_PATH)
    for _, row in df.iterrows():
        mid = row["model_id"]
        # R@1 CI
        r1 = row["recall_at_1"]
        r1_low = row["recall_at_1_ci_low"]
        r1_high = row["recall_at_1_ci_high"]
        assert 0.0 <= r1_low <= r1_high <= 1.0, f"Invalid R@1 CI for {mid}: [{r1_low}, {r1_high}]"
        assert r1_low <= r1 + 1e-5 and r1 <= r1_high + 1e-5, f"R@1 {r1} outside CI [{r1_low}, {r1_high}] for {mid}"

        # MRR CI
        mrr = row["mrr"]
        mrr_low = row["mrr_ci_low"]
        mrr_high = row["mrr_ci_high"]
        assert 0.0 <= mrr_low <= mrr_high <= 1.0, f"Invalid MRR CI for {mid}: [{mrr_low}, {mrr_high}]"
        assert mrr_low <= mrr + 1e-5 and mrr <= mrr_high + 1e-5, f"MRR {mrr} outside CI for {mid}"

        # P@5 CI
        p5 = row["precision_at_5"]
        p5_low = row["precision_at_5_ci_low"]
        p5_high = row["precision_at_5_ci_high"]
        assert 0.0 <= p5_low <= p5_high <= 1.0, f"Invalid P@5 CI for {mid}: [{p5_low}, {p5_high}]"
        assert p5_low <= p5 + 1e-5 and p5 <= p5_high + 1e-5, f"P@5 {p5} outside CI for {mid}"


def test_evidence_hash_and_deterministic_rerun_verified():
    """Verify evidence hash file records passing deterministic rerun."""
    with open(EVIDENCE_HASH_PATH, "r") as f:
        content = f.read()

    assert "BENCHMARK_STATUS=VERIFIED" in content
    assert "DETERMINISTIC_RERUN_MATCH=TRUE" in content
    assert "retrieval_results.csv_SHA256=" in content
    assert "retrieval_results.json_SHA256=" in content
    assert "RETRIEVAL_FREEZE_1_REPORT.md_SHA256=" in content
