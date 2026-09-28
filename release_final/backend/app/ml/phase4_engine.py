"""Phase 4 Acquisition-Aware Representation Engine with Lazy Loading."""

from pathlib import Path
from typing import Optional, Union
import numpy as np
import torch

from app.core.config import settings
from app.ml.model_registry import ModelRegistryService


class Phase4Engine:
    """Lazy-loaded singleton wrapper for frozen Phase 4 acquisition-aware adapter."""

    _instance = None
    _head = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Phase4Engine, cls).__new__(cls)
            cls._instance.checkpoint_hash = settings.EXPECTED_PHASE4_HASH
        return cls._instance

    def _ensure_loaded(self):
        if self._head is None:
            from src.adaptation.projection_head import ProjectionHead
            # 1. Verify checkpoint cryptographic integrity
            ModelRegistryService.verify_checkpoint_hash(
                settings.PHASE4_CHECKPOINT_PATH,
                settings.EXPECTED_PHASE4_HASH
            )

            # 2. Load weights
            ckpt = torch.load(settings.PHASE4_CHECKPOINT_PATH, map_location="cpu")
            self._head = ProjectionHead(
                input_dim=settings.DINOV2_EMBEDDING_DIM,
                hidden_dim=settings.DINOV2_EMBEDDING_DIM,
                output_dim=settings.DINOV2_EMBEDDING_DIM,
                head_type="linear",
                normalize_output=True
            )
            self._head.load_state_dict(ckpt["model_state_dict"])
            self._head.eval()
            for p in self._head.parameters():
                p.requires_grad = False

    def adapt_embedding(self, base_embedding: np.ndarray) -> np.ndarray:
        """Project 384-d DINOv2 embedding through Phase 4 adapter with L2 normalization."""
        self._ensure_loaded()
        with torch.no_grad():
            tensor = torch.from_numpy(base_embedding).float().unsqueeze(0)
            adapted = self._head(tensor).squeeze(0).numpy()
        return adapted
