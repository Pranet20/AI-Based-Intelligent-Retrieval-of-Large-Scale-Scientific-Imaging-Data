import numpy as np
import pytest
from app.ml.faiss_engine import FAISSEngine


def test_faiss_engine_exact_retrieval():
    engine = FAISSEngine()
    engine.reset()

    # Generate 20 random normalized vectors
    rng = np.random.default_rng(42)
    raw = rng.standard_normal((20, 384)).astype(np.float32)
    norms = np.linalg.norm(raw, axis=1, keepdims=True)
    vecs = raw / norms

    for i in range(20):
        engine.add_vector(i + 100, vecs[i])

    assert engine.index.ntotal == 20

    # Search with vector 0
    query = vecs[0]
    results = engine.search(query, top_k=3)

    assert len(results) == 3
    # Top 1 must be image_id 100 with similarity ~ 1.0
    assert results[0][0] == 100
    assert results[0][1] == pytest.approx(1.0, abs=1e-5)

    engine.reset()
    assert engine.index.ntotal == 0
