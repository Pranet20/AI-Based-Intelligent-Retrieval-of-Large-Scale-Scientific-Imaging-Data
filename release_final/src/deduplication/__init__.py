"""Exact and near-duplicate image detection."""

from src.deduplication.exact import ExactDuplicateDetector, DuplicateAuditStats
from src.deduplication.near_duplicate import NearDuplicateDetector, NearDuplicateGroup

__all__ = [
    "ExactDuplicateDetector",
    "DuplicateAuditStats",
    "NearDuplicateDetector",
    "NearDuplicateGroup",
]
