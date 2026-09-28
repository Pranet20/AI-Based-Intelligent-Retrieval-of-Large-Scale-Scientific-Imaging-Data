import os
import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add repo root and backend to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "platform" / "backend"))

from app.db.session import Base, get_db
from app.db.models import User, Project
from app.core.security import get_password_hash
from app.main import app

TEST_DB_PATH = Path("platform/storage/test_scidata.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if TEST_DB_PATH.exists():
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass
    Base.metadata.create_all(bind=engine)

    # Seed admin user
    db = TestingSessionLocal()
    admin = User(
        username="admin",
        email="admin@scidata.internal",
        hashed_password=get_password_hash("admin123"),
        role="ADMIN",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    proj = Project(
        name="Benchmark Project",
        description="Integration testing project",
        created_by=admin.id,
    )
    db.add(proj)
    db.commit()

    from app.ml.model_registry import ModelRegistryService
    ModelRegistryService.initialize_authoritative_models(db)
    db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    if TEST_DB_PATH.exists():
        try:
            os.remove(TEST_DB_PATH)
        except Exception:
            pass


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
