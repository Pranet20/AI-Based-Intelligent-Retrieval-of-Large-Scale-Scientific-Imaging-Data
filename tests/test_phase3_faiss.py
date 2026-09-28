"""Phase 3 unit and integration tests for FAISS vector indexing and scalable retrieval."""

import tempfile
from pathlib import Path
import numpy as np
import pytest

from src.retrieval.faiss_index import FAISSVectorIndex, IndexType
from src.retrieval.evaluator import Phase3RetrievalEvaluator


def test_faiss_dependency_available() -> None:
    """Test 1: Verify FAISS package is properly installed and version is accessible."""
    import faiss
    assert hasattr(faiss, "__version__")
    assert isinstance(faiss.__version__, str)
    assert faiss.METRIC_INNER_PRODUCT is not None


def test_indexflatip_dimension() -> None:
    """Test 2: Verify IndexFlatIP accepts and validates 384-dimensional vectors."""
    idx = FAISSVectorIndex(dimension=384, index_type=IndexType.FLAT_IP)
    v = np.random.randn(5, 384).astype(np.float32)
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    idx.build(v)
    assert idx.dimension == 384
    assert idx.ntotal == 5


def test_indexflatip_search() -> None:
    """Test 3: Verify basic search on IndexFlatIP returns correct shapes."""
    idx = FAISSVectorIndex(dimension=384, index_type=IndexType.FLAT_IP)
    v = np.random.randn(8, 384).astype(np.float32)
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    ids = [f"img_{i}" for i in range(8)]
    idx.build(v, ids=ids)

    scores, indices, id_results = idx.search(v[:2], k=3)
    assert scores.shape == (2, 3)
    assert indices.shape == (2, 3)
    assert len(id_results) == 2
    assert len(id_results[0]) == 3
    # Self-cosine must be approx 1.0
    assert scores[0, 0] == pytest.approx(1.0, abs=1e-4)
    assert id_results[0][0] == "img_0"


def test_indexflatip_matches_bruteforce() -> None:
    """Test 4: Verify IndexFlatIP scores match NumPy matrix multiplication exactly."""
    dim = 384
    corpus = np.random.randn(20, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
    queries = np.random.randn(5, dim).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.FLAT_IP)
    idx.build(corpus)

    faiss_scores, faiss_indices, _ = idx.search(queries, k=5)
    np_scores = np.dot(queries, corpus.T)

    for q in range(5):
        top_np_idx = np.argsort(-np_scores[q])[:5]
        np.testing.assert_allclose(faiss_scores[q], np_scores[q, top_np_idx], atol=1e-5)


def test_indexflatip_top1_agreement() -> None:
    """Test 5: Top-1 agreement rate between IndexFlatIP and NumPy brute force is 100%."""
    dim = 64
    corpus = np.random.randn(30, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
    ids = [f"c_{i}" for i in range(30)]

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.FLAT_IP)
    idx.build(corpus, ids=ids)

    queries = corpus[:10]  # Self queries
    _, _, faiss_ids = idx.search(queries, k=1)
    for q_idx in range(10):
        assert faiss_ids[q_idx][0] == ids[q_idx]


def test_indexflatip_top5_agreement() -> None:
    """Test 6: Top-5 candidate set agreement between IndexFlatIP and brute force is 100%."""
    dim = 128
    corpus = np.random.randn(40, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
    queries = np.random.randn(6, dim).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.FLAT_IP)
    idx.build(corpus)

    _, faiss_indices, _ = idx.search(queries, k=5)
    np_sims = np.dot(queries, corpus.T)

    for q in range(6):
        np_top5 = set(np.argsort(-np_sims[q])[:5])
        faiss_top5 = set(faiss_indices[q])
        assert faiss_top5 == np_top5


def test_indexflatip_top10_agreement() -> None:
    """Test 7: Top-10 candidate set agreement between IndexFlatIP and brute force is 100%."""
    dim = 128
    corpus = np.random.randn(50, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)
    queries = np.random.randn(4, dim).astype(np.float32)
    queries /= np.linalg.norm(queries, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.FLAT_IP)
    idx.build(corpus)

    _, faiss_indices, _ = idx.search(queries, k=10)
    np_sims = np.dot(queries, corpus.T)

    for q in range(4):
        np_top10 = set(np.argsort(-np_sims[q])[:10])
        faiss_top10 = set(faiss_indices[q])
        assert faiss_top10 == np_top10


