"""Score calibration for aligning visual and metadata similarity distributions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple
import numpy as np

from src.utils.logging import get_logger

logger = get_logger("retrieval.phase5_calibration")


class Phase5ScoreCalibrator:
    """Calibrates similarity scores to standard [0, 1] range using training distribution.
    
    Supports:
      - 'percentile': Empirical cumulative distribution function (ECDF) with linear interpolation.
      - 'minmax': Linear min-max scaling clipped to [0, 1].
    """

    def __init__(self, method: Literal["percentile", "minmax"] = "percentile") -> None:
        self.method = method
        self.is_fitted = False
        
        # Calibration state
        self.v_min: float = 0.0
        self.v_max: float = 1.0
        self.m_min: float = 0.0
        self.m_max: float = 1.0
        
        # Percentile interpolation knots
        self.v_knots: np.ndarray = np.array([])
        self.m_knots: np.ndarray = np.array([])
        self.p_knots: np.ndarray = np.array([])

    def fit(
        self,
        visual_scores: np.ndarray,
        metadata_scores: np.ndarray,
        num_quantiles: int = 10000,
    ) -> "Phase5ScoreCalibrator":
        """Learn calibration parameters strictly from training pairwise similarity scores.
        
        Args:
            visual_scores: 1D array of valid training visual similarities (excluding self).
            metadata_scores: 1D array of valid training metadata similarities (excluding self).
            num_quantiles: Number of quantile evaluation points for ECDF interpolation.
        """
        v_clean = visual_scores[~np.isnan(visual_scores) & ~np.isinf(visual_scores)]
        m_clean = metadata_scores[~np.isnan(metadata_scores) & ~np.isinf(metadata_scores)]

        if len(v_clean) == 0 or len(m_clean) == 0:
            raise ValueError("Empty training similarity scores provided for calibration.")

        # Min-max parameters
        self.v_min = float(np.min(v_clean))
        self.v_max = float(np.max(v_clean))
        self.m_min = float(np.min(m_clean))
        self.m_max = float(np.max(m_clean))

        # ECDF quantiles for compact, fast, monotonic percentile calibration
        q_grid = np.linspace(0.0, 1.0, min(num_quantiles, len(v_clean)))
        self.v_knots = np.quantile(v_clean, q_grid)
        self.m_knots = np.quantile(m_clean, q_grid)
        self.p_knots = q_grid

        # Ensure strict monotonicity for interp
        self.v_knots = np.maximum.accumulate(self.v_knots)
        self.m_knots = np.maximum.accumulate(self.m_knots)

        self.is_fitted = True
        logger.info(
            f"Fitted Phase5ScoreCalibrator ({self.method}): "
            f"V range=[{self.v_min:.4f}, {self.v_max:.4f}], M range=[{self.m_min:.4f}, {self.m_max:.4f}]"
        )
        return self

    def calibrate_visual(self, scores: np.ndarray) -> np.ndarray:
        """Calibrate visual similarity scores to [0, 1]."""
        if not self.is_fitted:
            raise RuntimeError("Calibrator must be fitted before transform.")

        if self.method == "minmax":
            denom = self.v_max - self.v_min
            if denom <= 0:
                denom = 1.0
            cal = (scores - self.v_min) / denom
            return np.clip(cal, 0.0, 1.0).astype(np.float32)
        else:  # percentile
            orig_shape = scores.shape
            flat = scores.ravel()
            cal = np.interp(flat, self.v_knots, self.p_knots, left=0.0, right=1.0)
            return cal.reshape(orig_shape).astype(np.float32)

    def calibrate_metadata(self, scores: np.ndarray) -> np.ndarray:
        """Calibrate metadata similarity scores to [0, 1]."""
        if not self.is_fitted:
            raise RuntimeError("Calibrator must be fitted before transform.")

        if self.method == "minmax":
            denom = self.m_max - self.m_min
            if denom <= 0:
                denom = 1.0
            cal = (scores - self.m_min) / denom
            return np.clip(cal, 0.0, 1.0).astype(np.float32)
        else:  # percentile
            orig_shape = scores.shape
            flat = scores.ravel()
            cal = np.interp(flat, self.m_knots, self.p_knots, left=0.0, right=1.0)
            return cal.reshape(orig_shape).astype(np.float32)

    def calibrate(self, S_V: np.ndarray, S_M: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calibrate both visual and metadata similarity matrices."""
        return self.calibrate_visual(S_V), self.calibrate_metadata(S_M)

    def save(self, filepath: str | Path) -> None:
        """Save calibrator parameters to JSON."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted calibrator.")
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "method": self.method,
            "v_min": self.v_min,
            "v_max": self.v_max,
            "m_min": self.m_min,
            "m_max": self.m_max,
            "v_knots": self.v_knots.tolist(),
            "m_knots": self.m_knots.tolist(),
            "p_knots": self.p_knots.tolist(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str | Path) -> "Phase5ScoreCalibrator":
        """Load calibrator parameters from JSON."""
        path = Path(filepath)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        cal = cls(method=data["method"])
        cal.v_min = float(data["v_min"])
        cal.v_max = float(data["v_max"])
        cal.m_min = float(data["m_min"])
        cal.m_max = float(data["m_max"])
        cal.v_knots = np.array(data["v_knots"], dtype=np.float32)
        cal.m_knots = np.array(data["m_knots"], dtype=np.float32)
        cal.p_knots = np.array(data["p_knots"], dtype=np.float32)
        cal.is_fitted = True
        return cal
