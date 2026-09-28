"""Relationship builder for constructing and validating Phase 4 positive/negative relationships."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
import torch

from src.utils.logging import get_logger

logger = get_logger("adaptation.relationship_builder")


class RelationshipBuilder:
    """Builds and validates scientifically grounded positive, negative, and exclusion masks."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def validate_no_fabricated_roi(
        metadata_df: pd.DataFrame,
    ) -> None:
        """Verify that roi_id is strictly unique and never used as a cross-acquisition positive pair key."""
        if "roi_id" in metadata_df.columns:
            unique_rois = metadata_df["roi_id"].nunique()
            total_images = len(metadata_df)
            assert unique_rois == total_images, (
                f"Integrity violation: roi_id has {unique_rois} unique values for {total_images} images. "
                "roi_id must not be used to infer cross-acquisition physical ROI correspondence."
            )

    @staticmethod
    def build_batch_masks(
        material_labels: torch.Tensor,
        acquisition_labels: torch.Tensor,
        mask_same_acquisition: bool = True,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Construct positive and valid-comparison masks for a mini-batch of embeddings.

        Args:
            material_labels: 1D Tensor of integer material/specimen IDs of shape (B,).
            acquisition_labels: 1D Tensor of integer acquisition condition IDs of shape (B,).
            mask_same_acquisition: Whether to exclude same-acquisition pairs of the same material from positive numerator.

        Returns:
            pos_mask: Binary Tensor (B, B) where pos_mask[i, j] = 1 iff (i, j) is a valid positive pair.
            valid_mask: Binary Tensor (B, B) where valid_mask[i, j] = 1 iff j is a valid comparison for anchor i.
        """
        B = material_labels.shape[0]
        device = material_labels.device

        # Self-mask: diagonal is 0
        diag_mask = ~torch.eye(B, dtype=torch.bool, device=device)

        # Same material mask: M_i == M_j
        same_material = (material_labels.unsqueeze(0) == material_labels.unsqueeze(1)) & diag_mask

        # Different acquisition mask: A_i != A_j
        diff_acquisition = acquisition_labels.unsqueeze(0) != acquisition_labels.unsqueeze(1)

        # Same acquisition mask: A_i == A_j
        same_acquisition = (acquisition_labels.unsqueeze(0) == acquisition_labels.unsqueeze(1)) & diag_mask

        if mask_same_acquisition:
            # Positive: same material AND different acquisition
            pos_mask = (same_material & diff_acquisition).float()
            # Valid comparison in denominator: exclude same-material same-acquisition peers
            # so they do not act as negatives, while keeping all cross-material negatives
            neutral_mask = same_material & same_acquisition
            valid_mask = (diag_mask & ~neutral_mask).float()
        else:
            # Standard SupCon (all same material are positive)
            pos_mask = same_material.float()
            valid_mask = diag_mask.float()

        return pos_mask, valid_mask

    @staticmethod
    def build_retrieval_ground_truth(
        df: pd.DataFrame,
    ) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        """Build exact retrieval ground-truth positives and exclusion sets for a dataset or split."""
        RelationshipBuilder.validate_no_fabricated_roi(df)

        image_ids = df["image_id"].tolist()
        specimens = df["specimen_id"].tolist()
        acquisitions = df["acquisition_id"].tolist()
        dup_groups = df.get("duplicate_group_id", [None] * len(df))
        near_groups = df.get("near_duplicate_group_id", [None] * len(df))
        hashes = df.get("sha256", [None] * len(df))

        meta = {}
        for i, img_id in enumerate(image_ids):
            meta[img_id] = {
                "specimen": specimens[i],
                "acquisition": acquisitions[i],
                "dup_group": dup_groups[i] if dup_groups is not None else None,
                "near_group": near_groups[i] if near_groups is not None else None,
                "sha256": hashes[i] if hashes is not None else None,
            }

        ground_truth: Dict[str, Set[str]] = {}
        exclusions: Dict[str, Set[str]] = {}

        for q_id in image_ids:
            q_spec = meta[q_id]["specimen"]
            q_acq = meta[q_id]["acquisition"]
            q_dup = meta[q_id]["dup_group"]
            q_near = meta[q_id]["near_group"]
            q_hash = meta[q_id]["sha256"]

            positives: Set[str] = set()
            excl_set: Set[str] = set()

            for c_id in image_ids:
                if c_id == q_id:
                    continue
                c_spec = meta[c_id]["specimen"]
                c_acq = meta[c_id]["acquisition"]
                c_dup = meta[c_id]["dup_group"]
                c_near = meta[c_id]["near_group"]
                c_hash = meta[c_id]["sha256"]

                is_dup = (
                    (q_dup is not None and c_dup is not None and q_dup == c_dup)
                    or (q_hash is not None and c_hash is not None and q_hash == c_hash)
                    or (q_near is not None and c_near is not None and q_near == c_near)
                )

                if is_dup:
                    excl_set.add(c_id)
                    continue

                if c_spec == q_spec and c_acq == q_acq:
                    excl_set.add(c_id)
                    continue

                if c_spec == q_spec and c_acq != q_acq:
                    positives.add(c_id)

            ground_truth[q_id] = positives
            exclusions[q_id] = excl_set

        return ground_truth, exclusions
