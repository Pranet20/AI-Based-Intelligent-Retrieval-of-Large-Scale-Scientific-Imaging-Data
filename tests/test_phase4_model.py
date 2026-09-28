"""Tests for Phase 4 adaptation model and projection head."""

import pytest
import torch
import numpy as np

from src.adaptation.projection_head import ProjectionHead
from src.adaptation.phase4_model import Phase4AdaptedModel


def test_projection_head_mlp_dimensions_and_norm():
    """Verify MLP projection head preserves 384-D shape and produces unit L2 norm."""
    head = ProjectionHead(input_dim=384, hidden_dim=384, output_dim=384, head_type="mlp")
    head.eval()

    x = torch.randn(16, 384)
    with torch.no_grad():
        out = head(x)

    assert out.shape == (16, 384)
    norms = torch.norm(out, p=2, dim=-1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)
    assert not torch.isnan(out).any()
    assert not torch.isinf(out).any()


def test_projection_head_linear_dimensions_and_norm():
    """Verify Linear projection head preserves 384-D shape and produces unit L2 norm."""
    head = ProjectionHead(input_dim=384, output_dim=384, head_type="linear")
    head.eval()

    x = torch.randn(8, 384)
    with torch.no_grad():
        out = head(x)

    assert out.shape == (8, 384)
    norms = torch.norm(out, p=2, dim=-1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)


def test_phase4_adapted_model_forward_features():
    """Verify Phase4AdaptedModel handles feature inputs."""
    model = Phase4AdaptedModel(backbone=None, head=None, input_dim=384, output_dim=384)
    model.eval()

    feat = torch.randn(4, 384)
    with torch.no_grad():
        out = model.forward_features(feat)

    assert out.shape == (4, 384)
    norms = torch.norm(out, p=2, dim=-1)
    assert torch.allclose(norms, torch.ones_like(norms), atol=1e-5)
