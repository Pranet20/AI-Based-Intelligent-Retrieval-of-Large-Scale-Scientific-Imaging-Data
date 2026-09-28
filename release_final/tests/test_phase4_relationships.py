"""Tests for Phase 4 relationship definitions and integrity rules."""

import pytest
import torch
import pandas as pd
import numpy as np

from src.adaptation.relationship_builder import RelationshipBuilder


def test_no_fabricated_roi_relationship():
    """Verify that RelationshipBuilder enforces that roi_id is strictly unique and non-fabricated."""
    # Synthetic df where roi_id is unique
    df_valid = pd.DataFrame({
        "image_id": [f"img_{i}" for i in range(10)],
        "roi_id": [f"roi_{i}" for i in range(10)],
        "specimen_id": ["AsCast"] * 5 + ["Q980"] * 5,
        "acquisition_id": ["acq1", "acq2"] * 5,
    })
    RelationshipBuilder.validate_no_fabricated_roi(df_valid)

    # Synthetic df where roi_id is reused across images (fabricated ROI correspondence)
    df_invalid = pd.DataFrame({
        "image_id": ["img_0", "img_1"],
        "roi_id": ["roi_common", "roi_common"],  # Reused ROI across images
        "specimen_id": ["AsCast", "AsCast"],
        "acquisition_id": ["acq1", "acq2"],
    })
    with pytest.raises(AssertionError, match="Integrity violation: roi_id has 1 unique values"):
        RelationshipBuilder.validate_no_fabricated_roi(df_invalid)


def test_build_batch_masks_acquisition_aware():
    """Verify positive, neutral, and negative masking in acquisition-aware SupCon."""
    # 4 samples:
    # 0: Material A, Acq 1
    # 1: Material A, Acq 2  (Positive for 0)
    # 2: Material A, Acq 1  (Same acq of same material: Neutral/masked for 0)
    # 3: Material B, Acq 2  (Negative for 0)
    mat_labels = torch.tensor([0, 0, 0, 1], dtype=torch.long)
    acq_labels = torch.tensor([1, 2, 1, 2], dtype=torch.long)

    pos_mask, valid_mask = RelationshipBuilder.build_batch_masks(
        material_labels=mat_labels,
        acquisition_labels=acq_labels,
        mask_same_acquisition=True,
    )

    # For Anchor 0:
    # Positives: only sample 1
    assert pos_mask[0, 0] == 0  # self is 0
    assert pos_mask[0, 1] == 1  # sample 1 is positive (same mat, diff acq)
    assert pos_mask[0, 2] == 0  # sample 2 is masked (same mat, same acq)
    assert pos_mask[0, 3] == 0  # sample 3 is negative (diff mat)

    # Valid comparisons in denominator for Anchor 0:
    assert valid_mask[0, 0] == 0  # self excluded
    assert valid_mask[0, 1] == 1  # positive included
    assert valid_mask[0, 2] == 0  # same-acq peer excluded from denominator
    assert valid_mask[0, 3] == 1  # negative included in denominator


def test_build_batch_masks_standard_supcon():
    """Verify standard SupCon treats all same-material samples as positive."""
    mat_labels = torch.tensor([0, 0, 0, 1], dtype=torch.long)
    acq_labels = torch.tensor([1, 2, 1, 2], dtype=torch.long)

    pos_mask, valid_mask = RelationshipBuilder.build_batch_masks(
        material_labels=mat_labels,
        acquisition_labels=acq_labels,
        mask_same_acquisition=False,
    )

    assert pos_mask[0, 1] == 1
    assert pos_mask[0, 2] == 1  # In standard SupCon, same-acq is also positive
    assert pos_mask[0, 3] == 0
    assert valid_mask[0, 2] == 1


def test_contrastive_loss_three_way_relationship_partition():
    """Explicitly verify the 3-way partition:
    1. Valid cross-acquisition same-material pair -> Positive (in pos_mask, in valid_mask)
    2. Same-material same-acquisition pair -> Neutral / Ignored (not in pos_mask, not in valid_mask)
    3. Different-material pair -> Negative (not in pos_mask, in valid_mask)
    """
    # Sample 0: Material 1, Acq A
    # Sample 1: Material 1, Acq B (Cross-acquisition positive for 0)
    # Sample 2: Material 1, Acq A (Same-acquisition peer for 0: MUST BE NEUTRAL/IGNORED, NOT NEGATIVE)
    # Sample 3: Material 2, Acq A (Different material: NEGATIVE for 0)
    mat_labels = torch.tensor([1, 1, 1, 2], dtype=torch.long)
    acq_labels = torch.tensor([10, 20, 10, 10], dtype=torch.long)

    pos_mask, valid_mask = RelationshipBuilder.build_batch_masks(
        material_labels=mat_labels,
        acquisition_labels=acq_labels,
        mask_same_acquisition=True,
    )

    # Check relation of sample 0 with all others:
    # Pair (0, 1): Positive
    assert pos_mask[0, 1] == 1.0, "Cross-acquisition same-material must be positive"
    assert valid_mask[0, 1] == 1.0, "Positive must be in valid denominator"

    # Pair (0, 2): Neutral / Ignored (MUST NOT be positive, and MUST NOT be negative in denominator)
    assert pos_mask[0, 2] == 0.0, "Same-acquisition peer must NOT be in positive numerator"
    assert valid_mask[0, 2] == 0.0, "Same-acquisition peer must NOT enter denominator as a negative"

    # Pair (0, 3): Negative
    assert pos_mask[0, 3] == 0.0, "Different-material must NOT be positive"
    assert valid_mask[0, 3] == 1.0, "Different-material MUST enter denominator as a negative"

