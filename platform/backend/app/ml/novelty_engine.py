"""Production Relative Embedding-Space Novelty Engine with Lazy Loading."""

from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np


class NoveltyEngine:
    """Computes relative embedding-space novelty using k-nearest-neighbor distances."""

    def __init__(self, k: int = 5):
        self.k = k
        self.reference_embeddings: Optional[np.ndarray] = None

    def _ensure_reference_corpus(self):
        if self.reference_embeddings is None:
            import pandas as pd
            ref_path = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
            if ref_path.exists():
                df = pd.read_parquet(ref_path)
                if "embedding" in df.columns:
                    self.reference_embeddings = np.vstack(df["embedding"].values)

    def evaluate_novelty(
        self,
        embedding: np.ndarray,
        corpus_embeddings: Optional[np.ndarray] = None,
    ) -> Dict[str, Union[float, str]]:
        """
        Compute relative embedding-space novelty:
        Mean cosine distance to k nearest neighbors in the reference corpus.
        Terminology: "relative embedding-space novelty".
        """
        self._ensure_reference_corpus()
        ref = corpus_embeddings if corpus_embeddings is not None else self.reference_embeddings
        if ref is None or len(ref) == 0:
            return {
                "novelty_score": 0.0,
                "novelty_percentile": 50.0,
                "reference_corpus": "empty_or_uninitialized",
                "interpretation": "Insufficient reference corpus to assess novelty",
            }

        q = embedding.reshape(1, -1)
        sims = np.dot(ref, q.T).flatten()  # Cosine similarities
        dists = 1.0 - sims  # Cosine distances

        k = min(self.k, len(dists))
        k_smallest_dists = np.partition(dists, k - 1)[:k]
        novelty_score = float(np.mean(k_smallest_dists))

        # Empirical percentile estimation
        percentile = float(np.clip(novelty_score / 0.80 * 100.0, 0.0, 100.0))

        return {
            "novelty_score": float(novelty_score),
            "novelty_percentile": float(percentile),
            "reference_corpus": "hcci_in_domain_reference",
            "interpretation": "relative embedding-space novelty",
        }
