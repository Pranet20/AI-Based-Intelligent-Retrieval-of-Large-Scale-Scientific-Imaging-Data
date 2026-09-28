"""Closure audit tests for provenance event tracking and persistent audit logging."""

import os
import io
import tempfile
import numpy as np
from PIL import Image as PILImage
from starlette.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.db.models import AuditLog, Image, ProvenanceEvent, User


def test_closure_provenance_and_audit_full_spectrum(db_session):
    """Verify that all required provenance event types and audit actions are properly persisted."""
    db = db_session
    try:
        # Create test users
        admin_user = db.query(User).filter(User.username == "closure_admin").first()
        if not admin_user:
            admin_user = User(
                username="closure_admin",
                email="admin@closure.org",
                hashed_password="hashed_pass_placeholder",
                role="ADMIN",
            )
            db.add(admin_user)

        curator_user = db.query(User).filter(User.username == "closure_curator").first()
        if not curator_user:
            curator_user = User(
                username="closure_curator",
                email="curator@closure.org",
                hashed_password="hashed_pass_placeholder",
                role="CURATOR",
            )
            db.add(curator_user)

        db.commit()
        db.refresh(admin_user)
        db.refresh(curator_user)

        admin_token = create_access_token(subject=admin_user.id, role="ADMIN")
        curator_token = create_access_token(subject=curator_user.id, role="CURATOR")

        with TestClient(app) as client:
            # 1. Audit MODEL_ACCESS
            res_models = client.get("/api/v1/models")
            assert res_models.status_code == 200

            # 2. Upload controlled image fixture
            buf = io.BytesIO()
            arr = (np.random.RandomState(42).rand(100, 100) * 255).astype(np.uint8)
            PILImage.fromarray(arr).save(buf, format="PNG")
            img_bytes = buf.getvalue()

            upload_res = client.post(
                "/api/v1/images/upload",
                files={"file": ("closure_prov_test.png", img_bytes, "image/png")},
                data={"microscope": "FEI Helios G4 FX", "accelerating_voltage_kv": 5.0},
                headers={"Authorization": f"Bearer {curator_token}"},
            )
            assert upload_res.status_code == 200, upload_res.text
            img_id = upload_res.json()["id"]

            # 3. Provenance & Audit for METADATA_UPDATE
            put_res = client.put(
                f"/api/v1/images/{img_id}/metadata",
                json={"magnification": 25000.0, "detector": "TLD"},
                headers={"Authorization": f"Bearer {curator_token}"},
            )
            assert put_res.status_code == 200
            assert put_res.json()["magnification"] == 25000.0

            # 4. Provenance & Audit for SEARCH
            search_res = client.post(
                "/api/v1/search",
                data={"image_id": img_id, "top_k": 5},
                headers={"Authorization": f"Bearer {curator_token}"},
            )
            assert search_res.status_code == 200

            # 5. Provenance & Audit for REVIEW
            review_res = client.post(
                "/api/v1/curation/reviews",
                json={
                    "image_id": img_id,
                    "decision": "KEEP",
                    "comment": "Verified nominal resolution micrograph.",
                },
                headers={"Authorization": f"Bearer {curator_token}"},
            )
            assert review_res.status_code == 200

            # Verify Provenance Events in DB
            prov_events = db.query(ProvenanceEvent).filter(ProvenanceEvent.image_id == img_id).all()
            event_types = {e.event_type for e in prov_events}

            expected_prov = {
                "UPLOAD",
                "METADATA_EXTRACTION",
                "QUALITY_ANALYSIS",
                "EMBEDDING_GENERATION",
                "DUPLICATE_ANALYSIS",
                "INDEXING",
                "METADATA_UPDATE",
                "SEARCH",
                "REVIEW",
            }
            for exp in expected_prov:
                assert exp in event_types, f"Missing provenance event type: {exp}"

            # Verify Audit Logs in DB
            audit_logs = db.query(AuditLog).all()
            actions = {a.action for a in audit_logs}

            expected_audit = {
                "UPLOAD",
                "IMAGE_PROCESSING",
                "METADATA_UPDATE",
                "SEARCH",
                "HUMAN_REVIEW_SUBMITTED",
                "MODEL_ACCESS",
            }
            for exp_act in expected_audit:
                assert exp_act in actions, f"Missing audit action: {exp_act}"

            # Verify audit logs do not contain secrets or passwords
            for log in audit_logs:
                param_str = str(log.parameters)
                assert "password" not in param_str.lower() or "hashed_password" in param_str.lower()
                assert "secret_key" not in param_str.lower()
    finally:
        db.close()
