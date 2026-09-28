"""Production Image-Derived Quality-Risk Engine."""

from pathlib import Path
from typing import Dict, Union
from src.integrity.quality_indicators import (
    compute_all_quality_metrics,
    QualityRiskEvaluator,
)


class QualityEngine:
    """Computes physically grounded image-derived quality-risk indicators."""

    _evaluator = QualityRiskEvaluator()

    @classmethod
    def evaluate_quality(cls, image_path: Union[str, Path]) -> Dict[str, Union[float, str]]:
        """
        Evaluate all 6 quality indicators and composite quality risk.
        Terminology: "image-derived quality-risk indicator".
        """
        metrics = compute_all_quality_metrics(image_path)
        comp_risk = cls._evaluator.compute_risk_score(metrics)

        # Threshold for quality risk flag (composite risk >= 0.50)
        label = "RISK_FLAGGED" if comp_risk >= 0.50 else "NOMINAL"

        return {
            "laplacian_variance": float(metrics["laplacian_variance"]),
            "edge_density": float(metrics["edge_density"]),
            "shannon_entropy": float(metrics["shannon_entropy"]),
            "dynamic_range": float(metrics["dynamic_range"]),
            "clipping_ratio": float(metrics["total_clipping_ratio"]),
            "high_freq_fft_ratio": float(metrics["high_freq_fft_ratio"]),
            "composite_quality_risk": float(comp_risk),
            "quality_label": label,
        }
