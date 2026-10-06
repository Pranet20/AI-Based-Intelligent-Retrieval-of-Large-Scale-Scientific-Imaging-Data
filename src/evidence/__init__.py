"""Scientific Evidence & Explanation Intelligence Layer (Phase 5)."""

from src.evidence.evidence_aggregator import EvidenceAggregator
from src.evidence.explanation_generator import ExplanationGenerator
from src.evidence.localization_engine import LocalizationEngine
from src.evidence.quality_risk_engine import QualityRiskEngine
from src.evidence.retrieval_evidence_engine import RetrievalEvidenceEngine
from src.evidence.schemas import (
    AcquisitionContext,
    ArtifactCategory,
    BoundingBox,
    ComparableEvidenceImage,
    DecisionStatus,
    EvidenceRole,
    QualityRiskSignal,
    StructuredEvidenceRecord,
    SuggestedReviewAction,
    SuspiciousRegion,
)

__all__ = [
    "AcquisitionContext",
    "ArtifactCategory",
    "BoundingBox",
    "ComparableEvidenceImage",
    "DecisionStatus",
    "EvidenceAggregator",
    "EvidenceRole",
    "ExplanationGenerator",
    "LocalizationEngine",
    "QualityRiskEngine",
    "QualityRiskSignal",
    "RetrievalEvidenceEngine",
    "StructuredEvidenceRecord",
    "SuggestedReviewAction",
    "SuspiciousRegion",
]
