"""Regression and reproducibility baseline tests for Phase 5 (Tests 25-27)."""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.adaptation.relationship_builder import RelationshipBuilder
from src.retrieval.phase5_evaluator import Phase5Evaluator


# TEST 25: Phase 2 baseline reproduction
def test_25_phase2_baseline_reproduction() -> None:
    manifest_path = Path("data/manifests/hcci_manifest.parquet")
    emb_path = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    
    assert manifest_path.exists(), f"Missing manifest {manifest_path}"
    assert emb_path.exists(), f"Missing Phase 2 embeddings {emb_path}"

    df = pd.read_parquet(manifest_path)
    emb_df = pd.read_parquet(emb_path)
    merged = df.merge(emb_df[["image_id", "embedding"]], on="image_id").reset_index(drop=True)

    embeddings = np.stack(merged["embedding"].values)
    image_ids = merged["image_id"].tolist()
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(merged)

    evaluator = Phase5Evaluator()
    S_V = embeddings @ embeddings.T
    res = evaluator.evaluate_at_alpha(
        S_V=S_V,
        S_M=np.zeros_like(S_V),
        alpha=1.0,
        query_ids=image_ids,
        candidate_ids=image_ids,
        gt_positives=gt,
        exclusions=excl,
    )

    # Machine-precision comparison to frozen Phase 2 report
    expected_r1 = 0.9819121447028424
    expected_mrr = 0.9894487510766581
    expected_p5 = 0.9692506459948321

    assert np.isclose(res["recall_at_1"], expected_r1, atol=1e-6), f"R@1 mismatch: {res['recall_at_1']} vs {expected_r1}"
    assert np.isclose(res["recall_at_5"], 1.0, atol=1e-6)
    assert np.isclose(res["recall_at_10"], 1.0, atol=1e-6)
    assert np.isclose(res["mrr"], expected_mrr, atol=1e-6), f"MRR mismatch: {res['mrr']} vs {expected_mrr}"
    assert np.isclose(res["precision_at_5"], expected_p5, atol=1e-6), f"P@5 mismatch: {res['precision_at_5']} vs {expected_p5}"


# TEST 26: Phase 4 baseline reproduction (Multi-Seed & Seed 42)
def test_26_phase4_baseline_reproduction() -> None:
    manifest_path = Path("data/manifests/hcci_manifest.parquet")
    splits_path = Path("data/processed/phase4/splits/hcci_instrument_splits.json")
    emb_dir = Path("data/processed/phase4/embeddings")

    assert manifest_path.exists()
    assert splits_path.exists()
    assert (emb_dir / "hcci_adapted_proposed_seed42.parquet").exists()
    assert (emb_dir / "hcci_adapted_proposed_seed123.parquet").exists()
    assert (emb_dir / "hcci_adapted_proposed_seed2024.parquet").exists()

    df = pd.read_parquet(manifest_path)
    with open(splits_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    test_df = df[df["image_id"].isin(splits["test"])].reset_index(drop=True)
    test_ids = test_df["image_id"].tolist()
    gt_test, excl_test = RelationshipBuilder.build_retrieval_ground_truth(test_df)
    evaluator = Phase5Evaluator()

    # 1. Baseline DINOv2 on held-out Zeiss Gemini (N=212)
    p2_path = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    p2_df = pd.read_parquet(p2_path)
    merged_p2 = test_df.merge(p2_df[["image_id", "embedding"]], on="image_id")
    v_p2 = np.stack(merged_p2["embedding"].values)
    res_p2 = evaluator.evaluate_at_alpha(
        S_V=v_p2 @ v_p2.T,
        S_M=np.zeros((len(test_ids), len(test_ids))),
        alpha=1.0,
        query_ids=test_ids,
        candidate_ids=test_ids,
        gt_positives=gt_test,
        exclusions=excl_test,
    )
    assert np.isclose(res_p2["recall_at_1"], 0.9481132, atol=1e-4)
    assert np.isclose(res_p2["mrr"], 0.9658019, atol=1e-4)
    assert np.isclose(res_p2["precision_at_5"], 0.8707547, atol=1e-4)
    assert np.isclose(res_p2["precision_at_10"], 0.7415094, atol=1e-4)

    # 2. Phase 4 Multi-Seed Evaluation across seeds 42, 123, 2024
    seed_results = {}
    for seed in [42, 123, 2024]:
        emb_file = emb_dir / f"hcci_adapted_proposed_seed{seed}.parquet"
        emb_df = pd.read_parquet(emb_file)
        merged = test_df.merge(emb_df[["image_id", "embedding"]], on="image_id")
        embs = np.stack(merged["embedding"].values)
        res = evaluator.evaluate_at_alpha(
            S_V=embs @ embs.T,
            S_M=np.zeros((len(test_ids), len(test_ids))),
            alpha=1.0,
            query_ids=test_ids,
            candidate_ids=test_ids,
            gt_positives=gt_test,
            exclusions=excl_test,
        )
        seed_results[seed] = res

    # Seed 42 reproduction
    res_42 = seed_results[42]
    assert np.isclose(res_42["recall_at_1"], 0.9433962, atol=1e-4)
    assert np.isclose(res_42["mrr"], 0.9641509, atol=1e-4)
    assert np.isclose(res_42["precision_at_5"], 0.8820755, atol=1e-4)
    assert np.isclose(res_42["precision_at_10"], 0.7877358, atol=1e-4)

    # Multi-seed mean reproduction (matching frozen Phase 4 Table 2 exactly)
    r1_mean = float(np.mean([seed_results[s]["recall_at_1"] for s in [42, 123, 2024]]))
    mrr_mean = float(np.mean([seed_results[s]["mrr"] for s in [42, 123, 2024]]))
    p5_mean = float(np.mean([seed_results[s]["precision_at_5"] for s in [42, 123, 2024]]))
    p10_mean = float(np.mean([seed_results[s]["precision_at_10"] for s in [42, 123, 2024]]))

    assert np.isclose(r1_mean, 0.9418, atol=1e-3)
    assert np.isclose(mrr_mean, 0.9632, atol=1e-3)
    assert np.isclose(p5_mean, 0.9053, atol=1e-3)
    assert np.isclose(p10_mean, 0.8186, atol=1e-3)


# TEST 27: repeated execution gives identical results
def test_27_repeated_execution_determinism() -> None:
    manifest_path = Path("data/manifests/hcci_manifest.parquet")
    emb_path = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    
    df = pd.read_parquet(manifest_path)
    emb_df = pd.read_parquet(emb_path)
    merged = df.merge(emb_df[["image_id", "embedding"]], on="image_id").head(50).reset_index(drop=True)

    embeddings = np.stack(merged["embedding"].values)
    image_ids = merged["image_id"].tolist()
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(merged)

    evaluator = Phase5Evaluator()
    S_V = embeddings @ embeddings.T

    res1 = evaluator.evaluate_at_alpha(S_V, np.zeros_like(S_V), alpha=1.0, query_ids=image_ids, candidate_ids=image_ids, gt_positives=gt, exclusions=excl)
    res2 = evaluator.evaluate_at_alpha(S_V, np.zeros_like(S_V), alpha=1.0, query_ids=image_ids, candidate_ids=image_ids, gt_positives=gt, exclusions=excl)

    assert res1["mrr"] == res2["mrr"]
    assert res1["recall_at_1"] == res2["recall_at_1"]
    assert res1["ranked_results"] == res2["ranked_results"]
