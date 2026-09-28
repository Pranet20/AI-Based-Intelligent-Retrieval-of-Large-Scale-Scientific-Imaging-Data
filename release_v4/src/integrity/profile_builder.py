"""
Master Integrity and Novelty Profile Builder.

Coordinates Tracks A through E:
- Exact and near-duplicate cascade & redundancy graph
- Measurable quality degradation indicators & quality risk calibration
- Distributional visual novelty scoring & zero-leakage threshold calibration
- Full provenance and consistency audit
- 2D diagnostic matrices and prioritized human review queue
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd

from src.integrity.duplicate_cascade import DuplicateCascade
from src.integrity.redundancy_graph import RedundancyGraph
from src.integrity.quality_indicators import compute_all_quality_metrics, QualityRiskEvaluator
from src.integrity.novelty_detectors import MultiNoveltyEnsemble, assert_no_leakage_features
from src.integrity.provenance_audit import audit_hcci_metadata, audit_carinthia_metadata
from src.integrity.diagnostic_matrix import assign_diagnostic_quadrants, compute_matrix_summary
from src.integrity.review_queue import build_review_queue, export_review_queue, simulate_review_budgets


class ScientificProfileBuilder:
    """
    Coordinates end-to-end scientific integrity, redundancy, quality, and novelty intelligence.
    """

    def __init__(
        self,
        config: dict,
    ):
        self.config = config
        self.quality_evaluator = QualityRiskEvaluator()
        self.novelty_ensemble = MultiNoveltyEnsemble(
            random_state=config.get("experiment", {}).get("random_seed", 42),
            default_k=config.get("novelty", {}).get("default_k", 5),
        )
        self.cascade = DuplicateCascade(
            phash_threshold=config.get("duplicates", {}).get("phash_hamming_threshold", 6),
            dhash_threshold=config.get("duplicates", {}).get("dhash_hamming_threshold", 6),
            dinov2_cosine_threshold=config.get("duplicates", {}).get("dinov2_cosine_threshold", 0.985),
            adapted_cosine_threshold=config.get("duplicates", {}).get("adapted_cosine_threshold", 0.985),
            min_ssim=config.get("duplicates", {}).get("verification", {}).get("min_ssim", 0.95),
            max_mae=config.get("duplicates", {}).get("verification", {}).get("max_mae", 5.0),
            min_ncc=config.get("duplicates", {}).get("verification", {}).get("min_ncc", 0.98),
        )

    def run_full_pipeline(
        self,
        manifest_df: pd.DataFrame,
        splits: Dict[str, List[str]],
        dinov2_embeddings: np.ndarray,
        adapted_embeddings: Optional[np.ndarray] = None,
        image_id_to_idx: Optional[Dict[str, int]] = None,
        artifacts_dir: str = "artifacts/phase6",
    ) -> Dict[str, Any]:
        """
        Execute full Phase 6 pipeline across dataset.
        """
        image_ids = manifest_df["image_id"].tolist()
        file_paths = manifest_df["file_path"].tolist()
        if image_id_to_idx is None:
            image_id_to_idx = {img_id: i for i, img_id in enumerate(image_ids)}

        train_ids = set(splits.get("train", []))
        val_ids = set(splits.get("val", []))
        test_ids = set(splits.get("test", []))

        # 1. Track D: Provenance Audit
        print("Running Track D: Provenance & Metadata Consistency Audit...")
        provenance_audit = audit_hcci_metadata(manifest_df)

        # 2. Track B: Quality Indicators
        print("Running Track B: Image-Quality Risk Indicators in parallel...")
        from concurrent.futures import ThreadPoolExecutor
        def _get_q(item):
            fp, img_id = item
            q = compute_all_quality_metrics(fp)
            q["image_id"] = img_id
            return q

        with ThreadPoolExecutor(max_workers=8) as ex:
            quality_records = list(ex.map(_get_q, zip(file_paths, image_ids)))
        quality_df = pd.DataFrame(quality_records)

        # Fit quality evaluator strictly on train split
        train_quality_df = quality_df[quality_df["image_id"].isin(train_ids)]
        self.quality_evaluator.fit(train_quality_df)

        risk_scores = []
        for _, row in quality_df.iterrows():
            r = self.quality_evaluator.compute_risk_score(row.to_dict())
            risk_scores.append(r)
        quality_df["quality_risk_score"] = risk_scores

        # 3. Track A: Duplicate Cascade & Redundancy Graph
        print("Running Track A: Duplicate Cascade & Redundancy Graph...")
        duplicate_pairs_df = self.cascade.run_cascade(
            image_ids=image_ids,
            file_paths=file_paths,
            dinov2_embeddings=dinov2_embeddings,
            adapted_embeddings=adapted_embeddings,
            id_to_idx=image_id_to_idx,
        )

        # Build Redundancy Graph
        graph = RedundancyGraph(all_image_ids=image_ids)
        for _, row in duplicate_pairs_df.iterrows():
            if row["match_type"] in ("EXACT_FILE", "EXACT_PIXEL", "NEAR_DUPLICATE"):
                graph.add_relationship(
                    img_id_1=row["image_id_1"],
                    img_id_2=row["image_id_2"],
                    match_type=row["match_type"],
                    metadata=row.to_dict(),
                )

        quality_score_map = dict(zip(quality_df["image_id"], quality_df["laplacian_variance"]))
        redundancy_summary_df = graph.build_summary(quality_scores=quality_score_map)

        # 4. Track C: Distributional Novelty Scoring
        print("Running Track C: Visual Novelty Intelligence...")
        train_indices = [image_id_to_idx[img_id] for img_id in splits.get("train", []) if img_id in image_id_to_idx]
        val_indices = [image_id_to_idx[img_id] for img_id in splits.get("val", []) if img_id in image_id_to_idx]

        train_feats = dinov2_embeddings[train_indices]
        val_feats = dinov2_embeddings[val_indices]

        # Fit solely on train, calibrate solely on val
        self.novelty_ensemble.fit(train_feats)
        self.novelty_ensemble.calibrate(val_feats)

        # Score all images
        novelty_df = self.novelty_ensemble.score_all(dinov2_embeddings)
        novelty_df["image_id"] = image_ids

        # 5. Track E: Master Integration & Diagnostic Matrix
        print("Running Track E: Diagnostic Matrix & Review Queue...")
        merged_df = manifest_df.copy()
        merged_df = merged_df.merge(quality_df, on="image_id", how="left")
        merged_df = merged_df.merge(redundancy_summary_df[["image_id", "cluster_id", "cluster_size", "is_representative", "redundancy_action"]], on="image_id", how="left")
        merged_df = merged_df.merge(novelty_df, on="image_id", how="left")

        # Add split label
        split_labels = []
        for img_id in merged_df["image_id"]:
            if img_id in train_ids:
                split_labels.append("train")
            elif img_id in val_ids:
                split_labels.append("val")
            elif img_id in test_ids:
                split_labels.append("test")
            else:
                split_labels.append("unknown")
        merged_df["split"] = split_labels

        # Assign quadrants
        diag_df = assign_diagnostic_quadrants(
            merged_df,
            novelty_col="composite_novelty_score",
            quality_risk_col="quality_risk_score",
            novelty_threshold=0.5,
            quality_risk_threshold=0.4,
        )
        diag_summary = compute_matrix_summary(diag_df)

        # Build Review Queue
        review_queue_df = build_review_queue(diag_df, top_n=self.config.get("review_queue", {}).get("top_n", 50))
        json_path, csv_path = export_review_queue(review_queue_df, artifacts_dir=artifacts_dir)
        budget_sim = simulate_review_budgets(
            review_queue_df,
            budgets=self.config.get("review_queue", {}).get("budget_eval_levels", [10, 25, 50, 100]),
        )

        return {
            "provenance_audit": provenance_audit,
            "duplicate_pairs_df": duplicate_pairs_df,
            "redundancy_summary_df": redundancy_summary_df,
            "quality_df": quality_df,
            "novelty_df": novelty_df,
            "integrated_profile_df": diag_df,
            "diagnostic_summary": diag_summary,
            "review_queue_df": review_queue_df,
            "review_queue_paths": (str(json_path), str(csv_path)),
            "budget_simulation": budget_sim,
        }
