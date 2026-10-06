"""
Track B: Measurable Image-Quality Risk Indicators.

Calculates six deterministic, physically grounded microscopy quality degradation metrics:
1. Laplacian Variance (sigma^2_Laplacian): Focus and sharpness proxy.
2. Edge Density: Mean gradient magnitude from Sobel filtering.
3. Shannon Entropy: Information richness of pixel intensity distribution.
4. Dynamic Range: Robust intensity spread (99th - 1st percentile).
5. Clipping / Saturation Ratio: Fraction of under-exposed (0) and saturated (255) pixels.
6. High-Frequency Spectral Energy Ratio: Fraction of 2D FFT energy in outer spatial frequencies.
7. Composite Quality Risk Score: Calibrated scalar in [0, 1] indicating quality failure severity.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import scipy.ndimage
import scipy.fft
import pandas as pd


def _to_gray_array(image_input: Union[str, Path, np.ndarray, Image.Image]) -> np.ndarray:
    """Helper to convert any image input to 2D float32 numpy array in [0, 255]."""
    arr: Optional[np.ndarray] = None
    if isinstance(image_input, np.ndarray):
        arr = image_input
    elif isinstance(image_input, (str, Path)):
        try:
            import tifffile
            arr = tifffile.imread(str(image_input))
        except Exception:
            img = Image.open(image_input)
            arr = np.asarray(img)
    elif isinstance(image_input, Image.Image):
        arr = np.asarray(image_input)
    else:
        raise TypeError(f"Unsupported image input: {type(image_input)}")

    # Handle multi-channel / extra dimensions
    if arr.ndim == 3:
        if arr.shape[2] in (3, 4):
            arr = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]
        else:
            arr = arr[:, :, 0]
    elif arr.ndim > 3:
        arr = np.squeeze(arr)
        if arr.ndim > 2:
            arr = arr[0]

    arr = arr.astype(np.float32)

    # If the array was 16-bit or values exceed 255, scale gracefully to [0, 255]
    if arr.max() > 255.0:
        p_low, p_high = np.percentile(arr, (0.1, 99.9))
        if p_high > p_low:
            norm = (arr - p_low) / (p_high - p_low) * 255.0
            return np.clip(norm, 0.0, 255.0).astype(np.float32)
        else:
            return np.zeros_like(arr, dtype=np.float32)

    return arr


def compute_laplacian_variance(image_input: Union[str, Path, np.ndarray, Image.Image]) -> float:
    """
    Compute focus/sharpness indicator as the sample variance of the Laplacian.
    Higher values indicate sharp edges; near-zero values indicate defocus blur or flat regions.
    """
    arr = _to_gray_array(image_input)
    # 3x3 discrete Laplacian kernel
    kernel = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]], dtype=np.float32)
    lap = scipy.ndimage.convolve(arr, kernel, mode="reflect")
    return float(np.var(lap))


def compute_edge_density(image_input: Union[str, Path, np.ndarray, Image.Image]) -> float:
    """
    Compute edge density as the mean Sobel gradient magnitude normalized by 255.
    """
    arr = _to_gray_array(image_input)
    gx = scipy.ndimage.sobel(arr, axis=1, mode="reflect") / 4.0
    gy = scipy.ndimage.sobel(arr, axis=0, mode="reflect") / 4.0
    mag = np.hypot(gx, gy)
    return float(np.mean(mag) / 255.0)


def compute_shannon_entropy(image_input: Union[str, Path, np.ndarray, Image.Image]) -> float:
    """
    Compute Shannon entropy (in bits) of the 8-bit intensity distribution.
    H = - sum(p_i * log2(p_i))
    """
    arr = _to_gray_array(image_input).clip(0, 255).astype(np.uint8)
    hist, _ = np.histogram(arr, bins=256, range=(0, 256))
    total_pixels = arr.size
    p = hist[hist > 0] / total_pixels
    return float(-np.sum(p * np.log2(p)))


def compute_dynamic_range(image_input: Union[str, Path, np.ndarray, Image.Image]) -> float:
    """
    Compute robust dynamic range as the difference between 99th and 1st percentiles.
    Ranges in [0, 255].
    """
    arr = _to_gray_array(image_input)
    p99 = np.percentile(arr, 99.0)
    p1 = np.percentile(arr, 1.0)
    return float(p99 - p1)


def compute_clipping_ratios(
    image_input: Union[str, Path, np.ndarray, Image.Image],
    low_thresh: float = 0.0,
    high_thresh: float = 255.0,
) -> Dict[str, float]:
    """
    Compute clipping ratios: fraction of pixels at or beyond detector limits.
    """
    arr = _to_gray_array(image_input)
    total = float(arr.size)
    under_ratio = float(np.count_nonzero(arr <= low_thresh)) / total
    over_ratio = float(np.count_nonzero(arr >= high_thresh)) / total
    return {
        "under_exposure_ratio": under_ratio,
        "over_exposure_ratio": over_ratio,
        "total_clipping_ratio": under_ratio + over_ratio,
    }


def compute_high_freq_fft_ratio(
    image_input: Union[str, Path, np.ndarray, Image.Image],
    cutoff_fraction: float = 0.25,
) -> float:
    """
    Compute ratio of high-spatial-frequency energy to total spectral energy in 2D FFT.

    Parameters
    ----------
    cutoff_fraction : fraction of Nyquist radius defining the high-frequency boundary.
    """
    arr = _to_gray_array(image_input)
    h, w = arr.shape
    f_shift = scipy.fft.fftshift(scipy.fft.fft2(arr))
    magnitude_sq = np.abs(f_shift) ** 2

    # Radial frequency coordinate grid
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    r = np.hypot(x - cx, y - cy)
    r_max = np.hypot(cx, cy)
    cutoff_r = cutoff_fraction * r_max

    high_freq_energy = np.sum(magnitude_sq[r > cutoff_r])
    total_energy = np.sum(magnitude_sq)

    if total_energy < 1e-12:
        return 0.0
    return float(high_freq_energy / total_energy)


def compute_all_quality_metrics(
    image_input: Union[str, Path, np.ndarray, Image.Image],
    fft_cutoff_fraction: float = 0.25,
) -> Dict[str, float]:
    """Compute all six quality degradation indicators for an image."""
    arr = _to_gray_array(image_input)
    clip = compute_clipping_ratios(arr)
    return {
        "laplacian_variance": compute_laplacian_variance(arr),
        "edge_density": compute_edge_density(arr),
        "shannon_entropy": compute_shannon_entropy(arr),
        "dynamic_range": compute_dynamic_range(arr),
        "under_exposure_ratio": clip["under_exposure_ratio"],
        "over_exposure_ratio": clip["over_exposure_ratio"],
        "total_clipping_ratio": clip["total_clipping_ratio"],
        "high_freq_fft_ratio": compute_high_freq_fft_ratio(arr, cutoff_fraction=fft_cutoff_fraction),
    }


class QualityRiskEvaluator:
    """
    Calibrates quality indicators on training images and assigns a composite
    Quality Risk score Q_risk in [0, 1].
    """

    def __init__(self):
        self.train_stats: Dict[str, Dict[str, float]] = {}
        self.fitted = False
        self.weights = {
            "blur": 0.35,
            "clip": 0.30,
            "dynamic_range": 0.20,
            "entropy": 0.15,
        }

    def fit(self, train_metrics_df: pd.DataFrame):
        """Fit empirical distribution bounds on training split images."""
        metrics_to_calibrate = [
            "laplacian_variance",
            "edge_density",
            "shannon_entropy",
            "dynamic_range",
            "total_clipping_ratio",
            "high_freq_fft_ratio",
        ]
        for m in metrics_to_calibrate:
            vals = train_metrics_df[m].to_numpy(dtype=np.float64)
            self.train_stats[m] = {
                "mean": float(np.mean(vals)),
                "std": float(np.std(vals) + 1e-8),
                "p5": float(np.percentile(vals, 5.0)),
                "p95": float(np.percentile(vals, 95.0)),
                "min": float(np.min(vals)),
                "max": float(np.max(vals)),
            }
        self.fitted = True

    def compute_risk_score(self, metrics: Dict[str, float]) -> float:
        """
        Compute composite quality risk score in [0, 1].
        High risk indicates high probability of acquisition failure (blur, saturation, low contrast).
        """
        if not self.fitted:
            # Fallback uncalibrated heuristic
            lap_risk = 1.0 / (1.0 + np.log1p(max(0.0, metrics.get("laplacian_variance", 0.0))))
            clip_risk = min(1.0, metrics.get("total_clipping_ratio", 0.0) * 10.0)
            dr_risk = max(0.0, 1.0 - (metrics.get("dynamic_range", 100.0) / 255.0))
            return float(np.clip(0.4 * lap_risk + 0.3 * clip_risk + 0.3 * dr_risk, 0.0, 1.0))

        # Risk components:
        # 1. Blur risk (low laplacian variance and low high-freq ratio)
        lap_p5 = self.train_stats["laplacian_variance"]["p5"]
        lap_val = metrics.get("laplacian_variance", 0.0)
        blur_risk = np.clip((lap_p5 - lap_val) / (lap_p5 + 1e-6), 0.0, 1.0) if lap_val < lap_p5 else 0.0

        # 2. Clipping risk (high total clipping)
        clip_p95 = max(0.01, self.train_stats["total_clipping_ratio"]["p95"])
        clip_val = metrics.get("total_clipping_ratio", 0.0)
        clip_risk = np.clip((clip_val - clip_p95) / (1.0 - clip_p95 + 1e-6), 0.0, 1.0) if clip_val > clip_p95 else 0.0

        # 3. Contrast/Dynamic range risk (low dynamic range)
        dr_p5 = self.train_stats["dynamic_range"]["p5"]
        dr_val = metrics.get("dynamic_range", 0.0)
        dr_risk = np.clip((dr_p5 - dr_val) / (dr_p5 + 1e-6), 0.0, 1.0) if dr_val < dr_p5 else 0.0

        # 4. Entropy risk (very low entropy = flat field)
        ent_p5 = self.train_stats["shannon_entropy"]["p5"]
        ent_val = metrics.get("shannon_entropy", 0.0)
        ent_risk = np.clip((ent_p5 - ent_val) / (ent_p5 + 1e-6), 0.0, 1.0) if ent_val < ent_p5 else 0.0

        # Weighted risk combination
        composite_risk = (
            0.35 * blur_risk +
            0.30 * clip_risk +
            0.20 * dr_risk +
            0.15 * ent_risk
        )
        return float(np.clip(composite_risk, 0.0, 1.0))
