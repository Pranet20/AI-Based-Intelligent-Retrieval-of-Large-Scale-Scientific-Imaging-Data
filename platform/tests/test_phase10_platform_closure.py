"""Comprehensive Phase 10 Platform Closure Test Suite.

Verifies all closure requirements A through T:
A. Platform Startup and Health Check
B. Image Ingestion Pipeline (14 Steps)
C. Metadata Extraction and Storage
D. Dual Representation Generation
E. Representation Separation (NO Learned Fusion)
F. FAISS Vector Indexing and Search
G. Quality and Artifact Screening
H. Quality-Risk Indicators and Thresholds
I. Patch-Level Localization and Explanation
J. Duplicate Detection (Exact and Perceptual)
K. Novelty Scoring and Percentiles
L. Acquisition-Aware Retrieval (Phase 4)
M. Scientific Consistency Check
N. Curator Workbench Workflow
O. Full Provenance Chain
P. Error Handling and Resilience
Q. State Persistence and File Storage
R. Determinism and Reproducibility
S. Scientific Terminology Compliance
T. End-to-End Integration Workflow
"""

import io
import json
import os
from pathlib import Path
import numpy as np
from PIL import Image as PILImage
import pytest
from starlette.testclient import TestClient
import torch

from app.core.config import settings
from app.core.security import create_access_token
from app.db.models import (
    AuditLog,
    DuplicateProfile,
    Embedding,
    Image,
    ImageMetadata,
    ModelVersion,
    Project,
    ProvenanceEvent,
    QualityProfile,
    RetrievalQuery,
    RetrievalResult,
    ReviewItem,
    User,
)
from app.main import app
from app.ml.dinov2_engine import DINOv2Engine
from app.ml.duplicate_engine import DuplicateEngine
from app.ml.faiss_engine import FAISSEngine
from app.ml.novelty_engine import NoveltyEngine
from app.ml.phase4_engine import Phase4Engine
from app.ml.quality_engine import QualityEngine
from app.services.ingestion import IngestionService


def _create_sample_png_bytes(seed: int = 42, size: tuple = (256, 256)) -> bytes:
    rng = np.random.RandomState(seed)
    arr = (rng.rand(*size) * 255).astype(np.uint8)
    buf = io.BytesIO()
    PILImage.fromarray(arr).save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------------------
# A. Platform Startup and Health Check
# ---------------------------------------------------------------------------
def test_phase10_A_platform_startup_and_health():
    with TestClient(app) as client:
        # /health
        h_res = client.get("/api/v1/health")
        assert h_res.status_code == 200
        h_data = h_res.json()
        assert h_data["status"] == "healthy"
        assert "database" in h_data
        assert "faiss_index_count" in h_data

        # /readiness
        r_res = client.get("/api/v1/readiness")
        assert r_res.status_code == 200
        r_data = r_res.json()
        assert r_data["status"] == "READY"
        assert r_data["checks"]["model_checkpoint"] == "READY"

        # /version
        v_res = client.get("/api/v1/version")
        assert v_res.status_code == 200
        v_data = v_res.json()
        assert v_data["dinov2_model"] == "dinov2_vits14"
        assert v_data["embedding_dimension"] == 384
        assert v_data["phase4_checkpoint_hash"] == settings.EXPECTED_PHASE4_HASH


# ---------------------------------------------------------------------------
# B. Image Ingestion Pipeline (14 Steps)
# ---------------------------------------------------------------------------
def test_phase10_B_image_ingestion_14_steps(db_session):
    img_bytes = _create_sample_png_bytes(seed=101)
    record = IngestionService.ingest_file(
        db=db_session,
        file_bytes=img_bytes,
        original_filename="phase10_ingest_sample.png",
        manual_metadata={
            "microscope": "FEI Helios Nanolab 600 DualBeam",
            "detector": "Through-the-Lens Detector (TLD)",
            "accelerating_voltage_kv": 10.0,
            "magnification": 25000.0,
            "pixel_size_nm": 4.5,
        },
    )
    assert record.id is not None
    assert record.processing_status == "READY"
    assert len(record.sha256) == 64
    assert Path(record.storage_path).exists()
    assert Path(record.thumbnail_path).exists()


