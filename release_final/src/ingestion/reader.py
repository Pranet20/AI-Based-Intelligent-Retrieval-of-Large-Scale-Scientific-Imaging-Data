"""Bit-depth preserving scientific image reader and integrity analyzer."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
from PIL import Image
import tifffile
import h5py

SUPPORTED_EXTENSIONS = {".tif", ".tiff", ".png", ".jpg", ".jpeg", ".h5", ".hdf5"}


@dataclass
class ImageIntegrityResult:
    """Complete image integrity and basic statistical profile."""

    file_path: str
    filename: str
    extension: str
    file_size_bytes: int
    sha256: str
    is_readable: bool
    is_corrupt: bool
    corruption_reason: Optional[str]
    width: Optional[int]
    height: Optional[int]
    channels: Optional[int]
    dtype: Optional[str]
    bit_depth: Optional[int]
    color_mode: Optional[str]
    min_intensity: Optional[float]
    max_intensity: Optional[float]
    mean_intensity: Optional[float]
    std_intensity: Optional[float]
    dynamic_range: Optional[float]
    nan_count: int
    inf_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "filename": self.filename,
            "extension": self.extension,
            "file_size_bytes": self.file_size_bytes,
            "sha256": self.sha256,
            "is_readable": self.is_readable,
            "is_corrupt": self.is_corrupt,
            "corruption_reason": self.corruption_reason,
            "width": self.width,
            "height": self.height,
            "channels": self.channels,
            "dtype": self.dtype,
            "bit_depth": self.bit_depth,
            "color_mode": self.color_mode,
            "min_intensity": self.min_intensity,
            "max_intensity": self.max_intensity,
            "mean_intensity": self.mean_intensity,
            "std_intensity": self.std_intensity,
            "dynamic_range": self.dynamic_range,
            "nan_count": self.nan_count,
            "inf_count": self.inf_count,
        }


def compute_sha256(file_path: Path) -> str:
    """Compute SHA-256 hash of file contents in binary mode."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class ScientificImageReader:
    """Reads scientific images preserving original numerical precision and bit depths."""

    @staticmethod
    def is_supported(file_path: Path | str) -> bool:
        ext = Path(file_path).suffix.lower()
        return ext in SUPPORTED_EXTENSIONS

    @staticmethod
    def load_array(file_path: Path | str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Load image as raw NumPy array without lossy casting.

        Returns (array, metadata_dict).
        """
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Image file does not exist: {p}")
        if p.stat().st_size == 0:
            raise ValueError(f"Zero-byte file encountered: {p}")

        ext = p.suffix.lower()
        meta: Dict[str, Any] = {}

        if ext in (".tif", ".tiff"):
            with tifffile.TiffFile(p) as tif:
                arr = tif.asarray()
                # Extract any TIFF tags if available
                if tif.pages and hasattr(tif.pages[0], "tags"):
                    for tag in tif.pages[0].tags.values():
                        name = tag.name
                        try:
                            val = tag.value
                            if isinstance(val, (int, float, str)):
                                meta[name] = val
                        except Exception:
                            pass
            return arr, meta

        if ext in (".h5", ".hdf5"):
            with h5py.File(p, "r") as hf:
                # Find the primary image/dataset
                dataset_key = None
                for key in ["image", "data", "stem", "target", "choice"]:
                    if key in hf:
                        dataset_key = key
                        break
                if dataset_key is None:
                    dataset_key = list(hf.keys())[0]
                arr = np.array(hf[dataset_key])
                for attr_key, attr_val in hf.attrs.items():
                    try:
                        meta[attr_key] = attr_val.tolist() if hasattr(attr_val, "tolist") else attr_val
                    except Exception:
                        pass
            return arr, meta

        if ext in (".png", ".jpg", ".jpeg"):
            with Image.open(p) as img:
                color_mode = img.mode
                meta["color_mode"] = color_mode
                meta["format"] = img.format
                arr = np.array(img)
            return arr, meta

        raise ValueError(f"Unsupported image format: {ext}")

    @classmethod
    def audit_image(cls, file_path: Path | str) -> ImageIntegrityResult:
        """Perform comprehensive integrity check and statistical profiling on an image."""
        p = Path(file_path)
        filename = p.name
        ext = p.suffix.lower()

        if not p.exists():
            return ImageIntegrityResult(
                file_path=str(p),
                filename=filename,
                extension=ext,
                file_size_bytes=0,
                sha256="",
                is_readable=False,
                is_corrupt=True,
                corruption_reason="File not found",
                width=None,
                height=None,
                channels=None,
                dtype=None,
                bit_depth=None,
                color_mode=None,
                min_intensity=None,
                max_intensity=None,
                mean_intensity=None,
                std_intensity=None,
                dynamic_range=None,
                nan_count=0,
                inf_count=0,
            )

        file_size = p.stat().st_size
        if file_size == 0:
            return ImageIntegrityResult(
                file_path=str(p),
                filename=filename,
                extension=ext,
                file_size_bytes=0,
                sha256="",
                is_readable=False,
                is_corrupt=True,
                corruption_reason="Zero-byte file",
                width=None,
                height=None,
                channels=None,
                dtype=None,
                bit_depth=None,
                color_mode=None,
                min_intensity=None,
                max_intensity=None,
                mean_intensity=None,
                std_intensity=None,
                dynamic_range=None,
                nan_count=0,
                inf_count=0,
            )

        if not cls.is_supported(p):
            return ImageIntegrityResult(
                file_path=str(p),
                filename=filename,
                extension=ext,
                file_size_bytes=file_size,
                sha256="",
                is_readable=False,
                is_corrupt=True,
                corruption_reason=f"Unsupported extension: {ext}",
                width=None,
                height=None,
                channels=None,
                dtype=None,
                bit_depth=None,
                color_mode=None,
                min_intensity=None,
                max_intensity=None,
                mean_intensity=None,
                std_intensity=None,
                dynamic_range=None,
                nan_count=0,
                inf_count=0,
            )

        sha = compute_sha256(p)

        try:
            arr, meta = cls.load_array(p)
        except Exception as e:
            return ImageIntegrityResult(
                file_path=str(p),
                filename=filename,
                extension=ext,
                file_size_bytes=file_size,
                sha256=sha,
                is_readable=False,
                is_corrupt=True,
                corruption_reason=f"Failed to read image: {str(e)}",
                width=None,
                height=None,
                channels=None,
                dtype=None,
                bit_depth=None,
                color_mode=None,
                min_intensity=None,
                max_intensity=None,
                mean_intensity=None,
                std_intensity=None,
                dynamic_range=None,
                nan_count=0,
                inf_count=0,
            )

        # Inspect dimensions
        shape = arr.shape
        if len(shape) == 2:
            h, w = shape
            c = 1
            mode = "Grayscale"
        elif len(shape) == 3:
            h, w, c = shape
            mode = "RGB" if c == 3 else ("RGBA" if c == 4 else f"Multispectral_{c}")
        else:
            return ImageIntegrityResult(
                file_path=str(p),
                filename=filename,
                extension=ext,
                file_size_bytes=file_size,
                sha256=sha,
                is_readable=False,
                is_corrupt=True,
                corruption_reason=f"Unexpected dimensionality: shape {shape}",
                width=None,
                height=None,
                channels=None,
                dtype=str(arr.dtype),
                bit_depth=None,
                color_mode=None,
                min_intensity=None,
                max_intensity=None,
                mean_intensity=None,
                std_intensity=None,
                dynamic_range=None,
                nan_count=0,
                inf_count=0,
            )

        dtype_str = str(arr.dtype)
        bit_depth = arr.itemsize * 8

        # Numerical checks
        nan_count = int(np.isnan(arr).sum()) if np.issubdtype(arr.dtype, np.floating) else 0
        inf_count = int(np.isinf(arr).sum()) if np.issubdtype(arr.dtype, np.floating) else 0

        valid_arr = arr
        if nan_count > 0 or inf_count > 0:
            valid_arr = arr[np.isfinite(arr)]

        if valid_arr.size > 0:
            min_val = float(np.min(valid_arr))
            max_val = float(np.max(valid_arr))
            mean_val = float(np.mean(valid_arr))
            std_val = float(np.std(valid_arr))
            dyn_range = float(max_val - min_val)
        else:
            min_val = max_val = mean_val = std_val = dyn_range = None

        return ImageIntegrityResult(
            file_path=str(p.resolve()),
            filename=filename,
            extension=ext,
            file_size_bytes=file_size,
            sha256=sha,
            is_readable=True,
            is_corrupt=False,
            corruption_reason=None,
            width=w,
            height=h,
            channels=c,
            dtype=dtype_str,
            bit_depth=bit_depth,
            color_mode=mode,
            min_intensity=min_val,
            max_intensity=max_val,
            mean_intensity=mean_val,
            std_intensity=std_val,
            dynamic_range=dyn_range,
            nan_count=nan_count,
            inf_count=inf_count,
        )
