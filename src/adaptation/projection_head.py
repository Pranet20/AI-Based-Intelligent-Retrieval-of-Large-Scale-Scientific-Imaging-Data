"""Projection head implementations for representation adaptation."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ProjectionHead(nn.Module):
    """Adaptation projection head mapping 384-D DINOv2 features to unit-normalized 384-D embeddings."""

    def __init__(
        self,
        input_dim: int = 384,
        hidden_dim: int = 384,
        output_dim: int = 384,
        head_type: str = "mlp",
        dropout: float = 0.0,
        normalize_output: bool = True,
    ) -> None:
        super().__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.head_type = head_type.lower()
        self.normalize_output = normalize_output

        if self.head_type == "mlp":
            self.net = nn.Sequential(
                nn.Linear(input_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout) if dropout > 0.0 else nn.Identity(),
                nn.Linear(hidden_dim, output_dim),
            )
        elif self.head_type == "linear":
            self.net = nn.Sequential(
                nn.Linear(input_dim, output_dim),
            )
        elif self.head_type == "identity":
            self.net = nn.Identity()
        else:
            raise ValueError(f"Unsupported head_type: {head_type}. Choose 'mlp', 'linear', or 'identity'.")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through projection head with optional L2 normalization."""
        z = self.net(x)
        if self.normalize_output:
            z = F.normalize(z, p=2, dim=-1)
        return z
