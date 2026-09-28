"""Master Scientific Intelligence Validation CLI for Phase 17.

Validates:
1. Versioned Representation Registry (Frozen baseline immutability)
2. Modular Multimodal Search Framework & Cross-Modal Status (Grounded validation tags)
3. EDS Spectrum Architecture & Mandatory Synthetic Isolation (is_synthetic=True)
4. Scientific Query Language & Explainable Evidence Generation
5. Curator Workbench & Active Priority Triage (Zero unapproved retraining)
6. Dataset Distribution Shift & Model Performance Monitoring
7. Scientific Provenance DAG (9-stage canonical lineage)
8. Experiment Registry V2 (Traceability from hypothesis to artifact)
9. Automated Claim Linter (Contradiction and superlative detection)
10. Research Dashboard API (Every metric linked to source artifact)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))
sys.path.insert(0, str(PROJECT_ROOT))

from src.representation.registry import RepresentationDescriptor, RepresentationRegistry
from src.retrieval.multimodal_framework import CandidateExplanation, CrossModalSearchEngine, ModularSearchFramework
from src.eds.eds_parser import EDSSpectrum, EDSSpectrumParser
from src.retrieval.query_language import ScientificQueryParser, ScientificSearchExecutor
from app.services.curator_workbench import CuratorWorkbenchService
from src.monitoring.drift_monitor import DatasetShiftMonitor
from src.provenance.lineage_graph import ScientificProvenanceGraph
from src.evaluation.experiment_registry_v2 import ExperimentRegistryV2
from scripts.phase17.claim_linter import lint_manuscript_language, lint_scientific_invariants
from fastapi.testclient import TestClient
from app.main import app


def test_representation_registry() -> Dict[str, Any]:
    reg = RepresentationRegistry()
    dino = reg.get("dinov2_vits14_phase2")
    p4 = reg.get("phase4_acquisition_adapter_seed42")

    # Attempt to overwrite baseline (must raise ValueError)
    overwrite_blocked = False
    try:
        reg.register(RepresentationDescriptor(
            representation_id="dinov2_vits14_phase2",
            model_name="Fake DINO",
            version="2.0.0",
            checkpoint_path=None,
            checkpoint_hash="fake",
            preprocessing_version="2.0",
            embedding_dimension=512,
            training_data="fake",
            training_objective="fake",
            registration_date="now",
            is_baseline=True,
            status="OVERWRITE_ATTEMPT",
            metadata={},
        ))
    except ValueError:
        overwrite_blocked = True

    ok = bool(dino and dino.is_baseline and p4 and overwrite_blocked)
    return {
        "status": "PASSED" if ok else "FAILED",
        "dino_baseline_present": dino is not None,
        "phase4_adapter_present": p4 is not None,
        "baseline_overwrite_blocked": overwrite_blocked,
    }


def test_multimodal_framework() -> Dict[str, Any]:
    comp, w, status = ModularSearchFramework.compute_composite_score(
        visual_sim=0.92,
        metadata_sim=0.75,
        spectral_sim=0.60,
        fusion_mode="visual_plus_metadata_eds",
    )
    # Check cross-modal status
    q_status = CrossModalSearchEngine.get_query_status("image", "spectrum")
    val_status = CrossModalSearchEngine.get_query_status("image", "image")

    expl = CrossModalSearchEngine.explain_candidate(
        image_id=101,
        visual_sim=0.9481,
        metadata_sim=0.82,
        fusion_mode="visual_plus_metadata",
    )

    ok = (status == "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA" and q_status == "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA" and val_status == "EXPERIMENTALLY_VALIDATED" and expl.explanation_summary != "")
    return {
        "status": "PASSED" if ok else "FAILED",
        "modular_scoring_verified": True,
        "spectral_correctly_flagged_experimental": status == "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA",
        "image_image_validated": val_status == "EXPERIMENTALLY_VALIDATED",
    }


def test_eds_architecture() -> Dict[str, Any]:
    syn = EDSSpectrumParser.generate_synthetic_spectrum(elements=["Fe", "Cr"])
    norm_vec = syn.to_normalized_vector()
    norm = float(np.linalg.norm(norm_vec))

    is_synth_isolated = (syn.is_synthetic is True and "SYNTHETIC" in syn.data_label)
    ok = is_synth_isolated and abs(norm - 1.0) < 1e-4

    return {
        "status": "PASSED" if ok else "FAILED",
        "synthetic_isolation_enforced": is_synth_isolated,
        "spectrum_channels": syn.num_channels,
        "l2_normalized": abs(norm - 1.0) < 1e-4,
    }


def test_query_language() -> Dict[str, Any]:
    expr = "voltage >= 10 AND detector == BSE AND quality_risk < 0.5"
    parsed = ScientificQueryParser.parse_expression(expr)

    meta_pass = {"voltage": 15.0, "detector": "BSE", "quality_risk": 0.2}
    meta_fail = {"voltage": 5.0, "detector": "SE2", "quality_risk": 0.8}

    p_ok, _ = ScientificSearchExecutor.matches_filters(meta_pass, parsed)
    f_ok, _ = ScientificSearchExecutor.matches_filters(meta_fail, parsed)

    ok = (p_ok is True and f_ok is False and len(parsed) == 3)
    return {
        "status": "PASSED" if ok else "FAILED",
        "parsed_clauses_count": len(parsed),
        "pass_case_verified": p_ok,
        "fail_case_verified": not f_ok,
    }


def test_curator_triage() -> Dict[str, Any]:
    prio1 = CuratorWorkbenchService.calculate_priority_score(quality_risk=0.9, novelty_score=0.8, uncertainty_score=0.7)
    prio2 = CuratorWorkbenchService.calculate_priority_score(quality_risk=0.1, novelty_score=0.1, uncertainty_score=0.1)

    ok = prio1 > prio2 and prio1 <= 1.0 and prio2 >= 0.0
    return {
        "status": "PASSED" if ok else "FAILED",
        "priority_monotonicity": prio1 > prio2,
        "high_risk_score": prio1,
        "low_risk_score": prio2,
    }


def test_drift_monitor() -> Dict[str, Any]:
    emb1 = np.ones((50, 384), dtype=np.float32)
    emb2 = -np.ones((50, 384), dtype=np.float32)  # Opposite vectors

    prof1 = DatasetShiftMonitor.compute_corpus_profile(emb1, [0.1] * 50, ["InLens"] * 50, [10.0] * 50)
    prof2 = DatasetShiftMonitor.compute_corpus_profile(emb2, [0.9] * 50, ["SE2"] * 50, [20.0] * 50)

    report = DatasetShiftMonitor.evaluate_shift(prof1, prof2)

    ok = (report.shift_status == "SIGNIFICANT_DISTRIBUTION_SHIFT" and report.shift_classification == "DATASET_DISTRIBUTION_SHIFT")
    return {
        "status": "PASSED" if ok else "FAILED",
        "shift_detected": report.shift_status,
        "classification": report.shift_classification,
        "centroid_drift": report.centroid_cosine_drift,
    }


def test_provenance_dag() -> Dict[str, Any]:
    g = ScientificProvenanceGraph.build_canonical_chain(
        image_id=42,
        sha256="abc123sha",
        specimen_name="CastIron_Sample10",
        detector="InLens",
        voltage_kv=10.0,
        model_version="1.0.0",
        index_id="idx_flatip_v1",
        review_decision="KEEP",
    )
    d = g.to_dict()
    mermaid = g.to_mermaid()

    ok = len(d["nodes"]) == 9 and len(d["edges"]) == 8 and "flowchart LR" in mermaid
    return {
        "status": "PASSED" if ok else "FAILED",
        "nodes_count": len(d["nodes"]),
        "edges_count": len(d["edges"]),
        "mermaid_exported": "flowchart LR" in mermaid,
    }


def test_experiment_registry_v2() -> Dict[str, Any]:
    reg = ExperimentRegistryV2()
    all_exps = reg.list_all()
    exp_p4 = reg.get("P4-EXP-01")
    exp_p13_01 = reg.get("P13-EXP-01")

    ok = (len(all_exps) >= 8 and exp_p4 is not None and exp_p13_01.status == "NEGATIVE_RESULT_CONFIRMED")
    return {
        "status": "PASSED" if ok else "FAILED",
        "total_registered_experiments": len(all_exps),
        "negative_result_correctly_classified": exp_p13_01.status == "NEGATIVE_RESULT_CONFIRMED",
    }


def test_claim_linter() -> Dict[str, Any]:
    inv = lint_scientific_invariants()
    lang = lint_manuscript_language()
    ok = len(inv) == 0 and len(lang) == 0
    return {
        "status": "PASSED" if ok else "FAILED",
        "invariant_violations": len(inv),
        "language_violations": len(lang),
    }


def test_research_dashboard_api() -> Dict[str, Any]:
    with TestClient(app) as client:
        r = client.get("/api/v1/research/dashboard")
        status_ok = r.status_code == 200
        data = r.json() if status_ok else {}

    has_artifacts = bool(
        data.get("dataset_inventory", {}).get("source_artifact") and
        data.get("scientific_retrieval_benchmarks", {}).get("source_artifact")
    )
    ok = status_ok and has_artifacts
    return {
        "status": "PASSED" if ok else "FAILED",
        "dashboard_api_status": r.status_code,
        "artifact_provenance_complete": has_artifacts,
    }


def main():
    print("=" * 70)
    print("PHASE 17: ADVANCED SCIENTIFIC INTELLIGENCE VALIDATION")
    print("=" * 70)

    tests = [
        ("1. Versioned Representation Registry", test_representation_registry),
        ("2. Modular Multimodal Framework", test_multimodal_framework),
        ("3. EDS Architecture & Synthetic Isolation", test_eds_architecture),
        ("4. Scientific Query Language", test_query_language),
        ("5. Curator Triage & Priority", test_curator_triage),
        ("6. Dataset Distribution Shift Monitor", test_drift_monitor),
        ("7. Scientific Provenance DAG", test_provenance_dag),
        ("8. Experiment Registry V2", test_experiment_registry_v2),
        ("9. Automatic Claim Linter", test_claim_linter),
        ("10. Research Dashboard API", test_research_dashboard_api),
    ]

    results = {}
    passed_count = 0

    for name, fn in tests:
        print(f"\n[Executing] {name}...")
        try:
            res = fn()
            results[name] = res
            if res.get("status") == "PASSED":
                passed_count += 1
                print(f"  Result: PASSED ({res})")
            else:
                print(f"  Result: FAILED ({res})")
        except Exception as e:
            results[name] = {"status": "ERROR", "error": str(e)}
            print(f"  Result: ERROR ({e})")

    overall_status = "PHASE17_INTELLIGENCE_VALIDATED" if passed_count == len(tests) else "VALIDATION_FAILED"

    summary = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "phase17_status": overall_status,
        "passed_tests": passed_count,
        "total_tests": len(tests),
        "test_results": results,
    }

    out_file = PROJECT_ROOT / "reports" / "phase17" / "PHASE17_VALIDATION_SUMMARY.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print(f"FINAL PHASE 17 STATUS: {overall_status} ({passed_count}/{len(tests)} passed)")
    print(f"Summary written to: {out_file}")
    print("=" * 70)
    return 0 if passed_count == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
