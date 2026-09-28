"""
Phase 6: Scientific Image Redundancy, Quality Anomaly and Novelty Intelligence.
"""

from src.integrity.exact_duplicates import (
    compute_file_sha256,
    compute_decoded_pixel_sha256,
    find_exact_file_duplicates,
    find_exact_pixel_duplicates,
)
from src.integrity.perceptual_hash import (
    compute_phash,
    compute_dhash,
    hamming_distance,
    hash_to_hex,
    hex_to_hash,
)
from src.integrity.duplicate_cascade import (
    compute_ssim,
    compute_pixel_metrics,
    DuplicateCascade,
)
from src.integrity.redundancy_graph import RedundancyGraph
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
from src.integrity.novelty_detectors import (
    KNNNoveltyDetector,
    MeanKNNNoveltyDetector,
    LOFNoveltyDetector,
    IsolationForestNoveltyDetector,
    CentroidNoveltyDetector,
    MultiNoveltyEnsemble,
    assert_no_leakage_features,
)
from src.integrity.provenance_audit import audit_hcci_metadata, audit_carinthia_metadata
from src.integrity.diagnostic_matrix import assign_diagnostic_quadrants, compute_matrix_summary
from src.integrity.review_queue import (
    build_review_queue,
    export_review_queue,
    simulate_review_budgets,
    evaluate_synthetic_review_queue,
)
from src.integrity.synthetic_benchmarks import (
    apply_near_duplicate_transforms,
    apply_quality_anomaly_artifacts,
    compute_binary_auroc,
    compute_binary_auprc,
    compute_detection_rate_at_threshold,
)
from src.integrity.profile_builder import ScientificProfileBuilder

__all__ = [
    "compute_file_sha256",
    "compute_decoded_pixel_sha256",
    "find_exact_file_duplicates",
    "find_exact_pixel_duplicates",
    "compute_phash",
    "compute_dhash",
    "hamming_distance",
    "hash_to_hex",
    "hex_to_hash",
    "compute_ssim",
    "compute_pixel_metrics",
    "DuplicateCascade",
    "RedundancyGraph",
    "compute_laplacian_variance",
    "compute_edge_density",
    "compute_shannon_entropy",
    "compute_dynamic_range",
    "compute_clipping_ratios",
    "compute_high_freq_fft_ratio",
    "compute_all_quality_metrics",
    "QualityRiskEvaluator",
    "KNNNoveltyDetector",
    "MeanKNNNoveltyDetector",
    "LOFNoveltyDetector",
    "IsolationForestNoveltyDetector",
    "CentroidNoveltyDetector",
    "MultiNoveltyEnsemble",
    "assert_no_leakage_features",
    "audit_hcci_metadata",
    "audit_carinthia_metadata",
    "assign_diagnostic_quadrants",
    "compute_matrix_summary",
    "build_review_queue",
    "export_review_queue",
    "simulate_review_budgets",
    "apply_near_duplicate_transforms",
    "apply_quality_anomaly_artifacts",
    "compute_binary_auroc",
    "ScientificProfileBuilder",
]