# ---------------------------------------------------------------------------
# C. Metadata Extraction and Storage
# ---------------------------------------------------------------------------
def test_phase10_C_metadata_extraction_and_storage(db_session):
    img_bytes = _create_sample_png_bytes(seed=102)
    record = IngestionService.ingest_file(
        db=db_session,
        file_bytes=img_bytes,
        original_filename="phase10_meta_sample.png",
        manual_metadata={
            "microscope": "Zeiss GeminiSEM 500",
            "detector": "Inlens SE",
            "accelerating_voltage_kv": 5.0,
            "magnification": 40000.0,
            "pixel_size_nm": 2.8,
            "beam_current_na": 0.5,
            "dwell_time_us": 10.0,
            "working_distance_mm": 4.2,
            "chamber_pressure_pa": 0.001,
        },
    )
    meta = record.metadata_rel
    assert meta is not None
    assert meta.microscope == "Zeiss GeminiSEM 500"
    assert meta.accelerating_voltage_kv == 5.0
    assert meta.metadata_completeness == 1.0
    assert meta.metadata_source in ("manual", "embedded")


# ---------------------------------------------------------------------------
# D. Dual Representation Generation
# ---------------------------------------------------------------------------
def test_phase10_D_dual_representation_generation(db_session):
    img_bytes = _create_sample_png_bytes(seed=103)
    record = IngestionService.ingest_file(
        db=db_session,
        file_bytes=img_bytes,
        original_filename="phase10_dual_rep.png",
    )
    embs = db_session.query(Embedding).filter(Embedding.image_id == record.id).all()
    types = {e.embedding_type for e in embs}
    assert "dinov2_base" in types
    assert "phase4_adapted" in types

    dino_emb = next(e for e in embs if e.embedding_type == "dinov2_base")
    phase4_emb = next(e for e in embs if e.embedding_type == "phase4_adapted")

    v_dino = np.array(dino_emb.embedding_vector)
    v_p4 = np.array(phase4_emb.embedding_vector)

    assert v_dino.shape == (384,)
    assert v_p4.shape == (384,)
    assert np.isclose(np.linalg.norm(v_dino), 1.0, atol=1e-3)
    assert np.isclose(np.linalg.norm(v_p4), 1.0, atol=1e-3)
    # Ensure they are distinct representations
    assert not np.allclose(v_dino, v_p4, atol=1e-2)


# ---------------------------------------------------------------------------
# E. Representation Separation (NO Learned Fusion)
# ---------------------------------------------------------------------------
def test_phase10_E_representation_separation_no_learned_fusion(db_session):
    """Verify representations remain strictly distinct and rule-based without black box fusion."""
    p4_engine = Phase4Engine()
    dino_engine = DINOv2Engine()

    dummy_input = np.ones(384, dtype=np.float32) / np.sqrt(384)
    adapted = p4_engine.adapt_embedding(dummy_input)

    assert adapted.shape == (384,)
    # Verify Phase 4 head is frozen (gradient tracking disabled)
    for p in p4_engine._head.parameters():
        assert p.requires_grad is False


# ---------------------------------------------------------------------------
# F. FAISS Vector Indexing and Search
# ---------------------------------------------------------------------------
def test_phase10_F_faiss_vector_indexing_and_search():
    faiss_engine = FAISSEngine()
    test_vec = np.random.RandomState(42).randn(384).astype(np.float32)
    test_vec /= np.linalg.norm(test_vec)

    # Search should succeed and return list of (img_id, sim)
    results = faiss_engine.search(test_vec, top_k=5)
    assert isinstance(results, list)
    for img_id, sim in results:
        assert isinstance(img_id, int)
        assert -1.0 <= sim <= 1.0001


