"""Tests for scientific image readers, bit-depth preservation, and integrity checks."""

from pathlib import Path
import numpy as np
import pytest

from src.ingestion.reader import ScientificImageReader, compute_sha256


def test_scientific_uint16_tiff_bit_depth(synthetic_uint16_tiff: Path) -> None:
    arr, meta = ScientificImageReader.load_array(synthetic_uint16_tiff)
    assert arr.dtype == np.uint16, f"Expected uint16 preservation, got {arr.dtype}"
    assert arr.shape == (64, 64)

    audit = ScientificImageReader.audit_image(synthetic_uint16_tiff)
    assert audit.is_readable is True
    assert audit.is_corrupt is False
    assert audit.bit_depth == 16
    assert audit.dtype == "uint16"
    assert audit.nan_count == 0
    assert audit.inf_count == 0


def test_png_reading(synthetic_uint8_png: Path) -> None:
    arr, meta = ScientificImageReader.load_array(synthetic_uint8_png)
    assert arr.dtype == np.uint8
    assert arr.shape == (128, 128)

    audit = ScientificImageReader.audit_image(synthetic_uint8_png)
    assert audit.is_readable is True
    assert audit.bit_depth == 8
    assert audit.width == 128
    assert audit.height == 128


def test_jpeg_reading(synthetic_jpeg: Path) -> None:
    arr, meta = ScientificImageReader.load_array(synthetic_jpeg)
    assert arr.ndim == 3
    assert arr.shape == (100, 100, 3)

    audit = ScientificImageReader.audit_image(synthetic_jpeg)
    assert audit.channels == 3
    assert audit.color_mode == "RGB"


def test_hdf5_reading(synthetic_hdf5: Path) -> None:
    arr, meta = ScientificImageReader.load_array(synthetic_hdf5)
    assert arr.shape == (128, 128)
    assert arr.dtype == np.float32
    assert "crystal_structure" in meta

    audit = ScientificImageReader.audit_image(synthetic_hdf5)
    assert audit.is_readable is True
    assert audit.width == 128
    assert audit.height == 128


def test_corrupt_file_handling(corrupted_image_file: Path) -> None:
    audit = ScientificImageReader.audit_image(corrupted_image_file)
    assert audit.is_readable is False
    assert audit.is_corrupt is True
    assert "Failed to read" in audit.corruption_reason or "cannot identify" in audit.corruption_reason.lower()


def test_zero_byte_file_handling(zero_byte_file: Path) -> None:
    audit = ScientificImageReader.audit_image(zero_byte_file)
    assert audit.is_readable is False
    assert audit.is_corrupt is True
    assert "Zero-byte" in audit.corruption_reason


def test_sha256_hash_calculation(synthetic_uint8_png: Path) -> None:
    sha = compute_sha256(synthetic_uint8_png)
    assert isinstance(sha, str)
    assert len(sha) == 64
