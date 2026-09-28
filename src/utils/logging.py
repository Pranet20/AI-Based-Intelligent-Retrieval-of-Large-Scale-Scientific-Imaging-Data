"""Structured logging and audit error tracking for Phase 1 scientific platform."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class JSONFormatter(logging.Formatter):
    """Custom logging formatter outputting structured JSON."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "dataset_id"):
            log_obj["dataset_id"] = record.dataset_id
        if hasattr(record, "file_path"):
            log_obj["file_path"] = str(record.file_path)
        if hasattr(record, "operation"):
            log_obj["operation"] = record.operation
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


class AuditErrorCollector:
    """Collects and reports errors encountered during dataset audits without silent failure."""

    def __init__(self) -> None:
        self.errors: List[Dict[str, Any]] = []

    def record_error(
        self,
        dataset_id: str,
        file_path: str,
        operation: str,
        exception: Exception | str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataset_id": dataset_id,
            "file": str(file_path),
            "operation": operation,
            "exception": str(exception),
            "context": context or {},
        }
        self.errors.append(entry)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def error_count(self) -> int:
        return len(self.errors)

    def to_dict(self) -> List[Dict[str, Any]]:
        return list(self.errors)

    def save_report(self, output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"total_errors": len(self.errors), "errors": self.errors}, f, indent=2)


def get_logger(
    name: str = "scidata",
    log_file: Optional[str | Path] = None,
    level: int = logging.INFO,
) -> logging.Logger:
    """Configure and return a structured logger."""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_format = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)

    return logger
