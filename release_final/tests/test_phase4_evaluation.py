"""Tests for Phase 4 retrieval evaluator, geometry metrics, and probes."""

from pathlib import Path
import pytest
import numpy as np
import pandas as pd

from src.adaptation.relationship_builder import RelationshipBuilder
from src.evaluation.acquisition_metrics import AcquisitionMetricsCalculator
from src.evaluation.phase4_evaluator import Phase4RetrievalEvaluator
from src.evaluation.probe_metrics import ProbeEvaluator


def test_evaluator_reproduces_frozen_phase2_hcci_metrics():
    """Verify that Phase4RetrievalEvaluator exactly reproduces Phase 2 frozen reference metrics on HCCI."""
    emb_path = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    manifest_path = Path("data/manifests/hcci_manifest.parquet")

    if not emb_path.is_file() or not manifest_path.is_file():
        pytest.skip("Phase 2 HCCI embeddings or manifest not available")

    df_emb = pd.read_parquet(emb_path)
    df_man = pd.read_parquet(manifest_path)

    df_man_indexed = df_man.set_index("image_id")
    df_eval = pd.DataFrame({
        "image_id": df_emb["image_id"],
        "specimen_id": df_emb["image_id"].map(df_man_indexed["specimen_id"]),
        "roi_id": df_emb["image_id"].map(df_man_indexed["roi_id"]),
        "acquisition_id": df_emb["image_id"].map(df_man_indexed["acquisition_id"]),
        "duplicate_group_id": df_emb["image_id"].map(df_man_indexed["duplicate_group_id"]),
        "near_duplicate_group_id": df_emb["image_id"].map(df_man_indexed["near_duplicate_group_id"]),
        "sha256": df_emb["image_id"].map(df_man_indexed["sha256"]),
    })

    vectors = np.vstack(df_emb["embedding"].to_numpy()).astype(np.float32)
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(df_eval)

    evaluator = Phase4RetrievalEvaluator(k_values=(1, 5, 10), eval_depth=50)
    results = evaluator.evaluate_retrieval(
        embeddings=vectors,
        image_ids=df_eval["image_id"].tolist(),
        ground_truth_positives=gt,
        exclusion_sets=excl,
    )

    # Compare against frozen Phase 2 benchmark down to 1e-4 tolerance
    assert np.isclose(results["recall_at_1"], 0.9819121447028424, atol=1e-4)
    assert np.isclose(results["recall_at_5"], 1.0000000000000000, atol=1e-4)
    assert np.isclose(results["recall_at_10"], 1.0000000000000000, atol=1e-4)
    assert np.isclose(results["mrr"], 0.9894487510766581, atol=1e-4)
    assert np.isclose(results["precision_at_5"], 0.9692506459948321, atol=1e-4)


def test_acquisition_metrics_calculation():
    """Verify geometry metrics calculation on synthetic data."""
    # 4 synthetic vectors
    v1 = np.array([1.0, 0.0], dtype=np.float32)
    v2 = np.array([0.9, 0.1], dtype=np.float32)
    v2 /= np.linalg.norm(v2)
    v3 = np.array([0.0, 1.0], dtype=np.float32)
    v4 = np.array([0.1, 0.9], dtype=np.float32)
    v4 /= np.linalg.norm(v4)

    embs = np.vstack([v1, v2, v3, v4])
    mats = ["A", "A", "B", "B"]
    acqs = ["acq1", "acq2", "acq1", "acq2"]

    res = AcquisitionMetricsCalculator.compute_similarity_metrics(embs, mats, acqs)
    assert res["cross_acquisition_count"] > 0
    assert "cross_within_similarity_ratio" in res
    assert res["within_acquisition_count"] == 0  # No two samples with same mat and same acq
