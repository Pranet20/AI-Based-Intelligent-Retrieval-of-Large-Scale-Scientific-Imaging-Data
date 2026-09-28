"""End-to-end and representation-level Phase 4 adaptation models."""

from __future__ import annotations

from typing import Optional
import torch
import torch.nn as nn

from src.adaptation.projection_head import ProjectionHead
from src.representation.dinov2_encoder import DINOv2Encoder
from src.utils.logging import get_logger

logger = get_logger("adaptation.phase4_model")


class Phase4AdaptedModel(nn.Module):
    """Phase 4 representation model combining frozen DINOv2 backbone with a trainable projection head."""

    def __init__(
        self,
        backbone: Optional[DINOv2Encoder] = None,
        head: Optional[ProjectionHead] = None,
        freeze_backbone: bool = True,
        input_dim: int = 384,
        hidden_dim: int = 384,
        output_dim: int = 384,
        head_type: str = "mlp",
    ) -> None:
        super().__init__()
        self.backbone = backbone
        if head is not None:
            self.head = head
        else:
            self.head = ProjectionHead(
                input_dim=input_dim,
                hidden_dim=hidden_dim,
                output_dim=output_dim,
                head_type=head_type,
            )

        if self.backbone is not None and freeze_backbone:
            torch_model = getattr(self.backbone, "model", self.backbone)
            if hasattr(torch_model, "eval"):
                torch_model.eval()
            if hasattr(torch_model, "parameters"):
                for p in torch_model.parameters():
                    p.requires_grad = False

    def forward_features(self, features: torch.Tensor) -> torch.Tensor:
        """Forward pre-extracted 384-D representation features through adaptation head."""
        return self.head(features)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward raw preprocessed image tensors (B, 3, 224, 224) through frozen backbone and head."""
        if self.backbone is None:
            raise RuntimeError("Backbone is not loaded; cannot forward raw image tensors. Use forward_features.")
        with torch.no_grad():
            if hasattr(self.backbone, "model"):
                feat = self.backbone.model(x)
            elif callable(self.backbone):
                feat = self.backbone(x)
            else:
                raise ValueError("Unsupported backbone type")
        return self.head(feat)
