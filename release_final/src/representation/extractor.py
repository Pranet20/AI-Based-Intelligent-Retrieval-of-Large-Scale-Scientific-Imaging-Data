"""Batch embedding extractor with checkpoint/resume and strict provenance tracking."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
import time
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import torch
import yaml

from src.ingestion.manifest import ManifestManager
from src.representation.dinov2_encoder import DINOv2Encoder
from src.representation.preprocessing import ScientificImagePreprocessor
from src.utils.logging import get_logger

logger = get_logger("representation.extractor")


class EmbeddingExtractor:
    """Orchestrates deterministic representation extraction for scientific image datasets."""

    def __init__(
        self,
        config_path: str | Path = "configs/phase2.yaml",
        device: Optional[str] = None,
    ) -> None:
        self.config_path = Path(config_path)
        with open(self.config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        model_cfg = self.config.get("model", {})
        prep_cfg = self.config.get("preprocessing", {})
        emb_cfg = self.config.get("embedding", {})

        self.model_name = model_cfg.get("name", "dinov2_vits14")
        self.normalize = emb_cfg.get("normalize", True)
        self.batch_size = emb_cfg.get("batch_size", 16)
        self.storage_dir = Path(emb_cfg.get("storage_dir", "data/processed/embeddings"))
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.failures_path = Path("reports/phase2/extraction_failures.csv")
        self.failures_path.parent.mkdir(parents=True, exist_ok=True)

        self.preprocessor = ScientificImagePreprocessor(
            image_size=tuple(prep_cfg.get("image_size", [224, 224])),
            version=prep_cfg.get("version", "1.0.0"),
            mean=tuple(prep_cfg.get("normalization", {}).get("mean", [0.485, 0.456, 0.406])),
            std=tuple(prep_cfg.get("normalization", {}).get("std", [0.229, 0.224, 0.225])),
        )

        self.encoder = DINOv2Encoder(
            model_name=self.model_name,
            hub_repo=model_cfg.get("hub_repo", "facebookresearch/dinov2"),
            device=device,
        )

    def extract_dataset(
        self,
        dataset_id: str,
        manifest_path: Optional[str | Path] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Extract representations for all valid records in a dataset manifest.

        Implements safe checkpoint and resume matching image_id and source SHA-256.
        """
        if manifest_path is None:
            manifest_path = Path(f"data/manifests/{dataset_id}_manifest.parquet")
        else:
            manifest_path = Path(manifest_path)

        if not manifest_path.is_file():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")

        df_manifest = ManifestManager.load_manifest(manifest_path)
        if limit and limit > 0:
            df_manifest = df_manifest.iloc[:limit]

        out_parquet = self.storage_dir / f"{dataset_id}_{self.model_name}_embeddings.parquet"
        existing_records: Dict[str, Dict[str, Any]] = {}

        # Resume support: check existing embeddings and verify provenance
        if out_parquet.is_file():
            try:
                df_existing = pd.read_parquet(out_parquet)
                for _, row in df_existing.iterrows():
                    # Key by image_id
                    existing_records[row["image_id"]] = row.to_dict()
                logger.info(
                    "Loaded %d existing embeddings from %s for resume.",
                    len(existing_records),
                    out_parquet,
                )
            except Exception as e:
                logger.warning("Could not read existing embeddings file: %s", e)

        output_rows: List[Dict[str, Any]] = []
        failures: List[Dict[str, Any]] = []
        batch_tensors: List[torch.Tensor] = []
        batch_metadata: List[Dict[str, Any]] = []

        total_images = len(df_manifest)
        t_start = time.time()
        logger.info(
            "Starting embedding extraction for %s: %d total images (batch_size=%d)...",
            dataset_id,
            total_images,
            self.batch_size,
        )

        def flush_batch() -> None:
            if not batch_tensors:
                return
            t_batch = torch.stack(batch_tensors, dim=0)
            emb_matrix = self.encoder.extract_features(t_batch, normalize=self.normalize)

            for i, meta in enumerate(batch_metadata):
                emb_vec = emb_matrix[i].astype(np.float32).tolist()
                rec = {
                    "image_id": meta["image_id"],
                    "dataset_id": dataset_id,
                    "embedding_model": self.model_name,
                    "embedding_version": "1.0.0",
                    "embedding_dimension": int(self.encoder.embedding_dimension),
                    "embedding_normalized": bool(self.normalize),
                    "embedding": emb_vec,
                    "source_manifest": str(manifest_path.name),
                    "source_sha256": meta["sha256"],
                    "preprocessing_version": self.preprocessor.version,
                    "specimen_id": meta.get("specimen_id"),
                    "roi_id": meta.get("roi_id"),
                    "acquisition_id": meta.get("acquisition_id"),
                    "label": meta.get("label"),
                    "group_id": meta.get("group_id"),
                }
                output_rows.append(rec)

            batch_tensors.clear()
            batch_metadata.clear()

        for idx, row in df_manifest.iterrows():
            img_id = str(row["image_id"])
            source_sha = str(row["sha256"])
            file_path = row.get("absolute_path_if_local_only")

            # Checkpoint match check
            if img_id in existing_records:
                existing = existing_records[img_id]
                if (
                    existing.get("source_sha256") == source_sha
                    and existing.get("embedding_model") == self.model_name
                    and existing.get("preprocessing_version") == self.preprocessor.version
                ):
                    output_rows.append(existing)
                    continue

            if not file_path or not Path(file_path).is_file():
                fail_rec = {
                    "image_id": img_id,
                    "source_path": str(file_path),
                    "dataset_id": dataset_id,
                    "error_type": "FileNotFoundError",
                    "error_message": f"Image path does not exist on disk: {file_path}",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                failures.append(fail_rec)
                self._record_failure(fail_rec)
                continue

            try:
                tensor, _ = self.preprocessor.preprocess_image_file(file_path)
                batch_tensors.append(tensor)
                batch_metadata.append(row.to_dict())

                if len(batch_tensors) >= self.batch_size:
                    flush_batch()
            except Exception as e:
                fail_rec = {
                    "image_id": img_id,
                    "source_path": str(file_path),
                    "dataset_id": dataset_id,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                failures.append(fail_rec)
                self._record_failure(fail_rec)

        # Flush trailing images
        flush_batch()
        elapsed_sec = time.time() - t_start

        # Save embeddings dataset Parquet
        df_out = pd.DataFrame(output_rows)
        df_out.to_parquet(out_parquet, index=False)
        logger.info(
            "Saved %d embeddings for %s to %s in %.2fs (%.2f img/s)",
            len(df_out),
            dataset_id,
            out_parquet,
            elapsed_sec,
            len(df_out) / max(elapsed_sec, 0.001),
        )

        return {
            "dataset_id": dataset_id,
            "total_images": total_images,
            "successful_embeddings": len(output_rows),
            "failed_images": len(failures),
            "output_path": str(out_parquet),
            "elapsed_seconds": elapsed_sec,
            "images_per_second": len(output_rows) / max(elapsed_sec, 0.001),
        }

    def _record_failure(self, failure_rec: Dict[str, Any]) -> None:
        """Append failure record to reports/phase2/extraction_failures.csv."""
        fieldnames = ["image_id", "source_path", "dataset_id", "error_type", "error_message", "timestamp"]
        write_header = not self.failures_path.is_file()
        with open(self.failures_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(failure_rec)

    def update_master_manifest(self) -> Path:
        """Build or update data/manifests/phase2_embedding_manifest.parquet."""
        master_path = Path("data/manifests/phase2_embedding_manifest.parquet")
        model_info = self.encoder.get_model_info()

        records: List[Dict[str, Any]] = []
        for emb_file in self.storage_dir.glob("*_embeddings.parquet"):
            df = pd.read_parquet(emb_file)
            dataset_id = df.iloc[0]["dataset_id"] if len(df) > 0 else emb_file.stem.split("_")[0]
            for row_idx, row in df.iterrows():
                records.append({
                    "image_id": row["image_id"],
                    "dataset_id": dataset_id,
                    "embedding_path": str(emb_file),
                    "embedding_row": int(row_idx),
                    "model_name": self.model_name,
                    "embedding_dimension": int(row["embedding_dimension"]),
                    "normalization": bool(row["embedding_normalized"]),
                    "preprocessing_version": str(row["preprocessing_version"]),
                    "source_sha256": str(row["source_sha256"]),
                    "extraction_timestamp": datetime.now(timezone.utc).isoformat(),
                    "python_version": model_info["python_version"],
                    "torch_version": model_info["torch_version"],
                    "device": model_info["device"],
                    "status": "SUCCESS",
                })

        df_master = pd.DataFrame(records)
        df_master.to_parquet(master_path, index=False)
        logger.info("Updated master embedding manifest: %d entries at %s", len(df_master), master_path)
        return master_path
