"""Exact retrieval evaluator for Phase 4 adapted scientific image representations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.adaptation.relationship_builder import RelationshipBuilder
from src.utils.logging import get_logger

logger = get_logger("evaluation.phase4_evaluator")


class Phase4RetrievalEvaluator:
    """Evaluates cross-acquisition representation retrieval under exact cosine similarity."""

    def __init__(
        self,
        k_values: Tuple[int, ...] = (1, 5, 10),
        eval_depth: int = 50,
    ) -> None:
        self.k_values = k_values
        self.eval_depth = max(eval_depth, max(k_values))

    def evaluate_retrieval(
        self,
        embeddings: np.ndarray,
        image_ids: List[str],
        ground_truth_positives: Dict[str, Set[str]],
        exclusion_sets: Dict[str, Set[str]],
        candidate_ids: Optional[List[str]] = None,
        candidate_embeddings: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """Compute exact cross-acquisition retrieval metrics.

        Args:
            embeddings: (Q, D) array of unit-normalized query embeddings.
            image_ids: List of Q query image IDs.
            ground_truth_positives: Dict mapping query_id -> set of positive candidate IDs.
            exclusion_sets: Dict mapping query_id -> set of candidate IDs to exclude from ranking.
            candidate_ids: Optional list of C candidate image IDs. If None, queries act as candidates.
            candidate_embeddings: Optional (C, D) array of candidate embeddings. If None, queries act as candidates.

        Returns:
            Dict containing R@1, R@5, R@10, MRR, P@5, and candidate counts.
        """
        if candidate_ids is None or candidate_embeddings is None:
            c_ids = image_ids
            c_embs = embeddings
        else:
            c_ids = candidate_ids
            c_embs = candidate_embeddings

        c_id_to_idx = {cid: idx for idx, cid in enumerate(c_ids)}
        N_c = len(c_ids)

        sim_matrix = embeddings @ c_embs.T

        total_queries = len(image_ids)
        evaluated_queries = 0
        no_positive_queries = 0

        reciprocal_ranks: List[float] = []
        recalls_at_k: Dict[int, List[float]] = {k: [] for k in self.k_values}
        precisions_at_k: Dict[int, List[float]] = {k: [] for k in self.k_values}
        first_positive_ranks: List[int] = []

        for q_idx, q_id in enumerate(image_ids):
            positives = ground_truth_positives.get(q_id, set())
            if not positives:
                no_positive_queries += 1
                continue

            evaluated_queries += 1
            excl = exclusion_sets.get(q_id, set())

            row_sim = sim_matrix[q_idx].copy()

            # Always exclude self if query is in candidate pool
            if q_id in c_id_to_idx:
                row_sim[c_id_to_idx[q_id]] = -1e9

            # Apply candidate exclusions
            for ex_id in excl:
                if ex_id in c_id_to_idx:
                    row_sim[c_id_to_idx[ex_id]] = -1e9

            # Rank candidates
            ranked_indices = np.argsort(-row_sim)[: self.eval_depth]
            ranked_cids = [c_ids[idx] for idx in ranked_indices]

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
            "candidate_pool_size": N_c,
            "mrr": float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0,
            "mean_first_positive_rank": float(np.mean(first_positive_ranks)) if first_positive_ranks else 0.0,
        }
        for k in self.k_values:
            summary[f"recall_at_{k}"] = float(np.mean(recalls_at_k[k])) if recalls_at_k[k] else 0.0
            summary[f"precision_at_{k}"] = float(np.mean(precisions_at_k[k])) if precisions_at_k[k] else 0.0

        return summary
