import numpy as np
import pytest
from app.ml.novelty_engine import NoveltyEngine


def test_novelty_engine_evaluation():
    engine = NoveltyEngine(k=3)

    # Reference corpus of 10 vectors clustered near unit x-axis
    ref = np.zeros((10, 384), dtype=np.float32)
    ref[:, 0] = 1.0

    # In-distribution vector
    in_dist = np.zeros(384, dtype=np.float32)
    in_dist[0] = 1.0

    res_in = engine.evaluate_novelty(in_dist, corpus_embeddings=ref)
    assert res_in["novelty_score"] == pytest.approx(0.0, abs=1e-5)
    assert "relative embedding-space novelty" in res_in["interpretation"]

    # Out-of-distribution orthogonal vector
    out_dist = np.zeros(384, dtype=np.float32)
    out_dist[1] = 1.0

    res_out = engine.evaluate_novelty(out_dist, corpus_embeddings=ref)
    assert res_out["novelty_score"] == pytest.approx(1.0, abs=1e-5)
    assert res_out["novelty_percentile"] > res_in["novelty_percentile"]
