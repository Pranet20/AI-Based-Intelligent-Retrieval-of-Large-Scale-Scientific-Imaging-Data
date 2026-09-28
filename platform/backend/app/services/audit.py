"""Audit Logging Service."""

from typing import Any, Dict, Optional
from sqlalchemy.orm import Session

from app.db.models import AuditLog


class AuditService:
    """Records security and operational audit logs."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        resource_type: str,
        user_id: Optional[int] = None,
        resource_id: Optional[int] = None,
        model_version: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        result_status: str = "SUCCESS",
    ) -> AuditLog:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            model_version=model_version,
            parameters=parameters or {},
            result_status=result_status,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
