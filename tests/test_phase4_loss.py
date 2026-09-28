"""Tests for Phase 4 acquisition-aware loss functions and numerical stability."""

import pytest
import torch
import torch.nn.functional as F

from src.adaptation.losses import AcquisitionAwareSupConLoss
from src.adaptation.projection_head import ProjectionHead


def test_acquisition_aware_supcon_loss_backward():
    """Verify loss calculation and gradient flow through projection head."""
    head = ProjectionHead(input_dim=384, output_dim=384, head_type="mlp")
    criterion = AcquisitionAwareSupConLoss(temperature=0.07, mask_same_acquisition=True)

    # 4 samples: 2 materials, differing acquisitions
    x = torch.randn(4, 384, requires_grad=True)
    mats = torch.tensor([0, 0, 1, 1], dtype=torch.long)
    acqs = torch.tensor([1, 2, 1, 2], dtype=torch.long)

    out = head(x)
    loss = criterion(out, mats, acqs)

    assert not torch.isnan(loss)
    assert not torch.isinf(loss)
    assert loss.item() > 0.0

    loss.backward()
    for p in head.parameters():
        assert p.grad is not None
        assert not torch.isnan(p.grad).any()


def test_loss_numerical_stability_no_positives():
    """Verify loss gracefully handles batches where no anchor has a valid cross-acquisition positive."""
    criterion = AcquisitionAwareSupConLoss(temperature=0.07, mask_same_acquisition=True)

    # 3 samples, all different materials -> zero positives
    embs = F.normalize(torch.randn(3, 384), p=2, dim=-1)
    mats = torch.tensor([0, 1, 2], dtype=torch.long)
    acqs = torch.tensor([1, 1, 1], dtype=torch.long)

    loss = criterion(embs, mats, acqs)
    assert not torch.isnan(loss)
    assert loss.item() == 0.0


def test_loss_single_sample_batch():
    """Verify loss handles B=1 without raising an error or returning NaN."""
    criterion = AcquisitionAwareSupConLoss(temperature=0.07)
    embs = F.normalize(torch.randn(1, 384), p=2, dim=-1)
    mats = torch.tensor([0], dtype=torch.long)
    acqs = torch.tensor([1], dtype=torch.long)

    loss = criterion(embs, mats, acqs)
    assert not torch.isnan(loss)
    assert loss.item() == 0.0
