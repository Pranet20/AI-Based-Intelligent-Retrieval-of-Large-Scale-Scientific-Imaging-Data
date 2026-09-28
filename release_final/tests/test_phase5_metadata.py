"""Comprehensive unit tests for Phase 5 metadata feature extraction and leakage prevention."""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from src.metadata.phase5_features import (
    FEATURE_GROUPS,
    SAFE_CATEGORICAL_FIELDS,
    SAFE_NUMERICAL_FIELDS,
    Phase5FeaturePipeline,
    extract_metadata_fields,
)
from src.metadata.phase5_encoder import Phase5MetadataEncoder, normalize_l2
from src.metadata.phase5_validator import (
    PROHIBITED_FEATURE_NAMES,
    MetadataLeakageError,
    MetadataValidationError,
    validate_feature_names,
    validate_metadata_vectors,
)


@pytest.fixture
def synthetic_train_df() -> pd.DataFrame:
    """Create a controlled training DataFrame with known statistics."""
    records = []
    for i in range(20):
        records.append({
            "image_id": f"img_train_{i}",
            "filename": f"train_{i}.png",
            "specimen_id": "Material_A" if i < 10 else "Material_B",
            "sample": "Material_A" if i < 10 else "Material_B",
            "sample_id": f"sample_{i}",
            "roi_id": f"roi_{i}",
            "acquisition_id": f"acq_{i % 4}",
            "duplicate_group_id": None,
            "near_duplicate_group_id": None,
            "metadata_json": json.dumps({
                "normalized": {
                    "magnification": float(1000 + i * 100),
                    "pixel_size_nm": float(10.0 + i * 0.5),
                    "accelerating_voltage_kv": 10.0 if i % 2 == 0 else 20.0,
                    "beam_current_na": 1.5 + (i * 0.1),
                    "dwell_time_us": 10.0,
                    "working_distance_mm": 5.0 + (i * 0.2),
                    "chamber_pressure_pa": 0.001 + (i * 0.0001),
                    "detector": "SE" if i % 2 == 0 else "BSE",
                    "etching_agent": "Nital" if i < 10 else "Vilella",
                    "sample": "Material_A" if i < 10 else "Material_B",
                }
            })
        })
    return pd.DataFrame(records)


@pytest.fixture
def synthetic_test_df() -> pd.DataFrame:
    """Create a controlled test DataFrame with unseen values and missing values."""
    records = []
    for i in range(10):
        records.append({
            "image_id": f"img_test_{i}",
            "filename": f"test_{i}.png",
            "specimen_id": "Material_A",
            "sample": "Material_A",
            "sample_id": f"sample_test_{i}",
            "roi_id": f"roi_test_{i}",
            "acquisition_id": f"acq_test_{i}",
            "duplicate_group_id": None,
            "near_duplicate_group_id": None,
            "metadata_json": json.dumps({
                "normalized": {
                    "magnification": float(5000 + i * 500) if i != 0 else None,  # test missingness
                    "pixel_size_nm": float(50.0 + i) if i != 1 else np.nan,      # test missingness
                    "accelerating_voltage_kv": 100.0,  # extreme unseen numerical
                    "beam_current_na": 50.0,
                    "dwell_time_us": 10.0,
                    "working_distance_mm": 15.0,
                    "chamber_pressure_pa": 0.05,
                    "detector": "InLens" if i == 0 else "SE",  # InLens is UNKNOWN to train!
                    "etching_agent": "Kalling" if i == 0 else "Nital",  # Kalling is UNKNOWN!
                    "sample": "Material_A",
                }
            })
        })
    return pd.DataFrame(records)


# TEST 1: specimen_id cannot enter metadata features
def test_1_specimen_id_cannot_enter_features(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)
    _, feat_names = encoder.encode(synthetic_train_df)
    for name in feat_names:
        assert "specimen" not in name.lower(), f"Leakage: 'specimen' found in feature '{name}'"


