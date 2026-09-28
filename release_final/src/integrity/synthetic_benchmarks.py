"""
Track F: Controlled Synthetic Benchmarks for Redundancy and Quality Anomalies.

Generates ground-truth controlled transformations and degradations with strict parent lineage:
1. Controlled Near-Duplicate Benchmarks:
   - Center cropping, downscale/upscale, JPEG compression, contrast/brightness jitter,
     mild Gaussian noise, and scale-bar/watermark overlay.
2. Controlled Quality Degradation Benchmarks:
   - Defocus blur, detector saturation, beam burn spot, scan line dropout, salt-and-pepper noise.
3. Rigorous Evaluation:
   - Cascade detection recall, precision, AUROC, and per-artifact sensitivity.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import io
import numpy as np
from PIL import Image, ImageDraw
import scipy.ndimage


def apply_near_duplicate_transforms(
    img: Image.Image,
    parent_id: str,
) -> List[Tuple[Image.Image, dict]]:
    """
    Generate a suite of controlled near-duplicate variations from a parent image.
    Returns list of (transformed_image, lineage_metadata).
    """
    if img.mode != "L":
        img = img.convert("L")

    w, h = img.size
    variants = []

    # 1. Center Crop 90%
    w90, h90 = int(w * 0.9), int(h * 0.9)
    left, top = (w - w90) // 2, (h - h90) // 2
    crop90 = img.crop((left, top, left + w90, top + h90)).resize((w, h), Image.Resampling.BILINEAR)
    variants.append((crop90, {
        "parent_image_id": parent_id,
        "transform_family": "geometric",
        "transform_type": "center_crop",
        "parameter": "90pct",
    }))

    # 2. Resize Down/Up (50%)
    w50, h50 = w // 2, h // 2
    res50 = img.resize((w50, h50), Image.Resampling.BILINEAR).resize((w, h), Image.Resampling.BILINEAR)
    variants.append((res50, {
        "parent_image_id": parent_id,
        "transform_family": "resolution",
        "transform_type": "downscale_upscale",
        "parameter": "50pct",
    }))

    # 3. JPEG Compression (Q=75)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=75)
    buf.seek(0)
    jpeg75 = Image.open(buf).convert("L")
    variants.append((jpeg75, {
        "parent_image_id": parent_id,
        "transform_family": "compression",
        "transform_type": "jpeg_compression",
        "parameter": "q75",
    }))

    # 4. Contrast Jitter (+20%)
    arr = np.asarray(img, dtype=np.float32)
    mean_val = np.mean(arr)
    arr_c = np.clip(mean_val + 1.2 * (arr - mean_val), 0, 255).astype(np.uint8)
    variants.append((Image.fromarray(arr_c), {
        "parent_image_id": parent_id,
        "transform_family": "photometric",
        "transform_type": "contrast_boost",
        "parameter": "1.2x",
    }))

    # 5. Brightness Jitter (+15 counts)
    arr_b = np.clip(arr + 15.0, 0, 255).astype(np.uint8)
    variants.append((Image.fromarray(arr_b), {
        "parent_image_id": parent_id,
        "transform_family": "photometric",
        "transform_type": "brightness_offset",
        "parameter": "+15",
    }))

    # 6. Mild Gaussian Noise (sigma=5)
    noise = np.random.RandomState(42).normal(0, 5.0, arr.shape)
    arr_n = np.clip(arr + noise, 0, 255).astype(np.uint8)
    variants.append((Image.fromarray(arr_n), {
        "parent_image_id": parent_id,
        "transform_family": "sensor_noise",
        "transform_type": "gaussian_noise",
        "parameter": "sigma5",
    }))

    # 7. Scale bar / annotation overlay
    annotated = img.copy()
    draw = ImageDraw.Draw(annotated)
    # Draw white scale bar rectangle in bottom right
    draw.rectangle([w - 120, h - 30, w - 20, h - 15], fill=255)
    variants.append((annotated, {
        "parent_image_id": parent_id,
        "transform_family": "annotation",
        "transform_type": "scale_bar_overlay",
        "parameter": "100px_bar",
    }))

    return variants


def apply_quality_anomaly_artifacts(
    img: Image.Image,
    parent_id: str,
) -> List[Tuple[Image.Image, dict]]:
    """
    Generate controlled physical microscopy degradation artifacts from a parent image.
    Returns list of (degraded_image, lineage_metadata).
    """
    if img.mode != "L":
        img = img.convert("L")

    arr = np.asarray(img, dtype=np.float32)
    h, w = arr.shape
    artifacts = []

    # 1. Defocus Blur (Gaussian filter sigma=5.0)
    arr_blur = scipy.ndimage.gaussian_filter(arr, sigma=5.0)
    artifacts.append((Image.fromarray(arr_blur.clip(0, 255).astype(np.uint8)), {
        "parent_image_id": parent_id,
        "artifact_type": "defocus_blur",
        "parameter": "sigma5.0",
        "expected_failure": "laplacian_variance_drop",
    }))

    # 2. Detector Saturation / Over-exposure (clipping top 25% of histogram)
    p75 = np.percentile(arr, 75.0)
    arr_sat = np.where(arr >= p75, 255.0, arr * (255.0 / max(p75, 1.0)))
    artifacts.append((Image.fromarray(arr_sat.clip(0, 255).astype(np.uint8)), {
        "parent_image_id": parent_id,
        "artifact_type": "detector_saturation",
        "parameter": "clip_p75_to_255",
        "expected_failure": "high_clipping_ratio",
    }))

    # 3. Beam Burn Spot (Localized circular intensity attenuation)
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    r = np.hypot(x - cx, y - cy)
    spot_radius = min(h, w) * 0.15
    mask = np.exp(-(r ** 2) / (2.0 * (spot_radius ** 2)))
    arr_burn = arr * (1.0 - 0.7 * mask)
    artifacts.append((Image.fromarray(arr_burn.clip(0, 255).astype(np.uint8)), {
        "parent_image_id": parent_id,
        "artifact_type": "beam_damage_burn",
        "parameter": "center_spot_15pct",
        "expected_failure": "intensity_irregularity",
    }))

    # 4. Scan Line Dropout (Horizontal periodic detector sync loss)
    arr_dropout = arr.copy()
    for row_idx in range(0, h, 20):
        arr_dropout[row_idx:row_idx+2, :] = 0.0
    artifacts.append((Image.fromarray(arr_dropout.clip(0, 255).astype(np.uint8)), {
        "parent_image_id": parent_id,
        "artifact_type": "scanline_dropout",
        "parameter": "periodic_step20",
        "expected_failure": "high_freq_fft_distortion",
    }))

    # 5. Severe Salt & Pepper Detector Noise (charging/sparking)
    rng = np.random.RandomState(42)
    sp_mask = rng.rand(h, w)
    arr_sp = arr.copy()
    arr_sp[sp_mask < 0.03] = 0.0
    arr_sp[sp_mask > 0.97] = 255.0
    artifacts.append((Image.fromarray(arr_sp.clip(0, 255).astype(np.uint8)), {
        "parent_image_id": parent_id,
        "artifact_type": "charging_salt_pepper",
        "parameter": "3pct_intensity_extremes",
        "expected_failure": "high_clipping_and_edge_noise",
    }))

    return artifacts


def compute_binary_auroc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Compute Area Under the Receiver Operating Characteristic curve (AUROC).
    Uses trapezoidal rule with rank-based formulation for exact computation.
    """
    y_true = np.asarray(y_true, dtype=bool)
    y_score = np.asarray(y_score, dtype=np.float64)

    n_pos = int(np.count_nonzero(y_true))
    n_neg = int(len(y_true) - n_pos)

    if n_pos == 0 or n_neg == 0:
        return 0.5

    # Rank scores
    order = np.argsort(y_score)
    ranks = np.empty_like(order, dtype=np.float64)
    ranks[order] = np.arange(len(y_score)) + 1.0

    # Handle tied scores
    sorted_scores = y_score[order]
    unique_scores, idx_starts, counts = np.unique(sorted_scores, return_index=True, return_counts=True)
    for start, count in zip(idx_starts, counts):
        if count > 1:
            mean_rank = start + 1.0 + (count - 1) / 2.0
            ranks[order[start:start+count]] = mean_rank

    pos_ranks_sum = np.sum(ranks[y_true])
    u = pos_ranks_sum - (n_pos * (n_pos + 1.0)) / 2.0
    return float(u / (n_pos * n_neg))


def compute_binary_auprc(y_true: np.ndarray, y_score: np.ndarray) -> float:
    """
    Compute Area Under the Precision-Recall Curve (AUPRC / Average Precision).
    """
    from sklearn.metrics import average_precision_score
    y_true = np.asarray(y_true, dtype=bool)
    y_score = np.asarray(y_score, dtype=np.float64)
    if np.count_nonzero(y_true) == 0:
        return 0.0
    return float(average_precision_score(y_true, y_score))


def compute_detection_rate_at_threshold(y_true: np.ndarray, y_score: np.ndarray, threshold: float) -> float:
    """
    Compute true positive detection rate (sensitivity / recall) at predefined decision threshold.
    """
    y_true = np.asarray(y_true, dtype=bool)
    preds = y_score >= threshold
    n_pos = np.count_nonzero(y_true)
    if n_pos == 0:
        return 0.0
    return float(np.count_nonzero(preds & y_true) / n_pos)
