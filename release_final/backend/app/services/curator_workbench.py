"""Research Curator Workbench & Active Learning Triage Service.

Features:
- Composite priority queue ranking (quality risk, novelty, uncertainty, duplicate ambiguity)
- Explicit auditable curation actions:
  (KEEP, REVIEW_LATER, DUPLICATE, LOW_QUALITY, INTERESTING_NOVEL, INCORRECT_METADATA)
- Complete audit logging and provenance recording
- Strict guard against unapproved automatic model retraining (human approval mandatory)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session

from app.db.models import AuditLog, DuplicateProfile, Image, QualityProfile, ReviewItem
from app.services.audit import AuditService
from app.services.provenance import ProvenanceService


VALID_CURATION_DECISIONS = {
    "KEEP",
    "REVIEW_LATER",
    "DUPLICATE",
    "LOW_QUALITY",
    "INTERESTING_NOVEL",
    "INCORRECT_METADATA",
}


class CuratorWorkbenchService:
    """Manages active curation triage queue and auditable review submissions."""

    @classmethod
    def calculate_priority_score(
        cls,
        quality_risk: float = 0.0,
        novelty_score: float = 0.0,
        uncertainty_score: float = 0.0,
        has_duplicate_flag: bool = False,
        metadata_inconsistency: float = 0.0,
    ) -> float:
        """Active curation priority score: higher values require earlier human review."""
        score = (
            0.35 * min(1.0, quality_risk)
            + 0.25 * min(1.0, novelty_score)
            + 0.20 * min(1.0, uncertainty_score)
            + (0.10 if has_duplicate_flag else 0.0)
            + 0.10 * min(1.0, metadata_inconsistency)
        )
        return round(float(score), 4)

    @classmethod
    def get_triage_queue(
        cls,
        db: Session,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Returns pending review queue sorted by composite urgency."""
        items = (
            db.query(ReviewItem)
            .filter(ReviewItem.status == "PENDING")
            .order_by(ReviewItem.priority.desc(), ReviewItem.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        queue = []
        for item in items:
            img: Image = item.image
            qp = img.quality_profile if img else None
            dp = img.duplicate_profile if img else None

            queue.append({
                "review_id": item.id,
                "image_id": item.image_id,
                "original_filename": img.original_filename if img else "Unknown",
                "priority_score": item.priority,
                "algorithmic_recommendation": item.algorithmic_recommendation,
                "quality_label": qp.quality_label if qp else "UNASSESSED",
                "quality_risk": qp.composite_quality_risk if qp else 0.0,
                "duplicate_status": dp.duplicate_status if dp else "UNCHECKED",
                "created_at": item.created_at.isoformat() if item.created_at else None,
            })
        return queue

    @classmethod
    def submit_decision(
        cls,
        db: Session,
        user_id: int,
        review_id: int,
        decision: str,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Submits human curator decision with synchronous audit and provenance logs."""
        decision_clean = decision.strip().upper()
        if decision_clean not in VALID_CURATION_DECISIONS:
            raise ValueError(
                f"Invalid curation decision '{decision}'. Allowed: {sorted(list(VALID_CURATION_DECISIONS))}"
            )

        review_item = db.query(ReviewItem).filter(ReviewItem.id == review_id).first()
        if not review_item:
            raise ValueError(f"ReviewItem with ID {review_id} not found.")

        now = datetime.now(timezone.utc)
        review_item.decision = decision_clean
        review_item.comment = comment
        review_item.reviewer_id = user_id
        review_item.status = "COMPLETED"
        review_item.reviewed_at = now

        # Record synchronous audit log
        AuditService.log_action(
            db=db,
            action="CURATION_DECISION",
            resource_type="review_items",
            resource_id=review_id,
            user_id=user_id,
            parameters={
                "decision": decision_clean,
                "comment": comment,
                "image_id": review_item.image_id,
                "automatic_retraining": "PROHIBITED_WITHOUT_APPROVAL",
            },
        )

        # Record provenance event
        ProvenanceService.record_event(
            db=db,
            image_id=review_item.image_id,
            event_type="HUMAN_CURATION",
            parameters={"decision": decision_clean, "reviewer_id": user_id},
            software_version="1.0.0",
        )

        db.commit()
        db.refresh(review_item)

        return {
            "review_id": review_item.id,
            "image_id": review_item.image_id,
            "decision": review_item.decision,
            "status": review_item.status,
            "reviewed_at": review_item.reviewed_at.isoformat(),
            "audit_status": "AUDITED_AND_COMMITTED",
        }
