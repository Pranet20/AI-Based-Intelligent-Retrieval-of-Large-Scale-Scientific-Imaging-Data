"""Idempotency audit test for scientific image ingestion."""

import io
import numpy as np
from PIL import Image as PILImage
from starlette.testclient import TestClient

from app.main import app
from app.core.security import create_access_token
from app.db.models import Image
from app.ml.faiss_engine import FAISSEngine


def test_strict_idempotency_double_ingestion(db_session):
    """Verify that uploading the exact same image twice is strictly idempotent."""
    db = db_session
    try:
        # Create controlled image
        rng = np.random.RandomState(999)
        arr = (rng.rand(128, 128) * 255).astype(np.uint8)
        buf = io.BytesIO()
        PILImage.fromarray(arr).save(buf, format="PNG")
        raw_bytes = buf.getvalue()

        token = create_access_token(subject=1, role="ADMIN")
        faiss_engine = FAISSEngine()
        initial_faiss_count = faiss_engine.index.ntotal

        with TestClient(app) as client:
            # First upload
            res1 = client.post(
                "/api/v1/images/upload",
                files={"file": ("idempotency_fixture.png", raw_bytes, "image/png")},
                data={"microscope": "Test Microscope", "accelerating_voltage_kv": 10.0},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res1.status_code == 200
            data1 = res1.json()
            image_id_1 = data1["id"]
            sha256_1 = data1["sha256"]

            count_after_first = faiss_engine.index.ntotal

            # Second upload of the exact same bytes
            res2 = client.post(
                "/api/v1/images/upload",
                files={"file": ("idempotency_fixture.png", raw_bytes, "image/png")},
                data={"microscope": "Test Microscope", "accelerating_voltage_kv": 10.0},
                headers={"Authorization": f"Bearer {token}"},
            )
            assert res2.status_code == 200
            data2 = res2.json()
            image_id_2 = data2["id"]
            sha256_2 = data2["sha256"]

            # Assertions
            assert image_id_1 == image_id_2, "Idempotent re-upload must return identical logical Image ID"
            assert sha256_1 == sha256_2, "SHA-256 must match exactly"

            # Check database: no duplicate records for this SHA-256
            db_records = db.query(Image).filter(Image.sha256 == sha256_1).all()
            assert len(db_records) == 1, "Database must not create duplicate Image records for identical hash"

            # Check FAISS index count: no duplicate entries added
            count_after_second = faiss_engine.index.ntotal
            assert count_after_second == count_after_first, "FAISS index must not have duplicate vectors added"
    finally:
        db.close()
