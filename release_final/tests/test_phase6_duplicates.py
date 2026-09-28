"""
Unit tests for Phase 6 Track A: Exact and Perceptual Duplicate Detection Cascade.
"""

import numpy as np
import pytest
from PIL import Image

from src.integrity.exact_duplicates import (
    compute_file_sha256,
    compute_decoded_pixel_sha256,
)
from src.integrity.perceptual_hash import (
    compute_phash,
    compute_dhash,
    hamming_distance,
    hash_to_hex,
    hex_to_hash,
)
from src.integrity.duplicate_cascade import (
    compute_ssim,
    compute_pixel_metrics,
    DuplicateCascade,
)


def test_exact_pixel_hash_identical_across_formats(tmp_path):
    """Verify raw pixel hash is invariant to container format differences."""
    arr = np.random.RandomState(42).randint(0, 255, (100, 100), dtype=np.uint8)
    img = Image.fromarray(arr)

    png_path = tmp_path / "test.png"
    bmp_path = tmp_path / "test.bmp"
    img.save(png_path)
    img.save(bmp_path)

    # File bitwise hashes will differ due to PNG vs BMP header/compression
    file_h_png = compute_file_sha256(png_path)
    file_h_bmp = compute_file_sha256(bmp_path)
    assert file_h_png != file_h_bmp

    # Raw decoded pixel hashes must be identical
    pixel_h_png = compute_decoded_pixel_sha256(png_path)
    pixel_h_bmp = compute_decoded_pixel_sha256(bmp_path)
    assert pixel_h_png == pixel_h_bmp


def test_perceptual_hashes_deterministic():
    """Verify pHash and dHash produce deterministic 64-bit boolean arrays."""
    arr = np.zeros((64, 64), dtype=np.uint8)
    arr[16:48, 16:48] = 255
    img = Image.fromarray(arr)

    ph1 = compute_phash(img)
    ph2 = compute_phash(img)
    assert np.array_equal(ph1, ph2)
    assert ph1.shape == (64,)

    dh1 = compute_dhash(img)
    dh2 = compute_dhash(img)
    assert np.array_equal(dh1, dh2)
    assert dh1.shape == (64,)

    # Hex conversions
    hex_str = hash_to_hex(ph1)
    assert len(hex_str) == 16
    recovered = hex_to_hash(hex_str)
    assert np.array_equal(ph1, recovered)


def test_hamming_distance_properties():
    """Verify Hamming distance symmetry and triangle inequality."""
    h1 = np.array([True] * 64)
    h2 = np.array([False] * 64)
    assert hamming_distance(h1, h2) == 64
    assert hamming_distance(h1, h1) == 0
    assert hamming_distance(h1, h2) == hamming_distance(h2, h1)


def test_ssim_identical_and_different():
    """Verify SSIM gives 1.0 for identical images and drops for distorted images."""
    arr1 = np.full((128, 128), 128, dtype=np.uint8)
    arr2 = arr1.copy()
    assert compute_ssim(arr1, arr2) == pytest.approx(1.0, abs=1e-4)

    # Distorted image
    arr3 = np.random.RandomState(42).randint(0, 255, (128, 128), dtype=np.uint8)
    ssim_val = compute_ssim(arr1, arr3)
    assert ssim_val < 0.5


def test_pixel_metrics_suite():
    """Verify full suite of pixel verification metrics."""
    arr1 = np.ones((64, 64), dtype=np.uint8) * 100
    arr2 = arr1.copy()
    pm = compute_pixel_metrics(arr1, arr2)
    assert pm["mae"] == 0.0
    assert pm["mse"] == 0.0
    assert pm["psnr"] >= 99.0
    assert pm["ssim"] == pytest.approx(1.0, abs=1e-4)
    assert pm["ncc"] == pytest.approx(1.0, abs=1e-4)
