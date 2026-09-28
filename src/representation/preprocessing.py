"""Deterministic scientific microscopy image preprocessor for DINOv2 visual representations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Tuple
import numpy as np
import torch
import torchvision.transforms.functional as TF
from PIL import Image

from src.ingestion.reader import ScientificImageReader


class ScientificImagePreprocessor:
    """Deterministic scientific image preprocessing pipeline adhering to Phase 2 protocol."""

    def __init__(
        self,
        image_size: Tuple[int, int] = (224, 224),
        version: str = "1.0.0",
        mean: Tuple[float, float, float] = (0.485, 0.456, 0.406),
        std: Tuple[float, float, float] = (0.229, 0.224, 0.225),
    ) -> None:
        self.image_size = image_size
        self.version = version
        self.mean = list(mean)
        self.std = list(std)

    def preprocess_array(
        self,
        arr: np.ndarray,
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """Preprocess an in-memory NumPy array deterministically without modifying source.

        Args:
            arr: Raw image array from ScientificImageReader.

        Returns:
            Tuple of (torch.Tensor of shape (3, H, W), metadata dictionary).
        """
        source_dtype = str(arr.dtype)
        orig_shape = arr.shape

        if arr.ndim == 2:
            # Grayscale (H, W) -> 1 channel
            source_height, source_width = arr.shape
            source_channels = 1
            # Replicate grayscale to 3 channels: ch1 = ch2 = ch3
            # Avoid pseudo-coloring, histogram equalization, CLAHE, or contrast enhancement
            stacked = np.stack([arr, arr, arr], axis=-1)
        elif arr.ndim == 3:
            source_height, source_width, source_channels = arr.shape
            if source_channels == 1:
                stacked = np.concatenate([arr, arr, arr], axis=-1)
            elif source_channels == 3:
                stacked = arr
            elif source_channels == 4:
                # RGBA -> take RGB channels without modifying underlying values
                stacked = arr[:, :, :3]
            else:
                raise ValueError(f"Unsupported number of channels: {source_channels}")
        else:
            raise ValueError(f"Unsupported array dimensions: {arr.ndim}")

        # Intensity scaling to [0.0, 1.0] preserving bit depth
        if np.issubdtype(arr.dtype, np.uint8):
            float_img = stacked.astype(np.float32) / 255.0
        elif np.issubdtype(arr.dtype, np.uint16):
            float_img = stacked.astype(np.float32) / 65535.0
        elif np.issubdtype(arr.dtype, np.floating):
            float_img = stacked.astype(np.float32)
            # Clip if already normalized [0, 1]
            float_img = np.clip(float_img, 0.0, 1.0)
        else:
            float_img = stacked.astype(np.float32) / float(np.max(stacked) if np.max(stacked) > 0 else 1.0)

        # Convert to Tensor (C, H, W)
        tensor = torch.from_numpy(float_img).permute(2, 0, 1).contiguous()

        # Deterministic bicubic resize with antialiasing (no random crops/flips/rotations)
        resized = TF.resize(
            tensor,
            size=list(self.image_size),
            interpolation=TF.InterpolationMode.BICUBIC,
            antialias=True,
        )

        # Deterministic ImageNet normalization
        normalized = TF.normalize(resized, mean=self.mean, std=self.std)

        meta = {
            "source_dtype": source_dtype,
            "source_channels": source_channels,
            "source_height": int(source_height),
            "source_width": int(source_width),
            "processed_channels": 3,
            "processed_height": int(self.image_size[0]),
            "processed_width": int(self.image_size[1]),
            "preprocessing_version": self.version,
            "grayscale_policy": "replicate_to_rgb",
            "interpolation": "bicubic",
        }

        return normalized, meta

    def preprocess_image_file(
        self,
        file_path: str | Path,
    ) -> Tuple[torch.Tensor, Dict[str, Any]]:
        """Load image via ScientificImageReader and preprocess deterministically.

        Guarantees source file on disk is never altered.
        """
        p = Path(file_path)
        if not p.is_file():
            raise FileNotFoundError(f"Source image file not found: {p}")

        arr, _ = ScientificImageReader.load_array(p)
        return self.preprocess_array(arr)
