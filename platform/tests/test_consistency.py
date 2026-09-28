import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from app.core.config import settings
from app.ml.dinov2_engine import DINOv2Engine
from app.ml.phase4_engine import Phase4Engine
from app.ml.model_registry import ModelRegistryService


def test_phase4_checkpoint_cryptographic_hash():
    """Verify that Phase 4 linear projection checkpoint hash matches authoritative frozen hash."""
    ckpt_path = Path("data/processed/phase4/checkpoints/best_checkpoint_seed42.pt")
    assert ckpt_path.exists(), "Phase 4 checkpoint must exist"
    with open(ckpt_path, "rb") as f:
        actual_hash = hashlib.sha256(f.read()).hexdigest()
    assert actual_hash == settings.EXPECTED_PHASE4_HASH
    assert ModelRegistryService.verify_checkpoint_hash(ckpt_path, settings.EXPECTED_PHASE4_HASH) is True


def test_dinov2_numerical_consistency():
    """Verify that platform DINOv2Engine reproduces frozen Phase 2 embeddings within 1e-4."""
    emb_parquet = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    manifest_parquet = Path("data/manifests/hcci_manifest.parquet")

    if not emb_parquet.exists() or not manifest_parquet.exists():
        pytest.skip("Frozen datasets not present on disk")

    df_emb = pd.read_parquet(emb_parquet)
    first_row = df_emb.iloc[0]
    img_id = first_row["image_id"]
    frozen_vec = np.array(first_row["embedding"], dtype=np.float32)

    df_man = pd.read_parquet(manifest_parquet)
    man_row = df_man[df_man["image_id"] == img_id].iloc[0]
    img_path = Path("data/raw/hcci") / man_row["relative_path"]

    engine = DINOv2Engine()
    platform_vec = engine.embed_image(img_path)

    cos_sim = float(np.dot(frozen_vec, platform_vec) / (np.linalg.norm(frozen_vec) * np.linalg.norm(platform_vec)))
    max_diff = float(np.max(np.abs(frozen_vec - platform_vec)))

    assert cos_sim >= 0.99999, f"Cosine similarity {cos_sim} below threshold 0.99999"
    assert max_diff < 1e-4, f"Max absolute difference {max_diff} exceeded 1e-4"


def test_phase4_adapter_numerical_consistency():
    """Verify that platform Phase4Engine reproduces frozen adapted embeddings within 1e-4."""
    base_parquet = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    adapted_parquet = Path("data/processed/phase4/embeddings/hcci_adapted_ablation_linear_head_seed42.parquet")

    if not base_parquet.exists() or not adapted_parquet.exists():
        pytest.skip("Frozen embeddings not present on disk")

    df_base = pd.read_parquet(base_parquet)
    first_img_id = df_base.iloc[0]["image_id"]
    base_vec = np.array(df_base.iloc[0]["embedding"], dtype=np.float32)

    df_adapted = pd.read_parquet(adapted_parquet)
    frozen_adapted_vec = np.array(
        df_adapted[df_adapted["image_id"] == first_img_id].iloc[0]["embedding"],
        dtype=np.float32,
    )

    p4_engine = Phase4Engine()
    platform_adapted_vec = p4_engine.adapt_embedding(base_vec)

    cos_sim = float(
        np.dot(frozen_adapted_vec, platform_adapted_vec)
        / (np.linalg.norm(frozen_adapted_vec) * np.linalg.norm(platform_adapted_vec))
    )
    max_diff = float(np.max(np.abs(frozen_adapted_vec - platform_adapted_vec)))

    assert cos_sim >= 0.99999, f"Cosine similarity {cos_sim} below threshold 0.99999"
    assert max_diff < 1e-4, f"Max absolute difference {max_diff} exceeded 1e-4"
