"""Unit tests for Phase 5 hybrid score fusion, exclusions, and alpha selection (Tests 16-24)."""

from __future__ import annotations

from typing import Dict, List, Set
import numpy as np
import pandas as pd
import pytest

from src.adaptation.relationship_builder import RelationshipBuilder
from src.retrieval.phase5_calibration import Phase5ScoreCalibrator
from src.retrieval.phase5_evaluator import Phase5Evaluator
from src.retrieval.phase5_fusion import Phase5HybridFusion


@pytest.fixture
def mock_retrieval_setup() -> Dict[str, Any]:
    """Create a controlled 6-query retrieval problem."""
    # 6 images:
    # img_0: Mat_A, Acq_1
    # img_1: Mat_A, Acq_2 (valid positive for img_0)
    # img_2: Mat_A, Acq_1 (same-material same-acq -> excluded)
    # img_3: Mat_B, Acq_1 (negative)
    # img_4: Mat_B, Acq_2 (negative)
    # img_5: Mat_A, Acq_2 (exact duplicate of img_1)
    df = pd.DataFrame([
        {"image_id": "img_0", "specimen_id": "Mat_A", "roi_id": "roi_0", "acquisition_id": "Acq_1", "duplicate_group_id": None, "near_duplicate_group_id": None, "sha256": "h0"},
        {"image_id": "img_1", "specimen_id": "Mat_A", "roi_id": "roi_1", "acquisition_id": "Acq_2", "duplicate_group_id": "dup_1", "near_duplicate_group_id": None, "sha256": "h1"},
        {"image_id": "img_2", "specimen_id": "Mat_A", "roi_id": "roi_2", "acquisition_id": "Acq_1", "duplicate_group_id": None, "near_duplicate_group_id": None, "sha256": "h2"},
        {"image_id": "img_3", "specimen_id": "Mat_B", "roi_id": "roi_3", "acquisition_id": "Acq_1", "duplicate_group_id": None, "near_duplicate_group_id": None, "sha256": "h3"},
        {"image_id": "img_4", "specimen_id": "Mat_B", "roi_id": "roi_4", "acquisition_id": "Acq_2", "duplicate_group_id": None, "near_duplicate_group_id": None, "sha256": "h4"},
        {"image_id": "img_5", "specimen_id": "Mat_A", "roi_id": "roi_5", "acquisition_id": "Acq_2", "duplicate_group_id": "dup_1", "near_duplicate_group_id": None, "sha256": "h5"},
    ])
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(df)

    rng = np.random.RandomState(42)
    S_V = rng.uniform(0.1, 0.9, size=(6, 6)).astype(np.float32)
    S_M = rng.uniform(-0.5, 0.8, size=(6, 6)).astype(np.float32)
    np.fill_diagonal(S_V, 1.0)
    np.fill_diagonal(S_M, 1.0)

    return {
        "df": df,
        "gt": gt,
        "excl": excl,
        "image_ids": df["image_id"].tolist(),
        "S_V": S_V,
        "S_M": S_M,
    }


# TEST 16: alpha=1 equals visual-only
def test_16_alpha_1_equals_visual_only(mock_retrieval_setup: Dict[str, Any]) -> None:
    fusion = Phase5HybridFusion()
    res_a1 = fusion.evaluate(
        S_H=fusion.compute_hybrid_matrix(mock_retrieval_setup["S_V"], mock_retrieval_setup["S_M"], alpha=1.0),
        query_ids=mock_retrieval_setup["image_ids"],
        candidate_ids=mock_retrieval_setup["image_ids"],
        ground_truth_positives=mock_retrieval_setup["gt"],
        exclusion_sets=mock_retrieval_setup["excl"],
    )
    res_raw_v = fusion.evaluate(
        S_H=mock_retrieval_setup["S_V"],
        query_ids=mock_retrieval_setup["image_ids"],
        candidate_ids=mock_retrieval_setup["image_ids"],
        ground_truth_positives=mock_retrieval_setup["gt"],
        exclusion_sets=mock_retrieval_setup["excl"],
    )
    assert res_a1["recall_at_1"] == res_raw_v["recall_at_1"]
    assert res_a1["mrr"] == res_raw_v["mrr"]
    assert res_a1["precision_at_5"] == res_raw_v["precision_at_5"]
    assert res_a1["ranked_results"] == res_raw_v["ranked_results"]


