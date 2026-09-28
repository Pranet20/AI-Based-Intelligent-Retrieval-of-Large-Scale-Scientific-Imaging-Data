"""
Unit tests for Phase 6 Track C: Visual Novelty Intelligence and Zero-Leakage Enforcement.
"""

import numpy as np
import pytest

from src.integrity.novelty_detectors import (
    KNNNoveltyDetector,
    MeanKNNNoveltyDetector,
    LOFNoveltyDetector,
    IsolationForestNoveltyDetector,
    CentroidNoveltyDetector,
    MultiNoveltyEnsemble,
    assert_no_leakage_features,
)


def test_adversarial_leakage_prohibition():
    """Verify prohibited metadata columns raise immediate ValueError."""
    bad_features = ["magnification", "specimen_id", "detector"]
    with pytest.raises(ValueError, match="Zero-leakage violation"):
        assert_no_leakage_features(bad_features)

    safe_features = ["laplacian_variance", "shannon_entropy"]
    assert_no_leakage_features(safe_features)  # should not raise


def test_novelty_detectors_deterministic_scoring():
    """Verify all 5 novelty detectors produce deterministic, valid scores."""
    rng = np.random.RandomState(42)
    train_x = rng.randn(50, 16)
    # L2 normalize
    train_x = train_x / np.linalg.norm(train_x, axis=1, keepdims=True)

    test_x = rng.randn(10, 16)
    test_x = test_x / np.linalg.norm(test_x, axis=1, keepdims=True)

    detectors = {
        "knn": KNNNoveltyDetector(k=5),
        "mean_knn": MeanKNNNoveltyDetector(k=5),
        "lof": LOFNoveltyDetector(n_neighbors=10),
        "iforest": IsolationForestNoveltyDetector(random_state=42),
        "centroid": CentroidNoveltyDetector(),
    }

    for name, det in detectors.items():
        det.fit(train_x)
        s1 = det.score(test_x)
        s2 = det.score(test_x)
        assert np.array_equal(s1, s2), f"Detector {name} is not deterministic"
        assert not np.isnan(s1).any(), f"Detector {name} produced NaNs"
        assert not np.isinf(s1).any(), f"Detector {name} produced Infs"


def test_multi_novelty_ensemble_calibration():
    """Verify MultiNoveltyEnsemble calibrates on validation set and outputs composite score."""
    rng = np.random.RandomState(42)
    train_x = rng.randn(40, 16)
    val_x = rng.randn(20, 16)
    test_x = rng.randn(15, 16)

    ensemble = MultiNoveltyEnsemble(random_state=42, default_k=3)
    ensemble.fit(train_x)
    ensemble.calibrate(val_x)

    scores_df = ensemble.score_all(test_x)
    assert "composite_novelty_score" in scores_df.columns
    assert len(scores_df) == 15
    assert (scores_df["composite_novelty_score"] >= 0.0).all()
    assert (scores_df["composite_novelty_score"] <= 1.0).all()
