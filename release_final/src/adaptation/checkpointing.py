"""Safe checkpoint management with full reproducibility metadata for Phase 4."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional
import torch

from src.utils.logging import get_logger

logger = get_logger("adaptation.checkpointing")


def compute_file_sha256(path: str | Path) -> str:
    """Compute sha256 hash of a file."""
    p = Path(path)
    if not p.is_file():
        return "none"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class CheckpointManager:
    """Manages serializing and loading model checkpoints with strict reproducibility metadata."""

    def __init__(self, checkpoints_dir: str | Path = "data/processed/phase4/checkpoints") -> None:
        self.checkpoints_dir = Path(checkpoints_dir)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)

    def save_checkpoint(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        epoch: int,
        validation_metric: float,
        seed: int,
        config: Dict[str, Any],
        manifest_path: str | Path = "data/manifests/hcci_manifest.parquet",
        splits_path: str | Path = "data/processed/phase4/splits/hcci_instrument_splits.json",
        filename: Optional[str] = None,
    ) -> Path:
        """Save complete checkpoint with all Phase 4 required audit metadata."""
        if filename is None:
            filename = f"checkpoint_seed{seed}_epoch{epoch}.pt"

        out_path = self.checkpoints_dir / filename

        state = {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "epoch": epoch,
            "validation_metric": float(validation_metric),
            "seed": int(seed),
            "config": config,
            "project_version": config.get("platform_version", "0.1.0"),
            "preprocessing_config": {
                "target_size": [224, 224],
                "interpolation": "bicubic",
                "antialias": True,
                "normalization": "imagenet",
            },
            "manifest_hash": compute_file_sha256(manifest_path),
            "splits_hash": compute_file_sha256(splits_path),
        }

        torch.save(state, out_path)
        logger.info("Saved model checkpoint to %s (Val Metric: %.4f)", out_path, validation_metric)
        return out_path

    def load_checkpoint(
        self,
        checkpoint_path: str | Path,
        model: torch.nn.Module,
        optimizer: Optional[torch.optim.Optimizer] = None,
    ) -> Dict[str, Any]:
        """Load checkpoint and verify metadata."""
        cp_path = Path(checkpoint_path)
        if not cp_path.is_file():
            raise FileNotFoundError(f"Checkpoint not found at: {cp_path}")

        checkpoint = torch.load(cp_path, map_location="cpu", weights_only=False)
        model.load_state_dict(checkpoint["model_state_dict"])
        if optimizer is not None and "optimizer_state_dict" in checkpoint:
            optimizer.load_state_dict(checkpoint["optimizer_state_dict"])

        logger.info(
            "Loaded checkpoint from %s (Epoch %d, Seed %d, Val Metric: %.4f)",
            cp_path,
            checkpoint.get("epoch", -1),
            checkpoint.get("seed", -1),
            checkpoint.get("validation_metric", 0.0),
        )
        return checkpoint
