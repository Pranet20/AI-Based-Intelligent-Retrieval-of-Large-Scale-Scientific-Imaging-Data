"""Metadata vector encoder and similarity calculator for Phase 5."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.metadata.phase5_features import Phase5FeaturePipeline
from src.metadata.phase5_validator import validate_metadata_vectors
from src.utils.logging import get_logger

logger = get_logger("metadata.phase5_encoder")


def normalize_l2(vectors: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Normalize 2D vectors to unit L2 norm along axis 1 safely.
    
    If a row has norm < eps, it is kept as an all-zero vector without NaN/Inf.
    """
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    zero_mask = norms < eps
    safe_norms = np.where(zero_mask, 1.0, norms)
    normalized = vectors / safe_norms
    normalized[zero_mask.squeeze(axis=1)] = 0.0
    return normalized.astype(np.float32)


class Phase5MetadataEncoder:
    """Encodes scientific metadata into L2-normalized representations."""

    def __init__(self, feature_group: str = "E") -> None:
        self.feature_group = feature_group
        self.pipeline = Phase5FeaturePipeline(feature_group=feature_group)
        self.is_fitted = False
        self.schema_hash: str = ""

    def fit(self, train_manifest: pd.DataFrame) -> "Phase5MetadataEncoder":
        """Fit feature extractor on training partition."""
        self.pipeline.fit(train_manifest)
        self.is_fitted = True
        
        # Calculate schema hash
        provenance = self.pipeline.get_provenance()
        prov_bytes = json.dumps(provenance, sort_keys=True).encode("utf-8")
        self.schema_hash = hashlib.sha256(prov_bytes).hexdigest()
        return self

    def encode(self, manifest: pd.DataFrame) -> Tuple[np.ndarray, List[str]]:
        """Extract and L2-normalize metadata feature vectors.
        
        Args:
            manifest: DataFrame containing metadata.
            
        Returns:
            Tuple of (normalized_vectors, feature_names) where vectors is (N, D).
        """
        raw_feats, feat_names = self.pipeline.transform(manifest)
        if raw_feats.shape[1] == 0:
            return raw_feats, feat_names
        
        norm_feats = normalize_l2(raw_feats)
        validate_metadata_vectors(norm_feats, feat_names)
        return norm_feats, feat_names

    def compute_similarity_matrix(
        self,
        query_vectors: np.ndarray,
        candidate_vectors: Optional[np.ndarray] = None,
    ) -> np.ndarray:
        """Compute cosine similarity between normalized metadata vectors.
        
        Args:
            query_vectors: (Q, D) array of unit-normalized metadata vectors.
            candidate_vectors: Optional (C, D) array of candidate metadata vectors.
            
        Returns:
            sim_matrix: (Q, C) cosine similarity matrix in [-1.0, 1.0].
        """
        if candidate_vectors is None:
            candidate_vectors = query_vectors

        if query_vectors.shape[1] == 0 or candidate_vectors.shape[1] == 0:
            return np.zeros((len(query_vectors), len(candidate_vectors)), dtype=np.float32)

        sim = query_vectors @ candidate_vectors.T
        return np.clip(sim, -1.0, 1.0).astype(np.float32)

    def save(self, filepath: str | Path) -> None:
        """Save encoder configuration and parameters to JSON."""
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted encoder.")
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "feature_group": self.feature_group,
            "schema_hash": self.schema_hash,
            "provenance": self.pipeline.get_provenance(),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved metadata encoder parameters to {path}")

    @classmethod
    def load(cls, filepath: str | Path) -> "Phase5MetadataEncoder":
        """Load encoder parameters from JSON."""
        path = Path(filepath)
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        encoder = cls(feature_group=data["feature_group"])
        prov = data["provenance"]
        
        pipe = encoder.pipeline
        pipe.num_means = {k: float(v) for k, v in prov["means"].items()}
        pipe.num_stds = {k: float(v) for k, v in prov["stds"].items()}
        pipe.num_medians = {k: float(v) for k, v in prov["medians"].items()}
        pipe.cat_vocabularies = prov["vocabularies"]
        pipe.fitted_feature_names = prov["feature_names"]
        pipe.is_fitted = True
        
        encoder.is_fitted = True
        encoder.schema_hash = data.get("schema_hash", "")
        return encoder
