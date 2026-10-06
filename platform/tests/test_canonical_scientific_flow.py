"""Canonical Scientific End-to-End Workflow Test.

Verifies the complete 17-stage scientific imaging curation workflow:
LOGIN -> UPLOAD -> VALIDATE -> STORE -> METADATA -> REPRESENTATION ->
QUALITY SCREENING -> LOCALIZATION -> RETRIEVAL -> EVIDENCE RETRIEVAL ->
EXPLANATION -> SUGGESTED CORRECTIVE ACTION -> UNCERTAINTY / ABSTENTION ->
HUMAN REVIEW -> CURATION -> AUDIT -> PROVENANCE.
"""

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image as PILImage
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.db.models import (
    AuditLog,
    Embedding,
    Image,
    ImageMetadata,
    Project,
    ProvenanceEvent,
    QualityProfile,
    ReviewItem,
    User,
)


def test_canonical_scientific_flow_complete(db_session):
    """Execute and verify the authoritative 17-stage scientific curation workflow."""
    db = db_session
    flow_log = {}

    with TestClient(app) as client:
        # STAGE 1: LOGIN & AUTHENTICATION
        username = f"scientist_lead_{int(datetime.now(timezone.utc).timestamp())}"
        reg_res = client.post(
            "/api/v1/auth/register",
            json={
                "username": username,
                "email": f"{username}@microscopy.org",
                "password": "SecureScientistPassword123!",
                "role": "CURATOR",
            },
        )
        assert reg_res.status_code == 200, f"Registration failed: {reg_res.text}"
        auth_token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {auth_token}"}
        flow_log["1_LOGIN"] = {"status": "SUCCESS", "username": username}

        # Create testing project
        proj_res = client.post(
            "/api/v1/projects",
            json={"name": "Scientific Validation Cohort", "description": "Validation study"},
            headers=headers,
        )
        assert proj_res.status_code == 200
        project_id = proj_res.json()["id"]

        # STAGE 2: UPLOAD MICROGRAPH
        # Prepare realistic 16-bit-like pattern array
        rng = np.random.RandomState(42)
        test_arr = np.zeros((256, 256), dtype=np.uint8)
        # Add synthetic microstructural features
        test_arr[64:192, 64:192] = 180
        test_arr[100:150, 100:150] = 40  # dark pore/inclusion
        test_arr = (test_arr + rng.normal(0, 5, (256, 256))).clip(0, 255).astype(np.uint8)

        buf = io.BytesIO()
        PILImage.fromarray(test_arr).save(buf, format="PNG")
        file_bytes = buf.getvalue()

        upload_res = client.post(
            "/api/v1/images/upload",
            files={"file": ("specimen_field_40111.png", file_bytes, "image/png")},
            data={
                "project_id": project_id,
                "microscope": "ImageXpress Micro Automated",
                "detector": "CoolSNAP HQ CCD",
                "accelerating_voltage_kv": 20.0,
                "magnification": 20.0,
                "pixel_size_nm": 650.0,
            },
            headers=headers,
        )
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        img_data = upload_res.json()
        image_id = img_data["id"]
        flow_log["2_UPLOAD"] = {"status": "SUCCESS", "image_id": image_id}

        # STAGE 3: VALIDATE & STORE
        img_record = db.query(Image).filter(Image.id == image_id).first()
        assert img_record is not None
        assert len(img_record.sha256) == 64
        assert Path(img_record.storage_path).exists()
        assert img_record.width == 256
        assert img_record.height == 256
        flow_log["3_VALIDATE_STORE"] = {
            "status": "SUCCESS",
            "sha256": img_record.sha256,
            "path": img_record.storage_path,
        }

        # STAGE 4: METADATA EXTRACTION & COMPLETENESS
        meta_record = db.query(ImageMetadata).filter(ImageMetadata.image_id == image_id).first()
        assert meta_record is not None
        assert meta_record.microscope == "ImageXpress Micro Automated"
        assert meta_record.detector == "CoolSNAP HQ CCD"
        assert meta_record.accelerating_voltage_kv == 20.0
        assert meta_record.metadata_completeness > 0.0
        flow_log["4_METADATA"] = {
            "status": "SUCCESS",
            "microscope": meta_record.microscope,
            "completeness": meta_record.metadata_completeness,
        }

        # STAGE 5: REPRESENTATION GENERATION (DINOv2)
        emb_record = db.query(Embedding).filter(
            Embedding.image_id == image_id, Embedding.embedding_type == "dinov2_base"
        ).first()
        assert emb_record is not None
        assert len(emb_record.embedding_vector) == 384
        flow_log["5_REPRESENTATION"] = {
            "status": "SUCCESS",
            "dim": len(emb_record.embedding_vector),
            "type": emb_record.embedding_type,
        }

        # STAGE 6: QUALITY-RISK SCREENING
        qp = db.query(QualityProfile).filter(QualityProfile.image_id == image_id).first()
        assert qp is not None
        assert qp.shannon_entropy > 0.0
        assert qp.laplacian_variance >= 0.0
        assert qp.quality_label in ["NOMINAL", "QUALITY_RISK"]
        flow_log["6_QUALITY_SCREENING"] = {
            "status": "SUCCESS",
            "quality_label": qp.quality_label,
            "risk_score": qp.composite_quality_risk,
        }

        # STAGE 7: SPATIAL LOCALIZATION
        loc_res = client.get(f"/api/v1/images/{image_id}/localization", headers=headers)
        assert loc_res.status_code == 200, f"Localization failed: {loc_res.text}"
        loc_data = loc_res.json()
        assert loc_data["region_type"] == "model-derived suspicious region"
        assert loc_data["saliency_threshold"] == 0.50
        assert "bounding_boxes" in loc_data
        assert "area_fraction" in loc_data
        flow_log["7_LOCALIZATION"] = {
            "status": "SUCCESS",
            "region_type": loc_data["region_type"],
            "boxes_count": len(loc_data["bounding_boxes"]),
        }

        # STAGE 8: SIMILARITY RETRIEVAL
        search_res = client.post(
            "/api/v1/search",
            json={"image_id": image_id, "top_k": 5, "representation": "dinov2_base"},
            headers=headers,
        )
        assert search_res.status_code == 200, f"Search failed: {search_res.text}"
        search_items = search_res.json().get("results", search_res.json())
        assert isinstance(search_items, list)
        flow_log["8_RETRIEVAL"] = {"status": "SUCCESS", "results_count": len(search_items)}

        # STAGE 9: EVIDENCE RETRIEVAL
        ev_res = client.get(f"/api/v1/images/{image_id}/evidence", headers=headers)
        assert ev_res.status_code == 200, f"Evidence retrieval failed: {ev_res.text}"
        ev_data = ev_res.json()
        assert "decision_status" in ev_data
        assert "primary_artifact_category" in ev_data
        assert "quality_signals" in ev_data
        assert "audit_hash" in ev_data
        assert len(ev_data["audit_hash"]) == 64
        flow_log["9_EVIDENCE_RETRIEVAL"] = {
            "status": "SUCCESS",
            "decision_status": ev_data["decision_status"],
            "audit_hash": ev_data["audit_hash"],
        }

        # STAGE 10: EXPLANATION GENERATION
        exp_res = client.get(f"/api/v1/images/{image_id}/explanation", headers=headers)
        assert exp_res.status_code == 200, f"Explanation failed: {exp_res.text}"
        exp_data = exp_res.json()
        assert "suggested_action" in exp_data
        action = exp_data["suggested_action"]
        assert "action_code" in action
        assert "recommendation_summary" in action
        assert "scientific_rationale" in action
        flow_log["10_EXPLANATION"] = {
            "status": "SUCCESS",
            "action_code": action["action_code"],
            "summary": action["recommendation_summary"],
        }

        # STAGE 11: SUGGESTED CORRECTIVE ACTION
        assert isinstance(action["operational_parameter_targets"], list)
        assert isinstance(action["requires_operator_intervention"], bool)
        flow_log["11_SUGGESTED_ACTION"] = {
            "status": "SUCCESS",
            "targets": action["operational_parameter_targets"],
            "requires_operator": action["requires_operator_intervention"],
        }

        # STAGE 12: UNCERTAINTY & ABSTENTION GATE
        assert "classification_confidence" in exp_data
        assert "normalized_entropy" in exp_data
        assert "prediction_margin" in exp_data
        assert "abstention_triggered" in exp_data
        flow_log["12_UNCERTAINTY_ABSTENTION"] = {
            "status": "SUCCESS",
            "confidence": exp_data["classification_confidence"],
            "entropy": exp_data["normalized_entropy"],
            "abstained": exp_data["abstention_triggered"],
        }

        # STAGE 13 & 14: HUMAN REVIEW & ACTIVE CURATION
        curation_res = client.post(
            "/api/v1/curation/reviews",
            json={
                "image_id": image_id,
                "decision": "KEEP",
                "comment": "Scientist review verified nominal quality metrics.",
            },
            headers=headers,
        )
        assert curation_res.status_code == 200, f"Curation submission failed: {curation_res.text}"
        review_item = db.query(ReviewItem).filter(ReviewItem.image_id == image_id).first()
        assert review_item is not None
        assert review_item.decision == "KEEP"
        flow_log["13_14_CURATION"] = {
            "status": "SUCCESS",
            "decision": review_item.decision,
            "reviewer_id": review_item.reviewer_id,
        }

        # STAGE 15: AUDIT TRAIL LOGGING
        audit_logs = db.query(AuditLog).filter(
            AuditLog.action == "HUMAN_REVIEW_SUBMITTED", AuditLog.resource_id == review_item.id
        ).all()
        assert len(audit_logs) >= 1
        flow_log["15_AUDIT"] = {"status": "SUCCESS", "logs_count": len(audit_logs)}

        # STAGE 16 & 17: PROVENANCE GRAPH & ENDPOINTS
        prov_res1 = client.get(f"/api/v1/provenance/{image_id}", headers=headers)
        assert prov_res1.status_code == 200
        prov_res2 = client.get(f"/api/v1/provenance/image/{image_id}", headers=headers)
        assert prov_res2.status_code == 200
        assert len(prov_res2.json()) >= 1
        flow_log["16_17_PROVENANCE"] = {
            "status": "SUCCESS",
            "events_count": len(prov_res2.json()),
        }

    # Verify all 17 workflow steps executed cleanly
    assert len(flow_log) >= 14
    for step_name, result in flow_log.items():
        assert result["status"] == "SUCCESS", f"Step {step_name} did not succeed"
