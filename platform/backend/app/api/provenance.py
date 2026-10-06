"""Provenance events API endpoints."""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.models import Image, ProvenanceEvent
from app.db.session import get_db

router = APIRouter(prefix="/provenance", tags=["Provenance"])


@router.get("")
def list_provenance_events(image_id: Optional[int] = None, limit: int = 50, db: Session = Depends(get_db)):
    query = db.query(ProvenanceEvent)
    if image_id:
        query = query.filter(ProvenanceEvent.image_id == image_id)
    events = query.order_by(ProvenanceEvent.id.desc()).limit(limit).all()
    out = []
    for e in events:
        out.append({
            "id": e.id,
            "image_id": e.image_id,
            "event_type": e.event_type,
            "software_version": e.software_version,
            "model_version": e.model_version,
            "parameters": e.parameters,
            "status": e.status,
            "timestamp": e.timestamp,
        })
    return out


@router.get("/image/{image_id}")
def get_image_provenance_list(image_id: int, db: Session = Depends(get_db)):
    """Return provenance events as a list for direct frontend / client consumption."""
    img = db.query(Image).filter(Image.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    events = db.query(ProvenanceEvent).filter(ProvenanceEvent.image_id == image_id).order_by(ProvenanceEvent.id.asc()).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "software_version": e.software_version,
            "model_version": e.model_version,
            "parameters": e.parameters,
            "status": e.status,
            "timestamp": e.timestamp,
        }
        for e in events
    ]


@router.get("/{image_id}")
def get_image_provenance_trail(image_id: int, db: Session = Depends(get_db)):
    """Return structured provenance report with image header and events array."""
    img = db.query(Image).filter(Image.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    events = db.query(ProvenanceEvent).filter(ProvenanceEvent.image_id == image_id).order_by(ProvenanceEvent.id.asc()).all()
    return {
        "image_id": image_id,
        "filename": img.original_filename,
        "sha256": img.sha256,
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "software_version": e.software_version,
                "model_version": e.model_version,
                "parameters": e.parameters,
                "status": e.status,
                "timestamp": e.timestamp,
            }
            for e in events
        ],
    }
