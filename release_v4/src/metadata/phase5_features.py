"""Feature extraction, training-only scaling, and categorical encoding for Phase 5."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple
import numpy as np
import pandas as pd

from src.metadata.phase5_validator import validate_feature_names, validate_metadata_vectors
from src.utils.logging import get_logger

logger = get_logger("metadata.phase5_features")

# Approved safe metadata fields
SAFE_NUMERICAL_FIELDS: List[str] = [
    "magnification",
    "pixel_size_nm",
    "accelerating_voltage_kv",
    "beam_current_na",
    "dwell_time_us",
    "working_distance_mm",
    "chamber_pressure_pa",
]

SAFE_CATEGORICAL_FIELDS: List[str] = [
    "detector",
    "etching_agent",
]

# Scientific feature groups
FEATURE_GROUPS: Dict[str, List[str]] = {
    "A": ["magnification", "pixel_size_nm"],  # Imaging Geometry
    "B": ["accelerating_voltage_kv", "beam_current_na", "dwell_time_us"],  # Beam Parameters
    "C": ["detector"],  # Detector Configuration
    "D": ["chamber_pressure_pa", "working_distance_mm"],  # Chamber Environment
    "E": [  # Full Safe Scientific Metadata
        "magnification",
        "pixel_size_nm",
        "accelerating_voltage_kv",
        "beam_current_na",
        "dwell_time_us",
        "detector",
        "chamber_pressure_pa",
        "working_distance_mm",
        "etching_agent",
    ],
}


def extract_metadata_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Extract flat normalized metadata fields from a manifest DataFrame.
    
    If 'metadata_json' column is present, parses JSON and unpacks 'normalized'.
    Otherwise, uses columns directly if already present.
    """
    if "metadata_json" in df.columns:
        parsed_records = []
        for val in df["metadata_json"]:
            if isinstance(val, str):
                try:
                    d = json.loads(val)
                    parsed_records.append(d.get("normalized", {}))
                except Exception:
                    parsed_records.append({})
            elif isinstance(val, dict):
                parsed_records.append(val.get("normalized", val))
            else:
                parsed_records.append({})
        extracted_df = pd.DataFrame(parsed_records, index=df.index)
    else:
        extracted_df = df.copy()

    # Ensure all approved safe fields exist in extracted_df (fill with NaN if absent)
    for field in SAFE_NUMERICAL_FIELDS + SAFE_CATEGORICAL_FIELDS:
        if field not in extracted_df.columns:
            extracted_df[field] = np.nan

    return extracted_df