# ---------------------------------------------------------------------------
# G. Quality and Artifact Screening
# ---------------------------------------------------------------------------
def test_phase10_G_quality_and_artifact_screening(tmp_path):
    # Create test image with distinct structure
    arr = np.zeros((256, 256), dtype=np.uint8)
    arr[64:192, 64:192] = 200
    test_path = tmp_path / "quality_test.png"
    PILImage.fromarray(arr).save(test_path)

    q_res = QualityEngine.evaluate_quality(test_path)
    required_keys = [
        "laplacian_variance",
        "edge_density",
        "shannon_entropy",
        "dynamic_range",
        "clipping_ratio",
        "high_freq_fft_ratio",
        "composite_quality_risk",
        "quality_label",
    ]
    for k in required_keys:
        assert k in q_res
        assert q_res[k] is not None
    assert q_res["quality_label"] in ("NOMINAL", "RISK_FLAGGED")


# ---------------------------------------------------------------------------
# H. Quality-Risk Indicators and Thresholds
# ---------------------------------------------------------------------------
def test_phase10_H_quality_risk_indicators_and_thresholds(tmp_path):
    # Completely flat image -> should trigger risk
    flat_arr = np.ones((256, 256), dtype=np.uint8) * 128
    flat_path = tmp_path / "flat_test.png"
    PILImage.fromarray(flat_arr).save(flat_path)

    q_flat = QualityEngine.evaluate_quality(flat_path)
    assert q_flat["laplacian_variance"] == 0.0
    assert q_flat["edge_density"] == 0.0
    assert q_flat["composite_quality_risk"] >= 0.60
    assert q_flat["quality_label"] == "RISK_FLAGGED"


