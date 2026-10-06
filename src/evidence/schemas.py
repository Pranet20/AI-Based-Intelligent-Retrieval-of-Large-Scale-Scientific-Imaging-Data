"""Scientific Evidence & Explanation Intelligence Layer Data Schemas for Phase 5.

Implements immutable, provenance-tracked, uncertainty-aware schemas for scientific
microscopy evidence aggregation, explanation generation, and scientist review payloads.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import datetime


class DecisionStatus(str, Enum):
    """Authoritative decision status for quality-risk triage."""
    ACCEPT = "ACCEPT"
    QUALITY_RISK = "QUALITY_RISK"
    UNCERTAIN_ABSTAIN = "UNCERTAIN_ABSTAIN"


class ArtifactCategory(str, Enum):
    """Controlled synthetic artifact and quality categories."""
    NORMAL = "NORMAL"
    BLUR = "BLUR"
    MOTION_BLUR = "MOTION_BLUR"
    NOISE = "NOISE"
    CONTRAST_REDUCTION = "CONTRAST_REDUCTION"
    OVEREXPOSURE = "OVEREXPOSURE"
    UNDEREXPOSURE = "UNDEREXPOSURE"
    CLIPPING = "CLIPPING"
    LOCAL_ILLUMINATION_ABNORMALITY = "LOCAL_ILLUMINATION_ABNORMALITY"
    ACQUISITION_PERTURBATION = "ACQUISITION_PERTURBATION"
    CHARGING_LIKE_SYNTHETIC_ARTIFACT = "CHARGING_LIKE_SYNTHETIC_ARTIFACT"
    UNKNOWN = "UNKNOWN"


class EvidenceRole(str, Enum):
    """Categorical role of retrieved comparable database images."""
    SAME_SPECIMEN_CROSS_ACQUISITION = "SAME_SPECIMEN_CROSS_ACQUISITION"
    SIMILAR_CLEAN_MICROGRAPH = "SIMILAR_CLEAN_MICROGRAPH"
    COMPARABLE_ARTIFACT_EXEMPLAR = "COMPARABLE_ARTIFACT_EXEMPLAR"
    SAME_ACQUISITION_PEER = "SAME_ACQUISITION_PEER"


@dataclass(frozen=True)
class AcquisitionContext:
    """Microscope instrument and acquisition parameters with strict null preservation.
    
    Adheres to Absolute Rule 24/25: Missing metadata must strictly remain None/'UNKNOWN'.
    No silent substitution or interpolation is permitted.
    """
    instrument: Optional[str] = None
    detector: Optional[str] = None
    accelerating_voltage_kv: Optional[float] = None
    magnification: Optional[float] = None
    working_distance_mm: Optional[float] = None
    specimen_id: Optional[str] = None
    acquisition_id: Optional[str] = None
    data_source: str = "UNKNOWN"
    metadata_provenance_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "instrument": self.instrument if self.instrument is not None else "UNKNOWN",
            "detector": self.detector if self.detector is not None else "UNKNOWN",
            "accelerating_voltage_kv": self.accelerating_voltage_kv,
            "magnification": self.magnification,
            "working_distance_mm": self.working_distance_mm,
            "specimen_id": self.specimen_id if self.specimen_id is not None else "UNKNOWN",
            "acquisition_id": self.acquisition_id if self.acquisition_id is not None else "UNKNOWN",
            "data_source": self.data_source,
            "metadata_provenance_hash": self.metadata_provenance_hash,
        }


@dataclass(frozen=True)
class QualityRiskSignal:
    """Individual image-derived quality indicator signal."""
    indicator_name: str
    measured_value: float
    threshold_applied: float
    is_risk_flagged: bool
    evaluation_criteria: str
    method_provenance: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "indicator_name": self.indicator_name,
            "measured_value": round(self.measured_value, 5),
            "threshold_applied": round(self.threshold_applied, 5),
            "is_risk_flagged": self.is_risk_flagged,
            "evaluation_criteria": self.evaluation_criteria,
            "method_provenance": self.method_provenance,
        }


@dataclass(frozen=True)
class BoundingBox:
    """Spatial bounding coordinates in [y_min, x_min, y_max, x_max]."""
    y_min: int
    x_min: int
    y_max: int
    x_max: int
    area_pixels: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "y_min": self.y_min,
            "x_min": self.x_min,
            "y_max": self.y_max,
            "x_max": self.x_max,
            "area_pixels": self.area_pixels,
        }


@dataclass(frozen=True)
class SuspiciousRegion:
    """Spatial localization metadata strictly bounded as a model-derived suspicious region.
    
    Adheres to Absolute Rule 13: Never designated as a 'confirmed physical defect'.
    """
    region_type: str = "model-derived suspicious region"
    saliency_threshold: float = 0.50
    area_fraction: float = 0.0
    bounding_boxes: List[BoundingBox] = field(default_factory=list)
    centroid_normalized: Tuple[float, float] = (0.5, 0.5)
    mean_saliency_in_mask: float = 0.0
    mask_storage_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "region_type": self.region_type,
            "saliency_threshold": round(self.saliency_threshold, 4),
            "area_fraction": round(self.area_fraction, 4),
            "bounding_boxes": [b.to_dict() for b in self.bounding_boxes],
            "centroid_normalized": (round(self.centroid_normalized[0], 4), round(self.centroid_normalized[1], 4)),
            "mean_saliency_in_mask": round(self.mean_saliency_in_mask, 4),
            "mask_storage_path": self.mask_storage_path,
        }


@dataclass(frozen=True)
class ComparableEvidenceImage:
    """Retrieved reference micrograph providing grounded visual comparison."""
    image_id: str
    role: EvidenceRole
    similarity_score: float
    specimen_id: Optional[str] = None
    acquisition_id: Optional[str] = None
    instrument: Optional[str] = None
    detector: Optional[str] = None
    accelerating_voltage_kv: Optional[float] = None
    file_path: Optional[str] = None
    provenance_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_id": self.image_id,
            "role": self.role.value,
            "similarity_score": round(self.similarity_score, 4),
            "specimen_id": self.specimen_id if self.specimen_id is not None else "UNKNOWN",
            "acquisition_id": self.acquisition_id if self.acquisition_id is not None else "UNKNOWN",
            "instrument": self.instrument if self.instrument is not None else "UNKNOWN",
            "detector": self.detector if self.detector is not None else "UNKNOWN",
            "accelerating_voltage_kv": self.accelerating_voltage_kv,
            "file_path": self.file_path,
            "provenance_hash": self.provenance_hash,
        }


@dataclass(frozen=True)
class SuggestedReviewAction:
    """Actionable, deterministically mapped recommendation for human reviewer.
    
    Adheres to Absolute Rules 15-18: Free-form generation and causal claims prohibited.
    """
    action_code: str
    recommendation_summary: str
    operational_parameter_targets: List[str]
    scientific_rationale: str
    requires_operator_intervention: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_code": self.action_code,
            "recommendation_summary": self.recommendation_summary,
            "operational_parameter_targets": self.operational_parameter_targets,
            "scientific_rationale": self.scientific_rationale,
            "requires_operator_intervention": self.requires_operator_intervention,
        }


@dataclass(frozen=True)
class StructuredEvidenceRecord:
    """Structured, end-to-end provenance-preserving scientific evidence record."""
    query_image_id: str
    decision_status: DecisionStatus
    primary_artifact_category: ArtifactCategory
    classification_confidence: float
    normalized_entropy: float
    prediction_margin: float
    abstention_triggered: bool
    abstention_reason: Optional[str]
    quality_signals: List[QualityRiskSignal]
    suspicious_region: Optional[SuspiciousRegion]
    acquisition_context: AcquisitionContext
    comparable_evidence: List[ComparableEvidenceImage]
    suggested_action: SuggestedReviewAction
    timestamp_utc: str = field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    pipeline_version: str = "sci-intel-phase5-v1.0"
    audit_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query_image_id": self.query_image_id,
            "decision_status": self.decision_status.value,
            "primary_artifact_category": self.primary_artifact_category.value,
            "classification_confidence": round(self.classification_confidence, 4),
            "normalized_entropy": round(self.normalized_entropy, 4),
            "prediction_margin": round(self.prediction_margin, 4),
            "abstention_triggered": self.abstention_triggered,
            "abstention_reason": self.abstention_reason,
            "quality_signals": [s.to_dict() for s in self.quality_signals],
            "suspicious_region": self.suspicious_region.to_dict() if self.suspicious_region else None,
            "acquisition_context": self.acquisition_context.to_dict(),
            "comparable_evidence": [e.to_dict() for e in self.comparable_evidence],
            "suggested_action": self.suggested_action.to_dict(),
            "timestamp_utc": self.timestamp_utc,
            "pipeline_version": self.pipeline_version,
            "audit_hash": self.audit_hash,
        }
