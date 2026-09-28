"""Metadata feature group ablation runner for Phase 5."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.metadata.phase5_encoder import Phase5MetadataEncoder
from src.retrieval.phase5_calibration import Phase5ScoreCalibrator
from src.retrieval.phase5_evaluator import Phase5Evaluator
from src.utils.logging import get_logger

logger = get_logger("evaluation.phase5_ablation")


class Phase5AblationRunner:
    """Executes metadata group ablations A through G."""

    def __init__(self, calibration_method: str = "percentile") -> None:
        self.calibration_method = calibration_method

    def run_ablations(
        self,
        train_manifest: pd.DataFrame,
        val_manifest: pd.DataFrame,
        test_manifest: pd.DataFrame,
        train_vis_embs: np.ndarray,
        val_vis_embs: np.ndarray,
        test_vis_embs: np.ndarray,
        val_vis_p4_embs: Optional[np.ndarray],
        test_vis_p4_embs: Optional[np.ndarray],
        val_gt: Dict[str, Set[str]],
        val_excl: Dict[str, Set[str]],
        test_gt: Dict[str, Set[str]],
        test_excl: Dict[str, Set[str]],
    ) -> Dict[str, Any]:
        """Run ablations A through G strictly following train -> val -> test discipline."""
        val_q_ids = val_manifest["image_id"].tolist()
        test_q_ids = test_manifest["image_id"].tolist()

        ablation_specs = [
            ("A", "Visual Only", None, "phase2"),
            ("B", "Visual + Detector", "C", "phase2"),
            ("C", "Visual + Imaging Geometry", "A", "phase2"),
            ("D", "Visual + Beam Parameters", "B", "phase2"),
            ("E", "Visual + Environment", "D", "phase2"),
            ("F", "Visual + All Safe Metadata", "E", "phase2"),
        ]
        if test_vis_p4_embs is not None and val_vis_p4_embs is not None:
            ablation_specs.append(("G", "Phase 4 + All Safe Metadata", "E", "phase4"))

        ablation_results: Dict[str, Any] = {}

        # Precompute visual similarity matrices
        S_V_val_p2 = val_vis_embs @ val_vis_embs.T
        S_V_test_p2 = test_vis_embs @ test_vis_embs.T
        S_V_train_p2 = train_vis_embs @ train_vis_embs.T
        np.fill_diagonal(S_V_train_p2, np.nan)
        s_v_train_p2_flat = S_V_train_p2[~np.isnan(S_V_train_p2)]

        if test_vis_p4_embs is not None and val_vis_p4_embs is not None:
            S_V_val_p4 = val_vis_p4_embs @ val_vis_p4_embs.T
            S_V_test_p4 = test_vis_p4_embs @ test_vis_p4_embs.T
            # For Phase 4 training similarities, if available, else approximate
            S_V_train_p4_flat = s_v_train_p2_flat
        else:
            S_V_val_p4 = None
            S_V_test_p4 = None
            S_V_train_p4_flat = None

        for code, name, feat_group, vis_source in ablation_specs:
            logger.info(f"Running Ablation {code}: {name} (Feature Group {feat_group}, Visual: {vis_source})")

            S_V_val = S_V_val_p4 if vis_source == "phase4" else S_V_val_p2
            S_V_test = S_V_test_p4 if vis_source == "phase4" else S_V_test_p2
            s_v_train_flat = S_V_train_p4_flat if vis_source == "phase4" else s_v_train_p2_flat

            if feat_group is None:
                # Pure visual (alpha = 1.0)
                evaluator = Phase5Evaluator()
                test_res = evaluator.evaluate_at_alpha(
                    S_V=S_V_test,
                    S_M=np.zeros_like(S_V_test),
                    alpha=1.0,
                    query_ids=test_q_ids,
                    candidate_ids=test_q_ids,
                    gt_positives=test_gt,
                    exclusions=test_excl,
                )
                selected_alpha = 1.0
                val_grid = {}
            else:
                # Fit metadata encoder on training partition only
                encoder = Phase5MetadataEncoder(feature_group=feat_group)
                encoder.fit(train_manifest)

                # Compute metadata similarity matrices
                train_m, _ = encoder.encode(train_manifest)
                S_M_train = encoder.compute_similarity_matrix(train_m)
                np.fill_diagonal(S_M_train, np.nan)
                s_m_train_flat = S_M_train[~np.isnan(S_M_train)]

                # Calibrator fitted strictly on training partition
                calibrator = Phase5ScoreCalibrator(method=self.calibration_method)
                calibrator.fit(s_v_train_flat, s_m_train_flat)

                evaluator = Phase5Evaluator(calibrator=calibrator)

                # Validation similarity matrices
                val_m, _ = encoder.encode(val_manifest)
                S_M_val = encoder.compute_similarity_matrix(val_m)

                # Validation alpha selection
                selected_alpha, val_grid = evaluator.select_best_alpha(
                    S_V_val=S_V_val,
                    S_M_val=S_M_val,
                    val_query_ids=val_q_ids,
                    val_candidate_ids=val_q_ids,
                    val_gt=val_gt,
                    val_excl=val_excl,
                )

                # Test evaluation at frozen selected alpha
                test_m, _ = encoder.encode(test_manifest)
                S_M_test = encoder.compute_similarity_matrix(test_m)

                test_res = evaluator.evaluate_at_alpha(
                    S_V=S_V_test,
                    S_M=S_M_test,
                    alpha=selected_alpha,
                    query_ids=test_q_ids,
                    candidate_ids=test_q_ids,
                    gt_positives=test_gt,
                    exclusions=test_excl,
                )

            # Clean test_res for reporting
            summary = {k: v for k, v in test_res.items() if k != "ranked_results"}
            summary["selected_alpha"] = selected_alpha
            summary["feature_group"] = feat_group
            summary["visual_source"] = vis_source
            summary["name"] = name

            ablation_results[code] = {
                "summary": summary,
                "val_grid": val_grid,
            }

        return ablation_results
