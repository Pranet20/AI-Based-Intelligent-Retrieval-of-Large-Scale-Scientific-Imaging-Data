"""Evaluates FAISS retrieval indexes against frozen Phase 2 exact brute-force reference."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.evaluation.retrieval_metrics import (
    RetrievalMetricsCalculator,
    compute_cosine_similarity_matrix,
)
from src.retrieval.faiss_index import FAISSVectorIndex, IndexType
from src.utils.logging import get_logger

logger = get_logger("retrieval.evaluator")


class Phase3RetrievalEvaluator:
    """Evaluates scalable FAISS vector retrieval against frozen Phase 2 exact reference."""

    def __init__(
        self,
        reports_dir: str | Path = "reports/phase3",
    ) -> None:
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_embeddings(parquet_path: str | Path) -> Tuple[np.ndarray, List[str], pd.DataFrame]:
        """Load embedding array, image IDs, and full dataframe."""
        df = pd.read_parquet(parquet_path)
        ids = df["image_id"].tolist()
        matrix = np.vstack(df["embedding"].to_numpy()).astype(np.float32)
        return matrix, ids, df

    def evaluate_exact_agreement(
        self,
        embeddings: np.ndarray,
        query_ids: List[str],
        ground_truth_positives: Dict[str, Set[str]],
        exclusion_sets: Dict[str, Set[str]],
        k_values: Tuple[int, ...] = (1, 5, 10),
    ) -> Dict[str, Any]:
        """Verify that FAISS IndexFlatIP reproduces exact brute-force search ordering."""
        logger.info("Computing exact brute-force cosine reference across %d queries...", len(query_ids))
        ref_sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

        ref_eval = RetrievalMetricsCalculator.evaluate_retrieval(
            similarity_matrix=ref_sim_mat,
            query_ids=query_ids,
            candidate_ids=query_ids,
            ground_truth_positives=ground_truth_positives,
            exclusion_sets=exclusion_sets,
            k_values=k_values,
        )

        logger.info("Building FAISS IndexFlatIP to test exact agreement...")
        flat_index = FAISSVectorIndex(dimension=embeddings.shape[1], index_type=IndexType.FLAT_IP)
        flat_index.build(embeddings, ids=query_ids)

        # Note on search_k: requests a sufficiently deep candidate list before exclusion filtering,
        # reducing candidate starvation caused by post-search filtering. For approximate indexes,
        # this does not guarantee exact recall because relevant candidates may still be omitted
        # by the ANN search itself.
        max_k = max(k_values)
        eval_depth = max(max_k, 50)
        max_excl = max(len(exclusion_sets.get(q, set())) for q in query_ids) if exclusion_sets else 1
        search_k = min(flat_index.ntotal, max(eval_depth + max_excl + 50, 100))

        _, _, retrieved_id_lists = flat_index.search(embeddings, k=search_k)

        # Compare per-query ranked results after applying exclusions
        cand_id_to_idx = {cid: idx for idx, cid in enumerate(query_ids)}
        top1_matches = 0
        top5_set_agreements: List[float] = []
        top10_set_agreements: List[float] = []
        total_eval_queries = 0

        for q_idx, q_id in enumerate(query_ids):
            excl = set(exclusion_sets.get(q_id, set()))
            excl.add(q_id)

            # Brute-force reference ranking
            ref_scores = ref_sim_mat[q_idx].copy()
            for eid in excl:
                if eid in cand_id_to_idx:
                    ref_scores[cand_id_to_idx[eid]] = -np.inf

            ref_ranked_idx = np.argsort(-ref_scores)
            ref_ranked_ids = [query_ids[i] for i in ref_ranked_idx if ref_scores[i] > -np.inf]

            # FAISS ranking after exclusion filtering
            faiss_raw_ids = retrieved_id_lists[q_idx]
            faiss_filtered_ids = [cid for cid in faiss_raw_ids if cid not in excl]

            if not ref_ranked_ids or not faiss_filtered_ids:
                continue

            total_eval_queries += 1

            # Top-1 agreement
            if ref_ranked_ids[0] == faiss_filtered_ids[0]:
                top1_matches += 1
            else:
                # Check for exact floating point score tie
                score_ref = ref_sim_mat[q_idx, cand_id_to_idx[ref_ranked_ids[0]]]
                score_faiss = ref_sim_mat[q_idx, cand_id_to_idx[faiss_filtered_ids[0]]]
                if np.isclose(score_ref, score_faiss, atol=1e-5):
                    top1_matches += 1

            # Top-5 set agreement (Jaccard similarity)
            s_ref_5 = set(ref_ranked_ids[:5])
            s_faiss_5 = set(faiss_filtered_ids[:5])
            jaccard_5 = len(s_ref_5 & s_faiss_5) / max(1, len(s_ref_5 | s_faiss_5))
            top5_set_agreements.append(jaccard_5)

            # Top-10 set agreement
            s_ref_10 = set(ref_ranked_ids[:10])
            s_faiss_10 = set(faiss_filtered_ids[:10])
            jaccard_10 = len(s_ref_10 & s_faiss_10) / max(1, len(s_ref_10 | s_faiss_10))
            top10_set_agreements.append(jaccard_10)

        agreement_report = {
            "total_queries": len(query_ids),
            "evaluated_queries": total_eval_queries,
            "top1_agreement_rate": float(top1_matches / total_eval_queries) if total_eval_queries else 0.0,
            "top5_agreement_rate": float(np.mean(top5_set_agreements)) if top5_set_agreements else 0.0,
            "top10_agreement_rate": float(np.mean(top10_set_agreements)) if top10_set_agreements else 0.0,
            "reference_summary": ref_eval["summary"],
        }
        return agreement_report

    def evaluate_faiss_index(
        self,
        index: FAISSVectorIndex,
        embeddings: np.ndarray,
        query_ids: List[str],
        ground_truth_positives: Dict[str, Set[str]],
        exclusion_sets: Dict[str, Set[str]],
        k_values: Tuple[int, ...] = (1, 5, 10),
        nprobe: Optional[int] = None,
        ef_search: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Evaluate a FAISS index configuration with strict anti-leakage self and candidate exclusions."""
        # Note on search_k: requests a sufficiently deep candidate list before exclusion filtering,
        # reducing candidate starvation caused by post-search filtering. For approximate indexes,
        # this does not guarantee exact recall because relevant candidates may still be omitted
        # by the ANN search itself.
        max_k = max(k_values)
        eval_depth = max(max_k, 50)
        max_excl = max(len(exclusion_sets.get(q, set())) for q in query_ids) if exclusion_sets else 1
        search_k = min(index.ntotal, max(eval_depth + max_excl + 50, 100))

        scores, indices, retrieved_id_lists = index.search(
            embeddings,
            k=search_k,
            nprobe=nprobe,
            ef_search=ef_search,
        )

        recalls_at_k: Dict[int, List[float]] = {k: [] for k in k_values}
        precisions_at_k: Dict[int, List[float]] = {k: [] for k in k_values}
        reciprocal_ranks: List[float] = []

        total_queries = len(query_ids)
        evaluated_queries = 0
        no_positive_queries = 0

        for q_idx, q_id in enumerate(query_ids):
            positives = ground_truth_positives.get(q_id, set())
            excl = set(exclusion_sets.get(q_id, set()))
            excl.add(q_id)  # Strict self exclusion

            valid_positives = positives - excl
            if not valid_positives:
                no_positive_queries += 1
                continue

            evaluated_queries += 1

            # Filter retrieved list by exclusions
            raw_ids = retrieved_id_lists[q_idx]
            ranked_cids = [cid for cid in raw_ids if cid not in excl][:eval_depth]

            first_rank: Optional[int] = None
            pos_hits_at_k: Dict[int, int] = {k: 0 for k in k_values}

            for rank_0, cid in enumerate(ranked_cids):
                rank_1 = rank_0 + 1
                if cid in valid_positives:
                    if first_rank is None:
                        first_rank = rank_1
                    for k in k_values:
                        if rank_1 <= k:
                            pos_hits_at_k[k] += 1

            rr = (1.0 / first_rank) if first_rank is not None else 0.0
            reciprocal_ranks.append(rr)

            for k in k_values:
                has_hit = 1.0 if pos_hits_at_k[k] > 0 else 0.0
                recalls_at_k[k].append(has_hit)
                prec = pos_hits_at_k[k] / float(k)
                precisions_at_k[k].append(prec)

        summary: Dict[str, Any] = {
            "total_queries": total_queries,
            "evaluated_queries": evaluated_queries,
            "no_valid_positive_queries": no_positive_queries,
            "mrr": float(np.mean(reciprocal_ranks)) if reciprocal_ranks else 0.0,
        }
        for k in k_values:
            summary[f"recall_at_{k}"] = float(np.mean(recalls_at_k[k])) if recalls_at_k[k] else 0.0
            summary[f"precision_at_{k}"] = float(np.mean(precisions_at_k[k])) if precisions_at_k[k] else 0.0

        return summary

    def build_hcci_ground_truth(
        self,
        df_emb: pd.DataFrame,
        manifest_path: Optional[str | Path] = "data/manifests/hcci_manifest.parquet",
    ) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        """Build exact audited HCCI ground truth and candidate exclusion sets."""
        manifest_meta: Dict[str, Dict[str, Any]] = {}
        if manifest_path is not None and Path(manifest_path).is_file():
            df_man = pd.read_parquet(manifest_path)
            for _, r in df_man.iterrows():
                manifest_meta[r["image_id"]] = {
                    "specimen_id": r.get("specimen_id"),
                    "roi_id": r.get("roi_id"),
                    "acquisition_id": r.get("acquisition_id"),
                    "duplicate_group_id": r.get("duplicate_group_id"),
                    "near_duplicate_group_id": r.get("near_duplicate_group_id"),
                    "sha256": r.get("sha256"),
                }

        query_ids = df_emb["image_id"].tolist()
        meta_dict = {}
        for _, row in df_emb.iterrows():
            q_id = row["image_id"]
            man_info = manifest_meta.get(q_id, {})
            meta_dict[q_id] = {
                "specimen_id": row.get("specimen_id") or man_info.get("specimen_id"),
                "acquisition_id": row.get("acquisition_id") or man_info.get("acquisition_id"),
                "duplicate_group_id": man_info.get("duplicate_group_id"),
                "near_duplicate_group_id": man_info.get("near_duplicate_group_id"),
                "sha256": row.get("source_sha256") or man_info.get("sha256"),
            }

        ground_truth: Dict[str, Set[str]] = {}
        exclusions: Dict[str, Set[str]] = {}

        for q_id in query_ids:
            q_meta = meta_dict[q_id]
            spec = q_meta["specimen_id"]
            acq = q_meta["acquisition_id"]
            dup_grp = q_meta["duplicate_group_id"]
            near_grp = q_meta["near_duplicate_group_id"]
            q_hash = q_meta["sha256"]

            positives: Set[str] = set()
            same_acq_excl: Set[str] = set()
            exact_dup_excl: Set[str] = set()
            near_dup_excl: Set[str] = set()

            for c_id in query_ids:
                if c_id == q_id:
                    continue
                c_meta = meta_dict[c_id]
                o_spec = c_meta["specimen_id"]
                o_acq = c_meta["acquisition_id"]
                o_dup = c_meta["duplicate_group_id"]
                o_near = c_meta["near_duplicate_group_id"]
                o_hash = c_meta["sha256"]

                # Exact duplicate check
                is_exact_dup = False
                if (dup_grp is not None and o_dup is not None and dup_grp == o_dup) or (
                    q_hash is not None and o_hash is not None and q_hash == o_hash
                ):
                    is_exact_dup = True
                    exact_dup_excl.add(c_id)

                # Near duplicate check
                is_near_dup = False
                if near_grp is not None and o_near is not None and near_grp == o_near:
                    is_near_dup = True
                    near_dup_excl.add(c_id)

                # Same acquisition check
                is_same_acq = False
                if o_spec == spec and spec is not None and o_acq == acq and acq is not None:
                    is_same_acq = True
                    same_acq_excl.add(c_id)

                # Valid positive
                if (
                    o_spec == spec
                    and spec is not None
                    and not is_same_acq
                    and not is_exact_dup
                    and not is_near_dup
                ):
                    positives.add(c_id)

            ground_truth[q_id] = positives
            exclusions[q_id] = same_acq_excl | exact_dup_excl | near_dup_excl

        return ground_truth, exclusions

    def build_carinthia_ground_truth(
        self,
        df_emb: pd.DataFrame,
    ) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Dict[str, List[str]]]:
        """Build Carinthia defect-class ground truth and self-exclusion sets."""
        query_ids = df_emb["image_id"].tolist()
        labels = df_emb["label"].tolist()

        label_to_ids: Dict[str, Set[str]] = {}
        class_query_map: Dict[str, List[str]] = {}
        for q_id, lbl in zip(query_ids, labels):
            label_to_ids.setdefault(lbl, set()).add(q_id)
            class_query_map.setdefault(lbl, []).append(q_id)

        ground_truth: Dict[str, Set[str]] = {}
        exclusions: Dict[str, Set[str]] = {}

        for q_id, lbl in zip(query_ids, labels):
            same_class_ids = label_to_ids.get(lbl, set()) - {q_id}
            ground_truth[q_id] = same_class_ids
            exclusions[q_id] = {q_id}

        return ground_truth, exclusions, class_query_map
