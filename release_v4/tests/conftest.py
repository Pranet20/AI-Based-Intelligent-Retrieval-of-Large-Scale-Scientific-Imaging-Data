"""Synthetic test fixtures for scientific image platform unit tests."""

from __future__ import annotations

import io
from pathlib import Path
import h5py
import numpy as np
from PIL import Image
import pytest
import tifffile


@pytest.fixture
def tmp_test_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test fixtures."""
    d = tmp_path / "test_data"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def synthetic_uint8_png(tmp_test_dir: Path) -> Path:
    """Create a synthetic 8-bit grayscale PNG with a high-contrast pattern."""
    img_path = tmp_test_dir / "synthetic_pattern.png"
    # 128x128 gradient pattern with a sharp box
    arr = np.linspace(0, 255, 128, dtype=np.uint8)
    img_arr = np.tile(arr, (128, 1))
    img_arr[40:80, 40:80] = 255  # bright box
    img_arr[90:110, 90:110] = 0   # dark box
    im = Image.fromarray(img_arr, mode="L")
    im.save(img_path)
    return img_path


@pytest.fixture
def synthetic_uint16_tiff(tmp_test_dir: Path) -> Path:
    """Create a synthetic 16-bit grayscale scientific TIFF."""
    img_path = tmp_test_dir / "synthetic_16bit.tif"
    # 64x64 uint16 array
    arr = np.arange(64 * 64, dtype=np.uint16).reshape((64, 64)) * 15
    tifffile.imwrite(img_path, arr)
    return img_path


@pytest.fixture
def synthetic_jpeg(tmp_test_dir: Path) -> Path:
    """Create a synthetic RGB JPEG."""
    img_path = tmp_test_dir / "synthetic_rgb.jpg"
    arr = np.zeros((100, 100, 3), dtype=np.uint8)
    arr[:, :, 0] = 120
    arr[:, :, 1] = 150
    arr[:, :, 2] = 180
    im = Image.fromarray(arr, mode="RGB")
    im.save(img_path, format="JPEG")
    return img_path


@pytest.fixture
def synthetic_hdf5(tmp_test_dir: Path) -> Path:
    """Create a synthetic HDF5 file simulating HAADF-STEM image and metadata attributes."""
    h5_path = tmp_test_dir / "synthetic_stem.h5"
    arr = np.random.RandomState(42).normal(100.0, 15.0, size=(128, 128)).astype(np.float32)
    with h5py.File(h5_path, "w") as hf:
        hf.create_dataset("stem", data=arr)
        hf.attrs["accelerating_voltage"] = "300kV"
        hf.attrs["probe_size"] = "0.08nm"
        hf.attrs["crystal_structure"] = "SrTiO3"
    return h5_path


@pytest.fixture
def corrupted_image_file(tmp_test_dir: Path) -> Path:
    """Create a file with an image extension but garbage binary bytes."""
    corrupt_path = tmp_test_dir / "corrupted_file.png"
    with open(corrupt_path, "wb") as f:
        f.write(b"NOT_A_VALID_IMAGE_DATA_HEADER_CORRUPTED")
    return corrupt_path


@pytest.fixture
def zero_byte_file(tmp_test_dir: Path) -> Path:
    """Create an empty 0-byte file."""
    empty_path = tmp_test_dir / "empty_image.tif"
    empty_path.touch()
    return empty_path
