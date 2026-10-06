"""Deterministic Scientific Explanation & Review Action Generator for Phase 5.

Produces structured, evidence-grounded review recommendations without free-form LLM
hallucinations or unsupported causal claims.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from src.evidence.schemas import (
    AcquisitionContext,
    ArtifactCategory,
    DecisionStatus,
    QualityRiskSignal,
    SuggestedReviewAction,
    SuspiciousRegion,
)


class ExplanationGenerator:
    """Generates traceable, deterministic scientific recommendations and review actions."""

    # Deterministic scientific action rules mapped strictly to verified operational microscopy parameters
    ACTION_CATALOG: Dict[ArtifactCategory, Dict[str, Any]] = {
        ArtifactCategory.OVEREXPOSURE: {
            "action_code": "ACT_DET_GAIN_REDUCE",
            "summary": "Review detector gain and beam current exposure settings.",
            "targets": ["detector_gain", "beam_current", "dwell_time"],
            "rationale": "High pixel saturation ratio or elevated intensity ceiling suggests potential dynamic range overflow.",
            "intervention": True,
        },
        ArtifactCategory.UNDEREXPOSURE: {
            "action_code": "ACT_DWELL_TIME_INCREASE",
            "summary": "Increase pixel dwell time or verify objective aperture alignment.",
            "targets": ["dwell_time", "aperture_alignment", "beam_current"],
            "rationale": "High proportion of pixels in noise floor indicates photon/electron starvation.",
            "intervention": True,
        },
        ArtifactCategory.BLUR: {
            "action_code": "ACT_FOCUS_STIGMATION_ALIGN",
            "summary": "Perform objective focus calibration and beam stigmation alignment.",
            "targets": ["objective_lens_current", "stigmators_x_y", "working_distance"],
            "rationale": "Laplacian second-derivative variance below threshold indicates high-frequency attenuation.",
            "intervention": True,
        },
        ArtifactCategory.MOTION_BLUR: {
            "action_code": "ACT_STAGE_VIBRATION_CHECK",
            "summary": "Inspect stage vibration isolation dampening and line scan speed.",
            "targets": ["stage_isolation", "line_scan_speed", "external_acoustic_shielding"],
            "rationale": "Directional gradient degradation indicates relative motion during raster acquisition.",
            "intervention": True,
        },
        ArtifactCategory.NOISE: {
            "action_code": "ACT_FRAME_AVERAGING_INCREASE",
            "summary": "Increase line/frame averaging count or reduce scan frequency.",
            "targets": ["frame_averaging", "scan_speed", "detector_bandwidth"],
            "rationale": "High-frequency spatial noise degrades signal-to-noise ratio across homogeneous phases.",
            "intervention": True,
        },
        ArtifactCategory.CONTRAST_REDUCTION: {
            "action_code": "ACT_CONTRAST_BIAS_OPTIMIZE",
            "summary": "Optimize photomultiplier / detector contrast and brightness bias.",
            "targets": ["contrast_bias", "pmt_voltage", "collector_bias"],
            "rationale": "Low RMS contrast compresses microstructural phase differentiation.",
            "intervention": True,
        },
        ArtifactCategory.CLIPPING: {
            "action_code": "ACT_ADC_RANGE_RESCALE",
            "summary": "Adjust analog-to-digital converter dynamic range scaling.",
            "targets": ["adc_gain", "preamplifier_offset"],
            "rationale": "Histogram truncation observed at intensity bounds without gradual rolloff.",
            "intervention": True,
        },
        ArtifactCategory.LOCAL_ILLUMINATION_ABNORMALITY: {
            "action_code": "ACT_DETECTOR_GEOMETRY_INSPECT",
            "summary": "Inspect specimen surface tilt and secondary electron detector geometry.",
            "targets": ["specimen_tilt", "working_distance", "detector_grid_bias"],
            "rationale": "Asymmetric spatial illumination gradients identified by localization saliency.",
            "intervention": True,
        },
        ArtifactCategory.ACQUISITION_PERTURBATION: {
            "action_code": "ACT_SCAN_COIL_SYNC_VERIFY",
            "summary": "Verify scan raster synchronization and scan coil driver power stability.",
            "targets": ["scan_generator_sync", "power_supply_ripple", "mains_interference_filter"],
            "rationale": "Periodic or stepped raster shifts observed across scan lines.",
            "intervention": True,
        },
        ArtifactCategory.CHARGING_LIKE_SYNTHETIC_ARTIFACT: {
            "action_code": "ACT_CHARGE_COMPENSATION_VERIFY",
            "summary": "Verify conductive specimen grounding, or engage low-kV / charge-compensation mode.",
            "targets": ["specimen_grounding", "accelerating_voltage_kv", "variable_pressure_nitrogen"],
            "rationale": "Localized intense directional brightness streaks and deflection halos consistent with electrostatic accumulation models.",
            "intervention": True,
        },
        ArtifactCategory.NORMAL: {
            "action_code": "ACT_NO_ACTION_REQUIRED",
            "summary": "No corrective action indicated; specimen conforms to baseline standards.",
            "targets": [],
            "rationale": "All image-derived quality indicators within acceptable operating limits.",
            "intervention": False,
        },
    }

    def generate_review_action(
        self,
        decision_status: DecisionStatus,
        predicted_category: ArtifactCategory,
        quality_signals: List[QualityRiskSignal],
        suspicious_region: Optional[SuspiciousRegion],
        acquisition_context: AcquisitionContext,
        abstention_reason: Optional[str] = None,
    ) -> SuggestedReviewAction:
        """Generate structured review action adhering strictly to scientific governance."""
        # Case 1: System abstains / uncertain
        if decision_status == DecisionStatus.UNCERTAIN_ABSTAIN:
            return SuggestedReviewAction(
                action_code="ACT_MANUAL_SCIENTIST_REVIEW",
                recommendation_summary="Ambiguous quality signals or low classification confidence; defer to human microscopy specialist.",
                operational_parameter_targets=["visual_manual_inspection", "acquisition_parameter_log"],
                scientific_rationale=abstention_reason or "Empirical uncertainty exceeds automated threshold.",
                requires_operator_intervention=True,
            )

        # Case 2: Standard mapped category
        cat_info = self.ACTION_CATALOG.get(
            predicted_category,
            {
                "action_code": "ACT_GENERIC_INSPECTION",
                "summary": "Inspect acquisition parameters and compare with verified reference images.",
                "targets": ["microscope_operator_log"],
                "rationale": "Uncataloged quality risk signal observed.",
                "intervention": True,
            },
        )

        # Append acquisition context notes if relevant
        rationale = cat_info["rationale"]
        if acquisition_context.accelerating_voltage_kv is not None:
            rationale += f" (Current accelerating voltage: {acquisition_context.accelerating_voltage_kv:.1f} kV)"
        if acquisition_context.detector is not None and acquisition_context.detector != "UNKNOWN":
            rationale += f" (Active detector: {acquisition_context.detector})"

        return SuggestedReviewAction(
            action_code=cat_info["action_code"],
            recommendation_summary=cat_info["summary"],
            operational_parameter_targets=cat_info["targets"],
            scientific_rationale=rationale,
            requires_operator_intervention=cat_info["intervention"],
        )