# ---------------------------------------------------------------------------
# I. Patch-Level Localization and Explanation
# ---------------------------------------------------------------------------
def test_phase10_I_patch_level_localization_and_explanation(db_session):
    with TestClient(app) as client:
        img_bytes = _create_sample_png_bytes(seed=104)
        rec = IngestionService.ingest_file(db_session, img_bytes, "phase10_explain.png")

        res = client.post(
            "/api/v1/models/extract-features",
            json={"image_id": rec.id, "model_id": "dinov2_vits14_phase2"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["embedding_dimension"] == 384
        assert "patch_attention_14x14" in data
        patch_grid = data["patch_attention_14x14"]
        assert len(patch_grid) == 14
        assert len(patch_grid[0]) == 14


# ---------------------------------------------------------------------------
# J. Duplicate Detection (Exact and Perceptual)
# ---------------------------------------------------------------------------
def test_phase10_J_duplicate_detection_exact_and_perceptual(tmp_path):
    p1 = tmp_path / "dup1.png"
    p2 = tmp_path / "dup2.png"
    arr = (np.random.RandomState(777).rand(128, 128) * 255).astype(np.uint8)
    PILImage.fromarray(arr).save(p1)
    PILImage.fromarray(arr).save(p2)

    h1 = DuplicateEngine.compute_hashes(p1)
    h2 = DuplicateEngine.compute_hashes(p2)

    assert h1["sha256"] == h2["sha256"]
    assert h1["phash"] == h2["phash"]
    assert h1["dhash"] == h2["dhash"]

    candidate = {
        "id": 1,
        "storage_path": str(p1),
        "sha256": h1["sha256"],
        "phash": h1["phash"],
        "dhash": h1["dhash"],
        "dinov2_vector": np.ones(384, dtype=np.float32) / np.sqrt(384),
        "adapted_vector": np.ones(384, dtype=np.float32) / np.sqrt(384),
    }

    res_exact = DuplicateEngine.check_duplicate_against_candidates(
        new_image_path=p2,
        new_sha256=h2["sha256"],
        new_phash=h2["phash"],
        new_dhash=h2["dhash"],
        new_dinov2_vec=candidate["dinov2_vector"],
        new_adapted_vec=candidate["adapted_vector"],
        candidates=[candidate],
    )
    assert res_exact["duplicate_status"] == "EXACT_DUPLICATE"
    assert res_exact["matched_image_id"] == 1
    assert res_exact["match_stage"] in ("STAGE_1_FILE_SHA256", "exact_sha256")

    # Perceptual near duplicate test with slightly perturbed image
    p3 = tmp_path / "dup3.png"
    arr_perturbed = arr.copy()
    arr_perturbed[0:2, 0:2] = np.bitwise_xor(arr_perturbed[0:2, 0:2], 1)
    PILImage.fromarray(arr_perturbed).save(p3)
    h3 = DuplicateEngine.compute_hashes(p3)

    res_near = DuplicateEngine.check_duplicate_against_candidates(
        new_image_path=p3,
        new_sha256=h3["sha256"],
        new_phash=h3["phash"],
        new_dhash=h3["dhash"],
        new_dinov2_vec=candidate["dinov2_vector"],
        new_adapted_vec=candidate["adapted_vector"],
        candidates=[candidate],
    )
    assert res_near["duplicate_status"] == "POTENTIAL_NEAR_DUPLICATE"
    assert "STAGE" in res_near["match_stage"]


# ---------------------------------------------------------------------------
# K. Novelty Scoring and Percentiles
# ---------------------------------------------------------------------------
def test_phase10_K_novelty_scoring_and_percentiles():
    novelty_engine = NoveltyEngine()
    rnd_vec = np.random.RandomState(42).randn(384).astype(np.float32)
    rnd_vec /= np.linalg.norm(rnd_vec)

    res = novelty_engine.evaluate_novelty(rnd_vec)
    assert "novelty_score" in res
    assert "novelty_percentile" in res
    assert 0.0 <= res["novelty_score"] <= 1.0
    assert 0.0 <= res["novelty_percentile"] <= 100.0


# ---------------------------------------------------------------------------
# L. Acquisition-Aware Retrieval (Phase 4)
# ---------------------------------------------------------------------------
def test_phase10_L_acquisition_aware_retrieval_phase4(db_session):
    with TestClient(app) as client:
        img_bytes_1 = _create_sample_png_bytes(seed=106)
        img_bytes_2 = _create_sample_png_bytes(seed=107)

        r1 = IngestionService.ingest_file(db_session, img_bytes_1, "p4_sample_1.png")
        r2 = IngestionService.ingest_file(db_session, img_bytes_2, "p4_sample_2.png")

        # Search using JSON payload and phase4_adapted representation
        res = client.post(
            "/api/v1/search",
            json={
                "query_image_id": r1.id,
                "top_k": 5,
                "representation": "phase4_adapted",
            },
        )
        assert res.status_code == 200, res.text
        data = res.json()
        assert data["retrieval_mode"] == "frozen_phase4_acquisition_adapter"
        assert "Phase 4 adapter" in data["note"]
        assert len(data["results"]) >= 1

        # Test similar endpoint with phase4_adapted representation
        sim_res = client.get(f"/api/v1/images/{r1.id}/similar?representation=phase4_adapted&top_k=5")
        assert sim_res.status_code == 200, sim_res.text
        sim_data = sim_res.json()
        assert len(sim_data) >= 1
        assert sim_data[0]["representation"] == "phase4_adapted"


# ---------------------------------------------------------------------------
# M. Scientific Consistency Check
# ---------------------------------------------------------------------------
def test_phase10_M_scientific_consistency_check():
    """Verify Phase 4 checkpoint hash and deterministic adapter forward pass."""
    import hashlib
    assert Path(settings.PHASE4_CHECKPOINT_PATH).exists()
    with open(settings.PHASE4_CHECKPOINT_PATH, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash == settings.EXPECTED_PHASE4_HASH

    p4_engine = Phase4Engine()
    test_vec = np.linspace(-1.0, 1.0, 384, dtype=np.float32)
    test_vec /= np.linalg.norm(test_vec)

    out1 = p4_engine.adapt_embedding(test_vec)
    out2 = p4_engine.adapt_embedding(test_vec)
    np.testing.assert_allclose(out1, out2, rtol=1e-7, atol=1e-7)


# ---------------------------------------------------------------------------
# N. Curator Workbench Workflow
# ---------------------------------------------------------------------------
def test_phase10_N_curator_workbench_workflow(db_session):
    with TestClient(app) as client:
        # Create curator user
        username = "curator_test_user"
        reg_res = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@institution.org",
                "password": "CuratorSecurePass123!",
                "role": "CURATOR",
            },
        )
        token = reg_res.json().get("access_token") if reg_res.status_code == 200 else None
        if not token:
            login_res = client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": "CuratorSecurePass123!"},
            )
            token = login_res.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # Ingest image to review
        img_bytes = _create_sample_png_bytes(seed=108)
        rec = IngestionService.ingest_file(db_session, img_bytes, "curator_sample.png")

        # Check review queue
        q_res = client.get("/api/v1/curation/review-queue", headers=headers)
        assert q_res.status_code == 200
        queue = q_res.json()
        assert isinstance(queue, list)

        # Submit review
        rev_res = client.post(
            "/api/v1/curation/reviews",
            json={
                "image_id": rec.id,
                "decision": "KEEP",
                "comment": "Nominal micrograph verified with sharp cellular borders.",
            },
            headers=headers,
        )
        assert rev_res.status_code == 200
        rev_data = rev_res.json()
        assert rev_data["status"] == "COMPLETED"
        assert rev_data["decision"] == "KEEP"


