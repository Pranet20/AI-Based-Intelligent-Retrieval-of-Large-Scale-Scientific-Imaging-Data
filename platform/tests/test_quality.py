from pathlib import Path
import numpy as np
from PIL import Image
import pytest

from app.ml.quality_engine import QualityEngine


@pytest.fixture
def sample_micrograph(tmp_path):
    img_path = tmp_path / "synthetic_micrograph.png"
    # Create realistic synthetic gradient pattern
    arr = np.linspace(20, 220, 256 * 256, dtype=np.uint8).reshape((256, 256))
    img = Image.fromarray(arr)
    img.save(img_path)
    return img_path


def test_quality_indicator_computation(sample_micrograph):
    res = QualityEngine.evaluate_quality(sample_micrograph)
    assert "laplacian_variance" in res
    assert "edge_density" in res
    assert "shannon_entropy" in res
    assert "dynamic_range" in res
    assert "clipping_ratio" in res
    assert "high_freq_fft_ratio" in res
    assert "composite_quality_risk" in res
    assert "quality_label" in res

    assert res["quality_label"] in ["NOMINAL", "RISK_FLAGGED"]
    assert 0.0 <= res["composite_quality_risk"] <= 1.0
    assert res["shannon_entropy"] > 0.0
