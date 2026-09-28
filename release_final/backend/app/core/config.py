"""Platform Configuration Settings."""

import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "SciData Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./platform/storage/scidata_platform.db"  # Defaults to local SQLite for tests, overridable to Postgres
    )

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:80",
        "http://localhost",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:80",
        "http://127.0.0.1",
    ]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "scidata-super-secret-production-key-phase8-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Storage Paths
    BASE_STORAGE_PATH: Path = Path("platform/storage")
    STORAGE_PATH: Path = Path("platform/storage")
    ORIGINALS_PATH: Path = Path("platform/storage/originals")
    THUMBNAILS_PATH: Path = Path("platform/storage/thumbnails")
    INDEXES_PATH: Path = Path("platform/storage/indexes")
    STORAGE_BACKEND_TYPE: str = os.getenv("STORAGE_BACKEND_TYPE", "LOCAL")  # LOCAL or S3

    # Authoritative Frozen Models & Checkpoints
    DINOV2_MODEL_NAME: str = "dinov2_vits14"
    DINOV2_EMBEDDING_DIM: int = 384
    PHASE4_CHECKPOINT_PATH: Path = Path("data/processed/phase4/checkpoints/best_checkpoint_seed42.pt")
    EXPECTED_PHASE4_HASH: str = "53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62"

    # Preprocessing
    PREPROCESSING_VERSION: str = "1.0.0"
    IMAGE_TARGET_SIZE: int = 224

    # Limits
    MAX_UPLOAD_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: set = {".tif", ".tiff", ".png", ".jpg", ".jpeg"}

    model_config = ConfigDict(
        env_file=".env",
        extra="allow",
    )


settings = Settings()
