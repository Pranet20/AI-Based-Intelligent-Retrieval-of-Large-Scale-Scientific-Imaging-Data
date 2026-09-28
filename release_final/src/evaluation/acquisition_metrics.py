"""Acquisition-robustness and representation geometry metrics for Phase 4."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


class AcquisitionMetricsCalculator:
    """Calculates acquisition-condition dependence and embedding geometry metrics."""

    @staticmethod
    def compute_similarity_metrics(
        embeddings: np.ndarray,
        material_labels: List[str] | np.ndarray,
        acquisition_labels: List[str] | np.ndarray,
    ) -> Dict[str, float]:
        """Compute within-acquisition, cross-acquisition, and different-material cosine similarities.

        Args:
            embeddings: (N, D) float32 array of unit-normalized embeddings.
            material_labels: (N,) array of material category strings.
            acquisition_labels: (N,) array of acquisition condition strings.

        Returns:
            Dictionary containing mean similarities, counts, and cross/within ratio.
        """
        N = len(embeddings)
        sim_mat = embeddings @ embeddings.T

        mats = np.asarray(material_labels)
        acqs = np.asarray(acquisition_labels)

        within_sims: List[float] = []
        cross_sims: List[float] = []
        diff_mat_sims: List[float] = []

        for i in range(N):
            for j in range(i + 1, N):
                s = float(sim_mat[i, j])
                if mats[i] == mats[j]:
                    if acqs[i] == acqs[j]:
                        within_sims.append(s)
                    else:
                        cross_sims.append(s)
                else:
                    diff_mat_sims.append(s)

        mean_within = float(np.mean(within_sims)) if within_sims else 0.0
        mean_cross = float(np.mean(cross_sims)) if cross_sims else 0.0
        mean_diff_mat = float(np.mean(diff_mat_sims)) if diff_mat_sims else 0.0
        ratio = (mean_cross / mean_within) if mean_within > 0 else 0.0

        return {
            "within_acquisition_mean_sim": mean_within,
            "within_acquisition_count": len(within_sims),
            "cross_acquisition_mean_sim": mean_cross,
            "cross_acquisition_count": len(cross_sims),
            "cross_within_similarity_ratio": ratio,
            "different_material_mean_sim": mean_diff_mat,
            "different_material_count": len(diff_mat_sims),
            "acquisition_gap": mean_within - mean_cross,
        }
