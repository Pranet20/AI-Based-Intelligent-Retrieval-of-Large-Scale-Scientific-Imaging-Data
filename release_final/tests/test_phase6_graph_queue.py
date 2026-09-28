"""
Unit tests for Phase 6 Track E: Redundancy Graph, 2D Diagnostic Matrix, and Review Queue.
"""

import pandas as pd
import pytest

from src.integrity.redundancy_graph import RedundancyGraph
from src.integrity.diagnostic_matrix import assign_diagnostic_quadrants, compute_matrix_summary
from src.integrity.review_queue import build_review_queue, simulate_review_budgets


def test_redundancy_graph_clustering_and_representative():
    """Verify graph extracts components and selects sharpest representative."""
    graph = RedundancyGraph(all_image_ids=["img1", "img2", "img3", "img4"])
    # img1 and img2 are near duplicates
    graph.add_relationship("img1", "img2", match_type="NEAR_DUPLICATE")

    components = graph.get_connected_components()
    assert len(components) == 3  # [img1, img2], [img3], [img4]

    # img2 is sharper than img1
    q_scores = {"img1": 100.0, "img2": 250.0, "img3": 50.0, "img4": 75.0}
    summary = graph.build_summary(quality_scores=q_scores)

    row_img2 = summary[summary["image_id"] == "img2"].iloc[0]
    row_img1 = summary[summary["image_id"] == "img1"].iloc[0]

    assert bool(row_img2["is_representative"]) is True
    assert row_img2["redundancy_action"] == "KEEP"
    assert bool(row_img1["is_representative"]) is False
    assert row_img1["redundancy_action"] == "REVIEW"


def test_diagnostic_matrix_quadrant_partitioning():
    """Verify 4 quadrant partitioning matches scientific definitions."""
    df = pd.DataFrame({
        "image_id": ["m1", "m2", "m3", "m4"],
        "composite_novelty_score": [0.8, 0.9, 0.1, 0.2],
        "quality_risk_score": [0.1, 0.8, 0.1, 0.7],
    })

    diag = assign_diagnostic_quadrants(
        df,
        novelty_threshold=0.5,
        quality_risk_threshold=0.4,
    )

    quads = dict(zip(diag["image_id"], diag["diagnostic_quadrant"]))
    assert quads["m1"] == "Q1"  # High Novelty, Low Risk -> Discovery
    assert quads["m2"] == "Q2"  # High Novelty, High Risk -> Corrupted
    assert quads["m3"] == "Q3"  # Low Novelty, Low Risk -> Nominal
    assert quads["m4"] == "Q4"  # Low Novelty, High Risk -> Sub-nominal


def test_review_queue_ranking_and_simulation():
    """Verify review queue prioritizes Q1 candidates and budget simulation tracks yield."""
    df = pd.DataFrame({
        "image_id": [f"img_{i}" for i in range(10)],
        "diagnostic_quadrant": ["Q1"] * 5 + ["Q3"] * 5,
        "composite_novelty_score": [0.9 - 0.05 * i for i in range(10)],
        "quality_risk_score": [0.1] * 10,
    })

    queue = build_review_queue(df, top_n=5)
    assert len(queue) == 5
    assert (queue["diagnostic_quadrant"] == "Q1").all()

    sim = simulate_review_budgets(queue, budgets=[3, 5])
    assert sim["budget_3"]["scientific_discoveries_yielded"] == 3
    assert sim["budget_3"]["actionable_yield_pct"] == 100.0
