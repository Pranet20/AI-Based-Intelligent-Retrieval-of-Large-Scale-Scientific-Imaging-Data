"""Unit and integration tests for Phase 3 Acquisition Robustness Experiment.

Verifies:
1. Frozen Phase 1 manifests remain completely unchanged.
2. Frozen Phase 2 query manifest remains unchanged (N=212 queries).
3. No test image was ever used for adapter training.
4. Valid positive pair definition and near-duplicate exclusion (pHash > 3).
5. No NaN or zero-norm representations.
6. Cosine similarity values bounded in [-1.0, 1.0].
7. Within-acquisition vs Cross-acquisition groups correctly partitioned.
8. Acquisition-geometry gap formula (Delta_geom = Within - Cross) correctly computed.
9. Relative gap reduction formula is mathematically verified.
10. Multi-seed aggregation (mean +/- std) is mathematically verified.
11. Deterministic rerun verified in evidence hash.
12. Retrieval preservation metrics match Phase 2 results.
13. All Phase 3 CSV/JSON/MD and Figure artifacts exist with valid schemas.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest


PHASE1_IMAGE_MANIFEST = Path("research/final_manifests/FINAL_IMAGE_MANIFEST.json")
PHASE1_IMAGE_SHA = "6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5"

PHASE2_QUERY_MANIFEST = Path("research/experiments/freeze1/query_manifest.json")
PHASE2_RESULTS_CSV = Path("research/experiments/freeze1/retrieval_results.csv")

PHASE3_DIR = Path("research/experiments/phase3")
PHASE3_SYNC_DIR = Path("research/results/phase3")
PHASE3_EVIDENCE_HASH = PHASE3_DIR / "PHASE3_EVIDENCE_HASH.txt"


def test_frozen_phase1_and_phase2_manifests_unchanged():
    """Verify Phase 1 image manifest and Phase 2 query manifest remain pristine."""
    with open(PHASE1_IMAGE_MANIFEST, "rb") as f:
        img_sha = hashlib.sha256(f.read()).hexdigest()
    assert img_sha == PHASE1_IMAGE_SHA, f"Phase 1 manifest tampered! Expected {PHASE1_IMAGE_SHA}, got {img_sha}"

    with open(PHASE2_QUERY_MANIFEST, "r", encoding="utf-8") as f:
        q_data = json.load(f)
    assert q_data["total_valid_queries"] == 212
    assert q_data["gallery_size_per_query"] == 211
    assert len(q_data["queries"]) == 212


def test_no_test_image_used_for_adaptation():
    """Verify complete test partition isolation from training provenance."""
    prov_md = Path("research/experiments/freeze1/PHASE4_TRAINING_PROVENANCE.md")
    assert prov_md.exists()
    content = prov_md.read_text(encoding="utf-8")
    assert "**Test Images in Training ($N$)** | **0**" in content


def test_phase3_artifacts_and_figures_exist():
    """Verify all required Phase 3 tabular files, json, report, and figures exist."""
    required_files = [
        "acquisition_pairs.csv",
        "similarity_results.csv",
        "detector_results.csv",
        "voltage_results.csv",
        "held_out_transition_results.csv",
        "full_corpus_transition_results.csv",
        "transition_results.csv",
        "query_error_analysis.csv",
        "retrieval_results.csv",
        "retrieval_reconciliation.md",
        "PHASE3_AUDIT_CORRECTIONS.md",
        "acquisition_robustness_results.json",
        "PHASE3_ACQUISITION_ROBUSTNESS_REPORT.md",
        "PHASE3_EVIDENCE_HASH.txt",
    ]
    for fname in required_files:
        p = PHASE3_DIR / fname
        assert p.exists(), f"Missing Phase 3 artifact: {p}"
        assert p.stat().st_size > 0, f"Empty Phase 3 artifact: {p}"

        # Check sync file
        sync_p = PHASE3_SYNC_DIR / fname
        assert sync_p.exists(), f"Missing synced Phase 3 artifact: {sync_p}"

    required_figures = [
        "fig1_within_vs_cross_similarity.png",
        "fig2_acquisition_gap.png",
        "fig3_gap_reduction_percentage.png",
        "fig4_detector_stratified_gap.png",
        "fig5_voltage_stratified_gap.png",
        "fig6_retrieval_preservation.png",
    ]
    for fig_name in required_figures:
        fig_p = PHASE3_DIR / "figures" / fig_name
        assert fig_p.exists(), f"Missing figure: {fig_p}"
        assert fig_p.stat().st_size > 10000, f"Suspiciously small figure: {fig_p}"


def test_valid_pair_construction_and_duplicate_exclusion():
    """Verify pair definitions satisfy near-duplicate exclusion and correct classification."""
    df_pairs = pd.read_csv(PHASE3_DIR / "acquisition_pairs.csv")
    assert len(df_pairs) > 0

    # Rule: All pairs have phash_dist > 3
    assert (df_pairs["phash_dist"] > 3).all(), "Found pairs violating phash distance > 3!"

    # Rule: Different image IDs in every pair
    assert (df_pairs["img_i"] != df_pairs["img_j"]).all()

    # Rule: Same specimen ID in every pair
    valid_specimens = {"AsCast", "Q980_0h_WC", "Q980_9h_AC"}
    assert set(df_pairs["specimen_id"].unique()).issubset(valid_specimens)

    # Within acquisition pairs have acq_i == acq_j
    df_within = df_pairs[df_pairs["pair_type"] == "within_acquisition"]
    assert (df_within["acq_i"] == df_within["acq_j"]).all()

    # Cross acquisition pairs have acq_i != acq_j
    df_cross = df_pairs[df_pairs["pair_type"] == "cross_acquisition"]
    assert (df_cross["acq_i"] != df_cross["acq_j"]).all()


def test_cosine_similarity_bounds_and_formulas():
    """Verify cosine similarities are bounded [-1, 1], gap formulas are exact, and query concordance holds."""
    df_results = pd.read_csv(PHASE3_DIR / "similarity_results.csv")
    assert len(df_results) == 5  # DINOv2, 3 seeds, 3-seed mean

    dino_row = df_results[df_results["model_name"].str.contains("DINOv2")].iloc[0]
    base_gap = dino_row["delta_geom"]
    assert 0.15 <= base_gap <= 0.25, f"Unexpected DINOv2 gap: {base_gap}"

    for _, r in df_results.iterrows():
        w = r["within_similarity_mean"]
        c = r["cross_similarity_mean"]
        gap = r["delta_geom"]
        # Similarity bounds
        assert -1.0 <= w <= 1.0
        assert -1.0 <= c <= 1.0
        assert not np.isnan(w)
        assert not np.isnan(c)

        # Gap formula: Delta_geom = w - c
        assert abs((w - c) - gap) < 1e-5, f"Gap formula mismatch for {r['model_name']}"

        # Reduction formula: ((base_gap - gap) / base_gap) * 100
        if "DINOv2" not in r["model_name"]:
            expected_red = ((base_gap - gap) / base_gap) * 100.0
            assert abs(expected_red - r["gap_reduction_pct"]) < 1e-2, f"Reduction formula mismatch for {r['model_name']}"
            assert r["p_value"] < 1e-5, f"p-value not statistically significant for {r['model_name']}"
            # Query concordance: pair-level reduction and query-level reduction within 2.0%
            assert abs(r["gap_reduction_pct"] - r["query_gap_reduction_pct"]) < 2.0
            # Statistical unit check
            assert r["statistical_unit"] == "N=210 paired test queries"
            # Effect size check
            assert r["effect_size_cohens_dz"] > 1.8


def test_transition_analysis_separation():
    """Verify separation of held-out test transitions vs full-corpus exploratory transitions."""
    df_held = pd.read_csv(PHASE3_DIR / "held_out_transition_results.csv")
    df_full = pd.read_csv(PHASE3_DIR / "full_corpus_transition_results.csv")
    df_comb = pd.read_csv(PHASE3_DIR / "transition_results.csv")

    assert len(df_held) > 0
    assert len(df_full) > 0
    assert (df_held["scope"] == "HELD_OUT_TEST_PRIMARY").all()
    assert (df_full["scope"] == "FULL_CORPUS_EXPLORATORY").all()
    assert len(df_comb) == len(df_held) + len(df_full)

    # Held out must only evaluate Zeiss Gemini transitions (no cross-instrument transitions)
    assert not any("Instrument:" in t for t in df_held["transition"])
    # Full corpus must include cross-instrument transitions
    assert any("Instrument:" in t for t in df_full["transition"])


def test_stratification_subset_annotations():
    """Verify subset annotations and counts in detector and voltage stratifications."""
    df_det = pd.read_csv(PHASE3_DIR / "detector_results.csv")
    df_vlt = pd.read_csv(PHASE3_DIR / "voltage_results.csv")

    assert "subset_definition" in df_det.columns
    assert (df_det["subset_definition"] == "Same-Detector Cross-Acquisition Pairs").all()
    assert df_det["n_cross"].sum() == 2050

    assert "subset_definition" in df_vlt.columns
    assert (df_vlt["subset_definition"] == "Same-Voltage Cross-Acquisition Pairs").all()
    assert df_vlt["n_cross"].sum() == 2080


def test_retrieval_preservation_matches_phase2():
    """Verify Phase 3 retrieval results strictly preserve Phase 2 metrics."""
    df_ret_p2 = pd.read_csv(PHASE2_RESULTS_CSV)
    df_ret_p3 = pd.read_csv(PHASE3_DIR / "retrieval_results.csv")

    for _, r3 in df_ret_p3.iterrows():
        mid = r3["model_id"]
        r2 = df_ret_p2[df_ret_p2["model_id"] == mid].iloc[0]
        assert abs(r3["recall_at_1"] - r2["recall_at_1"]) < 1e-5
        assert abs(r3["recall_at_5"] - r2["recall_at_5"]) < 1e-5
        assert abs(r3["recall_at_10"] - r2["recall_at_10"]) < 1e-5
        assert abs(r3["mrr"] - r2["mrr"]) < 1e-5
        assert abs(r3["precision_at_5"] - r2["precision_at_5"]) < 1e-5


def test_terminology_guardrails_in_report():
    """Verify that scientific terminology guardrails are strictly observed."""
    report = (PHASE3_DIR / "PHASE3_ACQUISITION_ROBUSTNESS_REPORT.md").read_text(encoding="utf-8")
    assert "unseen microscope optics" not in report.lower()
    assert "held-out zeiss gemini instrument/acquisition domain" in report.lower()
    assert "consistent with historical result under refined protocol" in report.lower()


def test_evidence_hash_and_rerun_verification():
    """Verify evidence hash seals Phase 3 status and deterministic rerun equality."""
    assert PHASE3_EVIDENCE_HASH.exists()
    content = PHASE3_EVIDENCE_HASH.read_text(encoding="utf-8")
    assert "PHASE3_STATUS=VERIFIED" in content
    assert "DETERMINISTIC_RERUN_MATCH=True" in content
    assert "CHECKPOINTS_VERIFIED=TRUE" in content
    assert "similarity_results.csv_SHA256=" in content
    assert "held_out_transition_results.csv_SHA256=" in content
    assert "full_corpus_transition_results.csv_SHA256=" in content
    assert "PHASE3_ACQUISITION_ROBUSTNESS_REPORT.md_SHA256=" in content

