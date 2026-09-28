"""Tests for retrieval metrics, self-match exclusion, and anti-leakage grouping."""

import numpy as np
import pytest

from src.evaluation.retrieval_metrics import (
    RetrievalMetricsCalculator,
    compute_cosine_similarity_matrix,
)


def test_retrieval_self_match_exclusion_and_recall() -> None:
    # 4 synthetic vectors (unit length)
    # v0 and v1 are close (sim ~ 0.99)
    # v2 and v3 are close
    v0 = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v1 = np.array([0.99, 0.14, 0.0], dtype=np.float32)
    v1 /= np.linalg.norm(v1)

    v2 = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    v3 = np.array([0.0, 0.99, 0.14], dtype=np.float32)
    v3 /= np.linalg.norm(v3)

    embeddings = np.stack([v0, v1, v2, v3])
    query_ids = ["img_0", "img_1", "img_2", "img_3"]

    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    # Diagonal is 1.0 (self-match)
    assert sim_mat[0, 0] == pytest.approx(1.0, abs=1e-5)

    # Positives: img_0 matches img_1, img_2 matches img_3
    positives = {
        "img_0": {"img_1"},
        "img_1": {"img_0"},
        "img_2": {"img_3"},
        "img_3": {"img_2"},
    }

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat,
        query_ids=query_ids,
        candidate_ids=query_ids,
        ground_truth_positives=positives,
        k_values=(1, 2),
    )

    summary = res["summary"]
    # Because self was excluded, for img_0 the top candidate is img_1!
    assert summary["recall_at_1"] == 1.0
    assert summary["recall_at_2"] == 1.0
    assert summary["mrr"] == 1.0
    assert summary["evaluated_queries"] == 4
    assert summary["no_valid_positive_queries"] == 0


def test_retrieval_no_valid_positive_handling() -> None:
    embeddings = np.eye(3, dtype=np.float32)
    query_ids = ["q0", "q1", "q2"]

    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    # q0 has positive q1, but q2 has NO positives
    positives = {
        "q0": {"q1"},
        "q1": {"q0"},
        "q2": set(),  # No positive counterpart
    }

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat,
        query_ids=query_ids,
        candidate_ids=query_ids,
        ground_truth_positives=positives,
        k_values=(1,),
    )

    summary = res["summary"]
    assert summary["total_queries"] == 3
    assert summary["evaluated_queries"] == 2
    assert summary["no_valid_positive_queries"] == 1


def test_anti_leakage_exclusion_sets() -> None:
    # 3 vectors where q0 is identical to duplicate d0, and true positive is p0
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_dup = np.array([1.0, 0.0], dtype=np.float32)  # Identical duplicate condition
    v_pos = np.array([0.9, 0.435], dtype=np.float32)
    v_pos /= np.linalg.norm(v_pos)

    embeddings = np.stack([v_q, v_dup, v_pos])
    query_ids = ["q", "dup", "pos"]

    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    positives = {"q": {"pos"}}
    # Explicitly exclude the duplicate acquisition from candidate ranking
    exclusions = {"q": {"dup"}}

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat,
        query_ids=["q"],
        candidate_ids=query_ids,
        ground_truth_positives=positives,
        exclusion_sets=exclusions,
        k_values=(1,),
    )

    details = res["query_details"][0]
    # top retrieved candidate must be "pos", not "dup" because "dup" was excluded!
    assert details["first_positive_rank"] == 1
    assert details["top_5_retrieved"][0] == "pos"


def test_hcci_positive_pair_definition() -> None:
    """Audit Test 1: Same specimen under different acquisition is positive; different specimen is negative."""
    v0 = np.array([1.0, 0.0], dtype=np.float32)
    v1 = np.array([0.9, 0.435], dtype=np.float32)
    v2 = np.array([0.0, 1.0], dtype=np.float32)
    embeddings = np.stack([v0, v1, v2])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    # q_AsCast (acq1) vs c_AsCast (acq2) -> positive
    # q_AsCast vs c_Q980 (acq3) -> negative
    positives = {"q_AsCast": {"c_AsCast"}}
    exclusions = {"q_AsCast": set()}

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["q_AsCast"],
        candidate_ids=["q_AsCast", "c_AsCast", "c_Q980"],
        ground_truth_positives=positives,
        exclusion_sets=exclusions,
        k_values=(1, 2),
    )
    assert res["summary"]["recall_at_1"] == 1.0
    assert res["query_details"][0]["first_positive_rank"] == 1


def test_hcci_same_acquisition_exclusion() -> None:
    """Audit Test 2: Identical acquisition conditions of same ROI/specimen must be strictly excluded."""
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_same_acq = np.array([0.999, 0.01], dtype=np.float32)
    v_diff_acq_pos = np.array([0.85, 0.52], dtype=np.float32)

    embeddings = np.stack([v_q, v_same_acq, v_diff_acq_pos])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    # Same acquisition candidate is masked out via exclusion set
    exclusions = {"q": {"same_acq"}}
    positives = {"q": {"diff_acq_pos"}}

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["q"],
        candidate_ids=["q", "same_acq", "diff_acq_pos"],
        ground_truth_positives=positives,
        exclusion_sets=exclusions,
        k_values=(1,),
    )
    # Even though same_acq had higher cosine similarity, it was excluded!
    assert res["query_details"][0]["first_positive_rank"] == 1
    assert res["query_details"][0]["top_5_retrieved"][0] == "diff_acq_pos"