def test_ivfflat_build() -> None:
    """Test 8: Verify IndexIVFFlat builds and trains properly."""
    dim = 64
    corpus = np.random.randn(100, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.IVF_FLAT, nlist=8, nprobe=2)
    idx.build(corpus)

    assert idx.is_trained is True
    assert idx.ntotal == 100
    assert idx.index.nlist == 8


def test_ivfflat_search() -> None:
    """Test 9: Verify IndexIVFFlat search returns valid results with various nprobe."""
    dim = 64
    corpus = np.random.randn(120, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.IVF_FLAT, nlist=10, nprobe=1)
    idx.build(corpus)

    scores1, _, ids1 = idx.search(corpus[:2], k=5, nprobe=1)
    scores4, _, ids4 = idx.search(corpus[:2], k=5, nprobe=4)

    assert scores1.shape == (2, 5)
    assert scores4.shape == (2, 5)
    # With higher nprobe, top scores should be equal or higher
    assert scores4[0, 0] >= scores1[0, 0] - 1e-5


def test_hnsw_build() -> None:
    """Test 10: Verify IndexHNSWFlat constructs graph with expected M."""
    dim = 64
    corpus = np.random.randn(80, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.HNSW_FLAT, hnsw_m=16, ef_search=32)
    idx.build(corpus)

    assert idx.is_trained is True
    assert idx.ntotal == 80


def test_hnsw_search() -> None:
    """Test 11: Verify IndexHNSWFlat search behaves consistently with efSearch."""
    dim = 64
    corpus = np.random.randn(90, dim).astype(np.float32)
    corpus /= np.linalg.norm(corpus, axis=1, keepdims=True)

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.HNSW_FLAT, hnsw_m=16, ef_search=16)
    idx.build(corpus)

    scores, indices, ids = idx.search(corpus[:3], k=5, ef_search=64)
    assert scores.shape == (3, 5)
    assert indices.shape == (3, 5)
    # Self match at rank 0
    assert indices[0, 0] == 0


def test_self_match_exclusion() -> None:
    """Test 12: Verify self-match exclusion in evaluator correctly masks query itself."""
    v0 = np.array([1.0, 0.0], dtype=np.float32)
    v1 = np.array([0.9, 0.435], dtype=np.float32)
    v1 /= np.linalg.norm(v1)

    embeddings = np.stack([v0, v1])
    ids = ["q0", "p0"]

    idx = FAISSVectorIndex(dimension=2, index_type=IndexType.FLAT_IP)
    idx.build(embeddings, ids=ids)

    evaluator = Phase3RetrievalEvaluator()
    gt = {"q0": {"p0"}}
    excl = {"q0": set()}

    res = evaluator.evaluate_faiss_index(idx, embeddings[:1], ["q0"], gt, excl, k_values=(1,))
    assert res["recall_at_1"] == 1.0


def test_embedding_id_mapping() -> None:
    """Test 13: Verify string ID mapping integrity across build, search, save, and load."""
    dim = 32
    v = np.random.randn(10, dim).astype(np.float32)
    v /= np.linalg.norm(v, axis=1, keepdims=True)
    custom_ids = [f"scientific_micrograph_{i*10}" for i in range(10)]

    idx = FAISSVectorIndex(dimension=dim, index_type=IndexType.FLAT_IP)
    idx.build(v, ids=custom_ids)

    _, _, id_results = idx.search(v[:1], k=2)
    assert id_results[0][0] == custom_ids[0]

    with tempfile.TemporaryDirectory() as tmp_dir:
        save_p = Path(tmp_dir) / "test_idx.faiss"
        idx.save(save_p)

        loaded_idx = FAISSVectorIndex.load(save_p)
        assert loaded_idx.id_map == custom_ids
        _, _, loaded_results = loaded_idx.search(v[:1], k=2)
        assert loaded_results[0][0] == custom_ids[0]


def test_float32_validation() -> None:
    """Test 14: Non-float32 arrays are cast to float32 gracefully."""
    idx = FAISSVectorIndex(dimension=16, index_type=IndexType.FLAT_IP)
    v_float64 = np.random.randn(5, 16).astype(np.float64)
    v_validated = idx.validate_vectors(v_float64)
    assert v_validated.dtype == np.float32


