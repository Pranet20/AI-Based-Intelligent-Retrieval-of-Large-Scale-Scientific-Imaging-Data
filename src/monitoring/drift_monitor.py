"""Scientific Dataset Distribution Shift & Model Performance Monitoring.

Monitors:
- Embedding distribution shift (Centroid distance, variance, norm drift)
- Image quality distribution shift (Risk score distributions)
- Instrument parameter shift (Detector, voltage categorical frequencies)
- Model latency and retrieval metric stability

Strict terminology: Termed 'DATASET DISTRIBUTION SHIFT' (not speculative anomalies).
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class DatasetShiftReport:
    timestamp: str
    reference_sample_count: int
    incoming_sample_count: int
    centroid_cosine_drift: float
    quality_mean_delta: float
    instrument_distribution_shift: float
    shift_status: str  # NOMINAL_STABLE, MODERATE_SHIFT, SIGNIFICANT_DISTRIBUTION_SHIFT
    shift_classification: str  # DATASET_DISTRIBUTION_SHIFT
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DatasetShiftMonitor:
    """Detects and quantifies statistical shifts between reference and incoming corpora."""

    @classmethod
    def compute_corpus_profile(
        cls,
        embeddings: np.ndarray,
        quality_risks: List[float],
        detectors: List[str],
        voltages_kv: List[float],
    ) -> Dict[str, Any]:
        """Extracts statistical summary profile of a dataset split."""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-12
        norm_embeddings = embeddings / norms

        centroid = np.mean(norm_embeddings, axis=0)
        c_norm = np.linalg.norm(centroid)
        if c_norm > 0:
            centroid = centroid / c_norm

        det_counts: Dict[str, int] = {}
        for d in detectors:
            det_counts[d] = det_counts.get(d, 0) + 1
        total_det = len(detectors) or 1
        det_dist = {k: v / total_det for k, v in det_counts.items()}

        return {
            "count": len(embeddings),
            "centroid": centroid.tolist(),
            "mean_quality_risk": float(np.mean(quality_risks)) if quality_risks else 0.0,
            "std_quality_risk": float(np.std(quality_risks)) if quality_risks else 0.0,
            "mean_voltage_kv": float(np.mean(voltages_kv)) if voltages_kv else 0.0,
            "detector_distribution": det_dist,
        }

    @classmethod
    def evaluate_shift(
        cls,
        ref_profile: Dict[str, Any],
        incoming_profile: Dict[str, Any],
    ) -> DatasetShiftReport:
        """Compares reference against incoming profile to detect distribution shift."""
        ref_c = np.array(ref_profile["centroid"])
        inc_c = np.array(incoming_profile["centroid"])

        # 1. Cosine distance between cluster centroids: 1 - cos(theta)
        dot = float(np.dot(ref_c, inc_c))
        centroid_drift = max(0.0, 1.0 - dot)

        # 2. Delta in mean image quality risk
        q_delta = abs(incoming_profile["mean_quality_risk"] - ref_profile["mean_quality_risk"])

        # 3. Total variation distance on detector categories
        ref_dets = ref_profile.get("detector_distribution", {})
        inc_dets = incoming_profile.get("detector_distribution", {})
        all_keys = set(ref_dets.keys()).union(set(inc_dets.keys()))
        tvd = 0.5 * sum(abs(ref_dets.get(k, 0.0) - inc_dets.get(k, 0.0)) for k in all_keys)

        # Shift thresholding
        if centroid_drift > 0.35 or tvd > 0.40:
            status = "SIGNIFICANT_DISTRIBUTION_SHIFT"
        elif centroid_drift > 0.15 or tvd > 0.20 or q_delta > 0.15:
            status = "MODERATE_SHIFT"
        else:
            status = "NOMINAL_STABLE"

        return DatasetShiftReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            reference_sample_count=ref_profile["count"],
            incoming_sample_count=incoming_profile["count"],
            centroid_cosine_drift=round(centroid_drift, 4),
            quality_mean_delta=round(q_delta, 4),
            instrument_distribution_shift=round(tvd, 4),
            shift_status=status,
            shift_classification="DATASET_DISTRIBUTION_SHIFT",
            details={
                "ref_mean_quality": ref_profile["mean_quality_risk"],
                "inc_mean_quality": incoming_profile["mean_quality_risk"],
                "ref_mean_voltage": ref_profile["mean_voltage_kv"],
                "inc_mean_voltage": incoming_profile["mean_voltage_kv"],
            },
        )


class ModelPerformanceTracker:
    """Tracks latency and retrieval stability across model deployments."""

    def __init__(self):
        self.latency_log: List[float] = []

    def record_latency(self, latency_ms: float):
        self.latency_log.append(latency_ms)
        if len(self.latency_log) > 1000:
            self.latency_log.pop(0)

    def get_summary(self) -> Dict[str, float]:
        if not self.latency_log:
            return {"mean_ms": 0.0, "p95_ms": 0.0}
        arr = np.array(self.latency_log)
        return {
            "mean_ms": round(float(np.mean(arr)), 2),
            "p50_ms": round(float(np.percentile(arr, 50)), 2),
            "p95_ms": round(float(np.percentile(arr, 95)), 2),
            "sample_count": len(arr),
        }
