"""Tests for DINOv2 model loading, evaluation mode, and parameter freezing."""

import numpy as np
import pytest
import torch

from src.representation.dinov2_encoder import DINOv2Encoder


def test_dinov2_model_loading_and_freeze() -> None:
    encoder = DINOv2Encoder(model_name="dinov2_vits14")

    # 1. Model is in eval mode
    assert not encoder.model.training, "DINOv2 model must be in eval mode."

    # 2. All parameters must be frozen (requires_grad = False)
    trainable_count = sum(p.numel() for p in encoder.model.parameters() if p.requires_grad)
    assert trainable_count == 0, f"Expected 0 trainable parameters, got {trainable_count}"

    # 3. Model info contains expected metadata
    info = encoder.get_model_info()
    assert info["model_name"] == "dinov2_vits14"
    assert info["embedding_dimension"] == 384
    assert info["parameter_count"] > 20_000_000
    assert "dinov2" in info["model_source"]
    assert info["device"] in ("cpu", "cuda")


def test_dinov2_feature_extraction_shape_and_norm() -> None:
    encoder = DINOv2Encoder(model_name="dinov2_vits14")

    # Synthetic batch of 2 images of size 224x224
    dummy_input = torch.randn(2, 3, 224, 224)

    # 1. Normalized output
    features = encoder.extract_features(dummy_input, normalize=True)
    assert isinstance(features, np.ndarray)
    assert features.shape == (2, 384)

    # Check L2 norm is ~1.0
    norms = np.linalg.norm(features, axis=1)
    np.testing.assert_allclose(norms, [1.0, 1.0], atol=1e-4)

    # 2. Unnormalized output
    raw_features = encoder.extract_features(dummy_input, normalize=False)
    assert raw_features.shape == (2, 384)


def test_dinov2_invalid_tensor_raises() -> None:
    encoder = DINOv2Encoder(model_name="dinov2_vits14")
    # Invalid channel count (e.g. 1 instead of 3)
    invalid_input = torch.randn(2, 1, 224, 224)
    with pytest.raises(ValueError):
        encoder.extract_features(invalid_input)