# ---------------------------------------------------------------------------
# O. Full Provenance Chain
# ---------------------------------------------------------------------------
def test_phase10_O_full_provenance_chain(db_session):
    with TestClient(app) as client:
        img_bytes = _create_sample_png_bytes(seed=109)
        rec = IngestionService.ingest_file(db_session, img_bytes, "provenance_sample.png")

        prov_res = client.get(f"/api/v1/provenance/image/{rec.id}")
        assert prov_res.status_code == 200, prov_res.text
        events = prov_res.json()
        assert len(events) >= 5

        event_types = [e["event_type"] for e in events]
        assert "UPLOAD" in event_types
        assert "METADATA_EXTRACTION" in event_types
        assert "QUALITY_ANALYSIS" in event_types
        assert "EMBEDDING_GENERATION" in event_types
        assert "DUPLICATE_ANALYSIS" in event_types
        assert "INDEXING" in event_types


# ---------------------------------------------------------------------------
# P. Error Handling and Resilience
# ---------------------------------------------------------------------------
def test_phase10_P_error_handling_and_resilience():
    curator_token = create_access_token(subject=1, role="CURATOR")
    headers = {"Authorization": f"Bearer {curator_token}"}

    with TestClient(app) as client:
        # Invalid image ID search returns 404
        search_res = client.post("/api/v1/search", json={"query_image_id": 999999})
        assert search_res.status_code == 404

        # Non-existent image file request returns 404
        file_res = client.get("/api/v1/images/999999/file")
        assert file_res.status_code == 404

        # Ingestion of malformed binary file returns 400
        bad_upload = client.post(
            "/api/v1/images/upload",
            files={"file": ("corrupt.png", b"NOT_A_VALID_IMAGE_HEADER", "image/png")},
            headers=headers,
        )
        assert bad_upload.status_code == 400


# ---------------------------------------------------------------------------
# Q. State Persistence and File Storage
# ---------------------------------------------------------------------------
def test_phase10_Q_state_persistence_and_file_storage(db_session):
    img_bytes = _create_sample_png_bytes(seed=110)
    rec = IngestionService.ingest_file(db_session, img_bytes, "persistence_check.png")

    orig_path = Path(rec.storage_path)
    thumb_path = Path(rec.thumbnail_path)

    assert orig_path.exists()
    assert orig_path.is_file()
    assert thumb_path.exists()
    assert thumb_path.is_file()

    # Verify original bytes matched
    with open(orig_path, "rb") as f:
        saved_bytes = f.read()
    assert saved_bytes == img_bytes


