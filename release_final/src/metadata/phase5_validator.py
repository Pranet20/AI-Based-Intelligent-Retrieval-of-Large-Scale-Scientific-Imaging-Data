"""Strict validation and leakage auditing for Phase 5 metadata features."""

from __future__ import annotations

import re
from typing import List, Sequence, Set
import numpy as np

# Forbidden field names that must NEVER appear in feature representations
PROHIBITED_FEATURE_NAMES: Set[str] = {
    "specimen_id",
    "specimen",
    "sample_id",
    "sample",
    "roi_id",
    "roi",
    "image_id",
    "filename",
    "acquisition_id",
    "acquisition",
    "duplicate_group_id",
    "near_duplicate_group_id",
    "group_id",
    "label",
    "source_label",
    "sha256",
    "relative_path",
    "absolute_path_if_local_only",
    "target",
    "ground_truth",
}


class MetadataLeakageError(ValueError):
    """Raised when an excluded or leakage-prone field is detected in metadata features."""
    pass


class MetadataValidationError(ValueError):
    """Raised when metadata vectors fail numeric or consistency checks."""
    pass


def validate_feature_names(feature_names: Sequence[str]) -> None:
    """Verify that no feature name contains or matches any forbidden identifier.
    
    Args:
        feature_names: Sequence of feature name strings.
        
    Raises:
        MetadataLeakageError: If any prohibited identifier is found.
    """
    for name in feature_names:
        clean_name = name.strip().lower()
        # Direct match check
        if clean_name in PROHIBITED_FEATURE_NAMES:
            raise MetadataLeakageError(
                f"Leakage violation: Forbidden field '{name}' detected in feature set."
            )
        # Prefix/component check
        for prohibited in PROHIBITED_FEATURE_NAMES:
            pattern = rf"(^|_{{1,2}}){re.escape(prohibited)}($|_{{1,2}})"
            if re.search(pattern, clean_name):
                raise MetadataLeakageError(
                    f"Leakage violation: Substring/token '{prohibited}' matched in feature '{name}'."
                )


def validate_metadata_vectors(vectors: np.ndarray, feature_names: Sequence[str]) -> None:
    """Verify numeric sanity of metadata feature vectors.
    
    Args:
        vectors: 2D numpy array of shape (N, D).
        feature_names: List of D feature names.
        
    Raises:
        MetadataValidationError: If NaN, Inf, or shape mismatches are detected.
    """
    if not isinstance(vectors, np.ndarray):
        raise MetadataValidationError(f"Expected numpy ndarray, got {type(vectors)}")
    if vectors.ndim != 2:
        raise MetadataValidationError(f"Expected 2D array (N, D), got shape {vectors.shape}")
    N, D = vectors.shape
    if len(feature_names) != D:
        raise MetadataValidationError(
            f"Dimension mismatch: feature names count ({len(feature_names)}) != vector dimension ({D})"
        )
    if np.isnan(vectors).any():
        raise MetadataValidationError("Metadata feature matrix contains NaN values.")
    if np.isinf(vectors).any():
        raise MetadataValidationError("Metadata feature matrix contains Inf values.")
