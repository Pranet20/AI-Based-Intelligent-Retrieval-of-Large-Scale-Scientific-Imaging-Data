"""
Track C: Distributional and Embedding Novelty Intelligence.

Provides unsupervised novelty scoring on frozen visual embeddings:
1. k-Nearest Neighbor (kNN) distance (to training set)
2. Mean kNN distance
3. Local Outlier Factor (LOF, novelty=True)
4. Isolation Forest (deterministic)
5. Robust Centroid / Mahalanobis distance

Enforces zero leakage:
- Evaluates purely on normalized visual embeddings.
- Prohibits all metadata identifiers or labels from entering feature space.
- Fits solely on the training split; selects thresholds solely on validation split.
"""

from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors, LocalOutlierFactor
from sklearn.ensemble import IsolationForest


PROHIBITED_LEAKAGE_COLUMNS = {
    "specimen_id",
    "sample",
    "sample_id",
    "acquisition_id",
    "roi_id",
    "image_id",
    "filename",
    "relative_path",
    "label",
    "source_label",
    "duplicate_group_id",
    "near_duplicate_group_id",
    "class",
    "material",
}


def assert_no_leakage_features(feature_names: List[str]):
    """Raise ValueError if any prohibited identifier or target label is found in features."""
    lowered = {f.lower().strip() for f in feature_names}
    intersection = lowered.intersection(PROHIBITED_LEAKAGE_COLUMNS)
    if intersection:
        raise ValueError(
            f"Zero-leakage violation: prohibited columns found in novelty features: {intersection}"
        )


class BaseNoveltyDetector:
    """Abstract base class for zero-leakage novelty detectors."""

    def __init__(self):
        self.fitted = False
        self.thresholds: Dict[str, float] = {}

    def fit(self, train_embeddings: np.ndarray):
        raise NotImplementedError

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        """Return raw novelty score (higher = more novel / anomalous)."""
        raise NotImplementedError

    def calibrate_thresholds(
        self,
        val_embeddings: np.ndarray,
        percentiles: Tuple[float, ...] = (95.0, 99.0),
    ):
        """Calibrate decision thresholds strictly on validation set."""
        val_scores = self.score(val_embeddings)
        for p in percentiles:
            self.thresholds[f"p{int(p)}"] = float(np.percentile(val_scores, p))


class KNNNoveltyDetector(BaseNoveltyDetector):
    """Novelty scoring via distance to k-th nearest neighbor in training set."""

    def __init__(self, k: int = 5, metric: str = "cosine"):
        super().__init__()
        self.k = k
        self.metric = metric
        self.nn_model: Optional[NearestNeighbors] = None

    def fit(self, train_embeddings: np.ndarray):
        assert train_embeddings.ndim == 2
        self.nn_model = NearestNeighbors(
            n_neighbors=self.k,
            metric=self.metric,
            algorithm="brute",
        )
        self.nn_model.fit(train_embeddings)
        self.fitted = True

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if not self.fitted or self.nn_model is None:
            raise RuntimeError("Model must be fitted before scoring.")
        # Return distance to the k-th neighbor
        distances, _ = self.nn_model.kneighbors(embeddings)
        return distances[:, self.k - 1].astype(np.float64)


class MeanKNNNoveltyDetector(BaseNoveltyDetector):
    """Novelty scoring via mean distance to top-k nearest neighbors in training set."""

    def __init__(self, k: int = 5, metric: str = "cosine"):
        super().__init__()
        self.k = k
        self.metric = metric
        self.nn_model: Optional[NearestNeighbors] = None

    def fit(self, train_embeddings: np.ndarray):
        assert train_embeddings.ndim == 2
        self.nn_model = NearestNeighbors(
            n_neighbors=self.k,
            metric=self.metric,
            algorithm="brute",
        )
        self.nn_model.fit(train_embeddings)
        self.fitted = True

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if not self.fitted or self.nn_model is None:
            raise RuntimeError("Model must be fitted before scoring.")
        distances, _ = self.nn_model.kneighbors(embeddings)
        return np.mean(distances, axis=1).astype(np.float64)


