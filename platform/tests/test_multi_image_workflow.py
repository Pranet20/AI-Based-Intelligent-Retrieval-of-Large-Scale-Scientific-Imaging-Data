"""Comprehensive Test Suite for Multi-Image Scientific Comparison,
Duplicate Detection, Quality-Risk Analysis, and Corrective-Action Workflow.
"""

import io
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image as PILImage
import pytest
from starlette.testclient import TestClient

from app.db.models import Image, AuditLog, ReviewItem
from app.main import app
from app.services.ingestion import IngestionService
from app.services.multi_image import MultiImageComparisonService


def _create_synthetic_image(tmp_path: Path, filename: str, pattern: str = "noise", blur: bool = False) -> Path:
    """Helper to generate scientific test images with controlled visual properties."""
    filepath = tmp_path / filename
    if pattern == "uniform":
        arr = np.full((128, 128), 120, dtype=np.uint8)
    elif pattern == "gradient":
        x = np.linspace(0, 255, 128, dtype=np.uint8)
        arr = np.tile(x, (128, 1))
    elif pattern == "high_contrast":
        arr = np.zeros((128, 128), dtype=np.uint8)
        arr[32:96, 32:96] = 240
    else:
        # Pseudo-deterministic noise
        np.random.seed(42 if pattern == "noise_a" else 99)
        arr = np.random.randint(40, 220, (128, 128), dtype=np.uint8)

    img = PILImage.fromarray(arr)
    if blur:
        # Create heavily blurred / defocused variant
        from PIL import ImageFilter
        img = img.filter(ImageFilter.GaussianBlur(radius=8))
    img.save(filepath, format="PNG")
    return filepath


@pytest.fixture
def test_image_cohort(tmp_path, db_session):
    """Fixture creating a cohort of 3 distinct test micrographs in the database."""
    p1 = _create_synthetic_image(tmp_path, "cohort_1.png", pattern="gradient")
    p2 = _create_synthetic_image(tmp_path, "cohort_2.png", pattern="high_contrast")
    p3 = _create_synthetic_image(tmp_path, "cohort_3.png", pattern="uniform", blur=True)

    img1 = IngestionService.ingest_file(db_session, p1.read_bytes(), "cohort_1.png")
    img2 = IngestionService.ingest_file(db_session, p2.read_bytes(), "cohort_2.png")
    img3 = IngestionService.ingest_file(db_session, p3.read_bytes(), "cohort_3.png")

    return [img1.id, img2.id, img3.id]


# ==============================================================================
# 1. Input Validation & Error Handling Tests
# ==============================================================================

def test_multi_image_min_count_validation_json():
    """Verify that fewer than 2 images via JSON payload triggers 400 error."""
    with TestClient(app) as client:
        res = client.post("/api/v1/multi-image/analyze", json={"image_ids": [1]})
        assert res.status_code == 400
        assert "at least 2" in res.json()["detail"].lower()


def test_multi_image_empty_files_validation():
    """Verify that 0 or 1 file upload triggers 400 error."""
    with TestClient(app) as client:
        # No files and no payload
        res = client.post("/api/v1/multi-image/analyze")
        assert res.status_code == 400


def test_multi_image_unsupported_representation(test_image_cohort):
    """Verify that an unsupported representation model string triggers 400 error."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort[:2], "representation": "resnet50_unsupported"},
        )
        assert res.status_code == 400
        assert "unsupported representation" in res.json()["detail"].lower()


def test_multi_image_phase4_fallback_prevention(test_image_cohort):
    """Verify that requesting Phase 4 when unavailable returns HTTP 503 with explicit error (no silent fallback)."""
    with patch("app.services.multi_image.Phase4Engine._ensure_loaded", side_effect=RuntimeError("Checkpoint missing")):
        with TestClient(app) as client:
            res = client.post(
                "/api/v1/multi-image/analyze",
                json={"image_ids": test_image_cohort[:2], "representation": "phase4_adapted"},
            )
            assert res.status_code == 503
            assert "unavailable" in res.json()["detail"].lower()
            assert "checkpoint missing" in res.json()["detail"].lower()


# ==============================================================================
# 2. Pairwise Counting & Formula Verification Tests N(N-1)/2
# ==============================================================================

def test_multi_image_two_images_pairwise_count(test_image_cohort):
    """2 images must result in exactly 2*(1)/2 = 1 pairwise comparison."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort[:2], "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_images"] == 2
        assert data["total_pairs"] == 1
        assert len(data["pairwise_comparisons"]) == 1
        assert data["summary"]["pairwise_comparisons"] == 1


