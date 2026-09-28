"""Configurable quality assessment grader (PASS / REVIEW / FAIL).

Classifies images based on computational indicators without deleting data.
Provides granular inspection reasons for flagged images.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import yaml

from src.quality.metrics import QualityMetricsResult


class QualityEvaluator:
    """Evaluates computational quality indicators against configurable research thresholds."""

    def __init__(self, config_path: Optional[str | Path] = None) -> None:
        self.config = self._load_config(config_path)
        self.thresholds = self.config.get("thresholds", {})
        self.weights = self.config.get("weights", {})

    def _load_config(self, config_path: Optional[str | Path]) -> Dict[str, Any]:
        default_config = {
            "thresholds": {
                "min_laplacian_variance_pass": 50.0,
                "min_laplacian_variance_review": 15.0,
                "max_saturation_ratio_pass": 0.05,
                "max_saturation_ratio_review": 0.15,
                "max_dark_ratio_pass": 0.10,
                "max_dark_ratio_review": 0.30,
                "min_dynamic_range_ratio_pass": 0.20,
                "min_dynamic_range_ratio_review": 0.05,
                "min_entropy_pass": 4.0,
                "min_entropy_review": 2.5,
                "min_contrast_pass": 15.0,
                "min_contrast_review": 5.0,
            },
            "weights": {
                "focus": 0.25,
                "contrast": 0.25,
                "dynamic_range": 0.20,
                "entropy": 0.20,
                "non_saturation": 0.10,
            },
        }
        if config_path:
            p = Path(config_path)
            if p.is_file():
                with open(p, "r", encoding="utf-8") as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        return loaded
        return default_config

    def evaluate(
        self,
        metrics: QualityMetricsResult,
        bit_depth: int = 8,
    ) -> Tuple[str, float, List[str]]:
        """Evaluate metrics and return (status, composite_score, flag_reasons).

        Status is one of: PASS, REVIEW, FAIL.
        Composite score is bounded between 0.0 and 1.0.
        """
        flags: List[str] = []
        max_possible = 65535.0 if bit_depth == 16 else 255.0
        dyn_ratio = metrics.dynamic_range / max_possible if max_possible > 0 else 0.0

        # Check Fail Conditions
        is_fail = False
        if metrics.laplacian_variance < self.thresholds.get("min_laplacian_variance_review", 15.0):
            flags.append(
                f"Severe blur / low Laplacian variance ({metrics.laplacian_variance:.1f} < {self.thresholds.get('min_laplacian_variance_review', 15.0)})"
            )
            is_fail = True

        if metrics.entropy < self.thresholds.get("min_entropy_review", 2.5):
            flags.append(
                f"Extremely low Shannon entropy ({metrics.entropy:.2f} bits < {self.thresholds.get('min_entropy_review', 2.5)})"
            )
            is_fail = True

        if dyn_ratio < self.thresholds.get("min_dynamic_range_ratio_review", 0.05):
            flags.append(
                f"Severely collapsed dynamic range ({dyn_ratio:.3f} < {self.thresholds.get('min_dynamic_range_ratio_review', 0.05)})"
            )
            is_fail = True

        if metrics.saturation_ratio > self.thresholds.get("max_saturation_ratio_review", 0.15):
            flags.append(
                f"Excessive clipping/saturation ({metrics.saturation_ratio * 100:.1f}% > {self.thresholds.get('max_saturation_ratio_review', 0.15) * 100:.0f}%)"
            )
            is_fail = True

        # Check Review Conditions
        is_review = False
        if not is_fail:
            if metrics.laplacian_variance < self.thresholds.get("min_laplacian_variance_pass", 50.0):
                flags.append(
                    f"Sub-optimal focus sharpness ({metrics.laplacian_variance:.1f} < {self.thresholds.get('min_laplacian_variance_pass', 50.0)})"
                )
                is_review = True

            if metrics.entropy < self.thresholds.get("min_entropy_pass", 4.0):
                flags.append(
                    f"Moderate entropy ({metrics.entropy:.2f} bits < {self.thresholds.get('min_entropy_pass', 4.0)})"
                )
                is_review = True

            if metrics.contrast < self.thresholds.get("min_contrast_pass", 15.0):
                flags.append(
                    f"Low contrast ({metrics.contrast:.1f} < {self.thresholds.get('min_contrast_pass', 15.0)})"
                )
                is_review = True

            if metrics.saturation_ratio > self.thresholds.get("max_saturation_ratio_pass", 0.05):
                flags.append(
                    f"Moderate pixel saturation ({metrics.saturation_ratio * 100:.1f}%)"
                )
                is_review = True

            if metrics.dark_pixel_ratio > self.thresholds.get("max_dark_ratio_pass", 0.10):
                flags.append(
                    f"Noticeable under-exposure ({metrics.dark_pixel_ratio * 100:.1f}% dark pixels)"
                )
                is_review = True

        status = "FAIL" if is_fail else ("REVIEW" if is_review else "PASS")

        # Compute normalized composite score [0.0, 1.0]
        # Focus score: sigmoid or min clip
        focus_score = min(1.0, max(0.0, metrics.laplacian_variance / 200.0))
        contrast_score = min(1.0, max(0.0, metrics.contrast / 60.0))
        dr_score = min(1.0, max(0.0, dyn_ratio / 0.8))
        entropy_score = min(1.0, max(0.0, metrics.entropy / 8.0))
        sat_penalty = min(1.0, max(0.0, 1.0 - (metrics.saturation_ratio + metrics.dark_pixel_ratio)))

        w = self.weights
        composite = (
            w.get("focus", 0.25) * focus_score
            + w.get("contrast", 0.25) * contrast_score
            + w.get("dynamic_range", 0.20) * dr_score
            + w.get("entropy", 0.20) * entropy_score
            + w.get("non_saturation", 0.10) * sat_penalty
        )
        composite = round(float(np.clip(composite, 0.0, 1.0)), 4)

        return status, composite, flags
