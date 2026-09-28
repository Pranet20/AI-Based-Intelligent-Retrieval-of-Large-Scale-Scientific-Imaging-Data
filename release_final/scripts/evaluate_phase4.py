"""Evaluation script comparing Phase 4 models against Phase 2 baseline across splits and probes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd
import yaml

from src.adaptation.relationship_builder import RelationshipBuilder
from src.adaptation.split_builder import SplitBuilder
from src.evaluation.acquisition_metrics import AcquisitionMetricsCalculator
from src.evaluation.phase4_evaluator import Phase4RetrievalEvaluator
from src.evaluation.probe_metrics import ProbeEvaluator
from src.utils.logging import get_logger

logger = get_logger("scripts.evaluate_phase4")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate Phase 4 representations.")
    parser.add_argument("--config", type=str, default="configs/phase4.yaml", help="Path to config YAML.")
    return parser.parse_args()


def load_dataset_metadata(manifest_path: str | Path, splits_path: str | Path) -> Tuple[pd.DataFrame, Dict[str, List[str]]]:
    df = pd.read_parquet(manifest_path)
    with open(splits_path, "r", encoding="utf-8") as f:
        splits = json.load(f)

    # Extract instrument from metadata_json
    sems = []
    for meta_str in df["metadata_json"]:
        try:
            data = json.loads(meta_str)
            sem = data.get("raw_metadata", {}).get("SEM") or data.get("normalized", {}).get("microscope")
            sems.append(sem)
        except Exception:
            sems.append("Unknown")
    df["SEM"] = sems
    return df, splits


def evaluate_representation(
    name: str,
    vectors: np.ndarray,
    df: pd.DataFrame,
    splits: Dict[str, List[str]],
    evaluator: Phase4RetrievalEvaluator,
) -> Dict[str, Any]:
    """Run full suite of retrieval, geometry, and probe metrics on a given representation."""
    logger.info("Evaluating representation: %s", name)

    # 1. Full HCCI Retrieval Benchmark (N=774)
    image_ids = df["image_id"].tolist()
    gt_full, excl_full = RelationshipBuilder.build_retrieval_ground_truth(df)
    full_retrieval = evaluator.evaluate_retrieval(
        embeddings=vectors,
        image_ids=image_ids,
        ground_truth_positives=gt_full,
        exclusion_sets=excl_full,
    )

    # 2. Held-Out Test Set Retrieval Benchmark (Zeiss Gemini, N=212)
    id_to_idx = {r["image_id"]: idx for idx, r in df.iterrows()}
    test_indices = [id_to_idx[img_id] for img_id in splits["test"]]
    test_df = df.iloc[test_indices].reset_index(drop=True)
    test_vecs = vectors[test_indices]
    test_ids = splits["test"]

    gt_test, excl_test = RelationshipBuilder.build_retrieval_ground_truth(test_df)
    test_retrieval = evaluator.evaluate_retrieval(
        embeddings=test_vecs,
        image_ids=test_ids,
        ground_truth_positives=gt_test,
        exclusion_sets=excl_test,
    )

    # 3. Acquisition Robustness & Cosine Geometry Metrics (on full corpus)
    geo_metrics = AcquisitionMetricsCalculator.compute_similarity_metrics(
        embeddings=vectors,
        material_labels=df["specimen_id"].to_numpy(),
        acquisition_labels=df["acquisition_id"].to_numpy(),
    )

    # 4. Classifier Probes (Instrument Domain vs Material Identity)
    probe_metrics = ProbeEvaluator.evaluate_probes(
        embeddings=vectors,
        material_labels=df["specimen_id"].to_numpy(),
        instrument_labels=df["SEM"].to_numpy(),
        n_splits=5,
        random_state=42,
    )

    return {
        "model_name": name,
        "full_retrieval": full_retrieval,
        "test_retrieval": test_retrieval,
        "geometry": geo_metrics,
        "probes": probe_metrics,
    }


def main() -> None:
    args = parse_args()
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    manifest_path = cfg["data"]["hcci_manifest"]
    splits_path = Path(cfg["data"]["splits_dir"]) / "hcci_instrument_splits.json"
    df, splits = load_dataset_metadata(manifest_path, splits_path)

    evaluator = Phase4RetrievalEvaluator(
        k_values=tuple(cfg["evaluation"]["k_values"]),
        eval_depth=cfg["evaluation"]["eval_depth"],
    )

    all_results: Dict[str, Any] = {}

    # 1. Baseline A: Frozen Phase 2 DINOv2
    p2_emb_path = cfg["data"]["hcci_embeddings"]
    df_p2 = pd.read_parquet(p2_emb_path)
    p2_vectors = np.vstack(df_p2["embedding"].to_numpy()).astype(np.float32)
    all_results["baseline_dinov2_frozen"] = evaluate_representation(
        name="Baseline A: Frozen Phase 2 DINOv2",
        vectors=p2_vectors,
        df=df,
        splits=splits,
        evaluator=evaluator,
    )

    # 2. Proposed Phase 4 Models (Multi-Seed: 42, 123, 2024)
    emb_dir = Path(cfg["data"]["embeddings_dir"])
    seeds = cfg["training"]["seeds"]
    proposed_runs: List[Dict[str, Any]] = []

    for s in seeds:
        emb_file = emb_dir / f"hcci_adapted_proposed_seed{s}.parquet"
        if emb_file.is_file():
            df_s = pd.read_parquet(emb_file)
            vecs_s = np.vstack(df_s["embedding"].to_numpy()).astype(np.float32)
            res_s = evaluate_representation(
                name=f"Proposed Phase 4 (Seed {s})",
                vectors=vecs_s,
                df=df,
                splits=splits,
                evaluator=evaluator,
            )
            all_results[f"proposed_seed{s}"] = res_s
            proposed_runs.append(res_s)

    # Compute Multi-seed mean and std for Proposed
    if proposed_runs:
        multi_seed_stats: Dict[str, Any] = {"full_retrieval": {}, "test_retrieval": {}, "geometry": {}, "probes": {}}
        for domain in ["full_retrieval", "test_retrieval", "geometry", "probes"]:
            keys = [k for k in proposed_runs[0][domain].keys() if isinstance(proposed_runs[0][domain][k], (int, float))]
            for k in keys:
                vals = [r[domain][k] for r in proposed_runs]
                multi_seed_stats[domain][f"{k}_mean"] = float(np.mean(vals))
                multi_seed_stats[domain][f"{k}_std"] = float(np.std(vals))
        all_results["proposed_multi_seed_stats"] = multi_seed_stats

    # 3. Ablations
    for ab_name in ["ablation_standard_supcon_seed42", "ablation_linear_head_seed42"]:
        emb_file = emb_dir / f"hcci_adapted_{ab_name}.parquet"
        if emb_file.is_file():
            df_ab = pd.read_parquet(emb_file)
            vecs_ab = np.vstack(df_ab["embedding"].to_numpy()).astype(np.float32)
            all_results[ab_name] = evaluate_representation(
                name=ab_name,
                vectors=vecs_ab,
                df=df,
                splits=splits,
                evaluator=evaluator,
            )

    # Save complete evaluation JSON
    metrics_dir = Path(cfg["data"]["metrics_dir"])
    metrics_dir.mkdir(parents=True, exist_ok=True)
    out_metrics_path = metrics_dir / "phase4_evaluation_results.json"
    with open(out_metrics_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    logger.info("Evaluation complete. Results saved to %s", out_metrics_path)


if __name__ == "__main__":
    main()
