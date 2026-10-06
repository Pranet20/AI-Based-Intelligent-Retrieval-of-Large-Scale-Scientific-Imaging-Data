"""Quality & Risk Screening Engine for Phase 5.

Combines computational image-derived quality indicators with foundation model representations
to compute classification probabilities, entropy-based uncertainty, prediction margins,
and deterministic abstention gates.

Scientific Disclaimer:
Image-derived quality indicators represent computational heuristics on pixel intensity
distributions (e.g., focus proxies, dynamic range, entropy, saturation ratios) and do NOT
directly measure the internal physical or hardware state of the microscope.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np

from src.evidence.schemas import (
    ArtifactCategory,
    DecisionStatus,
    QualityRiskSignal,
)
from src.evidence.threshold_config import DEFAULT_THRESHOLD_CONFIG, Phase5ThresholdConfig
from src.quality.metrics import QualityMetricsResult, calculate_quality_metrics


CATEGORIES: List[ArtifactCategory] = [
    ArtifactCategory.NORMAL,
    ArtifactCategory.BLUR,
    ArtifactCategory.MOTION_BLUR,
    ArtifactCategory.NOISE,
    ArtifactCategory.CONTRAST_REDUCTION,
    ArtifactCategory.OVEREXPOSURE,
    ArtifactCategory.UNDEREXPOSURE,
    ArtifactCategory.CLIPPING,
    ArtifactCategory.LOCAL_ILLUMINATION_ABNORMALITY,
    ArtifactCategory.ACQUISITION_PERTURBATION,
    ArtifactCategory.CHARGING_LIKE_SYNTHETIC_ARTIFACT,
]


class QualityRiskEngine:
    """Computes transparent image-derived quality indicators, classification probabilities, and uncertainty."""

    def __init__(
        self,
        config: Optional[Phase5ThresholdConfig] = None,
        confidence_abstain_threshold: Optional[float] = None,
        entropy_abstain_threshold: Optional[float] = None,
        margin_abstain_threshold: Optional[float] = None,
    ) -> None:
        self.config = config or DEFAULT_THRESHOLD_CONFIG
        self.conf_threshold = (
            confidence_abstain_threshold
            if confidence_abstain_threshold is not None
            else self.config.confidence_abstain_threshold
        )
        self.entropy_threshold = (
            entropy_abstain_threshold
            if entropy_abstain_threshold is not None
            else self.config.entropy_abstain_threshold
        )
        self.margin_threshold = (
            margin_abstain_threshold
            if margin_abstain_threshold is not None
            else self.config.margin_abstain_threshold
        )

    def evaluate_quality_signals(self, image: np.ndarray) -> List[QualityRiskSignal]:
        """Compute traceable handcrafted image-derived quality indicators on image array."""
        res: QualityMetricsResult = calculate_quality_metrics(image)
        signals: List[QualityRiskSignal] = []

        # 1. Focus / Sharpness indicator
        signals.append(
            QualityRiskSignal(
                indicator_name="laplacian_variance",
                measured_value=float(res.laplacian_variance),
                threshold_applied=50.0,
                is_risk_flagged=bool(res.laplacian_variance < 50.0),
                evaluation_criteria="Sharpness threshold: values < 50 indicate potential focus attenuation or motion blur",
                method_provenance="Discrete 3x3 Laplacian second-derivative variance",
            )
        )

        # 2. Saturation / Overexposure indicator
        signals.append(
            QualityRiskSignal(
                indicator_name="saturation_ratio",
                measured_value=float(res.saturation_ratio),
                threshold_applied=0.05,
                is_risk_flagged=bool(res.saturation_ratio > 0.05),
                evaluation_criteria="Pixel saturation threshold: > 5% clipped at maximum intensity indicates overexposure",
                method_provenance="Fraction of pixels at ceiling dynamic range (255/65535)",
            )
        )

        # 3. Dark Ratio / Underexposure indicator
        signals.append(
            QualityRiskSignal(
                indicator_name="dark_pixel_ratio",
                measured_value=float(res.dark_pixel_ratio),
                threshold_applied=0.10,
                is_risk_flagged=bool(res.dark_pixel_ratio > 0.10),
                evaluation_criteria="Low-signal threshold: > 10% in noise floor indicates potential underexposure",
                method_provenance="Fraction of pixels below minimum threshold ceiling (<=5)",
            )
        )

        # 4. Dynamic Range Span indicator
        signals.append(
            QualityRiskSignal(
                indicator_name="dynamic_range",
                measured_value=float(res.dynamic_range),
                threshold_applied=50.0,
                is_risk_flagged=bool(res.dynamic_range < 50.0),
                evaluation_criteria="Dynamic range span: values < 50 indicate severe dynamic range compression or clipping",
                method_provenance="max_intensity - min_intensity",
            )
        )

        # 5. Shannon Entropy indicator
        signals.append(
            QualityRiskSignal(
                indicator_name="entropy",
                measured_value=float(res.entropy),
                threshold_applied=4.0,
                is_risk_flagged=bool(res.entropy < 4.0),
                evaluation_criteria="Information density: entropy < 4.0 bits indicates information loss or severe artifacting",
                method_provenance="Discrete empirical probability distribution entropy",
            )
        )

        # 6. RMS Contrast indicator
        signals.append(
            QualityRiskSignal(
                indicator_name="contrast",
                measured_value=float(res.contrast),
                threshold_applied=15.0,
                is_risk_flagged=bool(res.contrast < 15.0),
                evaluation_criteria="Standard deviation of intensity: values < 15.0 indicate contrast reduction",
                method_provenance="Root-mean-square intensity dispersion",
            )
        )

        return signals

    # Alias for backward compatibility
    def evaluate_physical_signals(self, image: np.ndarray) -> List[QualityRiskSignal]:
        return self.evaluate_quality_signals(image)

    def compute_uncertainty_metrics(
        self,
        probabilities: np.ndarray,
    ) -> Tuple[float, float, float]:
        """Compute maximum confidence, normalized entropy, and prediction margin.
        
        Args:
            probabilities: 1D probability array summing to 1.0.
            
        Returns:
            (confidence, normalized_entropy, prediction_margin)
        """
        probs = np.clip(probabilities, 1e-12, 1.0)
        probs = probs / np.sum(probs)

        # 1. Top confidence
        confidence = float(np.max(probs))

        # 2. Normalized Shannon Entropy H_norm in [0, 1]
        c = len(probs)
        entropy = -float(np.sum(probs * np.log(probs)))
        max_entropy = np.log(c) if c > 1 else 1.0
        norm_entropy = float(entropy / max_entropy)

        # 3. Margin between top-1 and top-2
        sorted_probs = np.sort(probs)[::-1]
        margin = float(sorted_probs[0] - (sorted_probs[1] if c > 1 else 0.0))

        return confidence, norm_entropy, margin

    def screen_quality_risk(
        self,
        quality_signals: List[QualityRiskSignal],
        probabilities: np.ndarray,
    ) -> Tuple[DecisionStatus, ArtifactCategory, float, float, float, bool, Optional[str]]:
        """Synthesize image-derived quality signals and acquisition metadata into decision and uncertainty.
        
        Returns:
            (decision_status, predicted_category, confidence, normalized_entropy, margin, abstention_triggered, abstention_reason)
        """
        confidence, norm_entropy, margin = self.compute_uncertainty_metrics(probabilities)
        pred_idx = int(np.argmax(probabilities))
        pred_cat = CATEGORIES[pred_idx] if pred_idx < len(CATEGORIES) else ArtifactCategory.UNKNOWN

        # Abstention Gates (Rule 22 & 23: When evidence is insufficient, return UNCERTAIN_ABSTAIN)
        abstention_triggered = False
        abstention_reason = None

        if confidence < self.conf_threshold:
            abstention_triggered = True
            abstention_reason = f"Classification confidence ({confidence:.4f}) below abstention threshold ({self.conf_threshold:.2f})"
        elif norm_entropy > self.entropy_threshold:
            abstention_triggered = True
            abstention_reason = f"Normalized prediction entropy ({norm_entropy:.4f}) exceeds uncertainty ceiling ({self.entropy_threshold:.2f})"
        elif margin < self.margin_threshold:
            abstention_triggered = True
            abstention_reason = f"Top-2 prediction margin ({margin:.4f}) below discriminative threshold ({self.margin_threshold:.2f})"

        if abstention_triggered:
            status = DecisionStatus.UNCERTAIN_ABSTAIN
        elif pred_cat == ArtifactCategory.NORMAL:
            # Cross-check image-derived quality indicators: if multiple indicators flag risk, defer to review
            flagged_count = sum(1 for s in quality_signals if s.is_risk_flagged)
            if flagged_count >= 2:
                status = DecisionStatus.UNCERTAIN_ABSTAIN
                abstention_triggered = True
                abstention_reason = f"Representation predicts NORMAL but {flagged_count} image-derived quality indicators flag risk"
            else:
                status = DecisionStatus.ACCEPT
        else:
            status = DecisionStatus.QUALITY_RISK

        return (
            status,
            pred_cat,
            confidence,
            norm_entropy,
            margin,
            abstention_triggered,
            abstention_reason,
        )
