"""Model Registry API endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import ModelVersion
from app.db.session import get_db
from app.services.audit import AuditService

router = APIRouter(prefix="/models", tags=["Models"])


class ModelVersionResponse(BaseModel):
    id: int
    model_id: str
    version: str
    architecture: str
    embedding_dimension: int
    weights_hash: str
    preprocessing_version: str
    source: str
    is_active: bool


@router.get("", response_model=List[ModelVersionResponse])
def list_models(db: Session = Depends(get_db)):
    models = db.query(ModelVersion).all()
    AuditService.log_action(
        db=db,
        action="MODEL_ACCESS",
        resource_type="model_versions",
        parameters={"count": len(models)},
    )
    return [
        ModelVersionResponse(
            id=m.id,
            model_id=m.model_id,
            version=m.version,
            architecture=m.architecture,
            embedding_dimension=m.embedding_dimension,
            weights_hash=m.weights_hash,
            preprocessing_version=m.preprocessing_version,
            source=m.source,
            is_active=m.is_active,
        )
        for m in models
    ]
