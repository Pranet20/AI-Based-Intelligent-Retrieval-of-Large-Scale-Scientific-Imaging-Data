"""Strict, group-aware zero-shot retrieval metrics implementation."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
import numpy as np


def compute_cosine_similarity_matrix(query_embeddings: np.ndarray, candidate_embeddings: np.ndarray) -> np.ndarray:
    """Compute pairwise cosine similarities between query and candidate vectors.

    Assumes vectors are L2-normalized.
    """
    return np.matmul(query_embeddings, candidate_embeddings.T)


class RetrievalMetricsCalculator:
    """Calculates Recall@K, MRR, and Precision@K with strict self-exclusion and anti-leakage grouping."""

    @staticmethod
    def evaluate_retrieval(
        similarity_matrix: np.ndarray,
        query_ids: List[str],
        candidate_ids: List[str],
        ground_truth_positives: Dict[str, Set[str]],
        exclusion_sets: Optional[Dict[str, Set[str]]] = None,
        k_values: Tuple[int, ...] = (1, 5, 10),
    ) -> Dict[str, Any]:
        """Evaluate zero-shot retrieval performance across all queries.

        Args:
            similarity_matrix: (N_q, N_c) matrix of cosine similarities.
            query_ids: List of N_q query image IDs.
            candidate_ids: List of N_c candidate image IDs.
            ground_truth_positives: Mapping query_id -> set of valid positive candidate_ids.
            exclusion_sets: Optional mapping query_id -> set of candidate_ids to exclude from ranking
                            (e.g., identical source acquisitions, duplicates, self-matches).
            k_values: Tuple of K cutoffs to evaluate.

        Returns:
            Dictionary containing micro/macro Recall@K, MRR, Precision@K, and query counts.
        """
        cand_id_to_idx = {cid: idx for idx, cid in enumerate(candidate_ids)}
        max_k = max(k_values)

        recalls_at_k: Dict[int, List[float]] = {k: [] for k in k_values}
        precisions_at_k: Dict[int, List[float]] = {k: [] for k in k_values}
        reciprocal_ranks: List[float] = []

        total_queries = len(query_ids)
        evaluated_queries = 0
        no_positive_queries = 0

        query_details: List[Dict[str, Any]] = []

        for q_idx, q_id in enumerate(query_ids):
            positives = ground_truth_positives.get(q_id, set())

            # Candidate exclusions: query itself + any explicit exclusions
            exclusions = set()
            if exclusion_sets and q_id in exclusion_sets:
                exclusions.update(exclusion_sets[q_id])
            exclusions.add(q_id)  # Strict self-match exclusion

            # Valid positives after exclusions
            valid_positives = positives - exclusions

            if not valid_positives:
                no_positive_queries += 1
                query_details.append({
                    "query_id": q_id,
                    "status": "NO_VALID_POSITIVE",
                    "valid_positives_count": 0,
                    "reciprocal_rank": None,
                })
                continue

            evaluated_queries += 1

            # Get raw scores for candidates
            scores = similarity_matrix[q_idx].copy()

            # Mask excluded candidates with -infinity so they can never be ranked
            for excl_id in exclusions:
                if excl_id in cand_id_to_idx:
                    scores[cand_id_to_idx[excl_id]] = -np.inf

            # Rank candidate indices descending by score
            # Valid pool size excludes masked items
            valid_candidate_count = len(scores) - len(exclusions)
            ranked_indices = np.argsort(-scores)

            # Find rank of first positive
            found_first_rank: Optional[int] = None
            top_retrieved_ids = []
            positive_hits_at_k: Dict[int, int] = {k: 0 for k in k_values}

            for rank_0, c_idx in enumerate(ranked_indices[:max(max_k, 50)]):
                c_id = candidate_ids[c_idx]
                if scores[c_idx] == -np.inf:
                    break
                top_retrieved_ids.append(c_id)
                rank_1 = rank_0 + 1

                if c_id in valid_positives:
                    if found_first_rank is None:
                        found_first_rank = rank_1
                    for k in k_values:
                        if rank_1 <= k:
                            positive_hits_at_k[k] += 1

            # Metric updates
            rr = (1.0 / found_first_rank) if found_first_rank is not None else 0.0
            reciprocal_ranks.append(rr)

            for k in k_values:
                # Recall@K is 1 if any positive hit in top K, else 0
                has_hit = 1.0 if positive_hits_at_k[k] > 0 else 0.0
                recalls_at_k[k].append(has_hit)
                # Precision@K is fraction of top K that are positive
                prec = positive_hits_at_k[k] / float(k)
                precisions_at_k[k].append(prec)

            query_details.append({
                "query_id": q_id,
                "status": "SUCCESS",
                "valid_positives_count": len(valid_positives),
                "first_positive_rank": found_first_rank,
                "reciprocal_rank": round(rr, 6),
                "top_5_retrieved": top_retrieved_ids[:5],
            })

        summary: Dict[str, Any] = {
            "total_queries": total_queries,
            "evaluated_queries": evaluated_queries,
            "no_valid_positive_queries": no_positive_queries,
            "mrr": float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0,
        }

        for k in k_values:
            summary[f"recall_at_{k}"] = float(np.mean(recalls_at_k[k])) if recalls_at_k[k] else 0.0
            summary[f"precision_at_{k}"] = float(np.mean(precisions_at_k[k])) if precisions_at_k[k] else 0.0

        return {
            "summary": summary,
            "query_details": query_details,
        }
