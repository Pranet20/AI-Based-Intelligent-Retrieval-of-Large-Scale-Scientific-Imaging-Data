"""Multi-Image Scientific Comparison and Quality-Risk Analysis API Router."""

import hashlib
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_optional_user_payload
from app.db.models import Image, ReviewItem
from app.db.session import get_db
from app.services.audit import AuditService
from app.services.ingestion import IngestionService
from app.services.multi_image import MultiImageComparisonService
from app.services.provenance import ProvenanceService

logger = logging.getLogger("scidata.api.multi_image")
router = APIRouter(tags=["Multi-Image Analysis"])


class MultiImageAnalyzeRequest(BaseModel):
    image_ids: List[int]
    representation: str = "dinov2_base"


class MultiImageReviewRequest(BaseModel):
    image_id: int
    decision: str  # ACCEPT, FLAG, REQUEST_REACQUISITION, MARK_DUPLICATE, MARK_NOT_DUPLICATE, ADD_NOTE
    comment: Optional[str] = None
    peer_image_id: Optional[int] = None
    analysis_id: Optional[str] = None


@router.post("/analyze")
async def analyze_multi_images(
    request: Request,
    user_payload: Optional[Dict[str, Any]] = Depends(get_optional_user_payload),
    db: Session = Depends(get_db),
):
    """
    Executes full multi-image comparative workflow.
    Accepts either multipart file uploads or a JSON list of existing image IDs.
    """
    user_id = int(user_payload.get("sub")) if user_payload and user_payload.get("sub") else None
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        files = form.getlist("files")
        image_ids_str = form.get("image_ids_str")
        rep = form.get("representation") or form.get("representation_form") or "dinov2_base"
        project_id_raw = form.get("project_id")
        project_id = int(project_id_raw) if project_id_raw else None

        if files and len(files) > 0:
            ingested_ids = []
            for upload_file in files:
                if not hasattr(upload_file, "read"):
                    continue
                content = await upload_file.read()
                if not content:
                    continue
                img_rec = IngestionService.ingest_file(
                    db=db,
                    file_bytes=content,
                    original_filename=getattr(upload_file, "filename", None) or "uploaded_micrograph.png",
                    project_id=project_id,
                )
                ingested_ids.append(img_rec.id)

            if len(ingested_ids) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="At least 2 valid image files must be provided for multi-image analysis.",
                )

            return MultiImageComparisonService.analyze_images(
                db=db,
                image_ids=ingested_ids,
                representation=str(rep),
                current_user_id=user_id,
            )

        if image_ids_str:
            try:
                ids = [int(x.strip()) for x in str(image_ids_str).split(",") if x.strip()]
            except Exception:
                raise HTTPException(status_code=400, detail="Invalid image_ids_str format. Expected comma-separated integers.")
            return MultiImageComparisonService.analyze_images(
                db=db,
                image_ids=ids,
                representation=str(rep),
                current_user_id=user_id,
            )
    else:
        # JSON Payload
        try:
            body = await request.json()
        except Exception:
            body = {}

        if body and "image_ids" in body:
            ids = body.get("image_ids", [])
            rep = body.get("representation", "dinov2_base")
            return MultiImageComparisonService.analyze_images(
                db=db,
                image_ids=ids,
                representation=str(rep),
                current_user_id=user_id,
            )

    raise HTTPException(
        status_code=400,
        detail="Please provide at least 2 images either via file uploads or as image_ids.",
    )


@router.post("/review")
def submit_multi_image_review(
    req: MultiImageReviewRequest,
    user_payload: Optional[Dict[str, Any]] = Depends(get_optional_user_payload),
    db: Session = Depends(get_db),
):
    """
    Submits a scientist curation or routing decision from the multi-image comparison view.
    Allowed decisions: ACCEPT, FLAG, REQUEST_REACQUISITION, MARK_DUPLICATE, MARK_NOT_DUPLICATE, ADD_NOTE
    """
    user_id = int(user_payload.get("sub")) if user_payload and user_payload.get("sub") else None

    img = db.query(Image).filter(Image.id == req.image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail=f"Image ID {req.image_id} not found.")

    valid_decisions = [
        "ACCEPT",
        "FLAG",
        "REQUEST_REACQUISITION",
        "MARK_DUPLICATE",
        "MARK_NOT_DUPLICATE",
        "ADD_NOTE",
        "KEEP",
        "REVIEW_LATER",
        "LOW_QUALITY",
    ]
    norm_decision = req.decision.upper()
    if norm_decision not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid review decision '{req.decision}'. Allowed: {valid_decisions}",
        )

    # Record ReviewItem
    rev = ReviewItem(
        image_id=req.image_id,
        reviewer_id=user_id,
        decision=norm_decision,
        comment=req.comment,
        algorithmic_recommendation="MULTI_IMAGE_TRIAGE",
        status="COMPLETED",
    )
    db.add(rev)

    # Update processing status
    if norm_decision in ["FLAG", "LOW_QUALITY", "REQUEST_REACQUISITION", "MARK_DUPLICATE"]:
        img.processing_status = "FLAGGED"
    elif norm_decision in ["ACCEPT", "KEEP", "MARK_NOT_DUPLICATE"]:
        img.processing_status = "VERIFIED"
    else:
        img.processing_status = "REVIEWED"

    db.commit()
    db.refresh(rev)

    # Audit log
    AuditService.log_action(
        db=db,
        action="REVIEW_DECISION",
        resource_type="review_items",
        user_id=user_id,
        resource_id=rev.id,
        parameters={
            "image_id": req.image_id,
            "peer_image_id": req.peer_image_id,
            "decision": norm_decision,
            "analysis_id": req.analysis_id,
            "comment": req.comment,
        },
    )

    # Provenance log
    ProvenanceService.record_event(
        db=db,
        image_id=req.image_id,
        event_type="REVIEW_DECISION",
        parameters={
            "review_id": rev.id,
            "decision": norm_decision,
            "peer_image_id": req.peer_image_id,
            "analysis_id": req.analysis_id,
            "comment": req.comment,
        },
    )

    review_audit_hash = hashlib.sha256(
        f"REVIEW::{rev.id}::{img.id}::{norm_decision}::{req.analysis_id or 'NONE'}".encode("utf-8")
    ).hexdigest()

    return {
        "status": "SUCCESS",
        "review_id": rev.id,
        "image_id": req.image_id,
        "decision": norm_decision,
        "processing_status": img.processing_status,
        "audit_hash": review_audit_hash,
        "message": f"Review action '{norm_decision}' successfully recorded for micrograph #{req.image_id}",
    }
