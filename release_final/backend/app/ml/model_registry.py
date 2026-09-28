"""Authoritative Model Registry with cryptographic startup verification."""

import hashlib
from pathlib import Path
from typing import Any, Dict
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ModelVersion


class ModelVerificationError(RuntimeError):
    """Raised when model weights or checkpoint hash verification fails."""
    pass


class ModelRegistryService:
    """Manages model versions and enforces startup cryptographic verification."""

    @staticmethod
    def verify_checkpoint_hash(checkpoint_path: Path, expected_hash: str) -> bool:
        if not checkpoint_path.exists():
            raise ModelVerificationError(f"Model checkpoint not found at: {checkpoint_path}")
        with open(checkpoint_path, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        if actual_hash != expected_hash:
            raise ModelVerificationError(
                f"Model hash mismatch for {checkpoint_path}!\n"
                f"Expected: {expected_hash}\n"
                f"Actual:   {actual_hash}"
            )
        return True

    @classmethod
    def initialize_authoritative_models(cls, db: Session) -> Dict[str, ModelVersion]:
        """Verify checkpoints and ensure authoritative models exist in database."""
        # 1. Verify Phase 4 checkpoint hash
        cls.verify_checkpoint_hash(
            settings.PHASE4_CHECKPOINT_PATH,
            settings.EXPECTED_PHASE4_HASH
        )

        models = {}

        # DINOv2 ViT-S/14 (Frozen Phase 2 baseline)
        dinov2 = db.query(ModelVersion).filter(ModelVersion.model_id == "dinov2_vits14_phase2").first()
        if not dinov2:
            dinov2 = ModelVersion(
                model_id="dinov2_vits14_phase2",
                version="1.0.0",
                architecture="DINOv2 ViT-S/14",
                embedding_dimension=settings.DINOV2_EMBEDDING_DIM,
                weights_hash="torch_hub_facebookresearch_dinov2_vits14",
                preprocessing_version=settings.PREPROCESSING_VERSION,
                source="torch.hub facebookresearch/dinov2",
                is_active=True
            )
            db.add(dinov2)

        # Phase 4 Acquisition-Aware Adapter
        phase4 = db.query(ModelVersion).filter(ModelVersion.model_id == "phase4_acquisition_adapter_seed42").first()
        if not phase4:
            phase4 = ModelVersion(
                model_id="phase4_acquisition_adapter_seed42",
                version="1.0.0",
                architecture="LinearProjection (384 -> 384)",
                embedding_dimension=settings.DINOV2_EMBEDDING_DIM,
                weights_hash=settings.EXPECTED_PHASE4_HASH,
                preprocessing_version=settings.PREPROCESSING_VERSION,
                source=str(settings.PHASE4_CHECKPOINT_PATH),
                is_active=True
            )
            db.add(phase4)

        db.commit()
        db.refresh(dinov2)
        db.refresh(phase4)

        models["dinov2"] = dinov2
        models["phase4"] = phase4
        return models
