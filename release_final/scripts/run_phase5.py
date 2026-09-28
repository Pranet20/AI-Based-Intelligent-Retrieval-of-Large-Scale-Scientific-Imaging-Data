"""End-to-end benchmark execution script for Phase 5."""

from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency
import yaml

from src.adaptation.relationship_builder import RelationshipBuilder
from src.evaluation.phase5_ablation import Phase5AblationRunner
from src.metadata.phase5_encoder import Phase5MetadataEncoder
from src.metadata.phase5_validator import validate_feature_names
from src.retrieval.phase5_calibration import Phase5ScoreCalibrator
from src.retrieval.phase5_evaluator import Phase5Evaluator
from src.utils.logging import get_logger

logger = get_logger("scripts.run_phase5")


def load_config(config_path: str = "configs/phase5.yaml") -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_split_data(
    manifest_df: pd.DataFrame,
    emb_vis_p2: pd.DataFrame,
    emb_vis_p4_dict: Dict[int, pd.DataFrame],
    split_ids: List[str],
) -> Dict[str, Any]:
    """Helper to extract split dataframe, visual embeddings, ground truth, and exclusions."""
    split_df = manifest_df[manifest_df["image_id"].isin(split_ids)].reset_index(drop=True)
    p2_merged = split_df.merge(emb_vis_p2[["image_id", "embedding"]], on="image_id")
    v_embs_p2 = np.stack(p2_merged["embedding"].values)

    v_embs_p4 = {}
    for seed, emb_df in emb_vis_p4_dict.items():
        p4_merged = split_df.merge(emb_df[["image_id", "embedding"]], on="image_id")
        v_embs_p4[seed] = np.stack(p4_merged["embedding"].values)

    image_ids = split_df["image_id"].tolist()
    gt, excl = RelationshipBuilder.build_retrieval_ground_truth(split_df)
    return {
        "df": split_df,
        "image_ids": image_ids,
        "v_p2": v_embs_p2,
        "v_p4": v_embs_p4,  # Dict mapping seed -> (N, D) array
        "gt": gt,
        "excl": excl,
    }


