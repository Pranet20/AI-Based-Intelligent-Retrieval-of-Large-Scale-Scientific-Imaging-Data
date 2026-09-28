"""Deterministic trainer for Phase 4 representation adaptation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset

from src.adaptation.checkpointing import CheckpointManager
from src.adaptation.losses import AcquisitionAwareSupConLoss
from src.adaptation.projection_head import ProjectionHead
from src.adaptation.relationship_builder import RelationshipBuilder
from src.evaluation.phase4_evaluator import Phase4RetrievalEvaluator
from src.utils.logging import get_logger

logger = get_logger("adaptation.trainer")


class EmbeddingDataset(Dataset):
    """Dataset holding pre-extracted representations, material IDs, and acquisition IDs."""

    def __init__(
        self,
        embeddings: np.ndarray,
        material_ids: np.ndarray,
        acquisition_ids: np.ndarray,
        image_ids: List[str],
    ) -> None:
        self.embeddings = torch.tensor(embeddings, dtype=torch.float32)
        self.material_ids = torch.tensor(material_ids, dtype=torch.long)
        self.acquisition_ids = torch.tensor(acquisition_ids, dtype=torch.long)
        self.image_ids = image_ids

    def __len__(self) -> int:
        return len(self.embeddings)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
        return self.embeddings[idx], self.material_ids[idx], self.acquisition_ids[idx], idx


class Phase4Trainer:
    """Trains the adaptation projection head using supervised contrastive learning with early stopping."""

    def __init__(
        self,
        config: Dict[str, Any],
        device: Optional[torch.device] = None,
    ) -> None:
        self.config = config
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")

        model_cfg = config.get("model", {})
        self.head = ProjectionHead(
            input_dim=model_cfg.get("input_dim", 384),
            hidden_dim=model_cfg.get("hidden_dim", 384),
            output_dim=model_cfg.get("output_dim", 384),
            head_type=model_cfg.get("head_type", "mlp"),
            dropout=model_cfg.get("dropout", 0.0),
            normalize_output=model_cfg.get("normalize_output", True),
        ).to(self.device)

        loss_cfg = config.get("loss", {})
        self.criterion = AcquisitionAwareSupConLoss(
            temperature=loss_cfg.get("temperature", 0.07),
            mask_same_acquisition=loss_cfg.get("mask_same_acquisition", True),
        ).to(self.device)

        train_cfg = config.get("training", {})
        self.lr = train_cfg.get("lr", 1e-4)
        self.weight_decay = train_cfg.get("weight_decay", 1e-4)
        self.batch_size = train_cfg.get("batch_size", 64)
        self.epochs = train_cfg.get("epochs", 40)
        self.patience = train_cfg.get("patience", 10)
        self.max_grad_norm = train_cfg.get("max_grad_norm", 1.0)
        self.val_metric_key = train_cfg.get("validation_metric", "cross_acquisition_r10")

        self.optimizer = torch.optim.AdamW(
            self.head.parameters(),
            lr=self.lr,
            weight_decay=self.weight_decay,
        )

        chk_dir = config.get("data", {}).get("checkpoints_dir", "data/processed/phase4/checkpoints")
        self.chk_manager = CheckpointManager(checkpoints_dir=chk_dir)
        self.evaluator = Phase4RetrievalEvaluator()

    @staticmethod
    def set_seed(seed: int) -> None:
        """Enforce strict deterministic random seeds."""
        import random
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

    def train_epoch(self, dataloader: DataLoader) -> float:
        """Run one training epoch."""
        self.head.train()
        total_loss = 0.0
        num_batches = 0

        for embs, mats, acqs, _ in dataloader:
            embs = embs.to(self.device)
            mats = mats.to(self.device)
            acqs = acqs.to(self.device)

            self.optimizer.zero_grad()
            proj_embs = self.head(embs)
            loss = self.criterion(proj_embs, mats, acqs)

            if torch.isnan(loss) or torch.isinf(loss):
                continue

            loss.backward()
            if self.max_grad_norm > 0:
                torch.nn.utils.clip_grad_norm_(self.head.parameters(), self.max_grad_norm)
            self.optimizer.step()

            total_loss += float(loss.item())
            num_batches += 1

        return total_loss / max(num_batches, 1)

    def evaluate_split(
        self,
        embeddings: np.ndarray,
        df_split: pd.DataFrame,
    ) -> Dict[str, Any]:
        """Forward embeddings through head and evaluate retrieval."""
        self.head.eval()
        with torch.no_grad():
            t_embs = torch.tensor(embeddings, dtype=torch.float32, device=self.device)
            adapted_embs = self.head(t_embs).cpu().numpy()

        image_ids = df_split["image_id"].tolist()
        gt, excl = RelationshipBuilder.build_retrieval_ground_truth(df_split)
        metrics = self.evaluator.evaluate_retrieval(
            embeddings=adapted_embs,
            image_ids=image_ids,
            ground_truth_positives=gt,
            exclusion_sets=excl,
        )
        return metrics

    def fit(
        self,
        train_dataset: EmbeddingDataset,
        val_embeddings: np.ndarray,
        val_df: pd.DataFrame,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Train the model with validation checkpoint selection."""
        self.set_seed(seed)

        dataloader = DataLoader(
            train_dataset,
            batch_size=self.batch_size,
            shuffle=True,
            drop_last=False,
        )

        best_metric = -1.0
        best_epoch = -1
        patience_counter = 0
        history: List[Dict[str, Any]] = []
        best_checkpoint_path = None

        logger.info("Starting Phase 4 training for Seed %d (%d epochs, batch_size=%d)...", seed, self.epochs, self.batch_size)

        for epoch in range(1, self.epochs + 1):
            train_loss = self.train_epoch(dataloader)

            # Evaluate on validation set
            val_metrics = self.evaluate_split(val_embeddings, val_df)
            val_r10 = val_metrics["recall_at_10"]
            val_r1 = val_metrics["recall_at_1"]
            val_mrr = val_metrics["mrr"]

            # Target metric for checkpoint selection
            current_metric = val_mrr if self.val_metric_key == "mrr" else val_r10

            history.append({
                "epoch": epoch,
                "train_loss": train_loss,
                "val_recall_at_1": val_r1,
                "val_recall_at_10": val_r10,
                "val_mrr": val_mrr,
            })

            is_best = current_metric > best_metric or (
                current_metric == best_metric and val_mrr > best_metric
            )

            if is_best:
                best_metric = current_metric
                best_epoch = epoch
                patience_counter = 0
                best_checkpoint_path = self.chk_manager.save_checkpoint(
                    model=self.head,
                    optimizer=self.optimizer,
                    epoch=epoch,
                    validation_metric=best_metric,
                    seed=seed,
                    config=self.config,
                    filename=f"best_checkpoint_seed{seed}.pt",
                )
            else:
                patience_counter += 1

            if epoch % 5 == 0 or is_best:
                logger.info(
                    "Epoch %02d | Loss: %.4f | Val R@1: %.4f | Val R@10: %.4f | Val MRR: %.4f | Best: %.4f (Epoch %02d)",
                    epoch, train_loss, val_r1, val_r10, val_mrr, best_metric, best_epoch
                )

            if patience_counter >= self.patience:
                logger.info("Early stopping triggered at epoch %d (patience=%d)", epoch, self.patience)
                break

        # Load best weights before returning
        if best_checkpoint_path is not None:
            self.chk_manager.load_checkpoint(best_checkpoint_path, self.head)

        return {
            "best_epoch": best_epoch,
            "best_validation_metric": best_metric,
            "best_checkpoint_path": str(best_checkpoint_path),
            "history": history,
        }
