"""Embedding quality and numerical integrity validator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import pandas as pd


class EmbeddingValidator:
    """Validates numerical integrity, dimensions, uniqueness, and norm bounds of embeddings."""

    @staticmethod
    def validate_dataset_embeddings(
        embeddings_path: str | Path,
        expected_count: int,
        expected_dimension: int = 384,
        check_normalized: bool = True,
    ) -> Dict[str, Any]:
        """Validate embedding parquet file and compute statistical indicators."""
        path = Path(embeddings_path)
        if not path.is_file():
            raise FileNotFoundError(f"Embeddings file does not exist: {path}")

        df = pd.read_parquet(path)
        actual_count = len(df)
        dataset_id = str(df.iloc[0]["dataset_id"]) if actual_count > 0 else "unknown"

        # Unique image_ids
        duplicate_id_count = int(df["image_id"].duplicated().sum())

        # Vector validation
        nan_count = 0
        inf_count = 0
        zero_vector_count = 0
        norms: List[float] = []

        all_vectors = []
        for vec in df["embedding"]:
            arr = np.array(vec, dtype=np.float32)
            if len(arr) != expected_dimension:
                raise ValueError(
                    f"Vector dimension mismatch: expected {expected_dimension}, got {len(arr)}"
                )

            nan_count += int(np.isnan(arr).sum())
            inf_count += int(np.isinf(arr).sum())

            norm_val = float(np.linalg.norm(arr))
            if norm_val < 1e-7:
                zero_vector_count += 1
            norms.append(norm_val)
            all_vectors.append(arr)

        norms_arr = np.array(norms, dtype=np.float32)
        mean_norm = float(np.mean(norms_arr)) if len(norms_arr) > 0 else 0.0
        std_norm = float(np.std(norms_arr)) if len(norms_arr) > 0 else 0.0
        min_norm = float(np.min(norms_arr)) if len(norms_arr) > 0 else 0.0
        max_norm = float(np.max(norms_arr)) if len(norms_arr) > 0 else 0.0

        is_valid = (
            nan_count == 0
            and inf_count == 0
            and duplicate_id_count == 0
            and zero_vector_count == 0
            and actual_count == expected_count
        )
        if check_normalized:
            # Norms should be within 1e-3 of 1.0
            is_valid = is_valid and (abs(mean_norm - 1.0) < 1e-3)

        result = {
            "dataset": dataset_id,
            "expected_count": int(expected_count),
            "successful_count": int(actual_count),
            "failed_count": int(max(0, expected_count - actual_count)),
            "embedding_dimension": int(expected_dimension),
            "nan_count": int(nan_count),
            "inf_count": int(inf_count),
            "duplicate_image_id_count": int(duplicate_id_count),
            "zero_vector_count": int(zero_vector_count),
            "mean_norm": round(mean_norm, 6),
            "std_norm": round(std_norm, 6),
            "min_norm": round(min_norm, 6),
            "max_norm": round(max_norm, 6),
            "validation_status": "PASSED" if is_valid else "FAILED",
        }

        return result

    @staticmethod
    def save_validation_report(
        results: Dict[str, Any] | List[Dict[str, Any]],
        output_path: str | Path = "reports/phase2/embedding_validation.json",
    ) -> Path:
        """Save validation summary to JSON report."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        return out_p
