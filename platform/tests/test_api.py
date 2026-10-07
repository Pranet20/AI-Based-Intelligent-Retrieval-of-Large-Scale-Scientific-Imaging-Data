from starlette.testclient import TestClient
from app.main import app


def test_api_health_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert "database" in data
        assert "faiss_index_count" in data


def test_api_version_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/version")
        assert res.status_code == 200
        data = res.json()
        assert data["dinov2_model"] == "dinov2_vits14"
        assert data["embedding_dimension"] == 384
        assert data["phase4_checkpoint_hash"] == "53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62"


def test_api_dashboard_stats_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/dashboard/stats")
        assert res.status_code == 200
        data = res.json()
        assert "total_images" in data
        assert "total_projects" in data
        assert "potential_redundancies" in data
        assert "quality_risk_items" in data
        assert "pending_reviews" in data
        assert "completed_reviews" in data
        assert data["timestamp"] == "LIVE_DATABASE_DERIVED"


def test_api_projects_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/projects")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


def test_api_models_endpoint():
    with TestClient(app) as client:
        res = client.get("/api/v1/models")
        assert res.status_code == 200
        models = res.json()
        assert len(models) >= 2
        model_ids = [m["model_id"] for m in models]
        assert "dinov2_vits14_phase2" in model_ids
        assert "phase4_acquisition_adapter_seed42" in model_ids


def test_search_dual_representation_distinct_paths():
    """Verify dinov2_base and phase4_adapted execute distinct scientific retrieval paths without silent fallback."""
    with TestClient(app) as client:
        # Create test image in test database
        import io
        from PIL import Image as PILImage
        img = PILImage.new("RGB", (256, 256), color=(45, 55, 65))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        # Authenticate as admin
        login_res = client.post("/api/v1/auth/login", data={"username": "admin", "password": "admin123"})
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        auth_header = {"Authorization": f"Bearer {login_res.json()['access_token']}"}

        upload_res = client.post(
            "/api/v1/images/upload",
            files={"file": ("dual_rep_test.png", buf.getvalue(), "image/png")},
            data={"project_id": 1},
            headers=auth_header,
        )
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        image_id = upload_res.json()["id"]

        # 1. DINOv2 visual retrieval
        res_dino = client.post(
            "/api/v1/search/vector",
            json={"query_image_id": image_id, "top_k": 3, "representation": "dinov2_base"},
        )
        assert res_dino.status_code == 200
        dino_data = res_dino.json()
        assert dino_data["retrieval_mode"] == "frozen_visual_dinov2_vit_s14"
        assert "Visual quality retrieval" in dino_data["note"]

        # 2. Phase 4 acquisition-aware retrieval
        res_p4 = client.post(
            "/api/v1/search/vector",
            json={"query_image_id": image_id, "top_k": 3, "representation": "phase4_adapted"},
        )
        assert res_p4.status_code == 200
        p4_data = res_p4.json()
        assert p4_data["retrieval_mode"] == "frozen_phase4_acquisition_adapter"
        assert "Acquisition-aware retrieval" in p4_data["note"]


def test_search_unsupported_representation_rejection():
    """Verify that unsupported representations return explicit HTTP 400 error rather than silent fallback."""
    with TestClient(app) as client:
        res = client.post(
            "/api/v1/search/vector",
            json={"query_image_id": 1, "top_k": 3, "representation": "arbitrary_unsupported_model"},
        )
        assert res.status_code == 400
        assert "Unsupported representation" in res.json()["detail"]

