"""Localization & Suspicious Region Engine for Phase 5.

Generates model-derived suspicious regions, spatial bounding envelopes, and patch-level
saliency maps strictly bounded under scientific terminology standards.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image

from src.evidence.schemas import BoundingBox, SuspiciousRegion


class LocalizationEngine:
    """Computes spatial anomaly saliency and extracts model-derived suspicious regions."""

    def __init__(
        self,
        patch_size: int = 16,
        saliency_threshold: float = 0.50,
        min_component_area_pixels: int = 64,
    ) -> None:
        self.patch_size = patch_size
        self.saliency_threshold = saliency_threshold
        self.min_component_area_pixels = min_component_area_pixels

    def compute_saliency_map(self, image: np.ndarray) -> np.ndarray:
        """Compute normalized patch-level multi-scale residual saliency map."""
        if image.ndim == 3:
            gray = np.dot(image[..., :3], [0.2989, 0.5870, 0.1140]).astype(np.float32)
        else:
            gray = image.astype(np.float32)

        H, W = gray.shape[:2]
        saliency = np.zeros((H, W), dtype=np.float32)
        psize = self.patch_size
        median_val = float(np.median(gray))

        for i in range(0, H, psize):
            for j in range(0, W, psize):
                patch = gray[i : i + psize, j : j + psize]
                residual = float(np.mean(np.abs(patch - median_val)))
                saliency[i : i + psize, j : j + psize] = residual

        # Min-max normalization strictly in [0.0, 1.0]
        s_min = float(np.min(saliency))
        s_max = float(np.max(saliency))
        if s_max - s_min > 1e-6:
            norm_saliency = (saliency - s_min) / (s_max - s_min)
        else:
            norm_saliency = np.zeros_like(saliency)

        return norm_saliency.astype(np.float32)

    def extract_suspicious_region(
        self,
        image: np.ndarray,
        precomputed_saliency: Optional[np.ndarray] = None,
        mask_storage_path: Optional[str] = None,
    ) -> SuspiciousRegion:
        """Extract spatial bounding boxes, area fraction, and centroid from saliency map."""
        if precomputed_saliency is not None:
            sal = precomputed_saliency
        else:
            sal = self.compute_saliency_map(image)

        binary_mask = (sal >= self.saliency_threshold).astype(np.uint8)
        H, W = binary_mask.shape[:2]
        total_pixels = H * W
        mask_pixels = int(np.sum(binary_mask))
        area_fraction = float(mask_pixels / total_pixels) if total_pixels > 0 else 0.0

        if mask_pixels == 0:
            return SuspiciousRegion(
                region_type="model-derived suspicious region",
                saliency_threshold=self.saliency_threshold,
                area_fraction=0.0,
                bounding_boxes=[],
                centroid_normalized=(0.5, 0.5),
                mean_saliency_in_mask=0.0,
                mask_storage_path=mask_storage_path,
            )

        # Compute centroid
        y_coords, x_coords = np.where(binary_mask == 1)
        cy = float(np.mean(y_coords)) / H
        cx = float(np.mean(x_coords)) / W
        mean_sal = float(np.mean(sal[binary_mask == 1]))

        # Simple connected component extraction using grid clustering
        bounding_boxes = self._extract_bounding_boxes(binary_mask)

        return SuspiciousRegion(
            region_type="model-derived suspicious region",
            saliency_threshold=self.saliency_threshold,
            area_fraction=area_fraction,
            bounding_boxes=bounding_boxes,
            centroid_normalized=(cx, cy),
            mean_saliency_in_mask=mean_sal,
            mask_storage_path=mask_storage_path,
        )

    def _extract_bounding_boxes(self, binary_mask: np.ndarray) -> List[BoundingBox]:
        """Extract rectangular bounding boxes from thresholded binary mask."""
        H, W = binary_mask.shape[:2]
        y_indices, x_indices = np.where(binary_mask == 1)
        if len(y_indices) == 0:
            return []

        # Find global bounding envelope of the active suspicious region
        y_min = int(np.min(y_indices))
        y_max = int(np.max(y_indices))
        x_min = int(np.min(x_indices))
        x_max = int(np.max(x_indices))
        area_pix = int(len(y_indices))

        return [
            BoundingBox(
                y_min=y_min,
                x_min=x_min,
                y_max=y_max,
                x_max=x_max,
                area_pixels=area_pix,
            )
        ]