class Phase5FeaturePipeline:
    """Deterministic, leakage-safe metadata feature pipeline.
    
    All scaling parameters, medians, and categorical vocabularies are fitted
    strictly on the training partition.
    """

    def __init__(self, feature_group: str = "E") -> None:
        if feature_group not in FEATURE_GROUPS:
            raise ValueError(f"Unknown feature group '{feature_group}'. Available: {list(FEATURE_GROUPS.keys())}")
        self.feature_group = feature_group
        self.active_fields = FEATURE_GROUPS[feature_group]
        
        self.numerical_fields = [f for f in self.active_fields if f in SAFE_NUMERICAL_FIELDS]
        self.categorical_fields = [f for f in self.active_fields if f in SAFE_CATEGORICAL_FIELDS]
        
        # Training-fitted statistics
        self.is_fitted = False
        self.num_means: Dict[str, float] = {}
        self.num_stds: Dict[str, float] = {}
        self.num_medians: Dict[str, float] = {}
        self.cat_vocabularies: Dict[str, List[str]] = {}
        self.fitted_feature_names: List[str] = []

    def fit(self, train_manifest: pd.DataFrame) -> "Phase5FeaturePipeline":
        """Compute training statistics strictly from the training partition.
        
        Args:
            train_manifest: DataFrame representing the training partition.
        """
        train_df = extract_metadata_fields(train_manifest)

        # Fit numerical statistics
        self.num_means.clear()
        self.num_stds.clear()
        self.num_medians.clear()

        for field in self.numerical_fields:
            vals = pd.to_numeric(train_df[field], errors="coerce")
            valid = vals.dropna()
            if len(valid) == 0:
                mean_val = 0.0
                std_val = 1.0
                median_val = 0.0
            else:
                mean_val = float(valid.mean())
                std_val = float(valid.std(ddof=0))
                median_val = float(valid.median())
                if std_val == 0.0 or np.isnan(std_val):
                    std_val = 1.0  # Constant field protection; avoid div by zero

            self.num_means[field] = mean_val
            self.num_stds[field] = std_val
            self.num_medians[field] = median_val

        # Fit categorical vocabularies (sorted for deterministic column ordering)
        self.cat_vocabularies.clear()
        for field in self.categorical_fields:
            vals = train_df[field].dropna().astype(str).tolist()
            vocab = sorted(list(set(vals)))
            self.cat_vocabularies[field] = vocab

        # Determine feature names ordering
        feature_names: List[str] = []
        for field in self.numerical_fields:
            feature_names.append(f"{field}_scaled")
            feature_names.append(f"{field}_missing")

        for field in self.categorical_fields:
            for cat in self.cat_vocabularies[field]:
                feature_names.append(f"{field}_{cat}")
            feature_names.append(f"{field}_unknown")

        # Validate feature names against forbidden leakage identifiers
        validate_feature_names(feature_names)
        self.fitted_feature_names = feature_names
        self.is_fitted = True

        logger.info(
            f"Fitted Phase5FeaturePipeline for Group {self.feature_group}: "
            f"{len(self.fitted_feature_names)} features ({len(self.numerical_fields)} num, "
            f"{len(self.categorical_fields)} cat)."
        )
        return self

    def transform(self, manifest: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Transform metadata into normalized numerical feature vectors.
        
        Args:
            manifest: DataFrame to transform.
            
        Returns:
            Tuple of (features_array, feature_names) where features_array is (N, D).
        """
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before transform.")

        df = extract_metadata_fields(manifest)
        N = len(df)
        cols_data: List[np.ndarray] = []

        # 1. Numerical features: scaling + missingness indicator
        for field in self.numerical_fields:
            vals = pd.to_numeric(df[field], errors="coerce").values
            is_missing = np.isnan(vals)
            
            # Impute missing with training median
            imputed = vals.copy()
            imputed[is_missing] = self.num_medians[field]

            # Scale using training mean and std
            scaled = (imputed - self.num_means[field]) / self.num_stds[field]

            cols_data.append(scaled.reshape(N, 1))
            cols_data.append(is_missing.astype(np.float32).reshape(N, 1))

        # 2. Categorical features: one-hot encoding with unknown handling
        for field in self.categorical_fields:
            vals = df[field].astype(str).values
            is_na = df[field].isna().values
            vocab = self.cat_vocabularies[field]
            
            # Create indicator columns for known categories
            matched_any = np.zeros(N, dtype=bool)
            for cat in vocab:
                is_cat = (vals == cat) & (~is_na)
                matched_any = matched_any | is_cat
                cols_data.append(is_cat.astype(np.float32).reshape(N, 1))

            # Unknown indicator: True if value is not in training vocab or is NA
            is_unknown = (~matched_any).astype(np.float32).reshape(N, 1)
            cols_data.append(is_unknown)

        if not cols_data:
            # Empty feature group (e.g. visual-only)
            features = np.zeros((N, 0), dtype=np.float32)
        else:
            features = np.hstack(cols_data).astype(np.float32)

        # Validate output matrix
        validate_metadata_vectors(features, self.fitted_feature_names)

        return features, list(self.fitted_feature_names)

    def get_provenance(self) -> Dict[str, Any]:
        """Return parameters and provenance for reproduction logging."""
        if not self.is_fitted:
            raise RuntimeError("Pipeline must be fitted before exporting provenance.")
        return {
            "feature_group": self.feature_group,
            "active_fields": self.active_fields,
            "numerical_fields": self.numerical_fields,
            "categorical_fields": self.categorical_fields,
            "means": self.num_means,
            "stds": self.num_stds,
            "medians": self.num_medians,
            "vocabularies": self.cat_vocabularies,
            "feature_names": self.fitted_feature_names,
            "feature_dimension": len(self.fitted_feature_names),
        }
