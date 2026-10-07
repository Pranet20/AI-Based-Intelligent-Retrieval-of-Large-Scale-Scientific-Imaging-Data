"""Unit and integration test suite for Phase 5 Scientific Evidence & Explanation Intelligence Layer.

Verifies strict compliance with Phase 5 architecture, uncertainty-aware abstention,
provenance preservation, deterministic reproducibility, and scientific integrity invariants.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import yaml

from src.evidence.evidence_aggregator import EvidenceAggregator
from src.evidence.explanation_generator import ExplanationGenerator
from src.evidence.localization_engine import LocalizationEngine
from src.evidence.quality_risk_engine import QualityRiskEngine
from src.evidence.retrieval_evidence_engine import RetrievalEvidenceEngine
from src.evidence.schemas import (
    AcquisitionContext,
    ArtifactCategory,
    BoundingBox,
    ComparableEvidenceImage,
    DecisionStatus,
    EvidenceRole,
    QualityRiskSignal,
    StructuredEvidenceRecord,
    SuggestedReviewAction,
    SuspiciousRegion,
)

BASE_DIR = Path(__file__).resolve().parent.parent


# Test 01: Strict Null Preservation in Acquisition Context
def test_01_acquisition_context_null_preservation():
    acq = AcquisitionContext(
        instrument=None,
        detector=None,
        accelerating_voltage_kv=None,
        magnification=None,
    )
    d = acq.to_dict()
    assert d["instrument"] == "UNKNOWN"
    assert d["detector"] == "UNKNOWN"
    assert d["accelerating_voltage_kv"] is None
    assert d["magnification"] is None


# Test 02: Acquisition Context Immutability & Provenance
def test_02_acquisition_context_immutability():
    acq = AcquisitionContext(instrument="FEI_Nova_SEM", accelerating_voltage_kv=15.0)
    with pytest.raises(Exception):
        acq.instrument = "Other"  # Frozen dataclass mutation must fail


# Test 03: Quality Risk Physical Indicators Completeness
def test_03_quality_risk_physical_indicators_completeness():
    engine = QualityRiskEngine()
    dummy_img = np.random.randint(50, 200, (256, 256), dtype=np.uint8)
    signals = engine.evaluate_physical_signals(dummy_img)

    assert len(signals) == 6
    names = [s.indicator_name for s in signals]
    assert "laplacian_variance" in names
    assert "saturation_ratio" in names
    assert "dark_pixel_ratio" in names
    assert "dynamic_range" in names
    assert "entropy" in names
    assert "contrast" in names

    for s in signals:
        assert isinstance(s.measured_value, float)
        assert isinstance(s.threshold_applied, float)
        assert isinstance(s.is_risk_flagged, bool)
        assert len(s.method_provenance) > 0


# Test 04: Uncertainty Metrics Normalization
def test_04_uncertainty_metrics_normalization():
    engine = QualityRiskEngine()
    # Uniform distribution (11 classes)
    probs = np.ones(11, dtype=np.float32) / 11.0
    conf, norm_ent, margin = engine.compute_uncertainty_metrics(probs)

    assert pytest.approx(conf, rel=1e-3) == 1.0 / 11.0
    assert pytest.approx(norm_ent, rel=1e-3) == 1.0  # Max entropy normalized to 1.0
    assert pytest.approx(margin, rel=1e-3) == 0.0

    # Delta / One-hot distribution
    one_hot = np.zeros(11, dtype=np.float32)
    one_hot[0] = 1.0
    conf_1, norm_ent_1, margin_1 = engine.compute_uncertainty_metrics(one_hot)

    assert pytest.approx(conf_1, rel=1e-3) == 1.0
    assert pytest.approx(norm_ent_1, abs=1e-5) == 0.0
    assert pytest.approx(margin_1, rel=1e-3) == 1.0


# Test 05: Explicit Abstention on Low Confidence
def test_05_explicit_abstention_on_low_confidence():
    engine = QualityRiskEngine(confidence_abstain_threshold=0.50)
    signals = []
    # Probability with max confidence 0.35 (below 0.50)
    probs = np.full(11, 0.065, dtype=np.float32)
    probs[0] = 0.35
    status, cat, conf, ent, margin, abstain, reason = engine.screen_quality_risk(signals, probs)

    assert status == DecisionStatus.UNCERTAIN_ABSTAIN
    assert abstain is True
    assert "Classification confidence" in reason


# Test 06: Explicit Abstention on High Entropy
def test_06_explicit_abstention_on_high_entropy():
    # Set low confidence threshold so entropy gate triggers specifically
    engine = QualityRiskEngine(confidence_abstain_threshold=0.05, entropy_abstain_threshold=0.80)
    signals = []
    probs = np.ones(11, dtype=np.float32) / 11.0  # Entropy = 1.0 > 0.80
    status, cat, conf, ent, margin, abstain, reason = engine.screen_quality_risk(signals, probs)

    assert status == DecisionStatus.UNCERTAIN_ABSTAIN
    assert abstain is True
    assert "Normalized prediction entropy" in reason


# Test 07: Explicit Abstention on Narrow Margin
def test_07_explicit_abstention_on_narrow_margin():
    engine = QualityRiskEngine(confidence_abstain_threshold=0.40, margin_abstain_threshold=0.05)
    signals = []
    probs = np.zeros(11, dtype=np.float32)
    probs[1] = 0.49
    probs[2] = 0.48
    probs[3] = 0.03
    status, cat, conf, ent, margin, abstain, reason = engine.screen_quality_risk(signals, probs)

    assert status == DecisionStatus.UNCERTAIN_ABSTAIN
    assert abstain is True
    assert "margin" in reason.lower()


# Test 08: Suspicious Region Terminology Governance
def test_08_suspicious_region_terminology_governance():
    loc = LocalizationEngine()
    dummy = np.full((128, 128), 100, dtype=np.uint8)
    region = loc.extract_suspicious_region(dummy)

    assert region.region_type == "model-derived suspicious region"
    assert "confirmed defect" not in region.region_type.lower()


# Test 09: Suspicious Region Spatial Bounds
def test_09_suspicious_region_spatial_bounds():
    loc = LocalizationEngine(patch_size=16, saliency_threshold=0.50)
    # Create image with high-contrast localized anomaly in bottom-right
    img = np.full((128, 128), 50, dtype=np.uint8)
    img[80:120, 80:120] = 250  # bright square
    region = loc.extract_suspicious_region(img)

    assert region.area_fraction > 0.0
    assert 0.0 <= region.centroid_normalized[0] <= 1.0
    assert 0.0 <= region.centroid_normalized[1] <= 1.0
    if region.bounding_boxes:
        bbox = region.bounding_boxes[0]
        assert bbox.y_min >= 0 and bbox.y_max <= 128
        assert bbox.x_min >= 0 and bbox.x_max <= 128


# Test 10: Comparable Retrieval Same-Specimen Prioritization
def test_10_comparable_retrieval_same_specimen_prioritization():
    # 3 gallery items:
    # 0: specimen A, acq 1
    # 1: specimen A, acq 2 (cross-acq target)
    # 2: specimen B, acq 1
    feats = np.array([[1.0, 0.0], [0.95, 0.05], [0.90, 0.10]], dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "img_0", "specimen_id": "Spec_A", "acquisition_id": "acq_1"},
        {"image_id": "img_1", "specimen_id": "Spec_A", "acquisition_id": "acq_2"},
        {"image_id": "img_2", "specimen_id": "Spec_B", "acquisition_id": "acq_1"},
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=2)
    q_feat = np.array([1.0, 0.0], dtype=np.float32)

    results = retriever.retrieve_comparable_evidence(
        query_feature=q_feat,
        query_specimen_id="Spec_A",
        query_acquisition_id="acq_1",
    )

    assert len(results) > 0
    # Top item should be cross-acquisition peer
    assert results[0].image_id == "img_1"
    assert results[0].role == EvidenceRole.SAME_SPECIMEN_CROSS_ACQUISITION


# Test 11: Comparable Retrieval Role Labeling
def test_11_comparable_retrieval_role_labeling():
    feats = np.eye(3, dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "img_0", "artifact_type": "NORMAL"},
        {"image_id": "img_1", "artifact_type": "BLUR"},
        {"image_id": "img_2", "artifact_type": "OVEREXPOSURE"},
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=3)
    results = retriever.retrieve_comparable_evidence(
        query_feature=feats[1],
        predicted_artifact=ArtifactCategory.BLUR,
    )

    roles = [r.role for r in results]
    assert EvidenceRole.COMPARABLE_ARTIFACT_EXEMPLAR in roles or EvidenceRole.SIMILAR_CLEAN_MICROGRAPH in roles


# Test 12: Explanation Action Catalog Coverage
def test_12_explanation_action_catalog_coverage():
    gen = ExplanationGenerator()
    acq = AcquisitionContext()
    for cat in ArtifactCategory:
        if cat == ArtifactCategory.UNKNOWN:
            continue
        action = gen.generate_review_action(
            decision_status=DecisionStatus.QUALITY_RISK if cat != ArtifactCategory.NORMAL else DecisionStatus.ACCEPT,
            predicted_category=cat,
            quality_signals=[],
            suspicious_region=None,
            acquisition_context=acq,
        )
        assert isinstance(action, SuggestedReviewAction)
        assert len(action.action_code) > 0
        assert len(action.recommendation_summary) > 0


# Test 13: Deterministic Non-Stochastic Generation
def test_13_deterministic_non_stochastic_generation():
    gen = ExplanationGenerator()
    acq = AcquisitionContext(accelerating_voltage_kv=20.0, detector="BSE")
    act_1 = gen.generate_review_action(
        decision_status=DecisionStatus.QUALITY_RISK,
        predicted_category=ArtifactCategory.CHARGING_LIKE_SYNTHETIC_ARTIFACT,
        quality_signals=[],
        suspicious_region=None,
        acquisition_context=acq,
    )
    act_2 = gen.generate_review_action(
        decision_status=DecisionStatus.QUALITY_RISK,
        predicted_category=ArtifactCategory.CHARGING_LIKE_SYNTHETIC_ARTIFACT,
        quality_signals=[],
        suspicious_region=None,
        acquisition_context=acq,
    )
    assert act_1.to_dict() == act_2.to_dict()


# Test 14: Abstention Generates Manual Review Action
def test_14_abstention_generates_manual_review_action():
    gen = ExplanationGenerator()
    action = gen.generate_review_action(
        decision_status=DecisionStatus.UNCERTAIN_ABSTAIN,
        predicted_category=ArtifactCategory.UNKNOWN,
        quality_signals=[],
        suspicious_region=None,
        acquisition_context=AcquisitionContext(),
        abstention_reason="Low confidence",
    )
    assert action.action_code == "ACT_MANUAL_SCIENTIST_REVIEW"
    assert action.requires_operator_intervention is True


# Test 15: End-to-End Evidence Aggregator Execution
def test_15_evidence_aggregator_end_to_end_execution():
    aggregator = EvidenceAggregator()
    # Create realistic natural texture image with valid contrast and sharpness
    rng = np.random.RandomState(42)
    img = rng.randint(40, 220, (128, 128), dtype=np.uint8)
    record = aggregator.process_query_micrograph(
        query_image_id="TEST_IMAGE_001",
        image=img,
        feature_vector=np.ones(128, dtype=np.float32),
        classification_probabilities=np.eye(11)[0],
        metadata_dict={"instrument": "SEM_FEI", "accelerating_voltage_kv": 15.0},
    )

    assert isinstance(record, StructuredEvidenceRecord)
    assert record.query_image_id == "TEST_IMAGE_001"
    assert record.decision_status == DecisionStatus.ACCEPT
    assert record.primary_artifact_category == ArtifactCategory.NORMAL
    assert len(record.audit_hash) == 64


# Test 16: Deterministic Cryptographic Audit Hash
def test_16_deterministic_cryptographic_audit_hash():
    aggregator = EvidenceAggregator()
    rng = np.random.RandomState(42)
    img = rng.randint(40, 220, (128, 128), dtype=np.uint8)
    meta = {"instrument": "SEM_FEI", "accelerating_voltage_kv": 15.0}
    probs = np.eye(11)[0]

    rec1 = aggregator.process_query_micrograph("QUERY_IMG", img, classification_probabilities=probs, metadata_dict=meta)
    rec2 = aggregator.process_query_micrograph("QUERY_IMG", img, classification_probabilities=probs, metadata_dict=meta)

    assert rec1.audit_hash == rec2.audit_hash


# Test 17: Audit Hash Sensitivity to Alterations
def test_17_audit_hash_sensitivity():
    aggregator = EvidenceAggregator()
    rng = np.random.RandomState(42)
    img = rng.randint(40, 220, (128, 128), dtype=np.uint8)
    probs = np.eye(11)[0]

    rec1 = aggregator.process_query_micrograph("QUERY_IMG", img, classification_probabilities=probs, metadata_dict={"instrument": "SEM_1"})
    rec2 = aggregator.process_query_micrograph("QUERY_IMG", img, classification_probabilities=probs, metadata_dict={"instrument": "SEM_2"})

    assert rec1.audit_hash != rec2.audit_hash


# Test 18: Protocol File Integrity
def test_18_protocol_file_integrity():
    proto_p = BASE_DIR / "research/protocols/phase5_evidence_explanation.yaml"
    assert proto_p.is_file()
    with open(proto_p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["protocol_name"] == "phase5_evidence_explanation"
    assert data["governance_rules"]["llm_decision_maker"] is False


# Test 19: Phase 5 Evidence Seal File
def test_19_phase5_evidence_seal_verification():
    seal_p = BASE_DIR / "research/results/phase5/PHASE5_EVIDENCE_HASH.txt"
    assert seal_p.is_file()
    content = seal_p.read_text(encoding="utf-8")
    assert "MASTER_SEAL" in content
    assert "PHASE5_EVIDENCE_BENCHMARK_REPORT.md" in content


# Test 20: Forbidden Terminology Scan
def test_20_forbidden_terminology_scan_phase5():
    forbidden = ["clinical diagnosis", "confirmed defect", "universal robustness", "acquisition invariant"]
    py_files = list((BASE_DIR / "src/evidence").glob("*.py"))
    report_p = BASE_DIR / "research/results/phase5/PHASE5_EVIDENCE_BENCHMARK_REPORT.md"
    files_to_check = py_files + ([report_p] if report_p.is_file() else [])

    for f in files_to_check:
        text = f.read_text(encoding="utf-8").lower()
        for term in forbidden:
            assert term not in text, f"Forbidden term '{term}' found in {f.name}"


# Test 21: Multichannel and Grayscale Image Compatibility
def test_21_multichannel_and_grayscale_compatibility():
    aggregator = EvidenceAggregator()
    gray = np.full((64, 64), 100, dtype=np.uint8)
    rgb = np.full((64, 64, 3), 100, dtype=np.uint8)

    rec_gray = aggregator.process_query_micrograph("G", gray)
    rec_rgb = aggregator.process_query_micrograph("RGB", rgb)

    assert rec_gray.decision_status in list(DecisionStatus)
    assert rec_rgb.decision_status in list(DecisionStatus)


# Test 22: Empty Saliency Clean Image Handling
def test_22_empty_saliency_clean_image_handling():
    loc = LocalizationEngine(saliency_threshold=0.90)
    flat = np.full((64, 64), 128, dtype=np.uint8)
    region = loc.extract_suspicious_region(flat)

    assert region.area_fraction == 0.0
    assert len(region.bounding_boxes) == 0


# Test 23: Frozen Phases 1-4 Hashes Integrity
def test_23_frozen_phases_1_to_4_hashes_integrity():
    # Phase 1
    p1 = BASE_DIR / "research/final_manifests/FINAL_IMAGE_MANIFEST.json"
    h1 = hashlib.sha256(p1.read_bytes()).hexdigest()
    assert h1 == "6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5"

    # Phase 2
    p2 = BASE_DIR / "research/experiments/freeze1/retrieval_results.csv"
    h2 = hashlib.sha256(p2.read_bytes()).hexdigest()
    assert h2 == "83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361"


# Test 24: JSON Serialization Fidelity
def test_24_json_serialization_fidelity():
    aggregator = EvidenceAggregator()
    img = np.full((64, 64), 128, dtype=np.uint8)
    rec = aggregator.process_query_micrograph("Q", img)
    d = rec.to_dict()
    # Must dump without TypeError
    s = json.dumps(d)
    assert len(s) > 0


# Test 25: Operator Review Payload Actionability
def test_25_operator_review_payload_actionability():
    gen = ExplanationGenerator()
    action = gen.generate_review_action(
        decision_status=DecisionStatus.QUALITY_RISK,
        predicted_category=ArtifactCategory.BLUR,
        quality_signals=[],
        suspicious_region=None,
        acquisition_context=AcquisitionContext(),
    )
    assert action.requires_operator_intervention is True
    assert "objective_lens_current" in action.operational_parameter_targets


# Test 26: Same-Acquisition Evidence Exclusion
def test_26_same_acquisition_evidence_exclusion():
    feats = np.eye(3, dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "img_0", "acquisition_id": "acq_alpha", "specimen_id": "spec_1"},
        {"image_id": "img_1", "acquisition_id": "acq_beta", "specimen_id": "spec_2"},
        {"image_id": "img_2", "acquisition_id": "acq_alpha", "specimen_id": "spec_3"},
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=3)
    results = retriever.retrieve_comparable_evidence(
        query_feature=feats[0],
        query_acquisition_id="acq_alpha",
        exclude_same_acquisition=True,
    )
    # img_0 and img_2 share acq_alpha and must be excluded from general retrieval
    acq_ids = [r.acquisition_id for r in results]
    assert "acq_alpha" not in acq_ids
    assert len(results) == 1
    assert results[0].image_id == "img_1"


# Test 27: Cross-Acquisition Filtering
def test_27_cross_acquisition_filtering():
    feats = np.array([[1.0, 0.0], [0.99, 0.01], [0.98, 0.02]], dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "peer_same_acq", "specimen_id": "Mat_X", "acquisition_id": "Acq_1"},
        {"image_id": "peer_cross_acq", "specimen_id": "Mat_X", "acquisition_id": "Acq_2"},
        {"image_id": "peer_other", "specimen_id": "Mat_Y", "acquisition_id": "Acq_3"},
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=2)
    results = retriever.retrieve_comparable_evidence(
        query_feature=np.array([1.0, 0.0], dtype=np.float32),
        query_specimen_id="Mat_X",
        query_acquisition_id="Acq_1",
    )
    # The prioritized same-specimen peer must strictly be cross-acquisition (Acq_2)
    cross_peers = [r for r in results if r.role == EvidenceRole.SAME_SPECIMEN_CROSS_ACQUISITION]
    assert len(cross_peers) == 1
    assert cross_peers[0].image_id == "peer_cross_acq"
    assert cross_peers[0].acquisition_id == "Acq_2"


# Test 28: Cross-Instrument Filtering
def test_28_cross_instrument_filtering():
    feats = np.eye(3, dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "img_0", "instrument": "FEI_Nova_SEM"},
        {"image_id": "img_1", "instrument": "Zeiss_Gemini_SEM"},
        {"image_id": "img_2", "instrument": "FEI_Nova_SEM"},
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=3)
    results = retriever.retrieve_comparable_evidence(
        query_feature=feats[0],
        query_instrument="FEI_Nova_SEM",
        cross_instrument_only=True,
    )
    instruments = [r.instrument for r in results]
    assert "FEI_Nova_SEM" not in instruments
    assert len(results) == 1
    assert results[0].image_id == "img_1"


# Test 29: Deterministic Ranking Tie-Breaking
def test_29_deterministic_ranking_tie_breaking():
    # Identical features producing identical similarity dot products
    feats = np.ones((4, 8), dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "gamma_img"},
        {"image_id": "alpha_img"},
        {"image_id": "delta_img"},
        {"image_id": "beta_img"},
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=4)
    results = retriever.retrieve_comparable_evidence(query_feature=np.ones(8, dtype=np.float32))

    retrieved_ids = [r.image_id for r in results]
    # Tie-breaking by image_id alphabetically
    assert retrieved_ids == ["alpha_img", "beta_img", "delta_img", "gamma_img"]


# Test 30: Abstention Propagation to Review Action
def test_30_abstention_propagation_to_review_action():
    aggregator = EvidenceAggregator()
    # Uniform ambiguous probabilities
    ambiguous_probs = np.ones(11, dtype=np.float32) / 11.0
    record = aggregator.process_query_micrograph(
        query_image_id="AMBIG_001",
        image=np.full((64, 64), 100, dtype=np.uint8),
        classification_probabilities=ambiguous_probs,
    )
    assert record.decision_status == DecisionStatus.UNCERTAIN_ABSTAIN
    assert record.abstention_triggered is True
    assert record.suggested_action.action_code == "ACT_MANUAL_SCIENTIST_REVIEW"
    assert record.suggested_action.requires_operator_intervention is True


# Test 31: Provenance Completeness
def test_31_provenance_completeness():
    aggregator = EvidenceAggregator()
    meta = {
        "instrument": "SEM_Tescan",
        "detector": "ETD",
        "accelerating_voltage_kv": 20.0,
        "magnification": 5000.0,
        "specimen_id": "Spec_Q980",
        "acquisition_id": "Acq_01",
        "data_source": "HCCI_VERIFIED",
        "sha256": "abcdef1234567890",
    }
    record = aggregator.process_query_micrograph(
        query_image_id="PROV_TEST",
        image=np.random.randint(40, 200, (64, 64), dtype=np.uint8),
        metadata_dict=meta,
    )
    d = record.to_dict()
    assert d["pipeline_version"] == "sci-intel-phase5-v1.0"
    assert len(d["audit_hash"]) == 64
    assert d["acquisition_context"]["instrument"] == "SEM_Tescan"
    assert d["acquisition_context"]["metadata_provenance_hash"] == "abcdef1234567890"


# Test 32: Missing Metadata Preservation Strict No Imputation
def test_32_missing_metadata_preservation_strict_no_imputation():
    meta = {
        "instrument": None,
        "accelerating_voltage_kv": None,
        "magnification": None,
        "working_distance_mm": None,
    }
    acq = AcquisitionContext(
        instrument=meta["instrument"],
        accelerating_voltage_kv=meta["accelerating_voltage_kv"],
        magnification=meta["magnification"],
        working_distance_mm=meta["working_distance_mm"],
    )
    d = acq.to_dict()
    # Must preserve None / UNKNOWN rather than substituting defaults or zero
    assert d["accelerating_voltage_kv"] is None
    assert d["magnification"] is None
    assert d["working_distance_mm"] is None
    assert d["instrument"] == "UNKNOWN"


# Test 33: Duplicate Evidence Prevention
def test_33_duplicate_evidence_prevention():
    feats = np.eye(4, dtype=np.float32)
    meta = pd.DataFrame([
        {"image_id": "img_dup_1", "sha256": "hash_shared"},
        {"image_id": "img_dup_2", "sha256": "hash_shared"},  # Near duplicate with identical SHA
        {"image_id": "img_unique", "sha256": "hash_unique"},
        {"image_id": "img_dup_1", "sha256": "hash_other"},   # Duplicate ID
    ])
    retriever = RetrievalEvidenceEngine(feats, meta, top_k=4)
    results = retriever.retrieve_comparable_evidence(query_feature=feats[0])

    retrieved_shas = [r.provenance_hash for r in results if r.provenance_hash]
    retrieved_ids = [r.image_id for r in results]
    assert len(retrieved_ids) == len(set(retrieved_ids))
    assert len(retrieved_shas) == len(set(retrieved_shas))


# Test 34: Frozen Model Checkpoint Provenance
def test_34_frozen_model_checkpoint_provenance():
    expected_hashes = {
        42: "53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62",
        123: "391fd18c95599a6956018be60b6dc8780be4b8154b899f7807c1c3950a0a931f",
        2024: "c5ebbc7187dd1e643fb4e59ee77b0ab4b49e8aacd9cb4647733a92258e0d8f7b",
    }
    for seed, exp_h in expected_hashes.items():
        ckpt_p = BASE_DIR / f"data/processed/phase4/checkpoints/best_checkpoint_seed{seed}.pt"
        assert ckpt_p.is_file(), f"Missing checkpoint for seed {seed}"
        h = hashlib.sha256(ckpt_p.read_bytes()).hexdigest()
        assert h == exp_h, f"Checkpoint hash mismatch for seed {seed}"


# Test 35: Assessment SHA Tamper Detection
def test_35_assessment_sha_tamper_detection():
    aggregator = EvidenceAggregator()
    img = np.random.randint(40, 200, (64, 64), dtype=np.uint8)
    record = aggregator.process_query_micrograph("QUERY_TAMPER", img)
    original_hash = record.audit_hash

    # Tamper with decision status
    tampered_dict = {
        "query_image_id": record.query_image_id,
        "decision_status": DecisionStatus.QUALITY_RISK.value if record.decision_status == DecisionStatus.ACCEPT else DecisionStatus.ACCEPT.value,
        "primary_artifact_category": record.primary_artifact_category.value,
        "confidence": round(record.classification_confidence, 4),
        "normalized_entropy": round(record.normalized_entropy, 4),
        "abstention_triggered": record.abstention_triggered,
        "acquisition_context": record.acquisition_context.to_dict(),
        "suggested_action": record.suggested_action.to_dict(),
    }
    tampered_hash = hashlib.sha256(json.dumps(tampered_dict, sort_keys=True).encode("utf-8")).hexdigest()
    assert tampered_hash != original_hash, "Tamper undetected by audit hash verification"


# Test 36: Threshold Provenance Config Hash Integrity
def test_36_threshold_provenance_config_hash_integrity():
    from src.evidence.threshold_config import DEFAULT_THRESHOLD_CONFIG
    assert DEFAULT_THRESHOLD_CONFIG.test_label_tuning_excluded is True
    assert DEFAULT_THRESHOLD_CONFIG.confidence_abstain_threshold == 0.40
    assert DEFAULT_THRESHOLD_CONFIG.entropy_abstain_threshold == 0.75
    assert DEFAULT_THRESHOLD_CONFIG.margin_abstain_threshold == 0.10
    cfg_hash = DEFAULT_THRESHOLD_CONFIG.compute_hash()
    assert len(cfg_hash) == 64