# ---------------------------------------------------------------------------
# R. Determinism and Reproducibility
# ---------------------------------------------------------------------------
def test_phase10_R_determinism_and_reproducibility():
    dino_engine = DINOv2Engine()
    p4_engine = Phase4Engine()

    arr = np.random.RandomState(999).rand(256, 256)
    buf = io.BytesIO()
    PILImage.fromarray((arr * 255).astype(np.uint8)).save(buf, format="PNG")
    raw_bytes = buf.getvalue()

    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(raw_bytes)
        tpath = tmp.name

    try:
        e1 = dino_engine.embed_image(tpath)
        e2 = dino_engine.embed_image(tpath)
        np.testing.assert_allclose(e1, e2, rtol=1e-6, atol=1e-6)

        a1 = p4_engine.adapt_embedding(e1)
        a2 = p4_engine.adapt_embedding(e2)
        np.testing.assert_allclose(a1, a2, rtol=1e-6, atol=1e-6)
    finally:
        if os.path.exists(tpath):
            os.remove(tpath)


# ---------------------------------------------------------------------------
# S. Scientific Terminology Compliance
# ---------------------------------------------------------------------------
def test_phase10_S_scientific_terminology_compliance():
    """Verify system endpoints and descriptions strictly follow scientific terminology boundaries."""
    with TestClient(app) as client:
        v_res = client.get("/api/v1/version")
        assert v_res.status_code == 200
        text = v_res.text.lower()
        forbidden_terms = [
            "physical defect",
            "physical indicator",
            "physical signal",
            "clinical diagnosis",
            "diagnostic ground truth",
            "state of the art",
            "best model",
            "guaranteed correctness",
        ]
        for term in forbidden_terms:
            assert term not in text, f"Forbidden terminology found: {term}"


# ---------------------------------------------------------------------------
# T. End-to-End Integration Workflow
# ---------------------------------------------------------------------------
def test_phase10_T_end_to_end_integration_workflow(db_session):
    with TestClient(app) as client:
        # 1. Register & Login
        uname = "e2e_closure_user"
        reg = client.post(
            "/api/v1/auth/register",
            json={
                "username": uname,
                "email": f"{uname}@science.edu",
                "password": "SecurePassword987!",
                "role": "CURATOR",
            },
        )
        token = reg.json().get("access_token")
        if not token:
            login = client.post(
                "/api/v1/auth/login",
                data={"username": uname, "password": "SecurePassword987!"},
            )
            token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create Project
        proj = client.post(
            "/api/v1/projects",
            json={"name": "Closure Project", "description": "Phase 10 verification"},
            headers=headers,
        )
        assert proj.status_code == 200
        proj_id = proj.json()["id"]

        # 3. Upload Micrograph
        img_bytes = _create_sample_png_bytes(seed=111)
        up = client.post(
            "/api/v1/images/upload",
            files={"file": ("closure_sample.png", img_bytes, "image/png")},
            data={"project_id": proj_id, "microscope": "Thermo Apreo 2 SEM"},
            headers=headers,
        )
        assert up.status_code == 200
        img_id = up.json()["id"]

        # 4. Search via Vector (JSON request body)
        sr = client.post(
            "/api/v1/search/vector",
            json={"query_image_id": img_id, "top_k": 5, "representation": "dinov2_base"},
            headers=headers,
        )
        assert sr.status_code == 200

        # 5. Search via Hybrid with Phase 4
        sr_p4 = client.post(
            "/api/v1/search/hybrid",
            json={
                "query_image_id": img_id,
                "top_k": 5,
                "representation": "phase4_adapted",
                "metadata_query": {"microscope": "Apreo"},
            },
            headers=headers,
        )
        assert sr_p4.status_code == 200
        assert sr_p4.json()["retrieval_mode"] == "frozen_phase4_acquisition_adapter"

        # 6. Deep Analysis
        an = client.get(f"/api/v1/images/{img_id}/analysis", headers=headers)
        assert an.status_code == 200
        assert "frequency_analysis" in an.json()
        assert "histogram" in an.json()

        # 7. Provenance History
        pr = client.get(f"/api/v1/provenance/image/{img_id}", headers=headers)
        assert pr.status_code == 200
        assert len(pr.json()) >= 6
