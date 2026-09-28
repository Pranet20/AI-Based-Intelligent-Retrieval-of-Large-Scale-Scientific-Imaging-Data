import io
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
from starlette.testclient import TestClient

from app.main import app
from app.core.security import create_access_token


def test_14_step_ingestion_pipeline():
    # 1. Create synthetic PNG micrograph
    arr = np.linspace(10, 240, 224 * 224, dtype=np.uint8).reshape((224, 224))
    img_buf = io.BytesIO()
    Image.fromarray(arr).save(img_buf, format="PNG")
    img_bytes = img_buf.getvalue()

    token = create_access_token("1", role="ADMIN")
    auth_headers = {"Authorization": f"Bearer {token}"}

    with TestClient(app) as client:
        # Get or create project
        proj_res = client.get("/api/v1/projects")
        projects = proj_res.json()
        if projects and isinstance(projects, list) and len(projects) > 0:
            project_id = projects[0]["id"]
        else:
            p_res = client.post("/api/v1/projects", json={"name": "Ingestion Test Project"}, headers=auth_headers)
            project_id = p_res.json()["id"]

        # Step 1: Upload image
        files = {"file": ("micrograph_test_1.png", img_bytes, "image/png")}
        data = {
            "project_id": str(project_id),
            "modality": "SEM",
            "instrument": "Helios NanoLab",
            "specimen_id": "TEST-SPEC-01",
            "roi_id": "ROI-01",
            "acquisition_id": "RUN-01",
        }

        res = client.post("/api/v1/images/upload", data=data, files=files, headers=auth_headers)
        assert res.status_code == 200, f"Upload failed: {res.text}"
        upload_resp = res.json()
        assert upload_resp["processing_status"] == "READY"
        image_id = upload_resp["id"]

        # Step 2: Verify Image Retrieval via API with full profiles
        get_res = client.get(f"/api/v1/images/{image_id}", headers=auth_headers)
        assert get_res.status_code == 200
        img_data = get_res.json()
        assert img_data["id"] == image_id
        assert img_data["processing_status"] == "READY"
        assert img_data["width"] == 224
        assert img_data["height"] == 224
        assert "quality" in img_data
        assert img_data["quality"]["quality_label"] in ["NOMINAL", "RISK_FLAGGED"]
        assert "duplicate" in img_data

        # Step 3: Test Idempotency on Re-Upload (exact bytes return same image record)
        files_same = {"file": ("micrograph_test_1_same.png", img_bytes, "image/png")}
        res_same = client.post("/api/v1/images/upload", data=data, files=files_same, headers=auth_headers)
        assert res_same.status_code == 200
        same_id = res_same.json()["id"]
        assert same_id == image_id  # Idempotent response returns existing image

        # Step 4: Test Near Duplicate Detection via Cascade (single pixel modified)
        arr_perturbed = arr.copy()
        arr_perturbed[0, 0] = (arr_perturbed[0, 0] + 1) % 255
        buf_perturbed = io.BytesIO()
        Image.fromarray(arr_perturbed).save(buf_perturbed, format="PNG")

        files_pert = {"file": ("micrograph_test_1_near.png", buf_perturbed.getvalue(), "image/png")}
        res_pert = client.post("/api/v1/images/upload", data=data, files=files_pert, headers=auth_headers)
        assert res_pert.status_code == 200, f"Perturbed upload failed: {res_pert.text}"
        pert_id = res_pert.json()["id"]
        assert pert_id != image_id

        pert_detail = client.get(f"/api/v1/images/{pert_id}", headers=auth_headers).json()
        assert pert_detail["duplicate"]["duplicate_status"] == "POTENTIAL_NEAR_DUPLICATE"
        assert pert_detail["duplicate"]["matched_image_id"] == image_id
        assert pert_detail["duplicate"]["match_stage"] == "STAGE_6_PIXEL_SSIM"