class LOFNoveltyDetector(BaseNoveltyDetector):
    """Local Outlier Factor novelty detector."""

    def __init__(self, n_neighbors: int = 20, metric: str = "cosine"):
        super().__init__()
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.lof: Optional[LocalOutlierFactor] = None

    def fit(self, train_embeddings: np.ndarray):
        assert train_embeddings.ndim == 2
        k = min(self.n_neighbors, len(train_embeddings) - 1)
        self.lof = LocalOutlierFactor(
            n_neighbors=k,
            metric=self.metric,
            novelty=True,
        )
        self.lof.fit(train_embeddings)
        self.fitted = True

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if not self.fitted or self.lof is None:
            raise RuntimeError("Model must be fitted before scoring.")
        # decision_function: large values for inliers, small for outliers.
        # Negate so that higher = more novel/anomalous
        return (-self.lof.decision_function(embeddings)).astype(np.float64)


class IsolationForestNoveltyDetector(BaseNoveltyDetector):
    """Isolation Forest novelty detector."""

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        super().__init__()
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.iforest: Optional[IsolationForest] = None

    def fit(self, train_embeddings: np.ndarray):
        assert train_embeddings.ndim == 2
        self.iforest = IsolationForest(
            n_estimators=self.n_estimators,
            random_state=self.random_state,
        )
        self.iforest.fit(train_embeddings)
        self.fitted = True

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if not self.fitted or self.iforest is None:
            raise RuntimeError("Model must be fitted before scoring.")
        # score_samples returns negative anomaly score. Negate so higher = more novel.
        return (-self.iforest.score_samples(embeddings)).astype(np.float64)


class CentroidNoveltyDetector(BaseNoveltyDetector):
    """Novelty scoring via cosine distance to the training set robust centroid."""

    def __init__(self):
        super().__init__()
        self.centroid: Optional[np.ndarray] = None

    def fit(self, train_embeddings: np.ndarray):
        assert train_embeddings.ndim == 2
        # Normalize training vectors
        norms = np.linalg.norm(train_embeddings, axis=1, keepdims=True)
        normed = train_embeddings / np.maximum(norms, 1e-12)
        c = np.mean(normed, axis=0)
        c_norm = np.linalg.norm(c)
        self.centroid = c / max(c_norm, 1e-12)
        self.fitted = True

    def score(self, embeddings: np.ndarray) -> np.ndarray:
        if not self.fitted or self.centroid is None:
            raise RuntimeError("Model must be fitted before scoring.")
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normed = embeddings / np.maximum(norms, 1e-12)
        sim = np.dot(normed, self.centroid)
        # Cosine distance: 1 - cosine similarity
        return (1.0 - sim).astype(np.float64)


class MultiNoveltyEnsemble:
    """
    Fits and manages all 5 novelty detectors. Provides ensemble calibrated novelty score.
    """

    def __init__(self, random_state: int = 42, default_k: int = 5):
        self.detectors = {
            "knn": KNNNoveltyDetector(k=default_k),
            "mean_knn": MeanKNNNoveltyDetector(k=default_k),
            "lof": LOFNoveltyDetector(n_neighbors=20),
            "isolation_forest": IsolationForestNoveltyDetector(random_state=random_state),
            "centroid": CentroidNoveltyDetector(),
        }
        self.val_min_max: Dict[str, Tuple[float, float]] = {}

    def fit(self, train_embeddings: np.ndarray):
        for name, det in self.detectors.items():
            det.fit(train_embeddings)

    def calibrate(self, val_embeddings: np.ndarray):
        for name, det in self.detectors.items():
            det.calibrate_thresholds(val_embeddings, percentiles=(95.0, 99.0))
            scores = det.score(val_embeddings)
            s_min, s_max = float(np.min(scores)), float(np.max(scores))
            self.val_min_max[name] = (s_min, max(s_max, s_min + 1e-8))

    def score_all(self, embeddings: np.ndarray) -> pd.DataFrame:
        """Compute all detector scores, calibrated percentiles, and normalized composite score."""
        results = {}
        normed_scores = []
        for name, det in self.detectors.items():
            raw = det.score(embeddings)
            results[f"novelty_score_{name}"] = raw

            # Flags based on val thresholds
            p95 = det.thresholds.get("p95", float("inf"))
            p99 = det.thresholds.get("p99", float("inf"))
            results[f"is_novel_{name}_p95"] = raw >= p95
            results[f"is_novel_{name}_p99"] = raw >= p99

            # Normalize to [0, 1] using validation range
            s_min, s_max = self.val_min_max.get(name, (0.0, 1.0))
            normed = np.clip((raw - s_min) / (s_max - s_min), 0.0, 1.0)
            normed_scores.append(normed)

        # Composite novelty score: mean of normalized detector scores
        results["composite_novelty_score"] = np.mean(normed_scores, axis=0)
        return pd.DataFrame(results)