def test_multi_image_three_images_pairwise_count(test_image_cohort):
    """3 images must result in exactly 3*(2)/2 = 3 pairwise comparisons."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_images"] == 3
        assert data["total_pairs"] == 3
        assert len(data["pairwise_comparisons"]) == 3
        assert data["summary"]["pairwise_comparisons"] == 3


def test_multi_image_four_images_pairwise_count(tmp_path, db_session, test_image_cohort):
    """4 images must result in exactly 4*(3)/2 = 6 pairwise comparisons."""
    p4 = _create_synthetic_image(tmp_path, "cohort_4.png", pattern="noise_a")
    img4 = IngestionService.ingest_file(db_session, p4.read_bytes(), "cohort_4.png")
    four_ids = test_image_cohort + [img4.id]

    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": four_ids, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_images"] == 4
        assert data["total_pairs"] == 6
        assert len(data["pairwise_comparisons"]) == 6


def test_multi_image_no_self_comparison(test_image_cohort):
    """Pairwise comparisons must never include self-comparisons (A == B)."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        pairs = res.json()["pairwise_comparisons"]
        for p in pairs:
            assert p["image_a"]["id"] != p["image_b"]["id"]


# ==============================================================================
# 3. Similarity Matrix Dimensions & Symmetry Tests
# ==============================================================================

def test_multi_image_similarity_matrix_dimensions(test_image_cohort):
    """Similarity matrix must be NxN with diagonal equal to 100.0%."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        matrix_data = res.json()["similarity_matrix"]
        matrix = matrix_data["matrix"]
        assert len(matrix) == 3
        for row in matrix:
            assert len(row) == 3
        # Diagonal check (100.0% self-similarity)
        for i in range(3):
            assert matrix[i][i] == 100.0


def test_multi_image_similarity_matrix_symmetry(test_image_cohort):
    """Similarity matrix must be strictly symmetric: M[i][j] == M[j][i]."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        matrix = res.json()["similarity_matrix"]["matrix"]
        n = len(matrix)
        for i in range(n):
            for j in range(n):
                assert matrix[i][j] == matrix[j][i]


# ==============================================================================
# 4. Pipeline A: Duplicate Cascade & Redundancy Grouping Tests
# ==============================================================================

def test_multi_image_exact_duplicate_detection(tmp_path, db_session):
    """Identical decoded pixel images must yield DUPLICATE decision with Stage 2 pixel match."""
    arr = np.linspace(0, 255, 128, dtype=np.uint8)
    arr = np.tile(arr, (128, 1))

    p1 = tmp_path / "dup_a.png"
    p2 = tmp_path / "dup_b.tif"
    PILImage.fromarray(arr).save(p1, format="PNG")
    PILImage.fromarray(arr).save(p2, format="TIFF")

    img1 = IngestionService.ingest_file(db_session, p1.read_bytes(), "dup_a.png")
    img2 = IngestionService.ingest_file(db_session, p2.read_bytes(), "dup_b.tif")

    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": [img1.id, img2.id], "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        data = res.json()
        pair = data["pairwise_comparisons"][0]
        assert pair["decision"] == "DUPLICATE"
        assert pair["cascade_evidence"]["pixel_sha_match"] is True
        assert data["summary"]["duplicate_pairs"] == 1


