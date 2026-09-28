"""Production FAISS Vector Retrieval Engine."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import faiss
import numpy as np

from app.core.config import settings


class FAISSEngine:
    """FAISS retrieval engine supporting exact cosine search on L2-normalized embeddings."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FAISSEngine, cls).__new__(cls)
            cls._instance._init_index()
        return cls._instance

    def _init_index(self):
        self.dimension = settings.DINOV2_EMBEDDING_DIM
        self.index_path = settings.INDEXES_PATH / "faiss_exact_flatip.index"
        self.id_map_path = settings.INDEXES_PATH / "id_map.json"
        self.id_to_image_id: List[int] = []
        self.image_id_to_id: Dict[int, int] = {}

        if self.index_path.exists() and self.id_map_path.exists():
            import json
            self.index = faiss.read_index(str(self.index_path))
            with open(self.id_map_path, "r", encoding="utf-8") as f:
                self.id_to_image_id = json.load(f)
            self.image_id_to_id = {img_id: idx for idx, img_id in enumerate(self.id_to_image_id)}
        else:
            # Exact inner product (equivalent to cosine similarity on L2-normalized vectors)
            self.index = faiss.IndexFlatIP(self.dimension)

    def add_vector(self, image_id: int, vector: np.ndarray) -> int:
        """Add single L2-normalized vector mapped to image_id."""
        vec = np.asarray(vector, dtype=np.float32).reshape(1, -1)
        # Ensure L2 normalized
        norm = np.linalg.norm(vec)
        if norm > 1e-12:
            vec = vec / norm

        if image_id in self.image_id_to_id:
            # Already indexed
            return self.image_id_to_id[image_id]

        faiss_id = len(self.id_to_image_id)
        self.index.add(vec)
        self.id_to_image_id.append(image_id)
        self.image_id_to_id[image_id] = faiss_id
        self.save()
        return faiss_id

    def search(self, query_vector: np.ndarray, top_k: int = 10) -> List[Tuple[int, float]]:
        """Search nearest neighbors for L2-normalized query vector."""
        if self.index.ntotal == 0:
            return []

        q_vec = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        norm = np.linalg.norm(q_vec)
        if norm > 1e-12:
            q_vec = q_vec / norm

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q_vec, k)

        results = []
        for rank in range(k):
            idx = indices[0][rank]
            if idx >= 0 and idx < len(self.id_to_image_id):
                img_id = self.id_to_image_id[idx]
                sim = float(scores[0][rank])
                results.append((img_id, sim))
        return results

    def save(self) -> None:
        """Persist index and ID map to disk."""
        import json
        settings.INDEXES_PATH.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.id_map_path, "w", encoding="utf-8") as f:
            json.dump(self.id_to_image_id, f)

    def reset(self) -> None:
        """Clear the index and ID mapping."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.id_to_image_id.clear()
        self.image_id_to_id.clear()
        if self.index_path.exists():
            os.remove(self.index_path)
        if self.id_map_path.exists():
            os.remove(self.id_map_path)
