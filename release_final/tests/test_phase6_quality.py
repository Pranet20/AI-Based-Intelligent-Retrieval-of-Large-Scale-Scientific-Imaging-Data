"""
Unit tests for Phase 6 Track B: Measurable Image-Quality Degradation Indicators.
"""

import numpy as np
import pytest
from PIL import Image

from src.integrity.quality_indicators import (
    compute_laplacian_variance,
    compute_edge_density,
    compute_shannon_entropy,
    compute_dynamic_range,
    compute_clipping_ratios,
    compute_high_freq_fft_ratio,
    compute_all_quality_metrics,
    QualityRiskEvaluator,
)


def test_laplacian_variance_sharp_vs_flat():
    """Verify sharp checkerboard has much higher Laplacian variance than flat image."""
    flat = np.full((128, 128), 128, dtype=np.uint8)
    sharp = np.zeros((128, 128), dtype=np.uint8)
    sharp[::2, ::2] = 255
    sharp[1::2, 1::2] = 255

    var_flat = compute_laplacian_variance(flat)
    var_sharp = compute_laplacian_variance(sharp)
    assert var_flat == pytest.approx(0.0, abs=1e-5)
    assert var_sharp > 1000.0


def test_shannon_entropy_constant_vs_uniform():
    """Verify constant field has 0 entropy while uniform noise has near maximal entropy."""
    flat = np.full((100, 100), 50, dtype=np.uint8)
    ent_flat = compute_shannon_entropy(flat)
    assert ent_flat == pytest.approx(0.0, abs=1e-5)

    noise = np.arange(256, dtype=np.uint8).repeat(100).reshape(160, 160)
    ent_noise = compute_shannon_entropy(noise)
    assert ent_noise > 7.9


def test_clipping_ratios_extremes():
    """Verify clipping ratio detects saturated and under-exposed pixels accurately."""
    arr = np.zeros((100, 100), dtype=np.uint8)
    arr[:25, :] = 0
    arr[25:50, :] = 255
    arr[50:, :] = 128

    clip = compute_clipping_ratios(arr)
    assert clip["under_exposure_ratio"] == pytest.approx(0.25, abs=1e-4)
    assert clip["over_exposure_ratio"] == pytest.approx(0.25, abs=1e-4)
    assert clip["total_clipping_ratio"] == pytest.approx(0.50, abs=1e-4)


def test_dynamic_range_percentile():
    """Verify dynamic range is robust against isolated single dead pixels."""
    arr = np.full((100, 100), 100, dtype=np.uint8)
    arr[0, 0] = 0
    arr[0, 1] = 255
    # Percentiles P99 - P1 should filter single extreme pixel
    dr = compute_dynamic_range(arr)
    assert dr == pytest.approx(0.0, abs=1e-4)


def test_quality_risk_evaluator_grading():
    """Verify QualityRiskEvaluator assigns higher risk to degraded samples."""
    evaluator = QualityRiskEvaluator()
    # Nominal metrics
    nom = {
        "laplacian_variance": 500.0,
        "total_clipping_ratio": 0.001,
        "dynamic_range": 180.0,
        "shannon_entropy": 6.8,
    }
    # Degraded metrics (severe blur & saturation)
    deg = {
        "laplacian_variance": 0.5,
        "total_clipping_ratio": 0.35,
        "dynamic_range": 20.0,
        "shannon_entropy": 2.1,
    }

    r_nom = evaluator.compute_risk_score(nom)
    r_deg = evaluator.compute_risk_score(deg)
    assert r_nom < r_deg
    assert r_deg > 0.5
