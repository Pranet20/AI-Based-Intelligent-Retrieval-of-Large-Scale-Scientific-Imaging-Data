"""FAISS indexing abstraction supporting IndexFlatIP, IndexIVFFlat, and IndexHNSWFlat."""

from __future__ import annotations

import enum
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import faiss
import numpy as np

from src.utils.logging import get_logger

logger = get_logger("retrieval.faiss_index")


class IndexType(str, enum.Enum):
    FLAT_IP = "IndexFlatIP"
    IVF_FLAT = "IndexIVFFlat"
    HNSW_FLAT = "IndexHNSWFlat"


class FAISSVectorIndex:
    """Production-quality FAISS index manager for 384-dimensional scientific representations."""

    def __init__(
        self,
        dimension: int = 384,
        index_type: IndexType | str = IndexType.FLAT_IP,
        metric: str = "inner_product",
        nlist: int = 32,
        nprobe: int = 4,
        hnsw_m: int = 16,
        ef_search: int = 32,
        ef_construction: int = 64,
        seed: int = 42,
    ) -> None:
        self.dimension = dimension
        self.index_type = IndexType(index_type) if isinstance(index_type, str) else index_type
        self.metric_type = faiss.METRIC_INNER_PRODUCT if metric == "inner_product" else faiss.METRIC_L2
        self.nlist = nlist
        self.nprobe = nprobe
        self.hnsw_m = hnsw_m
        self.ef_search = ef_search
        self.ef_construction = ef_construction
        self.seed = seed

        self.index: Optional[faiss.Index] = None
        self.id_map: List[str] = []
        self._id_to_idx: Dict[str, int] = {}
        self.is_trained: bool = False
        self.ntotal: int = 0

    def validate_vectors(self, vectors: np.ndarray, check_normalized: bool = True) -> np.ndarray:
        """Validate vector array shape, dtype, finiteness, and unit normalization."""
        if not isinstance(vectors, np.ndarray):
            vectors = np.asarray(vectors)

        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)

        if not vectors.flags["C_CONTIGUOUS"]:
            vectors = np.ascontiguousarray(vectors)

        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        if vectors.shape[1] != self.dimension:
            raise ValueError(
                f"Vector dimension mismatch: expected {self.dimension}, got {vectors.shape[1]}"
            )

        if not np.all(np.isfinite(vectors)):
            raise ValueError("Vector array contains non-finite values (NaN or Inf).")

        if check_normalized and self.metric_type == faiss.METRIC_INNER_PRODUCT:
            norms = np.linalg.norm(vectors, axis=1)
            if not np.allclose(norms, 1.0, atol=1e-3):
                logger.warning(
                    "Inner product index expects unit-normalized vectors. Found norm range [%.4f, %.4f].",
                    float(np.min(norms)),
                    float(np.max(norms)),
                )

        return vectors

    def build(self, embeddings: np.ndarray, ids: Optional[List[str]] = None) -> None:
        """Instantiate index, train if necessary (IVF), and add vectors."""
        emb = self.validate_vectors(embeddings)
        n_samples = emb.shape[0]

        if ids is not None:
            if len(ids) != n_samples:
                raise ValueError(f"IDs length ({len(ids)}) does not match embeddings ({n_samples})")
            self.id_map = list(ids)
        else:
            self.id_map = [str(i) for i in range(n_samples)]

        self._id_to_idx = {sid: idx for idx, sid in enumerate(self.id_map)}

        logger.info(
            "Building %s with dimension=%d, metric=%s, samples=%d",
            self.index_type.value,
            self.dimension,
            "IP" if self.metric_type == faiss.METRIC_INNER_PRODUCT else "L2",
            n_samples,
        )

        if self.index_type == IndexType.FLAT_IP:
            self.index = faiss.IndexFlatIP(self.dimension)
            self.is_trained = True

        elif self.index_type == IndexType.IVF_FLAT:
            # Check valid nlist relative to sample count
            actual_nlist = min(self.nlist, max(1, n_samples // 4)) if n_samples < self.nlist * 4 else self.nlist
            if actual_nlist != self.nlist:
                logger.warning(
                    "Adjusting nlist from %d to %d because sample count (%d) is small.",
                    self.nlist,
                    actual_nlist,
                    n_samples,
                )
            self.nlist = actual_nlist

            quantizer = faiss.IndexFlatIP(self.dimension)
            self.index = faiss.IndexIVFFlat(
                quantizer,
                self.dimension,
                self.nlist,
                self.metric_type,
            )
            # Train quantizer on embeddings
            logger.info("Training IVF quantizer on %d vectors (nlist=%d)...", n_samples, self.nlist)
            self.index.train(emb)
            self.is_trained = self.index.is_trained
            self.index.nprobe = min(self.nprobe, self.nlist)

        elif self.index_type == IndexType.HNSW_FLAT:
            self.index = faiss.IndexHNSWFlat(self.dimension, self.hnsw_m, self.metric_type)
            self.index.hnsw.efConstruction = self.ef_construction
            self.index.hnsw.efSearch = self.ef_search
            self.is_trained = True

        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")

        # Add vectors
        self.index.add(emb)
        self.ntotal = self.index.ntotal
        logger.info("Successfully added %d vectors to %s", self.ntotal, self.index_type.value)

    def set_query_parameters(self, nprobe: Optional[int] = None, ef_search: Optional[int] = None) -> None:
        """Dynamically adjust search-time hyperparameters."""
        if self.index is None:
            raise RuntimeError("Index has not been built or loaded.")

        if nprobe is not None:
            self.nprobe = nprobe
            if hasattr(self.index, "nprobe"):
                self.index.nprobe = min(nprobe, self.nlist)

        if ef_search is not None:
            self.ef_search = ef_search
            if hasattr(self.index, "hnsw"):
                self.index.hnsw.efSearch = ef_search

    def search(
        self,
        queries: np.ndarray,
        k: int,
        nprobe: Optional[int] = None,
        ef_search: Optional[int] = None,
    ) -> Tuple[np.ndarray, np.ndarray, List[List[str]]]:
        """Search K nearest neighbors.

        Args:
            queries: Array of shape (N_q, dimension) float32.
            k: Number of nearest neighbors to retrieve.
            nprobe: Optional IVF nprobe override.
            ef_search: Optional HNSW efSearch override.

        Returns:
            Tuple of:
            - scores: (N_q, K) float32 cosine similarity scores
            - indices: (N_q, K) int64 FAISS row indices
            - id_results: List of length N_q containing lists of K string image IDs
        """
        if self.index is None:
            raise RuntimeError("Index is uninitialized. Call build() or load() first.")

        q = self.validate_vectors(queries)
        self.set_query_parameters(nprobe=nprobe, ef_search=ef_search)

        k_clamped = min(k, self.ntotal)
        scores, indices = self.index.search(q, k_clamped)

        # Map indices to string IDs
        id_results: List[List[str]] = []
        for row in indices:
            row_ids = [self.id_map[idx] if 0 <= idx < len(self.id_map) else "UNKNOWN" for idx in row]
            id_results.append(row_ids)

        return scores, indices, id_results

    def save(self, file_path: Union[str, Path]) -> Tuple[Path, Path]:
        """Serialize FAISS index and string ID mapping.

        Returns:
            Tuple of (index_path, metadata_json_path).
        """
        if self.index is None:
            raise RuntimeError("Cannot save uninitialized index.")

        index_p = Path(file_path)
        index_p.parent.mkdir(parents=True, exist_ok=True)
        if index_p.suffix != ".faiss":
            index_p = index_p.with_suffix(".faiss")

        meta_p = index_p.with_suffix(".meta.json")

        # Write FAISS binary
        faiss.write_index(self.index, str(index_p))

        # Write metadata & ID mapping
        meta = {
            "dimension": self.dimension,
            "index_type": self.index_type.value,
            "metric": "inner_product" if self.metric_type == faiss.METRIC_INNER_PRODUCT else "l2",
            "nlist": self.nlist,
            "nprobe": self.nprobe,
            "hnsw_m": self.hnsw_m,
            "ef_search": self.ef_search,
            "ef_construction": self.ef_construction,
            "ntotal": self.ntotal,
            "id_map": self.id_map,
        }
        with open(meta_p, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        logger.info("Saved FAISS index to %s and metadata to %s", index_p, meta_p)
        return index_p, meta_p

    @classmethod
    def load(cls, file_path: Union[str, Path]) -> "FAISSVectorIndex":
        """Load serialized FAISS index and ID mapping."""
        index_p = Path(file_path)
        if index_p.suffix != ".faiss":
            index_p = index_p.with_suffix(".faiss")

        meta_p = index_p.with_suffix(".meta.json")

        if not index_p.is_file():
            raise FileNotFoundError(f"FAISS index file not found: {index_p}")
        if not meta_p.is_file():
            raise FileNotFoundError(f"FAISS metadata file not found: {meta_p}")

        with open(meta_p, "r", encoding="utf-8") as f:
            meta = json.load(f)

        instance = cls(
            dimension=meta["dimension"],
            index_type=meta["index_type"],
            metric=meta["metric"],
            nlist=meta.get("nlist", 32),
            nprobe=meta.get("nprobe", 4),
            hnsw_m=meta.get("hnsw_m", 16),
            ef_search=meta.get("ef_search", 32),
            ef_construction=meta.get("ef_construction", 64),
        )

        instance.index = faiss.read_index(str(index_p))
        instance.id_map = meta["id_map"]
        instance._id_to_idx = {sid: idx for idx, sid in enumerate(instance.id_map)}
        instance.ntotal = instance.index.ntotal
        instance.is_trained = instance.index.is_trained

        logger.info("Loaded FAISS %s with %d vectors from %s", instance.index_type.value, instance.ntotal, index_p)
        return instance
