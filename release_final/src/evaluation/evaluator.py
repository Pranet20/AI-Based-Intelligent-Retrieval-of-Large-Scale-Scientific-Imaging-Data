"""Phase 2 zero-shot retrieval benchmark evaluator for HCCI and Carinthia."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import numpy as np
import pandas as pd

import json

from src.evaluation.retrieval_metrics import (
    RetrievalMetricsCalculator,
    compute_cosine_similarity_matrix,
)
from src.utils.logging import get_logger

logger = get_logger("evaluation.evaluator")


class Phase2Evaluator:
    """Executes zero-shot retrieval benchmarks with strict anti-leakage controls."""

    def __init__(
        self,
        tables_dir: str | Path = "reports/phase2/tables",
        reports_dir: str | Path = "reports/phase2",
    ) -> None:
        self.tables_dir = Path(tables_dir)
        self.tables_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_hcci(
        self,
        hcci_embeddings_path: str | Path,
        manifest_path: str | Path | None = "data/manifests/hcci_manifest.parquet",
    ) -> Dict[str, Any]:
        """Evaluate HCCI cross-condition retrieval with strict anti-leakage controls.

        Strict anti-leakage controls:
        - Query image itself is NEVER in candidate pool.
        - Identical acquisition condition matches of same ROI/specimen are strictly excluded.
        - Exact-duplicate matches (same duplicate_group_id or sha256) are strictly excluded.
        - Near-duplicate matches (same near_duplicate_group_id) are strictly excluded.
        - Ground truth positives require same specimen_id under differing acquisition conditions.
        - Different specimen_ids are true negative candidates.
        """
        df = pd.read_parquet(hcci_embeddings_path)
        logger.info("Evaluating HCCI zero-shot retrieval across %d embeddings...", len(df))

        # Check for manifest metadata if available
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

        query_ids = df["image_id"].tolist()
        matrix = np.vstack(df["embedding"].to_numpy()).astype(np.float32)

        # Build meta dictionary for fast lookup
        meta_dict: Dict[str, Dict[str, Any]] = {}
        for _, row in df.iterrows():
            q_id = row["image_id"]
            man_info = manifest_meta.get(q_id, {})
            meta_dict[q_id] = {
                "specimen_id": row.get("specimen_id") or man_info.get("specimen_id"),
                "roi_id": row.get("roi_id") or man_info.get("roi_id"),
                "acquisition_id": row.get("acquisition_id") or man_info.get("acquisition_id"),
                "duplicate_group_id": man_info.get("duplicate_group_id"),
                "near_duplicate_group_id": man_info.get("near_duplicate_group_id"),
                "sha256": row.get("source_sha256") or man_info.get("sha256"),
            }

        # Build ground-truth positives and exclusion mappings
        ground_truth: Dict[str, Set[str]] = {}
        exclusions: Dict[str, Set[str]] = {}
        query_audit_records: List[Dict[str, Any]] = []

        # Vectorized cosine similarity matrix
        sim_mat = compute_cosine_similarity_matrix(matrix, matrix)

        for i, q_id in enumerate(query_ids):
            q_meta = meta_dict[q_id]
            spec = q_meta["specimen_id"]
            roi = q_meta["roi_id"]
            acq = q_meta["acquisition_id"]
            dup_grp = q_meta["duplicate_group_id"]
            near_grp = q_meta["near_duplicate_group_id"]
            q_hash = q_meta["sha256"]

            positives: Set[str] = set()
            same_acq_excl: Set[str] = set()
            exact_dup_excl: Set[str] = set()
            near_dup_excl: Set[str] = set()

            for j, c_id in enumerate(query_ids):
                if c_id == q_id:
                    continue
                c_meta = meta_dict[c_id]
                o_spec = c_meta["specimen_id"]
                o_acq = c_meta["acquisition_id"]
                o_dup = c_meta["duplicate_group_id"]
                o_near = c_meta["near_duplicate_group_id"]
                o_hash = c_meta["sha256"]

                # 1. Exact duplicate check
                is_exact_dup = False
                if (dup_grp is not None and o_dup is not None and dup_grp == o_dup) or (
                    q_hash is not None and o_hash is not None and q_hash == o_hash
                ):
                    is_exact_dup = True
                    exact_dup_excl.add(c_id)

                # 2. Near duplicate check
                is_near_dup = False
                if near_grp is not None and o_near is not None and near_grp == o_near:
                    is_near_dup = True
                    near_dup_excl.add(c_id)

                # 3. Same acquisition condition of same ROI/specimen check
                is_same_acq = False
                if o_spec == spec and spec is not None and o_acq == acq and acq is not None:
                    is_same_acq = True
                    same_acq_excl.add(c_id)

                # 4. Valid positive: same specimen, different acquisition condition, no duplicates
                if (
                    o_spec == spec
                    and spec is not None
                    and not is_same_acq
                    and not is_exact_dup
                    and not is_near_dup
                ):
                    positives.add(c_id)

            total_exclusions = {q_id} | same_acq_excl | exact_dup_excl | near_dup_excl
            ground_truth[q_id] = positives
            exclusions[q_id] = total_exclusions

            # Query-level ranks within valid candidate pool
            cand_pool_size = len(query_ids) - len(total_exclusions)
            scores = sim_mat[i].copy()
            valid_cand_indices = [idx for idx, cid in enumerate(query_ids) if cid not in total_exclusions]
            sorted_indices = sorted(valid_cand_indices, key=lambda idx: scores[idx], reverse=True)
            ranked_cids = [query_ids[idx] for idx in sorted_indices]
            pos_ranks = [r + 1 for r, cid in enumerate(ranked_cids) if cid in positives]
            first_rank = pos_ranks[0] if pos_ranks else None

            query_audit_records.append({
                "query_id": q_id,
                "specimen_id": spec,
                "ROI_id": roi,
                "acquisition_id": acq,
                "valid_positive_count": len(positives),
                "same_acquisition_exclusion_count": len(same_acq_excl),
                "exact_duplicate_exclusion_count": len(exact_dup_excl),
                "near_duplicate_exclusion_count": len(near_dup_excl),
                "candidate_pool_size": cand_pool_size,
                "first_positive_rank": first_rank,
                "all_positive_ranks": json.dumps(pos_ranks),
            })

        # Save query-level audit CSV
        df_audit = pd.DataFrame(query_audit_records)
        query_audit_path = self.reports_dir / "hcci_query_audit.csv"
        df_audit.to_csv(query_audit_path, index=False)
        logger.info("Saved HCCI query audit to %s", query_audit_path)

        # Aggregate distributions for HCCI evaluation audit JSON
        eval_first_ranks = [r["first_positive_rank"] for r in query_audit_records if r["first_positive_rank"] is not None]
        val_pos_counts = [r["valid_positive_count"] for r in query_audit_records]

        audit_json = {
            "total_queries": len(query_ids),
            "evaluated_queries": len(eval_first_ranks),
            "zero_positive_queries": len(query_ids) - len(eval_first_ranks),
            "distribution_of_valid_positive_count": {
                "min": int(np.min(val_pos_counts)),
                "max": int(np.max(val_pos_counts)),
                "mean": float(np.mean(val_pos_counts)),
                "median": float(np.median(val_pos_counts)),
            },
            "distribution_of_first_positive_rank": {
                "min": int(np.min(eval_first_ranks)) if eval_first_ranks else None,
                "max": int(np.max(eval_first_ranks)) if eval_first_ranks else None,
                "mean": float(np.mean(eval_first_ranks)) if eval_first_ranks else None,
                "median": float(np.median(eval_first_ranks)) if eval_first_ranks else None,
            },
            "percentage_of_queries_where_first_positive_rank_is_1": float(np.mean([1.0 if r == 1 else 0.0 for r in eval_first_ranks])) * 100.0 if eval_first_ranks else 0.0,
            "percentage_of_queries_where_first_positive_rank_le_5": float(np.mean([1.0 if r <= 5 else 0.0 for r in eval_first_ranks])) * 100.0 if eval_first_ranks else 0.0,
            "percentage_of_queries_where_first_positive_rank_le_10": float(np.mean([1.0 if r <= 10 else 0.0 for r in eval_first_ranks])) * 100.0 if eval_first_ranks else 0.0,
        }
        audit_json_path = self.reports_dir / "hcci_evaluation_audit.json"
        with open(audit_json_path, "w", encoding="utf-8") as f:
            json.dump(audit_json, f, indent=2)
        logger.info("Saved HCCI evaluation audit JSON to %s", audit_json_path)

        eval_res = RetrievalMetricsCalculator.evaluate_retrieval(
            similarity_matrix=sim_mat,
            query_ids=query_ids,
            candidate_ids=query_ids,
            ground_truth_positives=ground_truth,
            exclusion_sets=exclusions,
            k_values=(1, 5, 10),
        )

        summary = eval_res["summary"]
        summary["dataset"] = "hcci"
        summary["protocol"] = "condition_invariance_same_specimen"

        # Save table
        df_summary = pd.DataFrame([summary])
        table_path = self.tables_dir / "retrieval_hcci.csv"
        df_summary.to_csv(table_path, index=False)
        logger.info("Saved HCCI retrieval evaluation table to %s", table_path)

        eval_res["audit"] = audit_json
        return eval_res

    def evaluate_carinthia(self, carinthia_embeddings_path: str | Path) -> Dict[str, Any]:
        """Evaluate Carinthia defect-class retrieval benchmark.

        Protocol:
        - POSITIVE = same defect class
        - NEGATIVE = different defect class
        - QUERY = one image
        - SELF = excluded
        Labels are used strictly for post-extraction evaluation (no model leakage).
        """
        df = pd.read_parquet(carinthia_embeddings_path)
        logger.info("Evaluating Carinthia defect retrieval across %d embeddings...", len(df))

        query_ids = df["image_id"].tolist()
        matrix = np.vstack(df["embedding"].to_numpy()).astype(np.float32)
        labels = df["label"].tolist()

        label_to_ids: Dict[str, Set[str]] = {}
        for q_id, lbl in zip(query_ids, labels):
            label_to_ids.setdefault(lbl, set()).add(q_id)

        ground_truth: Dict[str, Set[str]] = {}
        exclusions: Dict[str, Set[str]] = {}

        for q_id, lbl in zip(query_ids, labels):
            same_class_ids = label_to_ids.get(lbl, set()) - {q_id}
            ground_truth[q_id] = same_class_ids
            exclusions[q_id] = {q_id}

        # Vectorized similarity matrix
        sim_mat = compute_cosine_similarity_matrix(matrix, matrix)

        eval_res = RetrievalMetricsCalculator.evaluate_retrieval(
            similarity_matrix=sim_mat,
            query_ids=query_ids,
            candidate_ids=query_ids,
            ground_truth_positives=ground_truth,
            exclusion_sets=exclusions,
            k_values=(1, 5, 10),
        )

        summary = eval_res["summary"]
        summary["dataset"] = "carinthia"
        summary["protocol"] = "defect_class_retrieval"

        # Class-wise breakdowns
        class_rows = []
        class_wise_pos_counts: Dict[str, int] = {}
        class_wise_r1: Dict[str, float] = {}
        class_wise_r5: Dict[str, float] = {}
        class_wise_r10: Dict[str, float] = {}
        class_wise_mrr: Dict[str, float] = {}

        for lbl in sorted(label_to_ids.keys()):
            class_query_ids = [q for q in label_to_ids[lbl]]
            class_q_indices = [query_ids.index(q) for q in class_query_ids]
            sub_sim_mat = sim_mat[class_q_indices]

            sub_eval = RetrievalMetricsCalculator.evaluate_retrieval(
                similarity_matrix=sub_sim_mat,
                query_ids=class_query_ids,
                candidate_ids=query_ids,
                ground_truth_positives={q: ground_truth[q] for q in class_query_ids},
                exclusion_sets={q: exclusions[q] for q in class_query_ids},
                k_values=(1, 5, 10),
            )
            c_sum = sub_eval["summary"]
            c_sum["class_name"] = lbl
            c_sum["sample_count"] = len(class_query_ids)
            class_rows.append(c_sum)

            class_wise_pos_counts[lbl] = len(class_query_ids) - 1
            class_wise_r1[lbl] = c_sum["recall_at_1"]
            class_wise_r5[lbl] = c_sum["recall_at_5"]
            class_wise_r10[lbl] = c_sum["recall_at_10"]
            class_wise_mrr[lbl] = c_sum["mrr"]

        df_classes = pd.DataFrame(class_rows)
        table_path = self.tables_dir / "retrieval_carinthia.csv"
        df_classes.to_csv(table_path, index=False)
        logger.info("Saved Carinthia retrieval evaluation table to %s", table_path)

        # Generate carinthia_evaluation_audit.json
        carinthia_audit = {
            "benchmark_description": "Carinthia defect-class retrieval benchmark evaluating label-based retrieval, NOT universal semantic understanding.",
            "total_queries": len(query_ids),
            "evaluated_queries": summary["evaluated_queries"],
            "zero_positive_queries": summary["no_valid_positive_queries"],
            "class_wise_positive_counts": class_wise_pos_counts,
            "class_wise_recall_at_1": class_wise_r1,
            "class_wise_recall_at_5": class_wise_r5,
            "class_wise_recall_at_10": class_wise_r10,
            "class_wise_mrr": class_wise_mrr,
            "overall_recall_at_1": summary["recall_at_1"],
            "overall_recall_at_5": summary["recall_at_5"],
            "overall_recall_at_10": summary["recall_at_10"],
            "overall_mrr": summary["mrr"],
            "macro_recall_at_1": float(np.mean(list(class_wise_r1.values()))),
            "macro_recall_at_5": float(np.mean(list(class_wise_r5.values()))),
            "macro_recall_at_10": float(np.mean(list(class_wise_r10.values()))),
            "macro_mrr": float(np.mean(list(class_wise_mrr.values()))),
        }
        carinthia_audit_path = self.reports_dir / "carinthia_evaluation_audit.json"
        with open(carinthia_audit_path, "w", encoding="utf-8") as f:
            json.dump(carinthia_audit, f, indent=2)
        logger.info("Saved Carinthia evaluation audit JSON to %s", carinthia_audit_path)

        eval_res["class_breakdown"] = class_rows
        eval_res["audit"] = carinthia_audit
        return eval_res

    def generate_all_summary_tables(
        self,
        hcci_eval: Dict[str, Any],
        carinthia_eval: Dict[str, Any],
        hcci_validation: Dict[str, Any],
        carinthia_validation: Dict[str, Any],
        runtime_stats: List[Dict[str, Any]],
    ) -> None:
        """Export comprehensive paper-ready tables into reports/phase2/tables/."""
        # 1. Dataset Summary Table
        ds_summary = [
            {
                "dataset_id": "hcci",
                "name": "High-Chromium Cast Iron SEM",
                "modality": "SEM",
                "domain": "Metallurgy / Wear-resistant cast iron",
                "physical_images": 774,
                "missing_upstream_records": "10, 20, 30",
                "evaluated_queries": hcci_eval["summary"]["evaluated_queries"],
                "evaluation_task": "Cross-acquisition condition invariance (same ROI/specimen)",
            },
            {
                "dataset_id": "carinthia",
                "name": "Carinthia SEM Dataset",
                "modality": "SEM",
                "domain": "Semiconductor defect inspection",
                "physical_images": 4591,
                "missing_upstream_records": "None",
                "evaluated_queries": carinthia_eval["summary"]["evaluated_queries"],
                "evaluation_task": "Defect classification retrieval across 6 defect classes",
            },
        ]
        pd.DataFrame(ds_summary).to_csv(self.tables_dir / "dataset_summary.csv", index=False)

        # 2. Embedding Summary Table
        emb_summary = [
            {
                "dataset": hcci_validation["dataset"],
                "embedding_dimension": hcci_validation["embedding_dimension"],
                "valid_count": hcci_validation["successful_count"],
                "nan_count": hcci_validation["nan_count"],
                "inf_count": hcci_validation["inf_count"],
                "mean_norm": hcci_validation["mean_norm"],
                "std_norm": hcci_validation["std_norm"],
                "validation_status": hcci_validation["validation_status"],
            },
            {
                "dataset": carinthia_validation["dataset"],
                "embedding_dimension": carinthia_validation["embedding_dimension"],
                "valid_count": carinthia_validation["successful_count"],
                "nan_count": carinthia_validation["nan_count"],
                "inf_count": carinthia_validation["inf_count"],
                "mean_norm": carinthia_validation["mean_norm"],
                "std_norm": carinthia_validation["std_norm"],
                "validation_status": carinthia_validation["validation_status"],
            },
        ]
        pd.DataFrame(emb_summary).to_csv(self.tables_dir / "embedding_summary.csv", index=False)

        # 3. Runtime Summary Table
        pd.DataFrame(runtime_stats).to_csv(self.tables_dir / "runtime_summary.csv", index=False)
        logger.info("Exported all summary tables to %s", self.tables_dir)