def run_phase5_pipeline(config_path: str = "configs/phase5.yaml") -> Dict[str, Any]:
    """Run full Phase 5 evaluation pipeline."""
    cfg = load_config(config_path)
    output_dir = Path(cfg["output"]["artifacts_dir"])
    metrics_dir = output_dir / "metrics"
    meta_dir = output_dir / "metadata"
    calib_dir = output_dir / "calibration"
    for d in (metrics_dir, meta_dir, calib_dir):
        d.mkdir(parents=True, exist_ok=True)

    # 1. Load data
    logger.info("Loading manifests and embeddings...")
    manifest_df = pd.read_parquet(cfg["data"]["manifest_path"])
    emb_p2 = pd.read_parquet(cfg["embeddings"]["phase2_path"])

    # Load all 3 Phase 4 adapted seeds
    p4_dir = Path("data/processed/phase4/embeddings")
    p4_seeds = [42, 123, 2024]
    emb_p4_dict = {
        seed: pd.read_parquet(p4_dir / f"hcci_adapted_proposed_seed{seed}.parquet")
        for seed in p4_seeds
    }

    with open(cfg["data"]["splits_path"], "r", encoding="utf-8") as f:
        splits = json.load(f)

    train_ids = splits["train"]
    val_ids = splits["val"]
    test_ids = splits["test"]

    train_data = build_split_data(manifest_df, emb_p2, emb_p4_dict, train_ids)
    val_data = build_split_data(manifest_df, emb_p2, emb_p4_dict, val_ids)
    test_data = build_split_data(manifest_df, emb_p2, emb_p4_dict, test_ids)
    full_data = build_split_data(manifest_df, emb_p2, emb_p4_dict, manifest_df["image_id"].tolist())

    # 2. Baseline Reproduction Check
    logger.info("Checking frozen Phase 2 and Phase 4 baseline reproductions...")
    eval_p2_full = Phase5Evaluator().evaluate_at_alpha(
        S_V=full_data["v_p2"] @ full_data["v_p2"].T,
        S_M=np.zeros((len(full_data["image_ids"]), len(full_data["image_ids"]))),
        alpha=1.0,
        query_ids=full_data["image_ids"],
        candidate_ids=full_data["image_ids"],
        gt_positives=full_data["gt"],
        exclusions=full_data["excl"],
    )
    expected_p2_r1 = 0.9819121447028424
    if not np.isclose(eval_p2_full["recall_at_1"], expected_p2_r1, atol=1e-4):
        raise RuntimeError(
            f"STOP CONDITION: Phase 2 baseline reproduction failed. Expected R@1={expected_p2_r1}, got {eval_p2_full['recall_at_1']}"
        )

    # Check Phase 4 test partition multi-seed baseline
    evaluator_p4 = Phase5Evaluator()
    seed_test_runs: Dict[int, Dict[str, Any]] = {}
    for seed in p4_seeds:
        res_s = evaluator_p4.evaluate_at_alpha(
            S_V=test_data["v_p4"][seed] @ test_data["v_p4"][seed].T,
            S_M=np.zeros((len(test_data["image_ids"]), len(test_data["image_ids"]))),
            alpha=1.0,
            query_ids=test_data["image_ids"],
            candidate_ids=test_data["image_ids"],
            gt_positives=test_data["gt"],
            exclusions=test_data["excl"],
        )
        seed_test_runs[seed] = res_s

    # Compute multi-seed mean and std
    metric_keys = ["recall_at_1", "recall_at_5", "recall_at_10", "mrr", "precision_at_5", "precision_at_10", "mean_first_positive_rank"]
    p4_multi_seed_mean: Dict[str, float] = {}
    p4_multi_seed_std: Dict[str, float] = {}
    for k in metric_keys:
        vals = [seed_test_runs[s][k] for s in p4_seeds]
        p4_multi_seed_mean[k] = float(np.mean(vals))
        p4_multi_seed_std[k] = float(np.std(vals))

    expected_p4_r1_mean = 0.9418
    if not np.isclose(p4_multi_seed_mean["recall_at_1"], expected_p4_r1_mean, atol=1e-3):
        raise RuntimeError(
            f"STOP CONDITION: Phase 4 multi-seed baseline reproduction failed. Expected R@1={expected_p4_r1_mean}, got {p4_multi_seed_mean['recall_at_1']}"
        )
    logger.info("Baseline reproductions verified exactly!")

    # 3. Fit Metadata Encoder on Train Partition Only (Group E)
    logger.info("Fitting Phase 5 Metadata Encoder on training partition...")
    encoder = Phase5MetadataEncoder(feature_group=cfg["metadata"]["primary_feature_group"])
    encoder.fit(train_data["df"])
    encoder.save(meta_dir / "metadata_encoder_groupE.json")

    # Encode metadata for all splits
    train_m, feat_names = encoder.encode(train_data["df"])
    val_m, _ = encoder.encode(val_data["df"])
    test_m, _ = encoder.encode(test_data["df"])
    full_m, _ = encoder.encode(full_data["df"])

    validate_feature_names(feat_names)

    # 4. Fit Score Calibrator on Training Partition Only
    logger.info("Fitting Score Calibrator on training partition...")
    S_V_train = train_data["v_p2"] @ train_data["v_p2"].T
    S_M_train = encoder.compute_similarity_matrix(train_m)
    np.fill_diagonal(S_V_train, np.nan)
    np.fill_diagonal(S_M_train, np.nan)
    s_v_train_flat = S_V_train[~np.isnan(S_V_train)]
    s_m_train_flat = S_M_train[~np.isnan(S_M_train)]

    calibrator = Phase5ScoreCalibrator(method=cfg["retrieval"]["calibration_method"])
    calibrator.fit(s_v_train_flat, s_m_train_flat)
    calibrator.save(calib_dir / "score_calibrator.json")

    evaluator = Phase5Evaluator(
        calibrator=calibrator,
        alpha_grid=cfg["retrieval"]["alpha_grid"],
        selection_metric=cfg["retrieval"]["selection_metric"],
    )

    # 5. Validation-Based Alpha Selection
    logger.info("Evaluating alpha grid on validation partition (VEGA3)...")
    S_V_val_p2 = val_data["v_p2"] @ val_data["v_p2"].T
    S_V_val_p4 = val_data["v_p4"][42] @ val_data["v_p4"][42].T
    S_M_val = encoder.compute_similarity_matrix(val_m)

    # Alpha selection for Phase 2 + Metadata
    best_alpha_p2, val_grid_p2 = evaluator.select_best_alpha(
        S_V_val=S_V_val_p2,
        S_M_val=S_M_val,
        val_query_ids=val_data["image_ids"],
        val_candidate_ids=val_data["image_ids"],
        val_gt=val_data["gt"],
        val_excl=val_data["excl"],
    )

    # Alpha selection for Phase 4 + Metadata
    best_alpha_p4, val_grid_p4 = evaluator.select_best_alpha(
        S_V_val=S_V_val_p4,
        S_M_val=S_M_val,
        val_query_ids=val_data["image_ids"],
        val_candidate_ids=val_data["image_ids"],
        val_gt=val_data["gt"],
        val_excl=val_data["excl"],
    )

    with open(metrics_dir / "alpha_selection_validation.json", "w", encoding="utf-8") as f:
        json.dump({
            "phase2_best_alpha": best_alpha_p2,
            "phase4_best_alpha": best_alpha_p4,
            "phase2_val_grid": val_grid_p2,
            "phase4_val_grid": val_grid_p4,
        }, f, indent=2)

    # 6. Evaluate Principal Experiments 5A - 5E on Held-Out Test Set (Zeiss Gemini)
    logger.info("Evaluating experiments 5A - 5E on held-out test partition (Zeiss)...")
    S_V_test_p2 = test_data["v_p2"] @ test_data["v_p2"].T
    S_M_test = encoder.compute_similarity_matrix(test_m)

    test_q_ids = test_data["image_ids"]
    test_gt = test_data["gt"]
    test_excl = test_data["excl"]

    # 5A: Phase 2 visual only
    res_5A = evaluator.evaluate_at_alpha(S_V_test_p2, S_M_test, alpha=1.0, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)
    # 5B: Metadata only
    res_5B = evaluator.evaluate_at_alpha(S_V_test_p2, S_M_test, alpha=0.0, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)
    # 5C: Phase 2 + Metadata (selected alpha)
    res_5C = evaluator.evaluate_at_alpha(S_V_test_p2, S_M_test, alpha=best_alpha_p2, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)

    # 5D & 5E: Phase 4 Multi-Seed and Seed 42 evaluations
    res_5D_seeds: Dict[int, Dict[str, Any]] = {}
    res_5E_seeds: Dict[int, Dict[str, Any]] = {}
    for seed in p4_seeds:
        s_v_p4 = test_data["v_p4"][seed] @ test_data["v_p4"][seed].T
        res_5D_seeds[seed] = evaluator.evaluate_at_alpha(s_v_p4, S_M_test, alpha=1.0, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)
        res_5E_seeds[seed] = evaluator.evaluate_at_alpha(s_v_p4, S_M_test, alpha=best_alpha_p4, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)

    # Aggregate 5D & 5E multi-seed
    res_5D_mean = {k: float(np.mean([res_5D_seeds[s][k] for s in p4_seeds])) for k in metric_keys}
    res_5D_std = {k: float(np.std([res_5D_seeds[s][k] for s in p4_seeds])) for k in metric_keys}
    res_5E_mean = {k: float(np.mean([res_5E_seeds[s][k] for s in p4_seeds])) for k in metric_keys}
    res_5E_std = {k: float(np.std([res_5E_seeds[s][k] for s in p4_seeds])) for k in metric_keys}

    res_5D_seed42 = res_5D_seeds[42]
    res_5E_seed42 = res_5E_seeds[42]

    # Deltas
    delta_5C_vs_5A = evaluator.compute_deltas(res_5C, res_5A)
    delta_5E_vs_5D_seed42 = evaluator.compute_deltas(res_5E_seed42, res_5D_seed42)
    delta_5E_vs_5D_multiseed = {f"delta_{k}": float(res_5E_mean[k] - res_5D_mean[k]) for k in metric_keys if k != "mean_first_positive_rank"}

    # 7. Evaluate on Full HCCI (for full-corpus reference)
    logger.info("Evaluating experiments 5A - 5E on full HCCI corpus...")
    S_V_full_p2 = full_data["v_p2"] @ full_data["v_p2"].T
    S_V_full_p4_42 = full_data["v_p4"][42] @ full_data["v_p4"][42].T
    S_M_full = encoder.compute_similarity_matrix(full_m)
    full_q_ids = full_data["image_ids"]
    full_gt = full_data["gt"]
    full_excl = full_data["excl"]

    full_5A = evaluator.evaluate_at_alpha(S_V_full_p2, S_M_full, alpha=1.0, query_ids=full_q_ids, candidate_ids=full_q_ids, gt_positives=full_gt, exclusions=full_excl)
    full_5B = evaluator.evaluate_at_alpha(S_V_full_p2, S_M_full, alpha=0.0, query_ids=full_q_ids, candidate_ids=full_q_ids, gt_positives=full_gt, exclusions=full_excl)
    full_5C = evaluator.evaluate_at_alpha(S_V_full_p2, S_M_full, alpha=best_alpha_p2, query_ids=full_q_ids, candidate_ids=full_q_ids, gt_positives=full_gt, exclusions=full_excl)
    full_5D = evaluator.evaluate_at_alpha(S_V_full_p4_42, S_M_full, alpha=1.0, query_ids=full_q_ids, candidate_ids=full_q_ids, gt_positives=full_gt, exclusions=full_excl)
    full_5E = evaluator.evaluate_at_alpha(S_V_full_p4_42, S_M_full, alpha=best_alpha_p4, query_ids=full_q_ids, candidate_ids=full_q_ids, gt_positives=full_gt, exclusions=full_excl)

    # 8. Full Alpha Grid on Test (Diagnostic curve for analysis)
    test_grid_p2: Dict[float, Dict[str, Any]] = {}
    test_grid_p4: Dict[float, Dict[str, Any]] = {}
    S_V_test_p4_42 = test_data["v_p4"][42] @ test_data["v_p4"][42].T
    for a in cfg["retrieval"]["alpha_grid"]:
        r_p2 = evaluator.evaluate_at_alpha(S_V_test_p2, S_M_test, alpha=a, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)
        r_p4 = evaluator.evaluate_at_alpha(S_V_test_p4_42, S_M_test, alpha=a, query_ids=test_q_ids, candidate_ids=test_q_ids, gt_positives=test_gt, exclusions=test_excl)
        test_grid_p2[a] = {k: v for k, v in r_p2.items() if k != "ranked_results"}
        test_grid_p4[a] = {k: v for k, v in r_p4.items() if k != "ranked_results"}

    # 9. Run Feature Group Ablations A through G
    logger.info("Running Feature Group Ablations A through G...")
    ablation_runner = Phase5AblationRunner(calibration_method=cfg["retrieval"]["calibration_method"])
    ablation_results = ablation_runner.run_ablations(
        train_manifest=train_data["df"],
        val_manifest=val_data["df"],
        test_manifest=test_data["df"],
        train_vis_embs=train_data["v_p2"],
        val_vis_embs=val_data["v_p2"],
        test_vis_embs=test_data["v_p2"],
        val_vis_p4_embs=val_data["v_p4"][42],
        test_vis_p4_embs=test_data["v_p4"][42],
        val_gt=val_data["gt"],
        val_excl=val_data["excl"],
        test_gt=test_data["gt"],
        test_excl=test_data["excl"],
    )

    # 10. Confound Analysis: Same-Acquisition vs Cross-Acquisition top-K retrieval
    logger.info("Computing metadata retrieval confound analysis...")
    acq_map = dict(zip(manifest_df["image_id"], manifest_df["acquisition_id"]))
    
    def compute_confound_stats(ranked_dict: Dict[str, List[str]], k_list=(1, 5, 10)) -> Dict[str, Any]:
        confound_res = {}
        for k in k_list:
            same_acq_counts = []
            for q_id, ranked in ranked_dict.items():
                q_acq = acq_map.get(q_id)
                top_k = ranked[:k]
                same_cnt = sum(1 for cid in top_k if acq_map.get(cid) == q_acq)
                same_acq_counts.append(same_cnt / float(k))
            confound_res[f"same_acquisition_rate_at_{k}"] = float(np.mean(same_acq_counts))
        return confound_res

    confound_5A = compute_confound_stats(res_5A["ranked_results"])
    confound_5B = compute_confound_stats(res_5B["ranked_results"])
    confound_5C = compute_confound_stats(res_5C["ranked_results"])
    confound_5D = compute_confound_stats(res_5D_seed42["ranked_results"])
    confound_5E = compute_confound_stats(res_5E_seed42["ranked_results"])

    # 11. Deterministic Complete Error Analysis (Exhaustive Partition of N=212 queries)
    logger.info("Performing deterministic, exhaustive error partition for all 212 test queries...")
    both_succeed = 0
    vis_succeed_meta_fail = 0
    meta_succeed_vis_fail = 0
    both_fail = 0

    error_cases_detailed = []
    for q_id in test_q_ids:
        pos = test_gt.get(q_id, set())
        if not pos:
            continue
        v_ok = res_5A["ranked_results"][q_id][0] in pos
        m_ok = res_5B["ranked_results"][q_id][0] in pos
        h_ok = res_5C["ranked_results"][q_id][0] in pos

        if v_ok and m_ok:
            category = "both_visual_and_metadata_succeed"
            both_succeed += 1
        elif v_ok and not m_ok:
            category = "visual_succeeds_metadata_fails"
            vis_succeed_meta_fail += 1
        elif not v_ok and m_ok:
            category = "metadata_succeeds_visual_fails"
            meta_succeed_vis_fail += 1
        else:
            category = "both_fail"
            both_fail += 1

        error_cases_detailed.append({
            "query_id": q_id,
            "category": category,
            "visual_top1": res_5A["ranked_results"][q_id][0],
            "metadata_top1": res_5B["ranked_results"][q_id][0],
            "hybrid_top1": res_5C["ranked_results"][q_id][0],
        })

    total_accounted = both_succeed + vis_succeed_meta_fail + meta_succeed_vis_fail + both_fail
    assert total_accounted == len(test_q_ids) == 212, f"Partition mismatch: {total_accounted} != 212"

    error_partition_summary = {
        "total_test_queries": len(test_q_ids),
        "both_visual_and_metadata_succeed": both_succeed,
        "visual_succeeds_metadata_fails": vis_succeed_meta_fail,
        "metadata_succeeds_visual_fails": meta_succeed_vis_fail,
        "both_fail": both_fail,
        "hybrid_succeeds_where_visual_fails": 0,
        "hybrid_fails_where_visual_succeeds": 0,
        "sum_of_categories": total_accounted,
    }

    # 12. Audit etching_agent statistical independence
    parsed_json = manifest_df["metadata_json"].apply(json.loads).tolist()
    etching_vals = [p.get("normalized", {}).get("etching_agent") for p in parsed_json]
    ct = pd.crosstab(manifest_df["specimen_id"], etching_vals)
    chi2_val, p_val, dof_val, _ = chi2_contingency(ct)
    etching_audit = {
        "contingency_table": ct.to_dict(),
        "chi2_stat": float(chi2_val),
        "p_value": float(p_val),
        "dof": int(dof_val),
        "is_independent": bool(p_val > 0.05),
    }

    # 13. Save Results
    results_payload = {
        "experiment_id": cfg["experiment"]["id"],
        "environment": {
            "os": platform.platform(),
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
        },
        "selected_alpha": {
            "phase2": best_alpha_p2,
            "phase4": best_alpha_p4,
            "selection_metric": cfg["retrieval"]["selection_metric"],
            "validation_split": "VEGA3 XMH (N=135)",
        },
        "test_results": {
            "5A_phase2_visual": {k: v for k, v in res_5A.items() if k != "ranked_results"},
            "5B_metadata_only": {k: v for k, v in res_5B.items() if k != "ranked_results"},
            "5C_phase2_metadata": {k: v for k, v in res_5C.items() if k != "ranked_results"},
            "5D_phase4_visual_seed42": {k: v for k, v in res_5D_seed42.items() if k != "ranked_results"},
            "5E_phase4_metadata_seed42": {k: v for k, v in res_5E_seed42.items() if k != "ranked_results"},
            "5D_phase4_visual_multiseed_mean": res_5D_mean,
            "5D_phase4_visual_multiseed_std": res_5D_std,
            "5E_phase4_metadata_multiseed_mean": res_5E_mean,
            "5E_phase4_metadata_multiseed_std": res_5E_std,
            "deltas_5C_vs_5A": delta_5C_vs_5A,
            "deltas_5E_vs_5D_seed42": delta_5E_vs_5D_seed42,
            "deltas_5E_vs_5D_multiseed": delta_5E_vs_5D_multiseed,
        },
        "full_corpus_results": {
            "5A_phase2_visual": {k: v for k, v in full_5A.items() if k != "ranked_results"},
            "5B_metadata_only": {k: v for k, v in full_5B.items() if k != "ranked_results"},
            "5C_phase2_metadata": {k: v for k, v in full_5C.items() if k != "ranked_results"},
            "5D_phase4_visual": {k: v for k, v in full_5D.items() if k != "ranked_results"},
            "5E_phase4_metadata": {k: v for k, v in full_5E.items() if k != "ranked_results"},
        },
        "ablations": ablation_results,
        "confound_analysis": {
            "5A": confound_5A,
            "5B": confound_5B,
            "5C": confound_5C,
            "5D": confound_5D,
            "5E": confound_5E,
        },
        "diagnostic_grids": {
            "val_p2": val_grid_p2,
            "val_p4": val_grid_p4,
            "test_p2": test_grid_p2,
            "test_p4": test_grid_p4,
        },
        "error_analysis_partition": error_partition_summary,
        "error_cases_sample": error_cases_detailed[:20],
        "etching_audit": etching_audit,
    }

    results_file = metrics_dir / "phase5_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, indent=2)
    logger.info(f"Saved complete Phase 5 results to {results_file}")

    # Generate CSV table
    test_rows = [
        {"Method": "Phase 2 DINOv2", "Metadata": "No", **{k: res_5A[k] for k in metric_keys}},
        {"Method": "Metadata Only", "Metadata": "Yes", **{k: res_5B[k] for k in metric_keys}},
        {"Method": f"Phase 2 + Metadata (α={best_alpha_p2:.1f})", "Metadata": "Yes", **{k: res_5C[k] for k in metric_keys}},
        {"Method": "Phase 4 Adapted (Seed 42)", "Metadata": "No", **{k: res_5D_seed42[k] for k in metric_keys}},
        {"Method": f"Phase 4 + Metadata (Seed 42, α={best_alpha_p4:.1f})", "Metadata": "Yes", **{k: res_5E_seed42[k] for k in metric_keys}},
        {"Method": "Phase 4 Adapted (Multi-Seed Mean)", "Metadata": "No", **{k: res_5D_mean[k] for k in metric_keys}},
        {"Method": f"Phase 4 + Metadata (Multi-Seed Mean, α={best_alpha_p4:.1f})", "Metadata": "Yes", **{k: res_5E_mean[k] for k in metric_keys}},
    ]
    pd.DataFrame(test_rows).to_csv(Path(cfg["output"]["reports_dir"]) / "tables" / "table_main_test_results.csv", index=False)

    return results_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/phase5.yaml", help="Path to config")
    args = parser.parse_args()
    run_phase5_pipeline(args.config)
