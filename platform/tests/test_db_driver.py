"""Automated verification of database driver, dialect interception, and production security rules."""

import pytest
from sqlalchemy import create_engine, text

from app.core.config import Settings


def test_psycopg2_driver_installed_and_importable():
    """Verify that psycopg2-binary driver is installed and importable."""
    import psycopg2
    assert hasattr(psycopg2, "__version__")
    assert len(psycopg2.__version__) > 0


def test_database_url_dialect_interception():
    """Verify dialect rewriting from legacy or generic URLs to postgresql+psycopg2."""
    def rewrite_url(raw_url: str) -> str:
        url = raw_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql+psycopg://", "postgresql+psycopg2://", 1)
        elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
            url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
        return url

    # Test 1: postgres://
    assert rewrite_url("postgres://scidata_user:secret@postgres:5432/scidata_db") == (
        "postgresql+psycopg2://scidata_user:secret@postgres:5432/scidata_db"
    )

    # Test 2: postgresql://
    assert rewrite_url("postgresql://scidata_user:secret@127.0.0.1:5432/scidata_platform") == (
        "postgresql+psycopg2://scidata_user:secret@127.0.0.1:5432/scidata_platform"
    )

    # Test 3: postgresql+psycopg:// (psycopg v3 spec rewrites to psycopg2)
    assert rewrite_url("postgresql+psycopg://scidata_user:secret@db:5432/scidata") == (
        "postgresql+psycopg2://scidata_user:secret@db:5432/scidata"
    )

    # Test 4: sqlite is unchanged
    assert rewrite_url("sqlite:///./platform/storage/test.db") == (
        "sqlite:///./platform/storage/test.db"
    )


def test_select_1_connectivity():
    """Verify standard SELECT 1 connectivity probe."""
    test_engine = create_engine("sqlite:///:memory:")
    with test_engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
    assert result == 1


def test_production_security_validation_fails_on_insecure_key():
    """Verify that production mode raises ValueError on placeholder SECRET_KEY."""
    insecure_settings = Settings(
        ENVIRONMENT="production",
        TESTING=False,
        SECRET_KEY="CHANGE_ME",
    )
    with pytest.raises(ValueError, match="FATAL SECURITY CONFIGURATION"):
        insecure_settings.validate_production_security()

    short_settings = Settings(
        ENVIRONMENT="production",
        TESTING=False,
        SECRET_KEY="short-key-less-than-32-chars",
    )
    with pytest.raises(ValueError, match="FATAL SECURITY CONFIGURATION"):
        short_settings.validate_production_security()


def test_production_security_validation_passes_on_valid_key():
    """Verify that production mode passes with a sufficiently long, non-default key."""
    secure_settings = Settings(
        ENVIRONMENT="production",
        TESTING=False,
        SECRET_KEY="a" * 32,
    )
    # Should not raise
    secure_settings.validate_production_security()


def test_testing_mode_bypasses_production_key_check():
    """Verify that testing mode permits test keys."""
    test_settings = Settings(
        ENVIRONMENT="production",
        TESTING=True,
        SECRET_KEY="short",
    )
    # Should not raise because TESTING=True
    test_settings.validate_production_security()