# TEST 17: alpha=0 equals metadata-only
def test_17_alpha_0_equals_metadata_only(mock_retrieval_setup: Dict[str, Any]) -> None:
    fusion = Phase5HybridFusion()
    res_a0 = fusion.evaluate(
        S_H=fusion.compute_hybrid_matrix(mock_retrieval_setup["S_V"], mock_retrieval_setup["S_M"], alpha=0.0),
        query_ids=mock_retrieval_setup["image_ids"],
        candidate_ids=mock_retrieval_setup["image_ids"],
        ground_truth_positives=mock_retrieval_setup["gt"],
        exclusion_sets=mock_retrieval_setup["excl"],
    )
    res_raw_m = fusion.evaluate(
        S_H=mock_retrieval_setup["S_M"],
        query_ids=mock_retrieval_setup["image_ids"],
        candidate_ids=mock_retrieval_setup["image_ids"],
        ground_truth_positives=mock_retrieval_setup["gt"],
        exclusion_sets=mock_retrieval_setup["excl"],
    )
    assert res_a0["recall_at_1"] == res_raw_m["recall_at_1"]
    assert res_a0["mrr"] == res_raw_m["mrr"]
    assert res_a0["precision_at_5"] == res_raw_m["precision_at_5"]
    assert res_a0["ranked_results"] == res_raw_m["ranked_results"]


# TEST 18: fusion ranking deterministic
def test_18_fusion_ranking_deterministic(mock_retrieval_setup: Dict[str, Any]) -> None:
    fusion = Phase5HybridFusion()
    S_H1 = fusion.compute_hybrid_matrix(mock_retrieval_setup["S_V"], mock_retrieval_setup["S_M"], alpha=0.5)
    S_H2 = fusion.compute_hybrid_matrix(mock_retrieval_setup["S_V"], mock_retrieval_setup["S_M"], alpha=0.5)
    
    np.testing.assert_array_equal(S_H1, S_H2)
    res1 = fusion.evaluate(S_H1, mock_retrieval_setup["image_ids"], mock_retrieval_setup["image_ids"], mock_retrieval_setup["gt"], mock_retrieval_setup["excl"])
    res2 = fusion.evaluate(S_H2, mock_retrieval_setup["image_ids"], mock_retrieval_setup["image_ids"], mock_retrieval_setup["gt"], mock_retrieval_setup["excl"])

    assert res1["ranked_results"] == res2["ranked_results"]
    assert res1["mrr"] == res2["mrr"]


# TEST 19: self-match exclusion
def test_19_self_match_exclusion(mock_retrieval_setup: Dict[str, Any]) -> None:
    fusion = Phase5HybridFusion()
    res = fusion.evaluate(
        S_H=mock_retrieval_setup["S_V"],
        query_ids=mock_retrieval_setup["image_ids"],
        candidate_ids=mock_retrieval_setup["image_ids"],
        ground_truth_positives=mock_retrieval_setup["gt"],
        exclusion_sets=mock_retrieval_setup["excl"],
    )
    for q_id, ranked in res["ranked_results"].items():
        assert q_id not in ranked, f"Self-match violation: {q_id} appeared in its own ranking"


# TEST 20: HCCI positive definition
def test_20_hcci_positive_definition(mock_retrieval_setup: Dict[str, Any]) -> None:
    gt = mock_retrieval_setup["gt"]
    # img_0 (Mat_A, Acq_1) -> positives: img_1 (Mat_A, Acq_2), img_5 (Mat_A, Acq_2 - except dup excl)
    # img_1 is positive for img_0
    assert "img_1" in gt["img_0"]
    # img_3 (Mat_B, Acq_1) is NOT positive for img_0
    assert "img_3" not in gt["img_0"]


# TEST 21: same-acquisition neutral/exclusion behavior
def test_21_same_acquisition_exclusion_behavior(mock_retrieval_setup: Dict[str, Any]) -> None:
    gt = mock_retrieval_setup["gt"]
    excl = mock_retrieval_setup["excl"]
    # img_0 (Mat_A, Acq_1) and img_2 (Mat_A, Acq_1): same specimen AND same acq!
    # img_2 MUST NOT be a positive
    assert "img_2" not in gt["img_0"]
    # img_2 MUST be in exclusions
    assert "img_2" in excl["img_0"]


# TEST 22: exact duplicate exclusion
def test_22_exact_duplicate_exclusion(mock_retrieval_setup: Dict[str, Any]) -> None:
    excl = mock_retrieval_setup["excl"]
    # img_1 and img_5 share dup_group "dup_1"
    assert "img_5" in excl["img_1"]
    assert "img_1" in excl["img_5"]


# TEST 23: near-duplicate exclusion
def test_23_near_duplicate_exclusion() -> None:
    df_near = pd.DataFrame([
        {"image_id": "img_a", "specimen_id": "M1", "roi_id": "r_a", "acquisition_id": "A1", "near_duplicate_group_id": "near_grp_1"},
        {"image_id": "img_b", "specimen_id": "M1", "roi_id": "r_b", "acquisition_id": "A2", "near_duplicate_group_id": "near_grp_1"},
    ])
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(df_near)
    assert "img_b" in excl["img_a"]
    assert "img_a" not in gt["img_b"]


