"""Standardized Phase 5 retrieval evaluation harness."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.retrieval.phase5_calibration import Phase5ScoreCalibrator
from src.retrieval.phase5_fusion import Phase5HybridFusion
from src.utils.logging import get_logger

logger = get_logger("retrieval.phase5_evaluator")

ALPHA_GRID = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]


class Phase5Evaluator:
    """Orchestrates validation-based alpha selection and test partition evaluation."""

    def __init__(
        self,
        calibrator: Optional[Phase5ScoreCalibrator] = None,
        alpha_grid: List[float] = ALPHA_GRID,
        selection_metric: str = "mrr",
    ) -> None:
        self.calibrator = calibrator
        self.alpha_grid = alpha_grid
        self.selection_metric = selection_metric
        self.fusion = Phase5HybridFusion(calibrator=calibrator)

    def select_best_alpha(
        self,
        S_V_val: np.ndarray,
        S_M_val: np.ndarray,
        val_query_ids: List[str],
        val_candidate_ids: List[str],
        val_gt: Dict[str, Set[str]],
        val_excl: Dict[str, Set[str]],
    ) -> Tuple[float, Dict[float, Dict[str, Any]]]:
        """Evaluate the alpha grid strictly on the validation set and select optimal alpha.
        
        Args:
            S_V_val: Validation visual similarity matrix.
            S_M_val: Validation metadata similarity matrix.
            val_query_ids: Validation query IDs.
            val_candidate_ids: Validation candidate IDs.
            val_gt: Validation ground-truth positive pairs.
            val_excl: Validation exclusion sets.
            
        Returns:
            Tuple of (best_alpha, grid_results_dict).
        """
        grid_results: Dict[float, Dict[str, Any]] = {}
        best_alpha = 1.0
        best_score = -1.0

        for alpha in self.alpha_grid:
            S_H = self.fusion.compute_hybrid_matrix(S_V_val, S_M_val, alpha=alpha)
            res = self.fusion.evaluate(
                S_H=S_H,
                query_ids=val_query_ids,
                candidate_ids=val_candidate_ids,
                ground_truth_positives=val_gt,
                exclusion_sets=val_excl,
            )
            # Remove full ranking dict for compact serialization
            res_summary = {k: v for k, v in res.items() if k != "ranked_results"}
            grid_results[alpha] = res_summary

            score = res.get(self.selection_metric, 0.0)
            # Tie breaking: if scores are equal, prefer higher alpha (higher visual weight)
            if score > best_score:
                best_score = score
                best_alpha = alpha
            elif np.isclose(score, best_score, atol=1e-7) and alpha > best_alpha:
                best_alpha = alpha

        logger.info(
            f"Alpha selection completed. Selected alpha={best_alpha:.1f} "
            f"(Validation {self.selection_metric}={best_score:.4f})"
        )
        return best_alpha, grid_results

    def evaluate_at_alpha(
        self,
        S_V: np.ndarray,
        S_M: np.ndarray,
        alpha: float,
        query_ids: List[str],
        candidate_ids: List[str],
        gt_positives: Dict[str, Set[str]],
        exclusions: Dict[str, Set[str]],
    ) -> Dict[str, Any]:
        """Evaluate retrieval at a specific frozen alpha."""
        S_H = self.fusion.compute_hybrid_matrix(S_V, S_M, alpha=alpha)
        return self.fusion.evaluate(
            S_H=S_H,
            query_ids=query_ids,
            candidate_ids=candidate_ids,
            ground_truth_positives=gt_positives,
            exclusion_sets=exclusions,
        )

    @staticmethod
    def compute_deltas(
        hybrid_metrics: Dict[str, Any],
        visual_metrics: Dict[str, Any],
    ) -> Dict[str, float]:
        """Compute absolute metric differences: Delta = Hybrid - Visual."""
        keys = ["recall_at_1", "recall_at_5", "recall_at_10", "mrr", "precision_at_5", "precision_at_10"]
        deltas: Dict[str, float] = {}
        for k in keys:
            h_val = hybrid_metrics.get(k, 0.0)
            v_val = visual_metrics.get(k, 0.0)
            deltas[f"delta_{k}"] = float(h_val - v_val)
        return deltas
