"""Tests for deterministic scientific microscopy preprocessing."""

import hashlib
from pathlib import Path
import numpy as np
from PIL import Image
import pytest
import torch

from src.representation.preprocessing import ScientificImagePreprocessor


def test_grayscale_replication_to_three_channels() -> None:
    preprocessor = ScientificImagePreprocessor(image_size=(224, 224))

    # Synthetic single-channel grayscale array (64x64)
    gray_arr = np.full((64, 64), 128, dtype=np.uint8)
    tensor, meta = preprocessor.preprocess_array(gray_arr)

    # 1. Output tensor shape is (3, 224, 224)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.shape == (3, 224, 224)

    # 2. Check metadata
    assert meta["source_channels"] == 1
    assert meta["processed_channels"] == 3
    assert meta["grayscale_policy"] == "replicate_to_rgb"

    # 3. Verify underlying unnormalized channels 0, 1, 2 are identical (replicated grayscale)
    std_t = torch.tensor(preprocessor.std)[:, None, None]
    mean_t = torch.tensor(preprocessor.mean)[:, None, None]
    unnormalized = tensor * std_t + mean_t
    np.testing.assert_allclose(unnormalized[0].numpy(), unnormalized[1].numpy(), atol=1e-5)
    np.testing.assert_allclose(unnormalized[1].numpy(), unnormalized[2].numpy(), atol=1e-5)


def test_rgb_and_rgba_handling() -> None:
    preprocessor = ScientificImagePreprocessor(image_size=(224, 224))

    # RGB input
    rgb_arr = np.zeros((100, 100, 3), dtype=np.uint8)
    rgb_arr[:, :, 0] = 50
    rgb_arr[:, :, 1] = 100
    rgb_arr[:, :, 2] = 150
    tensor_rgb, meta_rgb = preprocessor.preprocess_array(rgb_arr)
    assert tensor_rgb.shape == (3, 224, 224)
    assert meta_rgb["source_channels"] == 3

    # RGBA input (e.g. HCCI PNGs)
    rgba_arr = np.zeros((100, 100, 4), dtype=np.uint8)
    rgba_arr[:, :, :3] = rgb_arr
    rgba_arr[:, :, 3] = 255
    tensor_rgba, meta_rgba = preprocessor.preprocess_array(rgba_arr)
    assert tensor_rgba.shape == (3, 224, 224)
    assert meta_rgba["source_channels"] == 4

    # Output tensors must match since alpha was just 255
    np.testing.assert_allclose(tensor_rgb.numpy(), tensor_rgba.numpy(), atol=1e-5)


def test_source_file_immutability(tmp_test_dir: Path) -> None:
    preprocessor = ScientificImagePreprocessor(image_size=(224, 224))

    # Create dummy PNG file
    test_file = tmp_test_dir / "micrograph_source.png"
    img = Image.new("L", (80, 80), color=200)
    img.save(test_file)

    # Compute SHA-256 before
    h_before = hashlib.sha256(test_file.read_bytes()).hexdigest()

    # Preprocess through file interface
    tensor, meta = preprocessor.preprocess_image_file(test_file)

    # Compute SHA-256 after
    h_after = hashlib.sha256(test_file.read_bytes()).hexdigest()

    # Source file must be 100% unchanged
    assert h_before == h_after, "Preprocessing must never modify the raw source file on disk."
    assert tensor.shape == (3, 224, 224)


def test_unsupported_channel_shape_raises() -> None:
    preprocessor = ScientificImagePreprocessor()
    invalid_arr = np.zeros((50, 50, 5), dtype=np.uint8)
    with pytest.raises(ValueError):
        preprocessor.preprocess_array(invalid_arr)