def test_multi_image_duplicate_group_election(tmp_path, db_session):
    """Duplicate images must be grouped with a single representative elected."""
    arr = np.linspace(0, 255, 128, dtype=np.uint8)
    arr = np.tile(arr, (128, 1))

    p1 = tmp_path / "group_1.png"
    p2 = tmp_path / "group_2.tif"
    p3 = tmp_path / "group_3.png"
    PILImage.fromarray(arr).save(p1, format="PNG", compress_level=1)
    PILImage.fromarray(arr).save(p2, format="TIFF")
    PILImage.fromarray(arr).save(p3, format="PNG", compress_level=9)

    img1 = IngestionService.ingest_file(db_session, p1.read_bytes(), "group_1.png")
    img2 = IngestionService.ingest_file(db_session, p2.read_bytes(), "group_2.tif")
    img3 = IngestionService.ingest_file(db_session, p3.read_bytes(), "group_3.png")

    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": [img1.id, img2.id, img3.id], "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        groups = res.json()["duplicate_groups"]
        assert len(groups) == 1
        group = groups[0]
        assert group["representative_image_id"] in [img1.id, img2.id, img3.id]
        assert len(group["member_image_ids"]) == 3


def test_multi_image_duplicate_group_advisory(tmp_path, db_session):
    """Duplicate group must include strict advisory forbidding automatic deletion."""
    arr = np.linspace(0, 255, 128, dtype=np.uint8)
    arr = np.tile(arr, (128, 1))

    p1 = tmp_path / "adv_1.png"
    p2 = tmp_path / "adv_2.tif"
    PILImage.fromarray(arr).save(p1, format="PNG")
    PILImage.fromarray(arr).save(p2, format="TIFF")

    img1 = IngestionService.ingest_file(db_session, p1.read_bytes(), "adv_1.png")
    img2 = IngestionService.ingest_file(db_session, p2.read_bytes(), "adv_2.tif")

    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": [img1.id, img2.id], "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        groups = res.json()["duplicate_groups"]
        assert len(groups) == 1
        advisory = groups[0]["advisory"]
        assert "redundancy detected" in advisory.lower()
        assert "archival" in advisory.lower() or "removal" in advisory.lower()


# ==============================================================================
# 5. Pipeline B: Quality-Risk Screening, Localization & Evidence Tests
# ==============================================================================

def test_multi_image_quality_indicators_present(test_image_cohort):
    """Every image must have image-derived indicators (focus, contrast, entropy)."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        for img in res.json()["images"]:
            assert "quality" in img
            assert "indicators" in img["quality"]
            indicator_names = [ind["indicator_name"] for ind in img["quality"]["indicators"]]
            assert "laplacian_variance" in indicator_names
            assert "saturation_ratio" in indicator_names
            assert "dynamic_range" in indicator_names
            assert "entropy" in indicator_names


def test_multi_image_quality_triage_statuses(test_image_cohort):
    """Quality decision status must strictly be NORMAL, QUALITY_RISK, or UNCERTAIN_ABSTAIN."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        allowed_statuses = {"NORMAL", "QUALITY_RISK", "UNCERTAIN_ABSTAIN"}
        for img in res.json()["images"]:
            assert img["quality"]["decision_status"] in allowed_statuses


def test_multi_image_localization_bounding_boxes(test_image_cohort):
    """Localization must return model-derived suspicious region envelopes."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        for img in res.json()["images"]:
            loc = img["localization"]
            assert "suspicious region" in loc["region_type"].lower()
            assert "bounding_boxes" in loc
            assert isinstance(loc["bounding_boxes"], list)


def test_multi_image_evidence_cohort_retrieval(test_image_cohort):
    """Comparable evidence must return cohort matches with similarity scores."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        for img in res.json()["images"]:
            ev = img["evidence"]
            assert "comparable_items" in ev
            assert ev["cohort_size"] >= 0


def test_multi_image_suggested_corrective_action(test_image_cohort):
    """Explanation must include suggested action code and operational targets."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        for img in res.json()["images"]:
            exp = img["explanation"]
            assert "action_code" in exp
            assert "recommendation_summary" in exp
            assert "operational_parameter_targets" in exp


# ==============================================================================
# 6. Comparative Quality View & Action Tests
# ==============================================================================

def test_multi_image_comparative_quality_summary(test_image_cohort):
    """Comparative summary must identify highest-risk image and ranking statement."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        comp = res.json()["comparative_quality_summary"]
        assert "highest_risk_image_id" in comp
        assert "comparative_statement" in comp
        assert "shows the strongest image-derived quality-risk signals" in comp["comparative_statement"]
        assert len(comp["ranking"]) == 3


