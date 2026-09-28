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
