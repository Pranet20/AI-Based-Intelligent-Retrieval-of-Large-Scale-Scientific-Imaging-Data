"""Curation review queue and human review submission endpoints."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import RoleChecker, get_current_user_payload
from app.db.models import (
    DuplicateProfile,
    Embedding,
    Image,
    ImageMetadata,
    QualityProfile,
    ReviewItem,
    User,
)
from app.db.session import get_db
from app.ml.novelty_engine import NoveltyEngine
from app.services.audit import AuditService
from app.services.provenance import ProvenanceService

router = APIRouter(tags=["Curation & Reviews"])


class ReviewCreate(BaseModel):
    image_id: int
    decision: str  # KEEP, REVIEW_LATER, DUPLICATE, LOW_QUALITY, INTERESTING_NOVEL, INCORRECT_METADATA
    comment: Optional[str] = None


class ReviewQueueItem(BaseModel):
    image_id: int
    original_filename: str
    duplicate_status: str
    composite_quality_risk: float
    quality_label: str
    novelty_score: float
    novelty_percentile: float
    priority: float
    algorithmic_recommendation: str
    microscope: Optional[str]


@router.get("/review-queue", response_model=List[ReviewQueueItem])
def get_review_queue(limit: int = 50, db: Session = Depends(get_db)):
    """
    Returns prioritized curation queue sorted by diagnostic risk score:
    priority = 0.5 * composite_quality_risk + 0.3 * novelty_percentile/100 + 0.2 * (1.0 if DUPLICATE else 0)
    """
    images = db.query(Image).all()
    novelty_engine = NoveltyEngine()

    queue = []
    for img in images:
        # Check if already reviewed
        existing_rev = db.query(ReviewItem).filter(ReviewItem.image_id == img.id, ReviewItem.status == "COMPLETED").first()
        if existing_rev:
            continue

        qp = img.quality_profile
        dp = img.duplicate_profile
        meta = img.metadata_rel

        q_risk = qp.composite_quality_risk if qp else 0.0
        q_label = qp.quality_label if qp else "NOMINAL"
        dup_stat = dp.duplicate_status if dp else "NO_DECLARED_REDUNDANCY_DETECTED"

        # Novelty
        emb = db.query(Embedding).filter(Embedding.image_id == img.id, Embedding.embedding_type == "dinov2_base").first()
        nov_score = 0.0
        nov_pct = 50.0
        if emb:
            import numpy as np
            nov_res = novelty_engine.evaluate_novelty(np.array(emb.embedding_vector))
            nov_score = nov_res["novelty_score"]
            nov_pct = nov_res["novelty_percentile"]

        # Algorithmic recommendation
        rec = "KEEP"
        if dup_stat != "NO_DECLARED_REDUNDANCY_DETECTED":
            rec = "DUPLICATE"
        elif q_risk >= 0.60:
            rec = "LOW_QUALITY"
        elif nov_pct >= 90.0:
            rec = "INTERESTING_NOVEL"

        dup_weight = 1.0 if dup_stat != "NO_DECLARED_REDUNDANCY_DETECTED" else 0.0
        priority = 0.5 * q_risk + 0.3 * (nov_pct / 100.0) + 0.2 * dup_weight

        queue.append(ReviewQueueItem(
            image_id=img.id,
            original_filename=img.original_filename,
            duplicate_status=dup_stat,
            composite_quality_risk=float(q_risk),
            quality_label=q_label,
            novelty_score=float(nov_score),
            novelty_percentile=float(nov_pct),
            priority=float(priority),
            algorithmic_recommendation=rec,
            microscope=meta.microscope if meta else None,
        ))

    queue.sort(key=lambda x: x.priority, reverse=True)
    return queue[:limit]


@router.post("/reviews")
def submit_review(
    review_in: ReviewCreate,
    payload: Dict[str, Any] = Depends(RoleChecker(["CURATOR", "ADMIN"])),
    db: Session = Depends(get_db),
):
    valid_decisions = {"KEEP", "REVIEW_LATER", "DUPLICATE", "LOW_QUALITY", "INTERESTING_NOVEL", "INCORRECT_METADATA"}
    if review_in.decision.upper() not in valid_decisions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision '{review_in.decision}'. Allowed: {valid_decisions}"
        )

    user_id = int(payload.get("sub"))
    img = db.query(Image).filter(Image.id == review_in.image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    decision = review_in.decision.upper()

    # Determine algorithmic recommendation from image profiles
    qp = img.quality_profile
    dp = img.duplicate_profile
    algo_rec = "KEEP"
    if dp and dp.duplicate_status != "NO_DECLARED_REDUNDANCY_DETECTED":
        algo_rec = "DUPLICATE"
    elif qp and qp.composite_quality_risk >= 0.60:
        algo_rec = "LOW_QUALITY"

    rev = ReviewItem(
        image_id=review_in.image_id,
        reviewer_id=user_id,
        decision=decision,
        comment=review_in.comment,
        algorithmic_recommendation=algo_rec,
        status="COMPLETED",
        reviewed_at=datetime.now(timezone.utc),
    )
    db.add(rev)

    # Update image processing status
    if decision in ["LOW_QUALITY", "DUPLICATE"]:
        img.processing_status = "FLAGGED"
    elif decision == "KEEP":
        img.processing_status = "VERIFIED"
    else:
        img.processing_status = "REVIEWED"

    db.commit()
    db.refresh(rev)

    # Record provenance event
    ProvenanceService.record_event(
        db=db,
        image_id=img.id,
        event_type="REVIEW",
        parameters={
            "decision": decision,
            "reviewer_id": user_id,
            "algorithmic_recommendation": algo_rec,
            "comment": rev.comment,
        },
    )

    # Log to audit log
    AuditService.log_action(
        db=db,
        action="HUMAN_REVIEW_SUBMITTED",
        resource_type="review_items",
        user_id=user_id,
        resource_id=rev.id,
        parameters={"decision": rev.decision, "image_id": img.id, "algorithmic_recommendation": algo_rec},
    )

    return {
        "review_id": rev.id,
        "image_id": rev.image_id,
        "decision": rev.decision,
        "algorithmic_recommendation": rev.algorithmic_recommendation,
        "reviewed_at": rev.reviewed_at,
        "status": "COMPLETED",
    }


@router.get("/reviews")
def list_completed_reviews(limit: int = 50, db: Session = Depends(get_db)):
    revs = db.query(ReviewItem).order_by(ReviewItem.id.desc()).limit(limit).all()
    out = []
    for r in revs:
        u = db.query(User).filter(User.id == r.reviewer_id).first()
        img = db.query(Image).filter(Image.id == r.image_id).first()
        out.append({
            "id": r.id,
            "image_id": r.image_id,
            "filename": img.original_filename if img else None,
            "reviewer_username": u.username if u else "unknown",
            "decision": r.decision,
            "comment": r.comment,
            "reviewed_at": r.reviewed_at,
        })
    return out