def test_multi_image_comparative_corrective_action(test_image_cohort):
    """Pairwise comparison must provide comparative quality rationale."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort, "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        for pair in res.json()["pairwise_comparisons"]:
            cq = pair["comparative_quality"]
            assert "image_a_status" in cq
            assert "image_b_status" in cq
            assert "comparative_rationale" in cq
            assert "suggested_comparative_action" in cq


# ==============================================================================
# 7. Audit Logging & Cryptographic Provenance Tests
# ==============================================================================

def test_multi_image_audit_logging(test_image_cohort, db_session):
    """Analysis must write MULTI_IMAGE_ANALYSIS record to audit log."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort[:2], "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        logs = db_session.query(AuditLog).filter(AuditLog.action == "MULTI_IMAGE_ANALYSIS").all()
        assert len(logs) >= 1


def test_multi_image_cryptographic_seal(test_image_cohort):
    """Analysis must return master audit hash."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/analyze",
            json={"image_ids": test_image_cohort[:2], "representation": "dinov2_base"},
        )
        assert res.status_code == 200
        prov = res.json()["provenance"]
        assert "audit_hash" in prov
        assert len(prov["audit_hash"]) == 64  # SHA-256


# ==============================================================================
# 8. Human-in-the-Loop Curator Review & Routing Tests
# ==============================================================================

def test_multi_image_review_routing_accept(test_image_cohort, db_session):
    """Curator can submit ACCEPT review action for an image."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/review",
            json={
                "image_id": test_image_cohort[0],
                "decision": "ACCEPT",
                "comment": "Scientist approved micrograph quality.",
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "SUCCESS"
        assert "review_id" in data
        assert "audit_hash" in data


def test_multi_image_review_routing_reacquisition(test_image_cohort):
    """Curator can submit REQUEST_REACQUISITION action."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/review",
            json={
                "image_id": test_image_cohort[1],
                "decision": "REQUEST_REACQUISITION",
                "comment": "Severe defocus detected; request re-scan with 5mm WD.",
            },
        )
        assert res.status_code == 200
        assert res.json()["status"] == "SUCCESS"


def test_multi_image_review_routing_mark_duplicate(test_image_cohort):
    """Curator can submit MARK_DUPLICATE action."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/review",
            json={
                "image_id": test_image_cohort[2],
                "decision": "MARK_DUPLICATE",
                "peer_image_id": test_image_cohort[0],
                "comment": "Verified redundant field with Image #1.",
            },
        )
        assert res.status_code == 200
        assert res.json()["status"] == "SUCCESS"


def test_multi_image_review_invalid_decision(test_image_cohort):
    """Invalid review decision must return 400 error."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/review",
            json={
                "image_id": test_image_cohort[0],
                "decision": "UNSUPPORTED_DECISION_ABC",
            },
        )
        assert res.status_code == 400
        assert "invalid review decision" in res.json()["detail"].lower()


def test_multi_image_review_nonexistent_image():
    """Reviewing non-existent image ID must return 404 error."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/multi-image/review",
            json={"image_id": 9999999, "decision": "ACCEPT"},
        )
        assert res.status_code == 404


# ==============================================================================
# 9. Multipart File Upload Workflow Test
# ==============================================================================

def test_multi_image_file_upload_workflow(tmp_path):
    """Uploading 2 real image files directly via multipart executes cleanly."""
    p1 = _create_synthetic_image(tmp_path, "upload_1.png", pattern="gradient")
    p2 = _create_synthetic_image(tmp_path, "upload_2.png", pattern="high_contrast")

    with TestClient(app) as client:
        files = [
            ("files", ("upload_1.png", p1.read_bytes(), "image/png")),
            ("files", ("upload_2.png", p2.read_bytes(), "image/png")),
        ]
        res = client.post(
            "/api/v1/multi-image/analyze",
            files=files,
            data={"representation_form": "dinov2_base"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["total_images"] == 2
        assert data["total_pairs"] == 1
        assert len(data["pairwise_comparisons"]) == 1
        assert "provenance" in data
