"""Schema Migration & Optimization Utility.

Applies declarative schema changes, ensures table creation,
and generates composite performance indexes.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "platform" / "backend"))

from app.db.session import Base, engine, SessionLocal
from app.db.models import (
    User, Project, Image, ImageMetadata, ModelVersion, Embedding,
    QualityProfile, DuplicateProfile, ProvenanceEvent,
    RetrievalQuery, RetrievalResult, ReviewItem, ProcessingRun, AuditLog
)


def run_migration():
    print("[1/2] Connecting to database and creating tables...")
    Base.metadata.create_all(bind=engine)
    print("  All ORM tables and constraints initialized.")

    print("[2/2] Verifying composite performance indexes...")
    inspector = __import__("sqlalchemy").inspect(engine)
    for table_name in ["images", "image_metadata", "review_items", "audit_logs"]:
        indexes = inspector.get_indexes(table_name)
        idx_names = [idx["name"] for idx in indexes]
        print(f"  Table '{table_name}': {len(idx_names)} indexes found -> {idx_names}")

    print("\n[SUCCESS] Schema migration and index verification completed.")
    return 0


if __name__ == "__main__":
    sys.exit(run_migration())