# TEST 2: acquisition_id cannot enter metadata features
def test_2_acquisition_id_cannot_enter_features(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)
    _, feat_names = encoder.encode(synthetic_train_df)
    for name in feat_names:
        assert "acquisition" not in name.lower(), f"Leakage: 'acquisition' found in feature '{name}'"


# TEST 3: roi_id cannot enter metadata features
def test_3_roi_id_cannot_enter_features(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)
    _, feat_names = encoder.encode(synthetic_train_df)
    for name in feat_names:
        assert "roi" not in name.lower(), f"Leakage: 'roi' found in feature '{name}'"


# TEST 4: image_id cannot enter metadata features
def test_4_image_id_cannot_enter_features(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)
    _, feat_names = encoder.encode(synthetic_train_df)
    for name in feat_names:
        assert "image_id" not in name.lower(), f"Leakage: 'image_id' found in feature '{name}'"


# TEST 5: filename cannot enter metadata features
def test_5_filename_cannot_enter_features(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)
    _, feat_names = encoder.encode(synthetic_train_df)
    for name in feat_names:
        assert "filename" not in name.lower(), f"Leakage: 'filename' found in feature '{name}'"


# TEST 6: training-only numerical statistics
def test_6_training_only_numerical_statistics(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    pipe = Phase5FeaturePipeline(feature_group="A")
    pipe.fit(synthetic_train_df)
    
    # Check that means match train_df exactly
    extracted = extract_metadata_fields(synthetic_train_df)
    expected_mag_mean = float(extracted["magnification"].mean())
    expected_mag_std = float(extracted["magnification"].std(ddof=0))
    expected_mag_med = float(extracted["magnification"].median())

    assert np.isclose(pipe.num_means["magnification"], expected_mag_mean)
    assert np.isclose(pipe.num_stds["magnification"], expected_mag_std)
    assert np.isclose(pipe.num_medians["magnification"], expected_mag_med)


# TEST 7: test data cannot modify mean/std/median
def test_7_test_data_cannot_modify_statistics(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    pipe = Phase5FeaturePipeline(feature_group="E")
    pipe.fit(synthetic_train_df)
    
    initial_means = dict(pipe.num_means)
    initial_stds = dict(pipe.num_stds)
    initial_medians = dict(pipe.num_medians)

    # Transform test set multiple times
    _ = pipe.transform(synthetic_test_df)
    _ = pipe.transform(synthetic_test_df)

    assert pipe.num_means == initial_means
    assert pipe.num_stds == initial_stds
    assert pipe.num_medians == initial_medians


# TEST 8: training-only category vocabulary
def test_8_training_only_category_vocabulary(synthetic_train_df: pd.DataFrame) -> None:
    pipe = Phase5FeaturePipeline(feature_group="C")  # detector
    pipe.fit(synthetic_train_df)

    # In train_df, detector only has SE and BSE
    assert pipe.cat_vocabularies["detector"] == ["BSE", "SE"]


# TEST 9: unknown test category handling
def test_9_unknown_test_category_handling(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    pipe = Phase5FeaturePipeline(feature_group="C")
    pipe.fit(synthetic_train_df)
    feats, names = pipe.transform(synthetic_test_df)

    # Check detector_unknown column exists
    assert "detector_unknown" in names
    idx_unk = names.index("detector_unknown")
    idx_se = names.index("detector_SE")

    # In synthetic_test_df, row 0 has InLens (unknown), row 1 has SE (known)
    assert feats[0, idx_unk] == 1.0
    assert feats[0, idx_se] == 0.0

    assert feats[1, idx_unk] == 0.0
    assert feats[1, idx_se] == 1.0


# TEST 10: missing numerical value handling (median imputation)
def test_10_missing_numerical_value_handling(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    pipe = Phase5FeaturePipeline(feature_group="A")
    pipe.fit(synthetic_train_df)
    feats, names = pipe.transform(synthetic_test_df)

    # In synthetic_test_df, row 0 has magnification = None
    mag_scaled_idx = names.index("magnification_scaled")
    # Imputed with train median: (median - mean) / std
    expected_imputed_scaled = (pipe.num_medians["magnification"] - pipe.num_means["magnification"]) / pipe.num_stds["magnification"]
    assert np.isclose(feats[0, mag_scaled_idx], expected_imputed_scaled)


# TEST 11: missingness indicator
def test_11_missingness_indicator(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    pipe = Phase5FeaturePipeline(feature_group="A")
    pipe.fit(synthetic_train_df)
    feats, names = pipe.transform(synthetic_test_df)

    mag_miss_idx = names.index("magnification_missing")
    assert feats[0, mag_miss_idx] == 1.0  # missing
    assert feats[1, mag_miss_idx] == 0.0  # present


# TEST 12: metadata vectors deterministic
def test_12_metadata_vectors_deterministic(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)

    feats1, names1 = encoder.encode(synthetic_train_df)
    feats2, names2 = encoder.encode(synthetic_train_df)

    assert names1 == names2
    np.testing.assert_array_equal(feats1, feats2)


# TEST 13: metadata vectors have no NaN
def test_13_metadata_vectors_have_no_nan(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)

    feats_train, _ = encoder.encode(synthetic_train_df)
    feats_test, _ = encoder.encode(synthetic_test_df)

    assert not np.isnan(feats_train).any()
    assert not np.isnan(feats_test).any()


# TEST 14: metadata vectors have no Inf
def test_14_metadata_vectors_have_no_inf(
    synthetic_train_df: pd.DataFrame,
    synthetic_test_df: pd.DataFrame,
) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)

    feats_train, _ = encoder.encode(synthetic_train_df)
    feats_test, _ = encoder.encode(synthetic_test_df)

    assert not np.isinf(feats_train).any()
    assert not np.isinf(feats_test).any()


# TEST 15: cosine metadata similarity deterministic
def test_15_cosine_similarity_deterministic(synthetic_train_df: pd.DataFrame) -> None:
    encoder = Phase5MetadataEncoder(feature_group="E")
    encoder.fit(synthetic_train_df)
    feats, _ = encoder.encode(synthetic_train_df)

    sim1 = encoder.compute_similarity_matrix(feats)
    sim2 = encoder.compute_similarity_matrix(feats)

    np.testing.assert_array_equal(sim1, sim2)
    assert np.all(sim1 >= -1.0 - 1e-6)
    assert np.all(sim1 <= 1.0 + 1e-6)


# SECTION 37 LEAKAGE REGRESSION TEST (adversarial metadata table)
def test_adversarial_leakage_regression() -> None:
    """Deliberately try to pass forbidden identifiers and assert immediate failure."""
    adversarial_feature_names = [
        "specimen_id",
        "acquisition_id",
        "roi_id",
        "image_id",
        "filename",
        "sample",
        "duplicate_group_id",
    ]
    for bad_name in adversarial_feature_names:
        with pytest.raises(MetadataLeakageError):
            validate_feature_names([bad_name])
            
        with pytest.raises(MetadataLeakageError):
            validate_feature_names([f"prefix_{bad_name}"])


def test_etching_agent_target_independence() -> None:
    """Verify that etching_agent is statistically independent from specimen_id and cannot act as a proxy."""
    from scipy.stats import chi2_contingency
    hcci_path = Path("data/manifests/hcci_manifest.parquet")
    assert hcci_path.exists()
    df = pd.read_parquet(hcci_path)
    parsed = df["metadata_json"].apply(json.loads).tolist()
    etching = [p.get("normalized", {}).get("etching_agent") for p in parsed]
    df["etching_agent"] = etching

    ct = pd.crosstab(df["specimen_id"], df["etching_agent"])
    chi2, p_val, dof, _ = chi2_contingency(ct)
    
    # Assert independence (p-value > 0.05 indicates no statistically significant association)
    assert p_val > 0.05, f"etching_agent correlates with specimen_id: p={p_val:.4f}"
    # Verify exact balanced counts
    assert ct.loc["AsCast", "Nital"] == 132
    assert ct.loc["AsCast", "Vilella"] == 128