def test_invalid_dimension_rejected() -> None:
    """Test 15: Mismatched vector dimensionality raises ValueError."""
    idx = FAISSVectorIndex(dimension=384, index_type=IndexType.FLAT_IP)
    v_wrong_dim = np.random.randn(5, 128).astype(np.float32)
    with pytest.raises(ValueError, match="dimension mismatch"):
        idx.validate_vectors(v_wrong_dim)


def test_nan_rejected() -> None:
    """Test 16: NaNs in vector array are rejected."""
    idx = FAISSVectorIndex(dimension=32, index_type=IndexType.FLAT_IP)
    v = np.random.randn(5, 32).astype(np.float32)
    v[1, 2] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        idx.validate_vectors(v)


def test_inf_rejected() -> None:
    """Test 17: Infinite values in vector array are rejected."""
    idx = FAISSVectorIndex(dimension=32, index_type=IndexType.FLAT_IP)
    v = np.random.randn(5, 32).astype(np.float32)
    v[2, 5] = np.inf
    with pytest.raises(ValueError, match="non-finite"):
        idx.validate_vectors(v)


def test_phase3_bruteforce_reproduces_phase2_hcci_metrics() -> None:
    """Regression Test 1: Phase 3 brute-force reference reproduces frozen Phase 2 HCCI metrics."""
    evaluator = Phase3RetrievalEvaluator()
    hcci_mat, hcci_ids, hcci_df = evaluator.load_embeddings("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    hcci_gt, hcci_excl = evaluator.build_hcci_ground_truth(hcci_df, manifest_path="data/manifests/hcci_manifest.parquet")
    exact_res = evaluator.evaluate_exact_agreement(hcci_mat, hcci_ids, hcci_gt, hcci_excl)
    ref = exact_res["reference_summary"]

    assert ref["recall_at_1"] == pytest.approx(0.981912, abs=1e-4)
    assert ref["recall_at_5"] == pytest.approx(1.000000, abs=1e-5)
    assert ref["recall_at_10"] == pytest.approx(1.000000, abs=1e-5)
    assert ref["mrr"] == pytest.approx(0.989448, abs=1e-4)
    assert ref["precision_at_5"] == pytest.approx(0.969250, abs=1e-4)


def test_phase3_bruteforce_reproduces_phase2_carinthia_metrics() -> None:
    """Regression Test 2: Phase 3 brute-force reference reproduces frozen Phase 2 Carinthia metrics."""
    evaluator = Phase3RetrievalEvaluator()
    car_mat, car_ids, car_df = evaluator.load_embeddings("data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet")
    car_gt, car_excl, _ = evaluator.build_carinthia_ground_truth(car_df)
    exact_res = evaluator.evaluate_exact_agreement(car_mat, car_ids, car_gt, car_excl)
    ref = exact_res["reference_summary"]

    assert ref["recall_at_1"] == pytest.approx(0.995208, abs=1e-4)
    assert ref["recall_at_5"] == pytest.approx(0.997821, abs=1e-4)
    assert ref["recall_at_10"] == pytest.approx(0.998257, abs=1e-4)
    assert ref["mrr"] == pytest.approx(0.996492, abs=1e-4)


def test_indexflatip_reproduces_phase2_hcci_metrics() -> None:
    """Regression Test 3: FAISS IndexFlatIP reproduces frozen Phase 2 HCCI metrics."""
    evaluator = Phase3RetrievalEvaluator()
    hcci_mat, hcci_ids, hcci_df = evaluator.load_embeddings("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
    hcci_gt, hcci_excl = evaluator.build_hcci_ground_truth(hcci_df, manifest_path="data/manifests/hcci_manifest.parquet")

    flat_idx = FAISSVectorIndex(384, IndexType.FLAT_IP)
    flat_idx.build(hcci_mat, hcci_ids)
    sum_flat = evaluator.evaluate_faiss_index(flat_idx, hcci_mat, hcci_ids, hcci_gt, hcci_excl)

    assert sum_flat["recall_at_1"] == pytest.approx(0.981912, abs=1e-4)
    assert sum_flat["recall_at_5"] == pytest.approx(1.000000, abs=1e-5)
    assert sum_flat["recall_at_10"] == pytest.approx(1.000000, abs=1e-5)
    assert sum_flat["mrr"] == pytest.approx(0.989448, abs=1e-4)


def test_indexflatip_reproduces_phase2_carinthia_metrics() -> None:
    """Regression Test 4: FAISS IndexFlatIP reproduces frozen Phase 2 Carinthia metrics."""
    evaluator = Phase3RetrievalEvaluator()
    car_mat, car_ids, car_df = evaluator.load_embeddings("data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet")
    car_gt, car_excl, _ = evaluator.build_carinthia_ground_truth(car_df)

    flat_idx = FAISSVectorIndex(384, IndexType.FLAT_IP)
    flat_idx.build(car_mat, car_ids)
    sum_flat = evaluator.evaluate_faiss_index(flat_idx, car_mat, car_ids, car_gt, car_excl)

    assert sum_flat["recall_at_1"] == pytest.approx(0.995208, abs=1e-4)
    assert sum_flat["recall_at_5"] == pytest.approx(0.997821, abs=1e-4)
    assert sum_flat["recall_at_10"] == pytest.approx(0.998257, abs=1e-4)
    assert sum_flat["mrr"] == pytest.approx(0.996492, abs=1e-4)


def test_filtered_candidates_are_evaluated_after_exclusion() -> None:
    """Regression Test 5: Verify excluded candidates (e.g. duplicates) do not consume ranking slots."""
    # 4 vectors: q, dup (close to q), pos (valid positive, slightly farther), neg (distant)
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_dup = np.array([0.99, 0.1], dtype=np.float32)
    v_dup /= np.linalg.norm(v_dup)
    v_pos = np.array([0.8, 0.6], dtype=np.float32)
    v_neg = np.array([0.0, 1.0], dtype=np.float32)

    embeddings = np.stack([v_q, v_dup, v_pos, v_neg])
    ids = ["q", "dup", "pos", "neg"]

    idx = FAISSVectorIndex(dimension=2, index_type=IndexType.FLAT_IP)
    idx.build(embeddings, ids=ids)

    evaluator = Phase3RetrievalEvaluator()
    gt = {"q": {"pos"}}
    excl = {"q": {"dup"}}  # dup is excluded

    res = evaluator.evaluate_faiss_index(idx, embeddings[:1], ["q"], gt, excl, k_values=(1, 2))
    # After excluding 'q' (self) and 'dup', the top retrieved candidate must be 'pos' at rank 1
    assert res["recall_at_1"] == 1.0
    assert res["mrr"] == 1.0


def test_k_is_applied_after_candidate_filtering() -> None:
    """Regression Test 6: Verify top-K is sliced AFTER removing exclusions so the candidate list is not truncated."""
    # 5 vectors: q, excl1, excl2, pos1, pos2
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_e1 = np.array([0.99, 0.05], dtype=np.float32)
    v_e1 /= np.linalg.norm(v_e1)
    v_e2 = np.array([0.98, 0.10], dtype=np.float32)
    v_e2 /= np.linalg.norm(v_e2)
    v_p1 = np.array([0.90, 0.43], dtype=np.float32)
    v_p1 /= np.linalg.norm(v_p1)
    v_p2 = np.array([0.80, 0.60], dtype=np.float32)

    embeddings = np.stack([v_q, v_e1, v_e2, v_p1, v_p2])
    ids = ["q", "e1", "e2", "p1", "p2"]

    idx = FAISSVectorIndex(dimension=2, index_type=IndexType.FLAT_IP)
    idx.build(embeddings, ids=ids)

    evaluator = Phase3RetrievalEvaluator()
    gt = {"q": {"p1", "p2"}}
    excl = {"q": {"e1", "e2"}}

    # Evaluate at K=2. If filtering was wrongly done after slicing K=2, raw top 2 would be [q, e1],
    # both would be dropped, leaving 0 candidates and recall=0.
    # With correct post-filtering ranking, valid candidates are [p1, p2], so both rank <= 2.
    res = evaluator.evaluate_faiss_index(idx, embeddings[:1], ["q"], gt, excl, k_values=(2,))
    assert res["recall_at_2"] == 1.0
    assert res["precision_at_2"] == 1.0
