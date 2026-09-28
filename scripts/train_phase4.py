"""Training script for Phase 4 representation adaptation across multiple seeds and ablations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import pandas as pd
import torch
import yaml

from src.adaptation.checkpointing import CheckpointManager
from src.adaptation.phase4_model import Phase4AdaptedModel
from src.adaptation.projection_head import ProjectionHead
from src.adaptation.split_builder import SplitBuilder
from src.adaptation.trainer import EmbeddingDataset, Phase4Trainer
from src.utils.logging import get_logger

logger = get_logger("scripts.train_phase4")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Phase 4 representation adaptation.")
    parser.add_argument("--config", type=str, default="configs/phase4.yaml", help="Path to config YAML.")
    parser.add_argument("--seed", type=int, default=None, help="Optional single seed override.")
    parser.add_argument("--run-all-seeds", action="store_true", help="Run seeds 42, 123, 2024.")
    parser.add_argument("--run-ablations", action="store_true", help="Run ablation configurations.")
    return parser.parse_args()


def load_data(cfg: Dict[str, Any]) -> Tuple[pd.DataFrame, np.ndarray, Dict[str, List[str]]]:
    manifest_path = cfg["data"]["hcci_manifest"]
    emb_path = cfg["data"]["hcci_embeddings"]
    splits_dir = cfg["data"]["splits_dir"]

    sb = SplitBuilder(hcci_manifest_path=manifest_path, output_dir=splits_dir)
    df = sb.load_data()
    splits = sb.build_instrument_split(df)
    sb.save_splits(splits)

    # Load frozen Phase 2 embeddings
    df_emb = pd.read_parquet(emb_path)
    vectors = np.vstack(df_emb["embedding"].to_numpy()).astype(np.float32)

    return df, vectors, splits


def train_single_run(
    cfg: Dict[str, Any],
    df: pd.DataFrame,
    vectors: np.ndarray,
    splits: Dict[str, List[str]],
    seed: int,
    run_name: str = "proposed",
    head_type: str = "mlp",
    mask_same_acquisition: bool = True,
) -> Dict[str, Any]:
    """Train a single configuration under a specified seed."""
    logger.info("==================================================")
    logger.info("Executing Phase 4 training: %s (Seed %d)", run_name, seed)
    logger.info("==================================================")

    id_to_idx = {r["image_id"]: idx for idx, r in df.iterrows()}

    # Map material categories and acquisition conditions to integer IDs
    mat_map = {m: i for i, m in enumerate(sorted(df["specimen_id"].unique()))}
    acq_map = {a: i for i, a in enumerate(sorted(df["acquisition_id"].unique()))}

    df["mat_int"] = df["specimen_id"].map(mat_map)
    df["acq_int"] = df["acquisition_id"].map(acq_map)

    # Extract Train indices and arrays
    train_indices = [id_to_idx[img_id] for img_id in splits["train"]]
    val_indices = [id_to_idx[img_id] for img_id in splits["val"]]

    train_vecs = vectors[train_indices]
    train_mats = df.loc[train_indices, "mat_int"].to_numpy()
    train_acqs = df.loc[train_indices, "acq_int"].to_numpy()
    train_ids = splits["train"]

    val_vecs = vectors[val_indices]
    val_df = df.iloc[val_indices].reset_index(drop=True)

    train_ds = EmbeddingDataset(
        embeddings=train_vecs,
        material_ids=train_mats,
        acquisition_ids=train_acqs,
        image_ids=train_ids,
    )

    # Update config copy for this run
    run_cfg = json.loads(json.dumps(cfg))
    run_cfg["model"]["head_type"] = head_type
    run_cfg["loss"]["mask_same_acquisition"] = mask_same_acquisition
    run_cfg["training"]["seed"] = seed

    trainer = Phase4Trainer(config=run_cfg)
    # Customize checkpoint manager filename
    trainer.chk_manager.checkpoints_dir = Path(cfg["data"]["checkpoints_dir"])

    res = trainer.fit(
        train_dataset=train_ds,
        val_embeddings=val_vecs,
        val_df=val_df,
        seed=seed,
    )

    # Save adapted embeddings across entire HCCI corpus
    head = trainer.head
    head.eval()
    with torch.no_grad():
        all_t = torch.tensor(vectors, dtype=torch.float32, device=trainer.device)
        adapted_vecs = head(all_t).cpu().numpy()

    # Construct split labels for full dataframe
    split_col = []
    set_train = set(splits["train"])
    set_val = set(splits["val"])
    for img_id in df["image_id"]:
        if img_id in set_train:
            split_col.append("train")
        elif img_id in set_val:
            split_col.append("val")
        else:
            split_col.append("test")

    out_emb_dir = Path(cfg["data"]["embeddings_dir"])
    out_emb_dir.mkdir(parents=True, exist_ok=True)
    out_emb_path = out_emb_dir / f"hcci_adapted_{run_name}_seed{seed}.parquet"

    df_out = pd.DataFrame({
        "image_id": df["image_id"],
        "dataset": df["dataset_id"],
        "split": split_col,
        "specimen_id": df["specimen_id"],
        "acquisition_id": df["acquisition_id"],
        "embedding": [v for v in adapted_vecs],
        "model_version": f"dinov2_vits14_adapted_{run_name}",
        "seed": seed,
    })
    df_out.to_parquet(out_emb_path, index=False)
    logger.info("Saved adapted embeddings to %s (Shape: %d x %d)", out_emb_path, len(df_out), len(adapted_vecs[0]))

    return {
        "run_name": run_name,
        "seed": seed,
        "best_epoch": res["best_epoch"],
        "best_val_metric": res["best_validation_metric"],
        "checkpoint_path": res["best_checkpoint_path"],
        "embeddings_path": str(out_emb_path),
    }


def main() -> None:
    args = parse_args()
    with open(args.config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    df, vectors, splits = load_data(cfg)

    seeds = [args.seed] if args.seed is not None else ([42, 123, 2024] if args.run_all_seeds else [42])

    results: List[Dict[str, Any]] = []

    # 1. Proposed Model (Acquisition-Aware SupCon + MLP head)
    for s in seeds:
        res = train_single_run(
            cfg=cfg,
            df=df,
            vectors=vectors,
            splits=splits,
            seed=s,
            run_name="proposed",
            head_type="mlp",
            mask_same_acquisition=True,
        )
        results.append(res)

    # 2. Ablations (if requested)
    if args.run_ablations:
        # Ablation B: Standard SupCon without acquisition masking (seed 42)
        res_ab_b = train_single_run(
            cfg=cfg,
            df=df,
            vectors=vectors,
            splits=splits,
            seed=42,
            run_name="ablation_standard_supcon",
            head_type="mlp",
            mask_same_acquisition=False,
        )
        results.append(res_ab_b)

        # Ablation D: Linear projection head (seed 42)
        res_ab_d = train_single_run(
            cfg=cfg,
            df=df,
            vectors=vectors,
            splits=splits,
            seed=42,
            run_name="ablation_linear_head",
            head_type="linear",
            mask_same_acquisition=True,
        )
        results.append(res_ab_d)

    summary_path = Path(cfg["data"]["output_dir"]) / "training_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    logger.info("Phase 4 training complete. Summary saved to %s", summary_path)


if __name__ == "__main__":
    main()
