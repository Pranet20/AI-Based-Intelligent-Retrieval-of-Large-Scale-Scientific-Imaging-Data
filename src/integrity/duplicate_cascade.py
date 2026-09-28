"""
Track A: Multi-Stage Duplicate and Redundancy Detection Cascade.

Implements the 5-stage screening pipeline:
Stage 1: Exact Bitwise File Hash (SHA-256)
Stage 2: Exact Decoded Raw Pixel Hash (SHA-256)
Stage 3: Perceptual Hash Candidate Filtering (pHash/dHash Hamming <= tau_H)
Stage 4: Deep Feature Representation Cosine Filtering (DINOv2 / Adapted)
Stage 5: High-Fidelity Pixel Verification (SSIM, MAE, MSE, PSNR, NCC)
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image
import scipy.ndimage
import pandas as pd

from src.integrity.exact_duplicates import (
    compute_file_sha256,
    compute_decoded_pixel_sha256,
)
from src.integrity.perceptual_hash import (
    compute_phash,
    compute_dhash,
    hamming_distance,
    _load_gray_image,
    pairwise_hamming_matrix,
)


def compute_ssim(
    img1: Union[str, Path, np.ndarray, Image.Image],
    img2: Union[str, Path, np.ndarray, Image.Image],
    k1: float = 0.01,
    k2: float = 0.03,
    sigma: float = 1.5,
    dynamic_range: float = 255.0,
) -> float:
    """
    Compute Structural Similarity Index (SSIM) using a Gaussian filter.

    Parameters
    ----------
    img1, img2 : Grayscale uint8 arrays, PIL Images, or file paths with identical dimensions.
    k1, k2 : SSIM stability constants.
    sigma : Gaussian blur window standard deviation.
    dynamic_range : Maximum pixel intensity range (255 for 8-bit).

    Returns
    -------
    float : Mean SSIM score in [-1, 1].
    """
    if isinstance(img1, (str, Path)):
        img1 = Image.open(img1)
    if isinstance(img2, (str, Path)):
        img2 = Image.open(img2)

    if isinstance(img1, Image.Image):
        arr1 = np.asarray(img1.convert("L"), dtype=np.float32)
    else:
        arr1 = np.asarray(img1, dtype=np.float32)

    if isinstance(img2, Image.Image):
        arr2 = np.asarray(img2.convert("L"), dtype=np.float32)
    else:
        arr2 = np.asarray(img2, dtype=np.float32)

    if arr1.shape != arr2.shape:
        # Resize img2 to match img1 shape if dimensions differ slightly
        pil2 = Image.fromarray(arr2.astype(np.uint8)).resize(
            (arr1.shape[1], arr1.shape[0]), Image.Resampling.BILINEAR
        )
        arr2 = np.asarray(pil2, dtype=np.float32)

    c1 = (k1 * dynamic_range) ** 2
    c2 = (k2 * dynamic_range) ** 2

    # Gaussian weights
    mu1 = scipy.ndimage.gaussian_filter(arr1, sigma=sigma, mode="reflect")
    mu2 = scipy.ndimage.gaussian_filter(arr2, sigma=sigma, mode="reflect")

    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = scipy.ndimage.gaussian_filter(arr1 * arr1, sigma=sigma, mode="reflect") - mu1_sq
    sigma2_sq = scipy.ndimage.gaussian_filter(arr2 * arr2, sigma=sigma, mode="reflect") - mu2_sq
    sigma12 = scipy.ndimage.gaussian_filter(arr1 * arr2, sigma=sigma, mode="reflect") - mu1_mu2

    numerator = (2.0 * mu1_mu2 + c1) * (2.0 * sigma12 + c2)
    denominator = (mu1_sq + mu2_sq + c1) * (sigma1_sq + sigma2_sq + c2)

    ssim_map = numerator / (denominator + 1e-12)
    return float(np.mean(ssim_map))


def compute_pixel_metrics(
    img1: Union[str, Path, np.ndarray, Image.Image],
    img2: Union[str, Path, np.ndarray, Image.Image],
) -> Dict[str, float]:
    """
    Compute full suite of pixel verification metrics between two images.
    Returns: MAE, MSE, PSNR, SSIM, NCC.
    """
    if isinstance(img1, (str, Path)):
        img1 = Image.open(img1)
    if isinstance(img2, (str, Path)):
        img2 = Image.open(img2)

    if isinstance(img1, Image.Image):
        arr1 = np.asarray(img1.convert("L"), dtype=np.float32)
    else:
        arr1 = np.asarray(img1, dtype=np.float32)

    if isinstance(img2, Image.Image):
        arr2 = np.asarray(img2.convert("L"), dtype=np.float32)
    else:
        arr2 = np.asarray(img2, dtype=np.float32)

    if arr1.shape != arr2.shape:
        pil2 = Image.fromarray(arr2.astype(np.uint8)).resize(
            (arr1.shape[1], arr1.shape[0]), Image.Resampling.BILINEAR
        )
        arr2 = np.asarray(pil2, dtype=np.float32)

    diff = arr1 - arr2
    mae = float(np.mean(np.abs(diff)))
    mse = float(np.mean(diff ** 2))

    if mse < 1e-10:
        psnr = 100.0
    else:
        psnr = float(10.0 * np.log10((255.0 ** 2) / mse))

    ssim_val = compute_ssim(arr1, arr2)

    # Normalized Cross Correlation
    norm1 = arr1 - np.mean(arr1)
    norm2 = arr2 - np.mean(arr2)
    std1 = np.std(arr1)
    std2 = np.std(arr2)
    if std1 < 1e-6 or std2 < 1e-6:
        ncc = 1.0 if std1 < 1e-6 and std2 < 1e-6 else 0.0
    else:
        ncc = float(np.mean(norm1 * norm2) / (std1 * std2))

    return {
        "mae": mae,
        "mse": mse,
        "psnr": psnr,
        "ssim": ssim_val,
        "ncc": ncc,
    }


class DuplicateCascade:
    """
    Orchestrates the 5-stage duplicate detection cascade across an image corpus.
    """

    def __init__(
        self,
        phash_threshold: int = 6,
        dhash_threshold: int = 6,
        dinov2_cosine_threshold: float = 0.985,
        adapted_cosine_threshold: float = 0.985,
        min_ssim: float = 0.95,
        max_mae: float = 5.0,
        min_ncc: float = 0.98,
    ):
        self.phash_threshold = phash_threshold
        self.dhash_threshold = dhash_threshold
        self.dinov2_cosine_threshold = dinov2_cosine_threshold
        self.adapted_cosine_threshold = adapted_cosine_threshold
        self.min_ssim = min_ssim
        self.max_mae = max_mae
        self.min_ncc = min_ncc

    def run_cascade(
        self,
        image_ids: List[str],
        file_paths: List[Union[str, Path]],
        dinov2_embeddings: Optional[np.ndarray] = None,
        adapted_embeddings: Optional[np.ndarray] = None,
        id_to_idx: Optional[Dict[str, int]] = None,
    ) -> pd.DataFrame:
        """
        Run the complete multi-stage cascade across all candidate pairs.

        Returns
        -------
        pd.DataFrame containing discovered duplicate / near-duplicate relationships.
        """
        n = len(image_ids)
        if id_to_idx is None:
            id_to_idx = {img_id: i for i, img_id in enumerate(image_ids)}

        from concurrent.futures import ThreadPoolExecutor

        # Parallel Stage 1 & 2 & 3 extraction
        with ThreadPoolExecutor(max_workers=8) as ex:
            file_hashes = list(ex.map(compute_file_sha256, file_paths))
            pixel_hashes = list(ex.map(compute_decoded_pixel_sha256, file_paths))
            p_hashes = np.array(list(ex.map(compute_phash, file_paths)), dtype=bool)
            d_hashes = np.array(list(ex.map(compute_dhash, file_paths)), dtype=bool)

        ph_dists = pairwise_hamming_matrix(p_hashes)
        dh_dists = pairwise_hamming_matrix(d_hashes)
        perceptual_candidates = (ph_dists <= self.phash_threshold) | (dh_dists <= self.dhash_threshold)

        # Stage 4: Deep feature similarity matrices
        deep_candidates = np.zeros((n, n), dtype=bool)
        dinov2_cosines = None
        if dinov2_embeddings is not None:
            # L2 normalized dot products
            norms = np.linalg.norm(dinov2_embeddings, axis=1, keepdims=True)
            normed_d = dinov2_embeddings / np.maximum(norms, 1e-12)
            dinov2_cosines = np.dot(normed_d, normed_d.T)
            deep_candidates |= (dinov2_cosines >= self.dinov2_cosine_threshold)

        adapted_cosines = None
        if adapted_embeddings is not None:
            norms_a = np.linalg.norm(adapted_embeddings, axis=1, keepdims=True)
            normed_a = adapted_embeddings / np.maximum(norms_a, 1e-12)
            adapted_cosines = np.dot(normed_a, normed_a.T)
            deep_candidates |= (adapted_cosines >= self.adapted_cosine_threshold)

        # Parallel thumbnail caching for ultra-fast Stage 5 pixel verification
        def _load_thumb(fp):
            with Image.open(fp) as im:
                return np.asarray(im.convert("L").resize((512, 512), Image.Resampling.BILINEAR), dtype=np.float32)

        with ThreadPoolExecutor(max_workers=8) as ex:
            thumbnails = list(ex.map(_load_thumb, file_paths))

        results = []

        # Compare pairs (i < j)
        for i in range(n):
            id_i = image_ids[i]
            f_hash_i = file_hashes[i]
            p_hash_i = pixel_hashes[i]

            for j in range(i + 1, n):
                id_j = image_ids[j]
                f_hash_j = file_hashes[j]
                p_hash_j = pixel_hashes[j]

                # Check exact file
                if f_hash_i == f_hash_j:
                    results.append({
                        "image_id_1": id_i,
                        "image_id_2": id_j,
                        "match_type": "EXACT_FILE",
                        "phash_hamming": 0,
                        "dhash_hamming": 0,
                        "dinov2_cosine": 1.0,
                        "adapted_cosine": 1.0,
                        "ssim": 1.0,
                        "mae": 0.0,
                        "ncc": 1.0,
                        "stage_passed": 1,
                    })
                    continue

                # Check exact pixel
                if p_hash_i == p_hash_j:
                    results.append({
                        "image_id_1": id_i,
                        "image_id_2": id_j,
                        "match_type": "EXACT_PIXEL",
                        "phash_hamming": 0,
                        "dhash_hamming": 0,
                        "dinov2_cosine": 1.0,
                        "adapted_cosine": 1.0,
                        "ssim": 1.0,
                        "mae": 0.0,
                        "ncc": 1.0,
                        "stage_passed": 2,
                    })
                    continue

                passed_perceptual = bool(perceptual_candidates[i, j])
                passed_deep = bool(deep_candidates[i, j])
                ph_dist = int(ph_dists[i, j])
                dh_dist = int(dh_dists[i, j])
                dinov2_cos = float(dinov2_cosines[i, j]) if dinov2_cosines is not None else float("nan")
                adapted_cos = float(adapted_cosines[i, j]) if adapted_cosines is not None else float("nan")

                # Multi-stage screening before expensive pixel verification:
                # 1) Exact / near-exact perceptual match: ph_dist <= 2 and dh_dist <= 2
                # 2) High deep feature similarity: dinov2_cos >= 0.985 or adapted_cos >= 0.985
                # 3) Moderately tight perceptual match (ph_dist <= 4 or dh_dist <= 4) with visual consistency (dinov2_cos >= 0.92)
                should_verify = (
                    (ph_dist <= 2 and dh_dist <= 2)
                    or passed_deep
                    or ((ph_dist <= 4 or dh_dist <= 4) and (not np.isnan(dinov2_cos) and dinov2_cos >= 0.92))
                )

                if should_verify:
                    # Stage 5: Fast Pixel Verification on cached standardized arrays
                    pm = compute_pixel_metrics(thumbnails[i], thumbnails[j])
                    ssim_val = pm["ssim"]
                    mae_val = pm["mae"]
                    ncc_val = pm["ncc"]

                    is_near_dup = (
                        ssim_val >= self.min_ssim
                        and mae_val <= self.max_mae
                        and ncc_val >= self.min_ncc
                    )

                    match_type = (
                        "NEAR_DUPLICATE"
                        if is_near_dup
                        else "VISUALLY_SIMILAR_NON_DUPLICATE"
                    )

                    results.append({
                        "image_id_1": id_i,
                        "image_id_2": id_j,
                        "match_type": match_type,
                        "phash_hamming": int(ph_dist),
                        "dhash_hamming": int(dh_dist),
                        "dinov2_cosine": dinov2_cos if dinov2_cos is not None else float("nan"),
                        "adapted_cosine": adapted_cos if adapted_cos is not None else float("nan"),
                        "ssim": ssim_val,
                        "mae": mae_val,
                        "ncc": ncc_val,
                        "stage_passed": 5 if is_near_dup else 4,
                    })

        return pd.DataFrame(results)
