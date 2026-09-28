"""Duplicate Detection Cascade Engine."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image

from src.integrity.duplicate_cascade import compute_ssim
from src.integrity.exact_duplicates import (
    compute_file_sha256,
    compute_decoded_pixel_sha256,
)
from src.integrity.perceptual_hash import (
    compute_phash,
    compute_dhash,
    hamming_distance,
)


class DuplicateEngine:
    """Multi-stage duplicate detection cascade."""

    @staticmethod
    def compute_hashes(image_path: Union[str, Path]) -> Dict[str, str]:
        """Compute SHA-256, pHash, and dHash strings for an image."""
        sha = compute_file_sha256(image_path)
        ph = compute_phash(image_path)
        dh = compute_dhash(image_path)
        # Convert bool array to hex string
        ph_str = "".join(["1" if b else "0" for b in ph])
        dh_str = "".join(["1" if b else "0" for b in dh])
        return {
            "sha256": sha,
            "phash": ph_str,
            "dhash": dh_str,
        }

    @classmethod
    def check_duplicate_against_candidates(
        cls,
        new_image_path: Union[str, Path],
        new_sha256: str,
        new_phash: str,
        new_dhash: str,
        new_dinov2_vec: np.ndarray,
        new_adapted_vec: np.ndarray,
        candidates: List[Dict[str, Any]],  # List of existing image dicts with hashes, vectors, paths
    ) -> Dict[str, Any]:
        """
        Evaluate candidate images through the cascade:
        1. Exact SHA-256 match
        2. Exact decoded pixel match
        3. pHash / dHash Hamming distance <= 10
        4. DINOv2 cosine similarity >= 0.985
        5. Phase 4 adapted cosine similarity >= 0.985
        6. Pixel SSIM verification >= 0.95
        """
        for cand in candidates:
            cand_id = cand["id"]
            cand_path = cand["storage_path"]
            cand_sha = cand.get("sha256")
            cand_phash = cand.get("phash")
            cand_dhash = cand.get("dhash")
            cand_dino = cand.get("dinov2_vector")
            cand_adapt = cand.get("adapted_vector")

            # Stage 1: File SHA-256
            if new_sha256 and cand_sha and new_sha256 == cand_sha:
                return {
                    "duplicate_status": "EXACT_DUPLICATE",
                    "matched_image_id": cand_id,
                    "similarity_score": 1.0,
                    "match_stage": "STAGE_1_FILE_SHA256",
                }

            # Stage 2: Decoded Pixel SHA-256
            if Path(cand_path).exists():
                pix1 = compute_decoded_pixel_sha256(new_image_path)
                pix2 = compute_decoded_pixel_sha256(cand_path)
                if pix1 == pix2:
                    return {
                        "duplicate_status": "EXACT_DUPLICATE",
                        "matched_image_id": cand_id,
                        "similarity_score": 1.0,
                        "match_stage": "STAGE_2_PIXEL_SHA256",
                    }

            # Stage 3: Perceptual Hash
            if new_phash and cand_phash and new_dhash and cand_dhash:
                h_ph = sum(c1 != c2 for c1, c2 in zip(new_phash, cand_phash))
                h_dh = sum(c1 != c2 for c1, c2 in zip(new_dhash, cand_dhash))
                if h_ph <= 10 or h_dh <= 10:
                    # Stage 4: DINOv2 Cosine Similarity
                    if cand_dino is not None:
                        dino_sim = float(np.dot(new_dinov2_vec, cand_dino))
                        if dino_sim >= 0.985:
                            # Stage 5: Adapted Cosine Similarity
                            if cand_adapt is not None:
                                adapt_sim = float(np.dot(new_adapted_vec, cand_adapt))
                                if adapt_sim >= 0.985:
                                    # Stage 6: Pixel SSIM
                                    if Path(cand_path).exists():
                                        ssim_val = compute_ssim(new_image_path, cand_path)
                                        if ssim_val >= 0.95:
                                            return {
                                                "duplicate_status": "POTENTIAL_NEAR_DUPLICATE",
                                                "matched_image_id": cand_id,
                                                "similarity_score": float(ssim_val),
                                                "match_stage": "STAGE_6_PIXEL_SSIM",
                                            }

        return {
            "duplicate_status": "NO_DECLARED_REDUNDANCY_DETECTED",
            "matched_image_id": None,
            "similarity_score": None,
            "match_stage": None,
        }
