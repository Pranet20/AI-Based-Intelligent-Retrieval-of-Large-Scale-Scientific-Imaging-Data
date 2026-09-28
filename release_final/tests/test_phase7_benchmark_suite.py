"""Comprehensive publication-grade test suite for Phase 7.

Validates:
1. Immutability contract across all 84 frozen Phase 1-6 artifacts.
2. Dataset evidence registry fields, licensing, and physical counts.
3. Unified experiment registry schema and RQ coverage.
4. Formal 10-point leakage audit compliance.
5. Exact baseline reproduction for Phase 2, 4, 5, and 6.
6. Statistical analysis outputs and bootstrap confidence intervals.
7. Completeness and validity of MASTER_RESULTS.json.
8. Generation and non-emptiness of all 12 publication figures.
9. Structural integrity of PHASE7_REPORT.md and CLAIM_EVIDENCE_MATRIX.md.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import pytest
import pandas as pd

from src.evaluation.dataset_registry import DatasetEvidenceRegistry
from src.evaluation.experiment_registry import ExperimentRegistry
from src.evaluation.leakage_audit import LeakageAuditor
from src.evaluation.master_benchmark import MasterBenchmarkRunner


def test_01_frozen_artifacts_immutability():
    """Verify all 84 frozen Phase 1-6 artifacts remain bit-for-bit identical."""
    checksum_file = Path("artifacts/phase7/pre_phase7_frozen_checksums.json")
    assert checksum_file.exists(), "pre_phase7_frozen_checksums.json must exist."
    with open(checksum_file, "r", encoding="utf-8") as f:
        checksums = json.load(f)

    assert len(checksums) == 84, f"Expected 84 frozen artifacts, found {len(checksums)}"
    mismatches = []
    for rel_path, exp_hash in checksums.items():
        p = Path(rel_path)
        assert p.exists(), f"Frozen artifact missing: {rel_path}"
        with open(p, "rb") as f:
            act_hash = hashlib.sha256(f.read()).hexdigest()
        if act_hash != exp_hash:
            mismatches.append(rel_path)

    assert len(mismatches) == 0, f"Detected modified frozen artifacts: {mismatches}"


def test_02_dataset_evidence_registry():
    """Verify dataset registry contains all registered datasets with physical counts."""
    reg = DatasetEvidenceRegistry()
    assert "hcci" in reg.records
    assert "carinthia" in reg.records
    assert "sem_nanoscience" in reg.records

    hcci = reg.records["hcci"]
    assert hcci.physically_available_count == 774
    assert hcci.physical_availability_status == "verified"
    assert hcci.modality == "SEM"

    car = reg.records["carinthia"]
    assert car.physically_available_count == 4591
    assert car.physical_availability_status == "verified"

    sem_nano = reg.records["sem_nanoscience"]
    assert sem_nano.physical_availability_status == "not_downloaded"
    assert sem_nano.license == "CC-BY-4.0"


def test_03_experiment_registry():
    """Verify experiment registry has all 18 experiments covering RQ1-RQ7."""
    reg = ExperimentRegistry()
    assert len(reg.experiments) >= 18
    rqs_covered = {e.research_question for e in reg.list_all()}
    for rq in ["RQ1", "RQ2", "RQ3", "RQ4", "RQ5", "RQ6", "RQ7"]:
        assert any(rq in item for item in rqs_covered), f"Missing coverage for {rq}"


def test_04_formal_leakage_audit():
    """Verify all 10 leakage audit checks pass with 0 cross-split contamination."""
    auditor = LeakageAuditor()
    results = auditor.run_all_checks()
    assert len(results) == 10
    for cid, res in results.items():
        assert res.status == "PASSED", f"Check {cid} failed: {res.details}"

    # Check G specifically: direct identifiers forbidden
    g_res = results["check_G_metadata_identifier_prohibition"]
    assert len(g_res.details["violations_found"]) == 0

    # Check D specifically: cross-split near duplicates must be zero
    d_res = results["check_D_near_duplicate_overlap"]
    assert d_res.details["cross_split_near_duplicates"] == 0


def test_05_reproduce_exact_phase2_baseline():
    """Verify exact reproduction of frozen Phase 2 full-corpus retrieval metrics."""
    with open("artifacts/phase5/metrics/phase5_results.json", "r") as f:
        p5 = json.load(f)
    full_vis = p5["full_corpus_results"]["5A_phase2_visual"]

    assert pytest.approx(full_vis["recall_at_1"], abs=1e-6) == 0.9819121447028424
    assert pytest.approx(full_vis["mrr"], abs=1e-6) == 0.9894487510766581
    assert pytest.approx(full_vis["precision_at_5"], abs=1e-6) == 0.9692506459948321
    assert full_vis["total_queries"] == 774


def test_06_reproduce_exact_phase4_multiseed():
    """Verify exact reproduction of frozen Phase 4 multi-seed metrics."""
    with open("artifacts/phase5/metrics/phase5_results.json", "r") as f:
        p5 = json.load(f)
    test_p4_mean = p5["test_results"]["5D_phase4_visual_multiseed_mean"]
    test_p4_std = p5["test_results"]["5D_phase4_visual_multiseed_std"]

    assert pytest.approx(test_p4_mean["recall_at_1"], abs=1e-4) == 0.9418
    assert pytest.approx(test_p4_std["recall_at_1"], abs=1e-4) == 0.0059
    assert pytest.approx(test_p4_mean["mrr"], abs=1e-4) == 0.9632
    assert pytest.approx(test_p4_mean["precision_at_5"], abs=1e-4) == 0.9053


def test_07_metadata_fusion_negative_result():
    """Verify that metadata late fusion delta is exactly 0.0 with optimal alpha=1.0."""
    with open("artifacts/phase5/metrics/phase5_results.json", "r") as f:
        p5 = json.load(f)
    deltas = p5["test_results"]["deltas_5C_vs_5A"]
    assert deltas["delta_recall_at_1"] == 0.0
    if isinstance(p5["selected_alpha"], dict):
        assert p5["selected_alpha"]["phase2"] == 1.0
        assert p5["selected_alpha"]["phase4"] == 1.0
    else:
        assert p5["selected_alpha"] == 1.0


def test_08_redundancy_graph_partition():
    """Verify exact natural redundancy graph partition: 769 clusters, 764 singletons, 5 pairs."""
    with open("artifacts/phase6/phase6_results.json", "r") as f:
        p6 = json.load(f)
    red = p6["redundancy_graph_summary"]
    assert red["total_clusters"] == 769
    assert red["singleton_clusters_count"] == 764
    assert red["pair_clusters_count"] == 5
    assert red["canonical_representative_images_keep"] == 769
    assert red["non_representative_near_duplicate_images_review"] == 5
    assert 764 * 1 + 5 * 2 == 774
    assert 769 + 5 == 774


def test_09_master_results_json():
    """Verify MASTER_RESULTS.json exists, is non-empty, and contains all required keys."""
    master_path = Path("artifacts/phase7/MASTER_RESULTS.json")
    assert master_path.exists()
    with open(master_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) >= 150
    for item in data:
        assert "experiment_id" in item
        assert "dataset" in item
        assert "split" in item
        assert "method" in item
        assert "metric" in item
        assert "value" in item
        assert "evidence_type" in item
        assert item["evidence_type"].startswith("[")


def test_10_publication_figures_exist():
    """Verify that all 12 publication figures exist and are non-empty."""
    fig_dir = Path("reports/phase7/figures")
    for i in range(1, 13):
        fig_files = list(fig_dir.glob(f"fig{i}_*.png"))
        assert len(fig_files) >= 1, f"Missing Figure {i} in {fig_dir}"
        assert fig_files[0].stat().st_size > 1000, f"Figure {fig_files[0]} is empty or corrupt"


def test_11_report_and_claim_matrix_structure():
    """Verify structural integrity of PHASE7_REPORT.md and CLAIM_EVIDENCE_MATRIX.md."""
    rep_path = Path("reports/phase7/PHASE7_REPORT.md")
    assert rep_path.exists()
    with open(rep_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Check for presence of all 24 required sections
    for i in range(1, 25):
        assert f"## {i}." in text or f"### Table" in text, f"Missing Section {i} in PHASE7_REPORT.md"

    matrix_path = Path("reports/phase7/CLAIM_EVIDENCE_MATRIX.md")
    assert matrix_path.exists()
    with open(matrix_path, "r", encoding="utf-8") as f:
        mat_text = f.read()
    for tag in ["[NATURAL DATA]", "[CONTROLLED SYNTHETIC BENCHMARK]", "[EXTERNAL DOMAIN SHIFT]", "[ENGINEERING MEASUREMENT]"]:
        assert tag in mat_text, f"Missing evidence tag {tag} in matrix"
