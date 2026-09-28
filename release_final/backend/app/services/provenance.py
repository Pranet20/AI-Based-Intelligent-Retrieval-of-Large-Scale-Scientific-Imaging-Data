"""Provenance Tracking Service."""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ProvenanceEvent


class ProvenanceService:
    """Manages scientific image provenance audit trail."""

    @staticmethod
    def record_event(
        db: Session,
        image_id: int,
        event_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        model_version: Optional[str] = None,
        status: str = "SUCCESS",
    ) -> ProvenanceEvent:
        event = ProvenanceEvent(
            image_id=image_id,
            event_type=event_type,
            software_version=settings.VERSION,
            model_version=model_version,
            parameters=parameters or {},
            status=status,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