def test_hcci_duplicate_exclusion() -> None:
    """Audit Test 3: Candidates belonging to the same exact duplicate cluster are excluded."""
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_dup = np.array([1.0, 0.0], dtype=np.float32)
    v_pos = np.array([0.8, 0.6], dtype=np.float32)

    embeddings = np.stack([v_q, v_dup, v_pos])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    exclusions = {"q": {"dup_img"}}
    positives = {"q": {"pos_img"}}

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["q"],
        candidate_ids=["q", "dup_img", "pos_img"],
        ground_truth_positives=positives,
        exclusion_sets=exclusions,
        k_values=(1,),
    )
    assert res["query_details"][0]["first_positive_rank"] == 1
    assert "dup_img" not in res["query_details"][0]["top_5_retrieved"]


def test_hcci_near_duplicate_handling() -> None:
    """Audit Test 4: Near-duplicate images must be excluded from candidate ranking."""
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_near = np.array([0.9999, 0.001], dtype=np.float32)
    v_pos = np.array([0.7, 0.71], dtype=np.float32)

    embeddings = np.stack([v_q, v_near, v_pos])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    exclusions = {"q": {"near_dup_img"}}
    positives = {"q": {"pos_img"}}

    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["q"],
        candidate_ids=["q", "near_dup_img", "pos_img"],
        ground_truth_positives=positives,
        exclusion_sets=exclusions,
        k_values=(1,),
    )
    assert res["query_details"][0]["first_positive_rank"] == 1
    assert res["query_details"][0]["top_5_retrieved"][0] == "pos_img"


def test_hcci_query_with_multiple_positives() -> None:
    """Audit Test 5: Query with multiple valid positive counterparts tracks ranks and Precision@K accurately."""
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_p1 = np.array([0.95, 0.31], dtype=np.float32)
    v_p2 = np.array([0.90, 0.43], dtype=np.float32)
    v_neg = np.array([0.10, 0.99], dtype=np.float32)

    embeddings = np.stack([v_q, v_p1, v_p2, v_neg])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    positives = {"q": {"p1", "p2"}}
    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["q"],
        candidate_ids=["q", "p1", "p2", "neg"],
        ground_truth_positives=positives,
        k_values=(1, 2),
    )
    assert res["summary"]["recall_at_1"] == 1.0
    assert res["summary"]["recall_at_2"] == 1.0
    # Both top 2 retrieved items are positive, precision@2 = 1.0
    assert res["summary"]["precision_at_2"] == 1.0


def test_hcci_query_with_zero_positives() -> None:
    """Audit Test 6: Queries with zero positives are safely tracked as un-evaluated."""
    v_q = np.array([1.0, 0.0], dtype=np.float32)
    v_neg = np.array([0.0, 1.0], dtype=np.float32)

    embeddings = np.stack([v_q, v_neg])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    positives = {"q": set()}
    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["q"],
        candidate_ids=["q", "neg"],
        ground_truth_positives=positives,
        k_values=(1,),
    )
    assert res["summary"]["total_queries"] == 1
    assert res["summary"]["evaluated_queries"] == 0
    assert res["summary"]["no_valid_positive_queries"] == 1


def test_carinthia_same_class_relevance() -> None:
    """Audit Test 7: In Carinthia, candidates from same class are positives, other classes are negatives."""
    # Class A: imgA1, imgA2; Class B: imgB1
    v_a1 = np.array([1.0, 0.0], dtype=np.float32)
    v_a2 = np.array([0.9, 0.43], dtype=np.float32)
    v_b1 = np.array([0.0, 1.0], dtype=np.float32)

    embeddings = np.stack([v_a1, v_a2, v_b1])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    positives = {"imgA1": {"imgA2"}}
    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["imgA1"],
        candidate_ids=["imgA1", "imgA2", "imgB1"],
        ground_truth_positives=positives,
        k_values=(1,),
    )
    assert res["summary"]["recall_at_1"] == 1.0
    assert res["query_details"][0]["top_5_retrieved"][0] == "imgA2"


def test_carinthia_self_exclusion() -> None:
    """Audit Test 8: Carinthia queries strictly exclude self-match (sim=1.0) from candidate ranking."""
    v0 = np.array([1.0, 0.0], dtype=np.float32)
    v1 = np.array([0.5, 0.86], dtype=np.float32)

    embeddings = np.stack([v0, v1])
    sim_mat = compute_cosine_similarity_matrix(embeddings, embeddings)

    # Even if self is in candidate_ids, it is never ranked
    positives = {"img0": {"img1"}}
    res = RetrievalMetricsCalculator.evaluate_retrieval(
        similarity_matrix=sim_mat[:1],
        query_ids=["img0"],
        candidate_ids=["img0", "img1"],
        ground_truth_positives=positives,
        k_values=(1,),
    )
    top_cands = res["query_details"][0]["top_5_retrieved"]
    assert "img0" not in top_cands
    assert top_cands[0] == "img1"

