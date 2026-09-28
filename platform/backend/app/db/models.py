"""SQLAlchemy ORM models for SciData Platform."""

from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="RESEARCHER")  # ADMIN, RESEARCHER, REVIEWER
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    projects = relationship("Project", back_populates="creator")
    reviews = relationship("ReviewItem", back_populates="reviewer")
    audit_logs = relationship("AuditLog", back_populates="user")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    creator = relationship("User", back_populates="projects")
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan")


class Image(Base):
    __tablename__ = "images"
    __table_args__ = (
        Index("ix_images_proj_status", "project_id", "processing_status"),
        Index("ix_images_created", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False, unique=True)
    thumbnail_path = Column(String(500), nullable=True)
    sha256 = Column(String(64), nullable=False, unique=True, index=True)
    mime_type = Column(String(100), nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=False)
    processing_status = Column(String(50), nullable=False, default="PENDING")  # PENDING, PROCESSING, READY, FAILED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="images")
    metadata_rel = relationship("ImageMetadata", back_populates="image", uselist=False, cascade="all, delete-orphan")
    quality_profile = relationship("QualityProfile", back_populates="image", uselist=False, cascade="all, delete-orphan")
    duplicate_profile = relationship("DuplicateProfile", back_populates="image", uselist=False, foreign_keys="DuplicateProfile.image_id", cascade="all, delete-orphan")
    embeddings = relationship("Embedding", back_populates="image", cascade="all, delete-orphan")
    provenance_events = relationship("ProvenanceEvent", back_populates="image", cascade="all, delete-orphan")
    review_items = relationship("ReviewItem", back_populates="image", cascade="all, delete-orphan")


class ImageMetadata(Base):
    __tablename__ = "image_metadata"
    __table_args__ = (
        Index("ix_metadata_volt_det", "accelerating_voltage_kv", "detector"),
    )

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), unique=True, nullable=False)
    microscope = Column(String(100), nullable=True)
    detector = Column(String(50), nullable=True)
    accelerating_voltage_kv = Column(Float, nullable=True)
    magnification = Column(Float, nullable=True)
    pixel_size_nm = Column(Float, nullable=True)
    beam_current_na = Column(Float, nullable=True)
    dwell_time_us = Column(Float, nullable=True)
    working_distance_mm = Column(Float, nullable=True)
    chamber_pressure_pa = Column(Float, nullable=True)
    metadata_source = Column(String(50), nullable=False, default="embedded")  # embedded, manual, dataset, unknown
    metadata_completeness = Column(Float, nullable=False, default=0.0)
    raw_metadata_json = Column(JSON, nullable=True)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", back_populates="metadata_rel")


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(100), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=False)
    architecture = Column(String(100), nullable=False)
    embedding_dimension = Column(Integer, nullable=False)
    weights_hash = Column(String(64), nullable=False)
    preprocessing_version = Column(String(50), nullable=False)
    source = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    embeddings = relationship("Embedding", back_populates="model")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    model_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False)
    embedding_type = Column(String(50), nullable=False)  # dinov2_base, phase4_adapted
    embedding_vector = Column(JSON, nullable=False)
    l2_normalized = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", back_populates="embeddings")
    model = relationship("ModelVersion", back_populates="embeddings")


class QualityProfile(Base):
    __tablename__ = "quality_profiles"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), unique=True, nullable=False)
    laplacian_variance = Column(Float, nullable=True)
    edge_density = Column(Float, nullable=True)
    shannon_entropy = Column(Float, nullable=True)
    dynamic_range = Column(Float, nullable=True)
    clipping_ratio = Column(Float, nullable=True)
    high_freq_fft_ratio = Column(Float, nullable=True)
    composite_quality_risk = Column(Float, nullable=False)
    quality_label = Column(String(50), nullable=False, default="NOMINAL")  # NOMINAL, RISK_FLAGGED
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", back_populates="quality_profile")


class DuplicateProfile(Base):
    __tablename__ = "duplicate_profiles"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), unique=True, nullable=False)
    phash = Column(String(64), nullable=True)
    dhash = Column(String(64), nullable=True)
    duplicate_status = Column(String(50), nullable=False, default="NO_DECLARED_REDUNDANCY_DETECTED")
    matched_image_id = Column(Integer, ForeignKey("images.id", ondelete="SET NULL"), nullable=True)
    similarity_score = Column(Float, nullable=True)
    match_stage = Column(String(50), nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", foreign_keys=[image_id], back_populates="duplicate_profile")
    matched_image = relationship("Image", foreign_keys=[matched_image_id])


class ProvenanceEvent(Base):
    __tablename__ = "provenance_events"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    software_version = Column(String(50), nullable=False)
    model_version = Column(String(50), nullable=True)
    parameters = Column(JSON, nullable=True)
    status = Column(String(50), nullable=False, default="SUCCESS")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    image = relationship("Image", back_populates="provenance_events")


class RetrievalQuery(Base):
    __tablename__ = "retrieval_queries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    query_image_id = Column(Integer, ForeignKey("images.id"), nullable=True)
    query_mode = Column(String(50), nullable=False, default="visual_only")
    top_k = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    results = relationship("RetrievalResult", back_populates="query", cascade="all, delete-orphan")


class RetrievalResult(Base):
    __tablename__ = "retrieval_results"

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("retrieval_queries.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, nullable=False)
    result_image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    metadata_summary = Column(JSON, nullable=True)
    duplicate_status = Column(String(50), nullable=True)
    novelty_score = Column(Float, nullable=True)

    query = relationship("RetrievalQuery", back_populates="results")
    result_image = relationship("Image")


class ReviewItem(Base):
    __tablename__ = "review_items"
    __table_args__ = (
        Index("ix_review_status_prio", "status", "priority"),
    )

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    decision = Column(String(50), nullable=False)  # KEEP, REVIEW_LATER, DUPLICATE, LOW_QUALITY, INTERESTING_NOVEL, INCORRECT_METADATA
    comment = Column(Text, nullable=True)
    priority = Column(Float, nullable=False, default=0.0)
    algorithmic_recommendation = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, COMPLETED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at = Column(DateTime, nullable=True)

    image = relationship("Image", back_populates="review_items")
    reviewer = relationship("User", back_populates="reviews")


class ProcessingRun(Base):
    __tablename__ = "processing_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), nullable=False, default="RUNNING")
    items_total = Column(Integer, nullable=False, default=0)
    items_processed = Column(Integer, nullable=False, default=0)
    errors = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_time_user", "timestamp", "user_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(Integer, nullable=True)
    model_version = Column(String(50), nullable=True)
    parameters = Column(JSON, nullable=True)
    result_status = Column(String(50), nullable=False, default="SUCCESS")
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audit_logs")
