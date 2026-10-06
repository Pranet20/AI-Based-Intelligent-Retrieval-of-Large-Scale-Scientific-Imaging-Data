"""Evidence Aggregation & Scientific Review Orchestrator for Phase 5.

Combines quality-risk screening, spatial localization, acquisition context,
comparable image retrieval, and deterministic review actions into an immutable,
traceable, cryptographically hashed evidence chain.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional
import numpy as np

from src.evidence.explanation_generator import ExplanationGenerator
from src.evidence.localization_engine import LocalizationEngine
from src.evidence.quality_risk_engine import QualityRiskEngine
from src.evidence.retrieval_evidence_engine import RetrievalEvidenceEngine
from src.evidence.schemas import (
    AcquisitionContext,
    ArtifactCategory,
    DecisionStatus,
    StructuredEvidenceRecord,
)


class EvidenceAggregator:
    """Orchestrates end-to-end evidence aggregation for scientific microscopy curation."""

    def __init__(
        self,
        quality_engine: Optional[QualityRiskEngine] = None,
        localization_engine: Optional[LocalizationEngine] = None,
        retrieval_engine: Optional[RetrievalEvidenceEngine] = None,
        explanation_generator: Optional[ExplanationGenerator] = None,
    ) -> None:
        self.quality_engine = quality_engine or QualityRiskEngine()
        self.localization_engine = localization_engine or LocalizationEngine()
        self.retrieval_engine = retrieval_engine
        self.explanation_generator = explanation_generator or ExplanationGenerator()

    def process_query_micrograph(
        self,
        query_image_id: str,
        image: np.ndarray,
        feature_vector: Optional[np.ndarray] = None,
        classification_probabilities: Optional[np.ndarray] = None,
        metadata_dict: Optional[Dict[str, Any]] = None,
        precomputed_saliency: Optional[np.ndarray] = None,
    ) -> StructuredEvidenceRecord:
        """Process a query micrograph through the complete Phase 5 evidence pipeline."""
        # 1. Parse acquisition context (Rules 24 & 25: Never substitute missing metadata silently)
        meta = metadata_dict or {}
        acq_context = AcquisitionContext(
            instrument=str(meta["instrument"]) if meta.get("instrument") else None,
            detector=str(meta["detector"]) if meta.get("detector") else None,
            accelerating_voltage_kv=float(meta["accelerating_voltage_kv"]) if meta.get("accelerating_voltage_kv") is not None else None,
            magnification=float(meta["magnification"]) if meta.get("magnification") is not None else None,
            working_distance_mm=float(meta["working_distance_mm"]) if meta.get("working_distance_mm") is not None else None,
            specimen_id=str(meta["specimen_id"]) if meta.get("specimen_id") else None,
            acquisition_id=str(meta["acquisition_id"]) if meta.get("acquisition_id") else None,
            data_source=str(meta.get("data_source", "UNKNOWN")),
            metadata_provenance_hash=meta.get("sha256") or meta.get("metadata_provenance_hash"),
        )

        # 2. Image-derived quality signals and acquisition metadata
        quality_signals = self.quality_engine.evaluate_quality_signals(image)

        # 3. Probabilities and Uncertainty
        if classification_probabilities is None:
            # Fallback uniform distribution if not provided
            c = 11
            probs = np.ones(c, dtype=np.float32) / c
        else:
            probs = np.array(classification_probabilities, dtype=np.float32)

        (
            decision_status,
            pred_cat,
            confidence,
            norm_entropy,
            margin,
            abstain_flag,
            abstain_reason,
        ) = self.quality_engine.screen_quality_risk(quality_signals, probs)

        # 4. Localization: Model-derived suspicious region
        suspicious_region = self.localization_engine.extract_suspicious_region(
            image=image,
            precomputed_saliency=precomputed_saliency,
            mask_storage_path=meta.get("mask_path"),
        )

        # 5. Comparable Image Retrieval
        comparable_items = []
        if self.retrieval_engine is not None and feature_vector is not None:
            comparable_items = self.retrieval_engine.retrieve_comparable_evidence(
                query_feature=feature_vector,
                query_specimen_id=acq_context.specimen_id,
                query_acquisition_id=acq_context.acquisition_id,
                query_instrument=acq_context.instrument,
                predicted_artifact=pred_cat,
            )

        # 6. Structured review action
        review_action = self.explanation_generator.generate_review_action(
            decision_status=decision_status,
            predicted_category=pred_cat,
            quality_signals=quality_signals,
            suspicious_region=suspicious_region,
            acquisition_context=acq_context,
            abstention_reason=abstain_reason,
        )

        # 7. Assembled Record & Cryptographic Audit Hash
        raw_record_dict = {
            "query_image_id": query_image_id,
            "decision_status": decision_status.value,
            "primary_artifact_category": pred_cat.value,
            "confidence": round(confidence, 4),
            "normalized_entropy": round(norm_entropy, 4),
            "abstention_triggered": abstain_flag,
            "acquisition_context": acq_context.to_dict(),
            "suggested_action": review_action.to_dict(),
        }
        raw_json_str = json.dumps(raw_record_dict, sort_keys=True)
        audit_hash = hashlib.sha256(raw_json_str.encode("utf-8")).hexdigest()

        return StructuredEvidenceRecord(
            query_image_id=query_image_id,
            decision_status=decision_status,
            primary_artifact_category=pred_cat,
            classification_confidence=confidence,
            normalized_entropy=norm_entropy,
            prediction_margin=margin,
            abstention_triggered=abstain_flag,
            abstention_reason=abstain_reason,
            quality_signals=quality_signals,
            suspicious_region=suspicious_region,
            acquisition_context=acq_context,
            comparable_evidence=comparable_items,
            suggested_action=review_action,
            audit_hash=audit_hash,
        )
