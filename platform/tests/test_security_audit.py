"""Comprehensive security audit tests covering RBAC, JWT, path traversal, and file validation."""

from datetime import timedelta
import io
import numpy as np
from PIL import Image as PILImage
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.db.models import User
from app.db.session import SessionLocal


def test_password_hashing_security():
    password = "SuperSecretPassword123!"
    hashed = get_password_hash(password)
    assert "$" in hashed
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False
    assert verify_password("", hashed) is False


def test_jwt_lifecycle_and_expiration():
    payload = {"sub": "123", "role": "RESEARCHER"}
    # Valid token
    token = create_access_token(payload, expires_delta=timedelta(minutes=15))
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"

    # Expired token
    expired_token = create_access_token(payload, expires_delta=timedelta(seconds=-10))
    decoded_expired = decode_access_token(expired_token)
    assert decoded_expired is None

    # Tampered token
    tampered_token = token[:-4] + "abcd"
    decoded_tampered = decode_access_token(tampered_token)
    assert decoded_tampered is None


def test_unauthenticated_requests_return_401():
    with TestClient(app) as client:
        # Protected endpoints without token
        res1 = client.get("/api/v1/auth/me")
        assert res1.status_code == 401

        res2 = client.post("/api/v1/curation/reviews", json={"image_id": 1, "decision": "KEEP"})
        assert res2.status_code == 401

        res3 = client.put("/api/v1/images/1/metadata", json={"magnification": 1000.0})
        assert res3.status_code == 401

        res4 = client.get("/api/v1/admin/audit-logs")
        assert res4.status_code == 401


def test_role_authorization_rbac_enforcement(db_session):
    db = db_session
    try:
        # Create users for all three roles
        researcher = db.query(User).filter(User.username == "sec_researcher").first()
        if not researcher:
            researcher = User(username="sec_researcher", email="res@test.org", hashed_password="pw", role="RESEARCHER")
            db.add(researcher)

        curator = db.query(User).filter(User.username == "sec_curator").first()
        if not curator:
            curator = User(username="sec_curator", email="cur@test.org", hashed_password="pw", role="CURATOR")
            db.add(curator)

        admin = db.query(User).filter(User.username == "sec_admin").first()
        if not admin:
            admin = User(username="sec_admin", email="adm@test.org", hashed_password="pw", role="ADMIN")
            db.add(admin)

        db.commit()
        db.refresh(researcher)
        db.refresh(curator)
        db.refresh(admin)

        r_token = create_access_token(subject=researcher.id, role="RESEARCHER")
        c_token = create_access_token(subject=curator.id, role="CURATOR")
        a_token = create_access_token(subject=admin.id, role="ADMIN")

        with TestClient(app) as client:
            # 1. Curator & Admin endpoints: PUT /images/{id}/metadata
            # Researcher must receive 403 Forbidden
            res_put_r = client.put(
                "/api/v1/images/1/metadata",
                json={"magnification": 50000.0},
                headers={"Authorization": f"Bearer {r_token}"},
            )
            assert res_put_r.status_code == 403

            # 2. Curator & Admin endpoints: POST /curation/reviews
            # Researcher must receive 403 Forbidden
            res_rev_r = client.post(
                "/api/v1/curation/reviews",
                json={"image_id": 1, "decision": "KEEP"},
                headers={"Authorization": f"Bearer {r_token}"},
            )
            assert res_rev_r.status_code == 403

            # 3. Admin-only endpoint: GET /admin/audit-logs
            # Researcher must receive 403
            res_adm_r = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {r_token}"})
            assert res_adm_r.status_code == 403

            # Curator must receive 403
            res_adm_c = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {c_token}"})
            assert res_adm_c.status_code == 403

            # Admin must receive 200 OK
            res_adm_a = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {a_token}"})
            assert res_adm_a.status_code == 200
            assert isinstance(res_adm_a.json(), list)
    finally:
        db.close()


def test_path_traversal_and_malformed_filename_protection():
    token = create_access_token(subject=1, role="ADMIN")
    buf = io.BytesIO(b"fake image bytes")

    with TestClient(app) as client:
        # Path traversal with ../
        res_trav1 = client.post(
            "/api/v1/images/upload",
            files={"file": ("../../etc/passwd.png", b"fake", "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_trav1.status_code == 400

        # Path traversal with ..\
        res_trav2 = client.post(
            "/api/v1/images/upload",
            files={"file": ("..\\evil.png", b"fake", "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_trav2.status_code == 400

        # Path traversal with absolute path /root/test.png
        res_trav3 = client.post(
            "/api/v1/images/upload",
            files={"file": ("/root/test.png", b"fake", "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res_trav3.status_code == 400


def test_unsupported_mime_type_protection():
    token = create_access_token(subject=1, role="ADMIN")
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/images/upload",
            files={"file": ("malicious.sh", b"#!/bin/bash\necho hack", "application/x-sh")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400


def test_oversized_upload_rejection():
    token = create_access_token(subject=1, role="ADMIN")
    # Generate bytes exceeding MAX_UPLOAD_SIZE_BYTES
    oversized = b"0" * (settings.MAX_UPLOAD_SIZE_BYTES + 1024)
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/images/upload",
            files={"file": ("large.png", oversized, "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert res.status_code == 400
