"""
Track E: 2D Scientific Diagnostic Matrices.

Partitions micrographs into 4 quadrants based on Novelty vs. Quality Risk:
- Q1: High Novelty, Low Risk (High Quality)  -> SCIENTIFIC_DISCOVERY_CANDIDATE
- Q2: High Novelty, High Risk (Low Quality) -> CORRUPTED_ACQUISITION / QUALITY_FAILURE
- Q3: Low Novelty, Low Risk (High Quality)   -> NOMINAL_REFERENCE_STANDARD
- Q4: Low Novelty, High Risk (Low Quality)  -> SUB_NOMINAL_ACQUISITION

Also constructs the Redundancy vs. Novelty interaction matrix.
"""

from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


def assign_diagnostic_quadrants(
    df: pd.DataFrame,
    novelty_col: str = "composite_novelty_score",
    quality_risk_col: str = "quality_risk_score",
    novelty_threshold: float = 0.5,
    quality_risk_threshold: float = 0.4,
) -> pd.DataFrame:
    """
    Assign each image to one of the 4 scientific diagnostic quadrants.
    """
    df_out = df.copy()

    is_high_novelty = df_out[novelty_col] >= novelty_threshold
    is_high_risk = df_out[quality_risk_col] >= quality_risk_threshold

    quadrant_labels = []
    quadrant_codes = []

    for hn, hr in zip(is_high_novelty, is_high_risk):
        if hn and not hr:
            quadrant_codes.append("Q1")
            quadrant_labels.append("HIGH_NOVELTY_HIGH_QUALITY_CANDIDATE")
        elif hn and hr:
            quadrant_codes.append("Q2")
            quadrant_labels.append("QUALITY_RISK_ALERT")
        elif not hn and not hr:
            quadrant_codes.append("Q3")
            quadrant_labels.append("NOMINAL_REFERENCE_STANDARD")
        else:
            quadrant_codes.append("Q4")
            quadrant_labels.append("SUB_NOMINAL_ACQUISITION_CANDIDATE")

    df_out["diagnostic_quadrant"] = quadrant_codes
    df_out["diagnostic_label"] = quadrant_labels
    return df_out


def compute_matrix_summary(df: pd.DataFrame) -> Dict[str, dict]:
    """
    Compute distribution of samples across quadrants.
    """
    total = len(df)
    counts = df["diagnostic_quadrant"].value_counts().to_dict()
    summary = {}
    labels = {
        "Q1": "High-Novelty / High-Quality Review Candidate (Screening Candidate for Expert Review)",
        "Q2": "Quality-Risk Alert / Corrupted Acquisition Candidate (High Novelty with Elevated Quality Risk)",
        "Q3": "Nominal Reference Standard (Low Novelty, Low Quality Risk)",
        "Q4": "Sub-nominal Acquisition Candidate (Low Novelty, Elevated Quality Risk)",
    }
    for q, desc in labels.items():
        c = counts.get(q, 0)
        summary[q] = {
            "description": desc,
            "count": c,
            "percentage": float((c / total) * 100.0) if total > 0 else 0.0,
        }
    return summary
