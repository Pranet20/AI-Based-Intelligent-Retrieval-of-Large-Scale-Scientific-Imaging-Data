"""Tests for embedding validation, statistics, and provenance."""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.representation.validator import EmbeddingValidator


def test_embedding_validator_passed(tmp_test_dir: Path) -> None:
    # Create valid synthetic normalized embeddings parquet
    emb_path = tmp_test_dir / "test_embeddings.parquet"

    n_samples = 10
    dim = 384
    rng = np.random.default_rng(42)
    raw_vecs = rng.normal(size=(n_samples, dim)).astype(np.float32)
    # L2 normalize
    norm_vecs = raw_vecs / np.linalg.norm(raw_vecs, axis=1, keepdims=True)

    df = pd.DataFrame({
        "image_id": [f"img_{i}" for i in range(n_samples)],
        "dataset_id": ["test_ds"] * n_samples,
        "embedding": [v.tolist() for v in norm_vecs],
        "embedding_dimension": [dim] * n_samples,
        "embedding_normalized": [True] * n_samples,
        "source_sha256": [f"sha_{i}" for i in range(n_samples)],
        "preprocessing_version": ["1.0.0"] * n_samples,
    })
    df.to_parquet(emb_path, index=False)

    res = EmbeddingValidator.validate_dataset_embeddings(
        embeddings_path=emb_path,
        expected_count=n_samples,
        expected_dimension=dim,
        check_normalized=True,
    )

    assert res["validation_status"] == "PASSED"
    assert res["nan_count"] == 0
    assert res["inf_count"] == 0
    assert res["duplicate_image_id_count"] == 0
    assert res["mean_norm"] == pytest.approx(1.0, abs=1e-3)


def test_embedding_validator_detects_nan_and_dimension_mismatch(tmp_test_dir: Path) -> None:
    emb_path = tmp_test_dir / "corrupt_embeddings.parquet"

    # Vector with NaN
    bad_vec = np.ones(384, dtype=np.float32)
    bad_vec[5] = np.nan

    df = pd.DataFrame({
        "image_id": ["img_0"],
        "dataset_id": ["test_ds"],
        "embedding": [bad_vec.tolist()],
        "embedding_dimension": [384],
        "embedding_normalized": [True],
        "source_sha256": ["sha_0"],
        "preprocessing_version": ["1.0.0"],
    })
    df.to_parquet(emb_path, index=False)

    res = EmbeddingValidator.validate_dataset_embeddings(
        embeddings_path=emb_path,
        expected_count=1,
        expected_dimension=384,
    )
    assert res["validation_status"] == "FAILED"
    assert res["nan_count"] == 1

    # Dimension mismatch
    short_vec = np.ones(128, dtype=np.float32)
    df_short = pd.DataFrame({
        "image_id": ["img_0"],
        "dataset_id": ["test_ds"],
        "embedding": [short_vec.tolist()],
    })
    short_path = tmp_test_dir / "short_embeddings.parquet"
    df_short.to_parquet(short_path, index=False)

    with pytest.raises(ValueError):
        EmbeddingValidator.validate_dataset_embeddings(
            embeddings_path=short_path,
            expected_count=1,
            expected_dimension=384,
        )
