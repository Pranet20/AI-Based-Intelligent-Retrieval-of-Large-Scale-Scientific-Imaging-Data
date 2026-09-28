"""Post-hoc linear and kNN classifier probes for acquisition and material retention."""

from __future__ import annotations

from typing import Any, Dict, List
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier


class ProbeEvaluator:
    """Evaluates how strongly embeddings predict acquisition conditions vs material identity."""

    @staticmethod
    def evaluate_probes(
        embeddings: np.ndarray,
        material_labels: List[str] | np.ndarray,
        instrument_labels: List[str] | np.ndarray,
        n_splits: int = 5,
        random_state: int = 42,
    ) -> Dict[str, float]:
        """Run 5-fold cross-validated logistic regression and kNN probes.

        Returns:
            Dict containing instrument probe accuracy, material linear probe accuracy,
            and material kNN probe accuracy.
        """
        X = np.asarray(embeddings, dtype=np.float32)
        y_mat = np.asarray(material_labels)
        y_inst = np.asarray(instrument_labels)

        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

        # 1. Acquisition Instrument Probe (Logistic Regression)
        inst_accs: List[float] = []
        for tr, te in skf.split(X, y_inst):
            clf = LogisticRegression(max_iter=1000, C=1.0, random_state=random_state)
            clf.fit(X[tr], y_inst[tr])
            preds = clf.predict(X[te])
            inst_accs.append(float(accuracy_score(y_inst[te], preds)))

        # 2. Material Identity Linear Probe (Logistic Regression)
        mat_accs: List[float] = []
        for tr, te in skf.split(X, y_mat):
            clf = LogisticRegression(max_iter=1000, C=1.0, random_state=random_state)
            clf.fit(X[tr], y_mat[tr])
            preds = clf.predict(X[te])
            mat_accs.append(float(accuracy_score(y_mat[te], preds)))

        # 3. Material Identity kNN Probe (k=5, cosine metric)
        knn_accs: List[float] = []
        for tr, te in skf.split(X, y_mat):
            knn = KNeighborsClassifier(n_neighbors=5, metric="cosine")
            knn.fit(X[tr], y_mat[tr])
            preds = knn.predict(X[te])
            knn_accs.append(float(accuracy_score(y_mat[te], preds)))

        return {
            "acquisition_probe_accuracy": float(np.mean(inst_accs)),
            "material_linear_probe_accuracy": float(np.mean(mat_accs)),
            "material_knn_probe_accuracy": float(np.mean(knn_accs)),
        }
