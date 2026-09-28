"""Computational image-quality indicators for scientific microscopy.

Important scientific disclaimer:
These indicators represent computational heuristics (focus proxies, dynamic range,
entropy, clipping ratios) and DO NOT represent absolute scientific image quality ground truth.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, Optional

import numpy as np
from scipy.ndimage import convolve


@dataclass
class QualityMetricsResult:
    """Container for computational image-quality indicators."""

    mean_intensity: float
    variance: float
    std_intensity: float
    dynamic_range: float
    contrast: float
    laplacian_variance: float  # focus sharpness proxy
    saturation_ratio: float    # clipping at maximum dynamic range
    dark_pixel_ratio: float    # under-exposure proxy
    bright_pixel_ratio: float  # near-saturation proxy
    entropy: float             # Shannon information entropy in bits

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mean_intensity": round(self.mean_intensity, 4),
            "variance": round(self.variance, 4),
            "std_intensity": round(self.std_intensity, 4),
            "dynamic_range": round(self.dynamic_range, 4),
            "contrast": round(self.contrast, 4),
            "laplacian_variance": round(self.laplacian_variance, 4),
            "saturation_ratio": round(self.saturation_ratio, 6),
            "dark_pixel_ratio": round(self.dark_pixel_ratio, 6),
            "bright_pixel_ratio": round(self.bright_pixel_ratio, 6),
            "entropy": round(self.entropy, 4),
        }


def compute_shannon_entropy(arr_gray: np.ndarray, num_bins: int = 256) -> float:
    """Compute Shannon entropy in bits for an image array."""
    if arr_gray.size == 0:
        return 0.0
    # Dynamic range normalization for binning
    min_v, max_v = float(np.min(arr_gray)), float(np.max(arr_gray))
    if min_v == max_v:
        return 0.0

    counts, _ = np.histogram(arr_gray, bins=num_bins, range=(min_v, max_v))
    probs = counts / float(arr_gray.size)
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log2(probs)))


def compute_laplacian_variance(arr_gray: np.ndarray) -> float:
    """Compute focus sharpness proxy via variance of the discrete 2D Laplacian operator."""
    if arr_gray.ndim != 2:
        return 0.0
    # Standard discrete Laplacian kernel
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    lap = convolve(arr_gray.astype(np.float32), kernel, mode="reflect")
    return float(np.var(lap))


def calculate_quality_metrics(
    image_arr: np.ndarray,
    bit_depth: Optional[int] = None,
) -> QualityMetricsResult:
    """Calculate the 10 standard computational quality indicators on an image array."""
    # Convert multi-channel images to 2D luminance / grayscale for metric computation
    if image_arr.ndim == 3:
        # Standard Rec.601 luma weights
        c = image_arr.shape[2]
        if c >= 3:
            arr_gray = (
                0.299 * image_arr[:, :, 0]
                + 0.587 * image_arr[:, :, 1]
                + 0.114 * image_arr[:, :, 2]
            ).astype(np.float32)
        else:
            arr_gray = image_arr[:, :, 0].astype(np.float32)
    else:
        arr_gray = image_arr.astype(np.float32)

    # Filter any non-finite values if present
    valid_mask = np.isfinite(arr_gray)
    if not np.all(valid_mask):
        arr_gray = np.nan_to_num(arr_gray, nan=0.0, posinf=0.0, neginf=0.0)

    total_pixels = float(arr_gray.size)
    if total_pixels == 0:
        return QualityMetricsResult(
            mean_intensity=0.0,
            variance=0.0,
            std_intensity=0.0,
            dynamic_range=0.0,
            contrast=0.0,
            laplacian_variance=0.0,
            saturation_ratio=0.0,
            dark_pixel_ratio=0.0,
            bright_pixel_ratio=0.0,
            entropy=0.0,
        )

    mean_val = float(np.mean(arr_gray))
    var_val = float(np.var(arr_gray))
    std_val = float(np.std(arr_gray))
    min_val = float(np.min(arr_gray))
    max_val = float(np.max(arr_gray))
    dyn_range = max_val - min_val

    # RMS contrast
    contrast = std_val

    # Determine maximum expected theoretical range based on dtype / bit-depth
    if image_arr.dtype == np.uint8:
        max_possible = 255.0
    elif image_arr.dtype == np.uint16:
        max_possible = 65535.0
    else:
        max_possible = max_val if max_val > 0 else 1.0

    # Clipping & saturation indicators
    # Saturation: within 0.5% of max possible value
    sat_thresh = max_possible * 0.995
    saturation_count = np.count_nonzero(arr_gray >= sat_thresh)
    saturation_ratio = float(saturation_count / total_pixels)

    # Dark pixels: near zero (lower 1% of dynamic scale)
    dark_thresh = max_possible * 0.01
    dark_count = np.count_nonzero(arr_gray <= dark_thresh)
    dark_pixel_ratio = float(dark_count / total_pixels)

    # Bright pixels: upper 5%
    bright_thresh = max_possible * 0.95
    bright_count = np.count_nonzero(arr_gray >= bright_thresh)
    bright_pixel_ratio = float(bright_count / total_pixels)

    # Laplacian variance (sharpness/focus proxy)
    lap_var = compute_laplacian_variance(arr_gray)

    # Shannon entropy
    entropy = compute_shannon_entropy(arr_gray)

    return QualityMetricsResult(
        mean_intensity=mean_val,
        variance=var_val,
        std_intensity=std_val,
        dynamic_range=dyn_range,
        contrast=contrast,
        laplacian_variance=lap_var,
        saturation_ratio=saturation_ratio,
        dark_pixel_ratio=dark_pixel_ratio,
        bright_pixel_ratio=bright_pixel_ratio,
        entropy=entropy,
    )
