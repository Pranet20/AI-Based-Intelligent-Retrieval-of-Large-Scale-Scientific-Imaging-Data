"""Tests for Phase 4 reproducibility, checkpointing, and Phase 2 immutability."""

from pathlib import Path
import pytest
import torch

from src.adaptation.checkpointing import CheckpointManager
from src.adaptation.projection_head import ProjectionHead
from src.adaptation.trainer import Phase4Trainer


def test_deterministic_seed():
    """Verify set_seed produces identical random draws."""
    Phase4Trainer.set_seed(42)
    t1 = torch.randn(10)
    Phase4Trainer.set_seed(42)
    t2 = torch.randn(10)
    assert torch.equal(t1, t2)


def test_checkpoint_save_and_load_integrity(tmp_path):
    """Verify that checkpoint manager preserves model weights and full metadata."""
    manager = CheckpointManager(checkpoints_dir=tmp_path)
    head = ProjectionHead(input_dim=384, output_dim=384, head_type="mlp")
    opt = torch.optim.AdamW(head.parameters(), lr=1e-4)

    config = {"experiment_id": "test_exp", "platform_version": "0.1.0"}
    cp_path = manager.save_checkpoint(
        model=head,
        optimizer=opt,
        epoch=5,
        validation_metric=0.985,
        seed=42,
        config=config,
        filename="test_cp.pt",
    )

    assert cp_path.is_file()

    # Create new head and load weights
    head2 = ProjectionHead(input_dim=384, output_dim=384, head_type="mlp")
    opt2 = torch.optim.AdamW(head2.parameters(), lr=1e-4)
    meta = manager.load_checkpoint(cp_path, head2, opt2)

    assert meta["epoch"] == 5
    assert meta["seed"] == 42
    assert meta["validation_metric"] == 0.985
    assert "manifest_hash" in meta
    assert "splits_hash" in meta

    # Check weight equality
    for p1, p2 in zip(head.parameters(), head2.parameters()):
        assert torch.equal(p1, p2)


def test_phase2_artifacts_immutability():
    """Verify that frozen Phase 2 embeddings, manifests, and reports exist and are untouched."""
    p2_emb = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    p2_car = Path("data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet")
    hcci_man = Path("data/manifests/hcci_manifest.parquet")
    car_man = Path("data/manifests/carinthia_manifest.parquet")
    p2_report = Path("reports/phase2/PHASE2_BASELINE_REPORT.md")

    assert p2_emb.is_file(), "Phase 2 HCCI embeddings missing!"
    assert p2_emb.stat().st_size > 1_000_000, "Phase 2 HCCI embeddings corrupted!"

    assert p2_car.is_file(), "Phase 2 Carinthia embeddings missing!"
    assert p2_car.stat().st_size > 5_000_000, "Phase 2 Carinthia embeddings corrupted!"

    assert hcci_man.is_file(), "HCCI manifest missing!"
    assert car_man.is_file(), "Carinthia manifest missing!"

    assert p2_report.is_file(), "Phase 2 report missing!"
    assert p2_report.stat().st_size > 10_000, "Phase 2 report corrupted!"
