import pytest
from sqlalchemy import inspect
from app.db.models import (
    User,
    Project,
    Image,
    ImageMetadata,
    QualityProfile,
    DuplicateProfile,
    Embedding,
    ReviewItem,
    ModelVersion,
    AuditLog,
)
from app.db.session import engine


def test_database_tables_exist():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected = [
        "users",
        "projects",
        "images",
        "image_metadata",
        "quality_profiles",
        "duplicate_profiles",
        "embeddings",
        "review_items",
        "model_versions",
        "audit_logs",
    ]
    for tbl in expected:
        assert tbl in tables, f"Expected table '{tbl}' to exist in database"


def test_user_and_project_models(db_session):
    u = db_session.query(User).filter(User.username == "admin").first()
    assert u is not None
    assert u.role == "ADMIN"
    assert u.email == "admin@scidata.internal"

    p = db_session.query(Project).filter(Project.name == "Benchmark Project").first()
    assert p is not None
    assert p.created_by == u.id
