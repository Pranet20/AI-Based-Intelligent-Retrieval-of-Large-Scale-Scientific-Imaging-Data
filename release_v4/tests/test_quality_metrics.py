"""Tests for computational image-quality indicators and evaluator grading."""

from pathlib import Path
import numpy as np
import pytest

from src.ingestion.reader import ScientificImageReader
from src.quality.evaluator import QualityEvaluator
from src.quality.metrics import calculate_quality_metrics


def test_quality_metrics_sharp_vs_flat(synthetic_uint8_png: Path) -> None:
    arr, _ = ScientificImageReader.load_array(synthetic_uint8_png)
    metrics_sharp = calculate_quality_metrics(arr, bit_depth=8)

    # Sharp image must have positive Laplacian variance and substantial entropy
    assert metrics_sharp.laplacian_variance > 10.0
    assert metrics_sharp.entropy > 1.0
    assert metrics_sharp.dynamic_range > 100.0

    # Perfectly flat image (zero contrast, zero sharpness)
    flat_arr = np.full((100, 100), 128, dtype=np.uint8)
    metrics_flat = calculate_quality_metrics(flat_arr, bit_depth=8)

    assert metrics_flat.laplacian_variance == 0.0
    assert metrics_flat.entropy == 0.0
    assert metrics_flat.variance == 0.0
    assert metrics_flat.contrast == 0.0


def test_quality_evaluator_grading() -> None:
    evaluator = QualityEvaluator()

    # Create sharp array with rich dynamic range and entropy
    x = np.linspace(20, 230, 100, dtype=np.uint8)
    sharp_arr = np.tile(x, (100, 1))
    sharp_arr[20:50, 20:50] = 240
    sharp_arr[60:80, 60:80] = 30
    m_sharp = calculate_quality_metrics(sharp_arr, bit_depth=8)
    status, score, flags = evaluator.evaluate(m_sharp, bit_depth=8)

    assert status in ("PASS", "REVIEW")
    assert 0.0 <= score <= 1.0

    # Create completely black/flat array
    fail_arr = np.zeros((100, 100), dtype=np.uint8)
    m_fail = calculate_quality_metrics(fail_arr, bit_depth=8)
    fail_status, fail_score, fail_flags = evaluator.evaluate(m_fail, bit_depth=8)

    assert fail_status == "FAIL"
    assert len(fail_flags) > 0
    assert fail_score < score
