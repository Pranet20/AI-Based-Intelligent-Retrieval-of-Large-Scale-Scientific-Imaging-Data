"""Hybrid score calculation and ranking for Phase 5."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np

from src.retrieval.phase5_calibration import Phase5ScoreCalibrator
from src.utils.logging import get_logger

logger = get_logger("retrieval.phase5_fusion")


class Phase5HybridFusion:
    """Combines calibrated visual and metadata similarity scores."""

    def __init__(
        self,
        calibrator: Optional[Phase5ScoreCalibrator] = None,
        k_values: Tuple[int, ...] = (1, 5, 10),
        eval_depth: int = 50,
    ) -> None:
        self.calibrator = calibrator
        self.k_values = k_values
        self.eval_depth = max(eval_depth, max(k_values))

    def compute_hybrid_matrix(
        self,
        S_V: np.ndarray,
        S_M: np.ndarray,
        alpha: float,
    ) -> np.ndarray:
        """Compute the hybrid similarity matrix: alpha * S_V_hat + (1 - alpha) * S_M_hat.
        
        Args:
            S_V: (Q, C) raw visual cosine similarity matrix.
            S_M: (Q, C) raw metadata cosine similarity matrix.
            alpha: Weight in [0.0, 1.0].
            
        Returns:
            S_H: (Q, C) hybrid similarity matrix.
        """
        if not (0.0 <= alpha <= 1.0):
            raise ValueError(f"Alpha must be in [0.0, 1.0], got {alpha}")

        # Exact boundary preservation for tie-breaking fidelity
        if alpha == 1.0:
            return S_V.copy().astype(np.float32)
        if alpha == 0.0:
            return S_M.copy().astype(np.float32)

        if self.calibrator is not None and self.calibrator.is_fitted:
            S_V_hat = self.calibrator.calibrate_visual(S_V)
            S_M_hat = self.calibrator.calibrate_metadata(S_M)
        else:
            S_V_hat = S_V
            S_M_hat = S_M

        S_H = alpha * S_V_hat + (1.0 - alpha) * S_M_hat
        return S_H.astype(np.float32)

    def evaluate(
        self,
        S_H: np.ndarray,
        query_ids: List[str],
        candidate_ids: List[str],
        ground_truth_positives: Dict[str, Set[str]],
        exclusion_sets: Dict[str, Set[str]],
    ) -> Dict[str, Any]:
        """Rank candidates and evaluate retrieval metrics under exclusions.
        
        Args:
            S_H: (Q, C) hybrid similarity matrix.
            query_ids: List of Q query image IDs.
            candidate_ids: List of C candidate image IDs.
            ground_truth_positives: Dict mapping query_id -> set of true positive candidate IDs.
            exclusion_sets: Dict mapping query_id -> set of candidate IDs to exclude.
            
        Returns:
            Dict containing R@1, R@5, R@10, MRR, P@5, P@10, and diagnostics.
        """
        c_id_to_idx = {cid: idx for idx, cid in enumerate(candidate_ids)}
        total_queries = len(query_ids)
        evaluated_queries = 0
        no_positive_queries = 0

        reciprocal_ranks: List[float] = []
        recalls_at_k: Dict[int, List[float]] = {k: [] for k in self.k_values}
        precisions_at_k: Dict[int, List[float]] = {k: [] for k in self.k_values}
        first_positive_ranks: List[int] = []

        # Per-query rankings for error analysis
        ranked_results: Dict[str, List[str]] = {}

        for q_idx, q_id in enumerate(query_ids):
            positives = ground_truth_positives.get(q_id, set())
            if not positives:
                no_positive_queries += 1
                continue

            evaluated_queries += 1
            excl = exclusion_sets.get(q_id, set())

            row_sim = S_H[q_idx].copy()

            # Always exclude self if query is in candidate pool
            if q_id in c_id_to_idx:
                row_sim[c_id_to_idx[q_id]] = -1e9

            # Apply candidate exclusions (duplicates, same-acquisition peers)
            for ex_id in excl:
                if ex_id in c_id_to_idx:
                    row_sim[c_id_to_idx[ex_id]] = -1e9

            # Rank candidates descending (filtering out excluded candidates and self)
            ranked_indices = np.argsort(-row_sim)[: self.eval_depth]
            ranked_cids = [candidate_ids[idx] for idx in ranked_indices if row_sim[idx] > -1e8]
            ranked_results[q_id] = ranked_cids

            first_rank = None
            pos_hits_at_k = {k: 0 for k in self.k_values}

            for rank_0, cid in enumerate(ranked_cids):
                rank_1 = rank_0 + 1
                if cid in positives:
                    if first_rank is None:
                        first_rank = rank_1
                    for k in self.k_values:
                        if rank_1 <= k:
                            pos_hits_at_k[k] += 1

            if first_rank is not None:
                first_positive_ranks.append(first_rank)
                reciprocal_ranks.append(1.0 / first_rank)
            else:
                reciprocal_ranks.append(0.0)

            for k in self.k_values:
                recalls_at_k[k].append(1.0 if pos_hits_at_k[k] > 0 else 0.0)
                precisions_at_k[k].append(pos_hits_at_k[k] / float(k))

        summary: Dict[str, Any] = {
            "total_queries": total_queries,
            "evaluated_queries": evaluated_queries,
            "no_valid_positive_queries": no_positive_queries,
            "candidate_pool_size": len(candidate_ids),
            "mrr": float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0,
            "mean_first_positive_rank": float(np.mean(first_positive_ranks)) if first_positive_ranks else 0.0,
        }
        for k in self.k_values:
            summary[f"recall_at_{k}"] = float(np.mean(recalls_at_k[k])) if recalls_at_k[k] else 0.0
            summary[f"precision_at_{k}"] = float(np.mean(precisions_at_k[k])) if precisions_at_k[k] else 0.0

        summary["ranked_results"] = ranked_results
        return summary