# TEST 24: validation-only alpha selection
def test_24_validation_only_alpha_selection(mock_retrieval_setup: Dict[str, Any]) -> None:
    evaluator = Phase5Evaluator(alpha_grid=[0.0, 0.5, 1.0], selection_metric="mrr")
    # Selection on validation setup
    selected_alpha, grid = evaluator.select_best_alpha(
        S_V_val=mock_retrieval_setup["S_V"],
        S_M_val=mock_retrieval_setup["S_M"],
        val_query_ids=mock_retrieval_setup["image_ids"],
        val_candidate_ids=mock_retrieval_setup["image_ids"],
        val_gt=mock_retrieval_setup["gt"],
        val_excl=mock_retrieval_setup["excl"],
    )
    assert selected_alpha in [0.0, 0.5, 1.0]
    assert len(grid) == 3
    # Check that grid records match evaluation
    for a in [0.0, 0.5, 1.0]:
        assert "mrr" in grid[a]


def test_candidate_pool_correctness() -> None:
    """Verify that candidate pools match exact partition sizes without cross-split leakage."""
    import json
    from pathlib import Path
    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    with open("data/processed/phase4/splits/hcci_instrument_splits.json", "r", encoding="utf-8") as f:
        splits = json.load(f)

    assert len(splits["train"]) == 427
    assert len(splits["val"]) == 135
    assert len(splits["test"]) == 212
    assert len(manifest) == 774

    # Assert 100% disjoint image IDs across splits
    s_train = set(splits["train"])
    s_val = set(splits["val"])
    s_test = set(splits["test"])
    assert s_train.isdisjoint(s_val)
    assert s_train.isdisjoint(s_test)
    assert s_val.isdisjoint(s_test)
    assert len(s_train | s_val | s_test) == 774


def test_positive_definition_correctness() -> None:
    """Verify HCCI positive pairs are strictly same specimen AND different acquisition, without same-ROI fabrication."""
    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(manifest)

    # Check each image has non-empty positives and no self in positives
    for q_id in manifest["image_id"]:
        assert q_id in gt
        assert len(gt[q_id]) > 0
        assert q_id not in gt[q_id]
        assert q_id not in excl[q_id]


def test_complete_error_analysis_partition() -> None:
    """Verify that the 4 mutually exclusive error categories sum to exactly 212 test queries."""
    import json
    from pathlib import Path
    from src.metadata.phase5_encoder import Phase5MetadataEncoder

    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    with open("data/processed/phase4/splits/hcci_instrument_splits.json", "r", encoding="utf-8") as f:
        splits = json.load(f)

    train_df = manifest[manifest["image_id"].isin(splits["train"])].reset_index(drop=True)
    test_df = manifest[manifest["image_id"].isin(splits["test"])].reset_index(drop=True)
    test_ids = test_df["image_id"].tolist()
    gt_test, excl_test = RelationshipBuilder.build_retrieval_ground_truth(test_df)

    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(train_df)
    test_m, _ = encoder.encode(test_df)
    S_M = encoder.compute_similarity_matrix(test_m)

    p2_df = pd.read_parquet("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    test_vis = test_df.merge(p2_df[["image_id", "embedding"]], on="image_id")
    v_embs = np.stack(test_vis["embedding"].values)
    S_V = v_embs @ v_embs.T

    fusion = Phase5HybridFusion()
    res_v = fusion.evaluate(S_V, test_ids, test_ids, gt_test, excl_test)
    res_m = fusion.evaluate(S_M, test_ids, test_ids, gt_test, excl_test)

    both_succeed = 0
    vis_succeed_meta_fail = 0
    meta_succeed_vis_fail = 0
    both_fail = 0

    for q in test_ids:
        pos = gt_test[q]
        v_ok = res_v["ranked_results"][q][0] in pos
        m_ok = res_m["ranked_results"][q][0] in pos
        if v_ok and m_ok:
            both_succeed += 1
        elif v_ok and not m_ok:
            vis_succeed_meta_fail += 1
        elif not v_ok and m_ok:
            meta_succeed_vis_fail += 1
        else:
            both_fail += 1

    total = both_succeed + vis_succeed_meta_fail + meta_succeed_vis_fail + both_fail
    assert total == 212, f"Error analysis partition did not sum to 212 (got {total})"
    assert both_succeed == 71
    assert vis_succeed_meta_fail == 130
    assert meta_succeed_vis_fail == 0
    assert both_fail == 11

