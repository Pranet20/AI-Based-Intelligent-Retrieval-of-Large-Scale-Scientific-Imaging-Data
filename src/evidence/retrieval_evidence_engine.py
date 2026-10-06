"""Comparable Image Retrieval & Evidence Engine for Phase 5.

Queries verified reference galleries using foundation model and acquisition-adapted
embeddings to retrieve grounded visual evidence, cross-instrument peers, and artifact exemplars.
Supports deterministic ranking tie-breaking, same-acquisition exclusion, and cross-instrument filtering.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.evidence.schemas import (
    ArtifactCategory,
    ComparableEvidenceImage,
    EvidenceRole,
)


class RetrievalEvidenceEngine:
    """Retrieves and ranks comparable reference micrographs with strict provenance metadata."""

    def __init__(
        self,
        gallery_features: np.ndarray,
        gallery_metadata: pd.DataFrame,
        top_k: int = 5,
    ) -> None:
        """
        Args:
            gallery_features: (N, D) normalized feature vectors of verified gallery images.
            gallery_metadata: DataFrame containing image_id, specimen_id, acquisition_id,
                              instrument, detector, accelerating_voltage_kv, etc.
            top_k: Number of comparable evidence micrographs to retrieve per query.
        """
        self.features = gallery_features.astype(np.float32)
        # Ensure L2 normalized
        norms = np.linalg.norm(self.features, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.features = self.features / norms
        self.metadata = gallery_metadata.reset_index(drop=True)
        self.top_k = top_k

    def retrieve_comparable_evidence(
        self,
        query_feature: np.ndarray,
        query_specimen_id: Optional[str] = None,
        query_acquisition_id: Optional[str] = None,
        query_instrument: Optional[str] = None,
        predicted_artifact: Optional[ArtifactCategory] = None,
        exclude_same_acquisition: bool = False,
        cross_instrument_only: bool = False,
    ) -> List[ComparableEvidenceImage]:
        """Retrieve structured comparable micrographs demonstrating clean structure and cross-acquisition variation.
        
        Features deterministic tie-breaking by (-similarity, image_id), duplicate prevention,
        and selective cross-acquisition / cross-instrument filtering.
        """
        q_feat = query_feature.astype(np.float32).flatten()
        q_norm = float(np.linalg.norm(q_feat))
        if q_norm > 0:
            q_feat = q_feat / q_norm

        sims = np.dot(self.features, q_feat)

        # Deterministic ranking with lexical tie-breaking:
        # Sort primary by negative similarity, secondary by image_id alphabetically
        img_ids = [str(self.metadata.iloc[i].get("image_id", f"gal_{i}")) for i in range(len(self.metadata))]
        # Create sorting keys
        indices = list(range(len(self.metadata)))
        ranked_indices = sorted(indices, key=lambda idx: (-round(float(sims[idx]), 7), img_ids[idx]))

        evidence_items: List[ComparableEvidenceImage] = []
        seen_images: Set[str] = set()
        seen_shas: Set[str] = set()

        # 1. First priority: Same-specimen cross-acquisition peers if query specimen is known
        if query_specimen_id is not None and "specimen_id" in self.metadata.columns:
            for idx in ranked_indices:
                if len(evidence_items) >= 2:
                    break
                row = self.metadata.iloc[idx]
                img_id = img_ids[idx]
                row_specimen = str(row.get("specimen_id", "UNKNOWN"))
                row_acq = str(row.get("acquisition_id", "UNKNOWN"))
                row_inst = str(row.get("instrument", "UNKNOWN"))

                # Check same specimen
                if row_specimen != query_specimen_id:
                    continue

                # Check cross-acquisition requirement
                if query_acquisition_id is not None and row_acq == query_acquisition_id:
                    continue

                # Check cross-instrument requirement
                if cross_instrument_only and query_instrument is not None and row_inst == query_instrument:
                    continue

                sha = str(row.get("sha256", ""))
                if img_id in seen_images or (sha and sha in seen_shas):
                    continue

                seen_images.add(img_id)
                if sha:
                    seen_shas.add(sha)

                evidence_items.append(
                    ComparableEvidenceImage(
                        image_id=img_id,
                        role=EvidenceRole.SAME_SPECIMEN_CROSS_ACQUISITION,
                        similarity_score=float(sims[idx]),
                        specimen_id=row_specimen,
                        acquisition_id=row_acq,
                        instrument=str(row.get("instrument", "UNKNOWN")) if pd.notna(row.get("instrument")) else None,
                        detector=str(row.get("detector", "UNKNOWN")) if pd.notna(row.get("detector")) else None,
                        accelerating_voltage_kv=float(row["accelerating_voltage_kv"]) if pd.notna(row.get("accelerating_voltage_kv")) else None,
                        file_path=str(row.get("image_path", "")) if pd.notna(row.get("image_path")) else None,
                        provenance_hash=sha if sha else None,
                    )
                )

        # 2. General top similar clean reference micrographs
        for idx in ranked_indices:
            if len(evidence_items) >= self.top_k:
                break
            row = self.metadata.iloc[idx]
            img_id = img_ids[idx]
            sha = str(row.get("sha256", ""))

            # Filter duplicate evidence
            if img_id in seen_images or (sha and sha in seen_shas):
                continue

            row_acq = str(row.get("acquisition_id", "UNKNOWN"))
            row_inst = str(row.get("instrument", "UNKNOWN"))

            # Filter same acquisition if requested
            if exclude_same_acquisition and query_acquisition_id is not None and row_acq == query_acquisition_id:
                continue

            # Filter cross-instrument only if requested
            if cross_instrument_only and query_instrument is not None and row_inst == query_instrument:
                continue

            # Determine role
            row_artifact = str(row.get("artifact_type", "NORMAL"))
            if row_artifact == "NORMAL":
                role = EvidenceRole.SIMILAR_CLEAN_MICROGRAPH
            elif predicted_artifact is not None and row_artifact == predicted_artifact.value:
                role = EvidenceRole.COMPARABLE_ARTIFACT_EXEMPLAR
            else:
                role = EvidenceRole.SIMILAR_CLEAN_MICROGRAPH

            seen_images.add(img_id)
            if sha:
                seen_shas.add(sha)

            evidence_items.append(
                ComparableEvidenceImage(
                    image_id=img_id,
                    role=role,
                    similarity_score=float(sims[idx]),
                    specimen_id=str(row.get("specimen_id", "UNKNOWN")),
                    acquisition_id=row_acq,
                    instrument=str(row.get("instrument", "UNKNOWN")) if pd.notna(row.get("instrument")) else None,
                    detector=str(row.get("detector", "UNKNOWN")) if pd.notna(row.get("detector")) else None,
                    accelerating_voltage_kv=float(row["accelerating_voltage_kv"]) if pd.notna(row.get("accelerating_voltage_kv")) else None,
                    file_path=str(row.get("image_path", "")) if pd.notna(row.get("image_path")) else None,
                    provenance_hash=sha if sha else None,
                )
            )

        return evidence_items
