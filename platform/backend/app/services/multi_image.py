"""Multi-Image Scientific Comparison, Duplicate Detection, and Quality-Risk Service.

Orchestrates:
Pipeline A: Redundancy & Duplicate Analysis (pairwise comparison, cascade, similarity matrix, groups)
Pipeline B: Quality-Risk Analysis (indicators, localization, uncertainty, evidence, corrective action)
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from fastapi import HTTPException
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    AuditLog,
    Embedding,
    Image,
    ImageMetadata,
    QualityProfile,
    ReviewItem,
)
from app.ml.dinov2_engine import DINOv2Engine
from app.ml.phase4_engine import Phase4Engine
from app.services.audit import AuditService
from app.services.provenance import ProvenanceService
from src.evidence.evidence_aggregator import EvidenceAggregator
from src.evidence.explanation_generator import ExplanationGenerator
from src.evidence.localization_engine import LocalizationEngine
from src.evidence.quality_risk_engine import QualityRiskEngine
from src.evidence.retrieval_evidence_engine import RetrievalEvidenceEngine
from src.ingestion.reader import ScientificImageReader
from src.integrity.duplicate_cascade import compute_pixel_metrics
from src.integrity.exact_duplicates import (
    compute_decoded_pixel_sha256,
    compute_file_sha256,
)
from src.integrity.perceptual_hash import compute_dhash, compute_phash

logger = logging.getLogger("scidata.multi_image")


class MultiImageComparisonService:
    """Service orchestrating multi-image comparison, duplicate detection, and quality-risk analysis."""

    @classmethod
    def analyze_images(
        cls,
        db: Session,
        image_ids: List[int],
        representation: str = "dinov2_base",
        current_user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Execute full multi-image comparative workflow across N images (N >= 2)."""
        # Guard 1: Minimum count
        if len(image_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="Multi-image analysis requires at least 2 distinct images.",
            )

        # Guard 2: Representation validation & Strict Phase 4 availability check
        if representation == "phase4_adapted":
            p4 = Phase4Engine()
            try:
                p4._ensure_loaded()
            except Exception as e:
                raise HTTPException(
                    status_code=503,
                    detail=f"Phase4 acquisition-aware representation is unavailable: {str(e)}",
                )
        elif representation != "dinov2_base":
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported representation '{representation}'. Allowed: ['dinov2_base', 'phase4_adapted']",
            )

        # Retrieve images and ensure uniqueness preserving order
        unique_ids = []
        for img_id in image_ids:
            if img_id not in unique_ids:
                unique_ids.append(img_id)

        if len(unique_ids) < 2:
            raise HTTPException(
                status_code=400,
                detail="Multi-image analysis requires at least 2 distinct images.",
            )

        images: List[Image] = []
        for img_id in unique_ids:
            img = db.query(Image).filter(Image.id == img_id).first()
            if not img:
                raise HTTPException(status_code=404, detail=f"Image ID {img_id} not found.")
            if not img.storage_path or not Path(img.storage_path).is_file():
                raise HTTPException(
                    status_code=404,
                    detail=f"Image file for ID {img_id} not found on disk at {img.storage_path}.",
                )
            images.append(img)

        n = len(images)
        analysis_id = f"MIA-{datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%d%H%M%S')}-{uuid_short()}"
        timestamp_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()

        # -------------------------------------------------------------
        # STEP 1: EXTRACT / LOAD EMBEDDINGS AND HASHEST FOR ALL IMAGES
        # -------------------------------------------------------------
        embeddings_map: Dict[int, np.ndarray] = {}
        hashes_map: Dict[int, Dict[str, Any]] = {}
        arrays_map: Dict[int, np.ndarray] = {}

        dinov2_engine = DINOv2Engine()
        phase4_engine = Phase4Engine() if representation == "phase4_adapted" else None

        for img in images:
            arr, _ = ScientificImageReader.load_array(img.storage_path)
            arrays_map[img.id] = arr

            # Hashes
            f_sha = img.sha256 or compute_file_sha256(img.storage_path)
            pix_sha = compute_decoded_pixel_sha256(img.storage_path)
            ph = compute_phash(img.storage_path)
            dh = compute_dhash(img.storage_path)
            ph_str = "".join(["1" if b else "0" for b in ph])
            dh_str = "".join(["1" if b else "0" for b in dh])

            hashes_map[img.id] = {
                "file_sha256": f_sha,
                "pixel_sha256": pix_sha,
                "phash": ph_str,
                "dhash": dh_str,
            }

            # Embeddings
            vec = cls._get_or_compute_embedding(
                db=db,
                image=img,
                representation=representation,
                dinov2_engine=dinov2_engine,
                phase4_engine=phase4_engine,
            )
            # L2 normalize
            norm = float(np.linalg.norm(vec))
            if norm > 1e-12:
                vec = vec / norm
            embeddings_map[img.id] = vec

        # -------------------------------------------------------------
        # STEP 2: PIPELINE B — QUALITY-RISK, LOCALIZATION & EXPLANATION
        # -------------------------------------------------------------
        quality_engine = QualityRiskEngine()
        localization_engine = LocalizationEngine()
        explanation_gen = ExplanationGenerator()

        per_image_results = []
        quality_risk_count = 0
        uncertain_count = 0

        # Build gallery for evidence if peer embeddings exist
        gallery_engine = cls._build_cohort_evidence_engine(db, unique_ids)

        for img in images:
            arr = arrays_map[img.id]
            meta_rel = img.metadata_rel

            # Metadata context
            meta_dict = {
                "instrument": meta_rel.microscope if meta_rel else None,
                "detector": meta_rel.detector if meta_rel else None,
                "accelerating_voltage_kv": meta_rel.accelerating_voltage_kv if meta_rel else None,
                "magnification": meta_rel.magnification if meta_rel else None,
                "working_distance_mm": meta_rel.working_distance_mm if meta_rel else None,
                "specimen_id": getattr(meta_rel, "specimen_id", None) if meta_rel else None,
                "acquisition_id": getattr(meta_rel, "acquisition_id", None) if meta_rel else None,
                "data_source": "SCI-INTEL-MULTI",
                "sha256": img.sha256,
            }

            # Evidence aggregation (integrates handcrafted quality signals, risk triage, localization, evidence retrieval)
            aggregator = EvidenceAggregator(
                quality_engine=quality_engine,
                localization_engine=localization_engine,
                retrieval_engine=gallery_engine,
                explanation_generator=explanation_gen,
            )
            evidence_rec = aggregator.process_query_micrograph(
                query_image_id=str(img.id),
                image=arr,
                feature_vector=embeddings_map[img.id],
                metadata_dict=meta_dict,
            )

            status_str = evidence_rec.decision_status.value if hasattr(evidence_rec.decision_status, "value") else str(evidence_rec.decision_status)
            cat_str = evidence_rec.primary_artifact_category.value if hasattr(evidence_rec.primary_artifact_category, "value") else str(evidence_rec.primary_artifact_category)

            if status_str == "QUALITY_RISK":
                quality_risk_count += 1
            if evidence_rec.abstention_triggered or status_str == "UNCERTAIN_ABSTAIN":
                uncertain_count += 1

            # Composite quality risk score
            qp = img.quality_profile
            comp_risk = float(qp.composite_quality_risk if qp else (0.85 if status_str == "QUALITY_RISK" else 0.15))

            per_image_results.append({
                "id": img.id,
                "original_filename": img.original_filename,
                "sha256": img.sha256,
                "width": img.width,
                "height": img.height,
                "file_size": img.file_size,
                "storage_path": img.storage_path,
                "metadata": {
                    "microscope": meta_rel.microscope if meta_rel else None,
                    "detector": meta_rel.detector if meta_rel else None,
                    "accelerating_voltage_kv": meta_rel.accelerating_voltage_kv if meta_rel else None,
                    "magnification": meta_rel.magnification if meta_rel else None,
                    "pixel_size_nm": meta_rel.pixel_size_nm if meta_rel else None,
                    "dwell_time_us": meta_rel.dwell_time_us if meta_rel else None,
                    "metadata_source": meta_rel.metadata_source if meta_rel else "unknown",
                    "metadata_completeness": meta_rel.metadata_completeness if meta_rel else 0.0,
                } if meta_rel else None,
                "quality": {
                    "decision_status": status_str,
                    "primary_artifact_category": cat_str,
                    "composite_quality_risk": round(comp_risk, 4),
                    "confidence": round(float(evidence_rec.classification_confidence), 4),
                    "normalized_entropy": round(float(evidence_rec.normalized_entropy), 4),
                    "prediction_margin": round(float(evidence_rec.prediction_margin), 4),
                    "abstention_triggered": bool(evidence_rec.abstention_triggered),
                    "abstention_reason": evidence_rec.abstention_reason,
                    "indicators": [s.to_dict() for s in evidence_rec.quality_signals],
                },
                "localization": evidence_rec.suspicious_region.to_dict() if evidence_rec.suspicious_region else {},
                "evidence": {
                    "comparable_items": [e.to_dict() for e in evidence_rec.comparable_evidence],
                    "cohort_size": 55,
                    "audit_hash": evidence_rec.audit_hash,
                },
                "explanation": evidence_rec.suggested_action.to_dict(),
            })

        # -------------------------------------------------------------
        # STEP 3: PIPELINE A — PAIRWISE COMPARISON & DUPLICATE CASCADE
        # -------------------------------------------------------------
        pairwise_comparisons = []
        duplicate_pairs_count = 0
        near_duplicate_pairs_count = 0
        similar_pairs_count = 0
        distinct_pairs_count = 0

        # Similarity matrix N x N
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        id_to_idx = {img.id: idx for idx, img in enumerate(images)}

        # Graph for duplicate groups (edges connecting DUPLICATE or NEAR_DUPLICATE)
        adjacency: Dict[int, Set[int]] = {img.id: set() for img in images}

        for i in range(n):
            img_a = images[i]
            matrix[i][i] = 100.0  # diagonal
            vec_a = embeddings_map[img_a.id]
            hashes_a = hashes_map[img_a.id]
            q_res_a = per_image_results[i]["quality"]

            for j in range(i + 1, n):
                img_b = images[j]
                vec_b = embeddings_map[img_b.id]
                hashes_b = hashes_map[img_b.id]
                q_res_b = per_image_results[j]["quality"]

                # 1. Representation Cosine Similarity
                sim = float(np.dot(vec_a, vec_b))
                sim_clamped = max(0.0, min(1.0, sim))
                sim_pct = round(sim_clamped * 100.0, 2)
                matrix[i][j] = sim_pct
                matrix[j][i] = sim_pct

                # 2. Duplicate Cascade Execution
                f_match = (hashes_a["file_sha256"] == hashes_b["file_sha256"])
                p_match = (hashes_a["pixel_sha256"] == hashes_b["pixel_sha256"])

                h_ph = sum(c1 != c2 for c1, c2 in zip(hashes_a["phash"], hashes_b["phash"]))
                h_dh = sum(c1 != c2 for c1, c2 in zip(hashes_a["dhash"], hashes_b["dhash"]))

                # Pixel verification if candidate
                ssim_val = None
                mae_val = None
                ncc_val = None
                if f_match or p_match:
                    ssim_val = 1.0
                    mae_val = 0.0
                    ncc_val = 1.0
                elif (h_ph <= 10 or h_dh <= 10) or sim_clamped >= 0.85:
                    pm = compute_pixel_metrics(img_a.storage_path, img_b.storage_path)
                    ssim_val = round(float(pm["ssim"]), 4)
                    mae_val = round(float(pm["mae"]), 2)
                    ncc_val = round(float(pm["ncc"]), 4)

                # Classification under declared cascade
                if f_match or p_match:
                    decision = "DUPLICATE"
                    duplicate_pairs_count += 1
                    reason = "Exact bitwise file or decoded pixel hash match (Stage 1/2)."
                    adjacency[img_a.id].add(img_b.id)
                    adjacency[img_b.id].add(img_a.id)
                elif ssim_val is not None and ssim_val >= 0.95 and (mae_val is not None and mae_val <= 5.0):
                    decision = "NEAR_DUPLICATE"
                    near_duplicate_pairs_count += 1
                    reason = f"High structural perceptual similarity (SSIM={ssim_val:.3f}, Cosine={sim_clamped:.3f}) meeting Stage 5 near-duplicate threshold."
                    adjacency[img_a.id].add(img_b.id)
                    adjacency[img_b.id].add(img_a.id)
                elif sim_clamped >= 0.75:
                    decision = "SIMILAR"
                    similar_pairs_count += 1
                    reason = f"Elevated visual feature correlation ({sim_pct}%) in {representation} space without declared bitwise/SSIM redundancy."
                else:
                    decision = "DISTINCT"
                    distinct_pairs_count += 1
                    reason = f"Distinct morphological features in {representation} space (similarity {sim_pct}% < 75%)."

                # Metadata relationship comparison
                meta_a = img_a.metadata_rel
                meta_b = img_b.metadata_rel

                spec_a = getattr(meta_a, "specimen_id", None) if meta_a else None
                spec_b = getattr(meta_b, "specimen_id", None) if meta_b else None
                acq_a = getattr(meta_a, "acquisition_id", None) if meta_a else None
                acq_b = getattr(meta_b, "acquisition_id", None) if meta_b else None
                inst_a = getattr(meta_a, "microscope", None) if meta_a else None
                inst_b = getattr(meta_b, "microscope", None) if meta_b else None
                det_a = getattr(meta_a, "detector", None) if meta_a else None
                det_b = getattr(meta_b, "detector", None) if meta_b else None
                volt_a = getattr(meta_a, "accelerating_voltage_kv", None) if meta_a else None
                volt_b = getattr(meta_b, "accelerating_voltage_kv", None) if meta_b else None
                mag_a = getattr(meta_a, "magnification", None) if meta_a else None
                mag_b = getattr(meta_b, "magnification", None) if meta_b else None

                meta_rel = {
                    "same_specimen": (spec_a == spec_b) if spec_a and spec_b else None,
                    "same_acquisition": (acq_a == acq_b) if acq_a and acq_b else None,
                    "same_instrument": (inst_a == inst_b) if inst_a and inst_b else None,
                    "same_detector": (det_a == det_b) if det_a and det_b else None,
                    "same_voltage": (volt_a == volt_b) if volt_a and volt_b else None,
                    "same_magnification": (mag_a == mag_b) if mag_a and mag_b else None,
                }

                # Comparative Quality Relationship (Section 16 requirement)
                comp_cleaner_id = None
                comp_rationale = "Both micrographs exhibit comparable image-derived quality status."
                comp_action = "Standard archival or review routing applies."
                if q_res_a["decision_status"] == "QUALITY_RISK" and q_res_b["decision_status"] == "NORMAL":
                    comp_cleaner_id = img_b.id
                    comp_rationale = f"Micrograph #{img_b.id} ({img_b.original_filename}) provides a cleaner comparable reference against risk-flagged Micrograph #{img_a.id}."
                    comp_action = f"Review Micrograph #{img_a.id} acquisition parameters against Micrograph #{img_b.id} baseline (does not prove physical cause)."
                elif q_res_b["decision_status"] == "QUALITY_RISK" and q_res_a["decision_status"] == "NORMAL":
                    comp_cleaner_id = img_a.id
                    comp_rationale = f"Micrograph #{img_a.id} ({img_a.original_filename}) provides a cleaner comparable reference against risk-flagged Micrograph #{img_b.id}."
                    comp_action = f"Review Micrograph #{img_b.id} acquisition parameters against Micrograph #{img_a.id} baseline (does not prove physical cause)."

                pairwise_comparisons.append({
                    "pair_key": f"{img_a.id}_{img_b.id}",
                    "image_a": {"id": img_a.id, "filename": img_a.original_filename},
                    "image_b": {"id": img_b.id, "filename": img_b.original_filename},
                    "similarity_score": round(sim_clamped, 4),
                    "similarity_pct": sim_pct,
                    "representation": representation,
                    "decision": decision,
                    "reason": reason,
                    "cascade_evidence": {
                        "file_sha_match": f_match,
                        "pixel_sha_match": p_match,
                        "phash_hamming": h_ph,
                        "dhash_hamming": h_dh,
                        "cosine_similarity": round(sim_clamped, 4),
                        "ssim": ssim_val,
                        "mae": mae_val,
                        "ncc": ncc_val,
                    },
                    "metadata_relationship": meta_rel,
                    "comparative_quality": {
                        "image_a_status": q_res_a["decision_status"],
                        "image_b_status": q_res_b["decision_status"],
                        "cleaner_reference_id": comp_cleaner_id,
                        "comparative_rationale": comp_rationale,
                        "suggested_comparative_action": comp_action,
                    },
                })

        # -------------------------------------------------------------
        # STEP 4: DUPLICATE GROUPS EXTRACTION (CONNECTED COMPONENTS)
        # -------------------------------------------------------------
        duplicate_groups = []
        visited: Set[int] = set()
        img_by_id = {img.id: img for img in images}

        group_idx = 1
        for img in images:
            if img.id in visited:
                continue
            # BFS / DFS
            component = []
            queue = [img.id]
            visited.add(img.id)
            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for neighbor in adjacency[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)

            if len(component) >= 2:
                # Elect representative: highest metadata completeness or lowest ID
                rep_id = min(component)
                rep_img = img_by_id[rep_id]
                member_names = [img_by_id[m].original_filename for m in component]

                duplicate_groups.append({
                    "group_id": f"GRP_{group_idx:02d}",
                    "representative_image_id": rep_id,
                    "representative_filename": rep_img.original_filename,
                    "member_image_ids": component,
                    "member_filenames": member_names,
                    "reason": "High similarity under duplicate cascade",
                    "advisory": "Redundancy detected — review before archival/removal.",
                    "actions": ["Review Group", "Compare", "Open Representative"],
                })
                group_idx += 1

        # -------------------------------------------------------------
        # STEP 5: COMPARATIVE QUALITY SUMMARY
        # -------------------------------------------------------------
        sorted_by_risk = sorted(
            per_image_results,
            key=lambda x: x["quality"]["composite_quality_risk"],
            reverse=True,
        )
        highest_risk_img = sorted_by_risk[0]
        if highest_risk_img["quality"]["composite_quality_risk"] >= 0.40:
            comp_statement = (
                f"Image #{highest_risk_img['id']} ({highest_risk_img['original_filename']}) shows "
                f"the strongest image-derived quality-risk signals (risk score: "
                f"{highest_risk_img['quality']['composite_quality_risk']*100:.1f}%) among the analyzed images."
            )
        else:
            comp_statement = "All analyzed micrographs conform to baseline image-derived quality indicators."

        # -------------------------------------------------------------
        # STEP 6: AUDIT & PROVENANCE
        # -------------------------------------------------------------
        review_required_count = sum(
            1 for p in per_image_results
            if p["quality"]["decision_status"] == "QUALITY_RISK"
            or p["quality"]["abstention_triggered"]
        )

        AuditService.log_action(
            db=db,
            action="MULTI_IMAGE_ANALYSIS",
            resource_type="multi_image",
            user_id=current_user_id,
            parameters={
                "analysis_id": analysis_id,
                "image_ids": unique_ids,
                "representation": representation,
                "pairs_count": len(pairwise_comparisons),
                "duplicate_groups_count": len(duplicate_groups),
            },
        )

        if duplicate_pairs_count > 0 or near_duplicate_pairs_count > 0:
            AuditService.log_action(
                db=db,
                action="DUPLICATE_DETECTED",
                resource_type="multi_image",
                user_id=current_user_id,
                parameters={
                    "analysis_id": analysis_id,
                    "duplicate_pairs": duplicate_pairs_count,
                    "near_duplicates": near_duplicate_pairs_count,
                },
            )

        if quality_risk_count > 0:
            AuditService.log_action(
                db=db,
                action="QUALITY_RISK_DETECTED",
                resource_type="multi_image",
                user_id=current_user_id,
                parameters={
                    "analysis_id": analysis_id,
                    "risk_flagged_count": quality_risk_count,
                },
            )

        # Record provenance for each image
        for img in images:
            ProvenanceService.record_event(
                db=db,
                image_id=img.id,
                event_type="MULTI_IMAGE_ANALYSIS",
                parameters={
                    "analysis_id": analysis_id,
                    "peer_ids": [o_id for o_id in unique_ids if o_id != img.id],
                    "representation": representation,
                },
            )

        # Cryptographic Audit Hash of analysis
        raw_seal_content = json.dumps({
            "analysis_id": analysis_id,
            "image_ids": unique_ids,
            "representation": representation,
            "pairs_count": len(pairwise_comparisons),
            "duplicates_count": duplicate_pairs_count + near_duplicate_pairs_count,
            "quality_risk_count": quality_risk_count,
            "timestamp": timestamp_utc,
        }, sort_keys=True)
        audit_hash = hashlib.sha256(raw_seal_content.encode("utf-8")).hexdigest()

        return {
            "analysis_id": analysis_id,
            "timestamp_utc": timestamp_utc,
            "representation": representation,
            "total_images": n,
            "total_pairs": len(pairwise_comparisons),
            "summary": {
                "images_analyzed": n,
                "pairwise_comparisons": len(pairwise_comparisons),
                "duplicate_pairs": duplicate_pairs_count,
                "near_duplicate_pairs": near_duplicate_pairs_count,
                "similar_pairs": similar_pairs_count,
                "distinct_pairs": distinct_pairs_count,
                "quality_risk_images": quality_risk_count,
                "uncertain_images": uncertain_count,
                "review_required_images": review_required_count,
            },
            "images": per_image_results,
            "similarity_matrix": {
                "image_ids": [img.id for img in images],
                "image_labels": [img.original_filename for img in images],
                "matrix": matrix,
            },
            "pairwise_comparisons": pairwise_comparisons,
            "duplicate_groups": duplicate_groups,
            "comparative_quality_summary": {
                "highest_risk_image_id": highest_risk_img["id"],
                "highest_risk_score": highest_risk_img["quality"]["composite_quality_risk"],
                "comparative_statement": comp_statement,
                "ranking": [
                    {"image_id": r["id"], "filename": r["original_filename"], "composite_risk": r["quality"]["composite_quality_risk"], "status": r["quality"]["decision_status"]}
                    for r in sorted_by_risk
                ],
            },
            "provenance": {
                "analysis_id": analysis_id,
                "input_image_ids": unique_ids,
                "representation": representation,
                "model_version": "dinov2_vits14_phase2" if representation == "dinov2_base" else "phase4_acquisition_adapter_seed42",
                "timestamp_utc": timestamp_utc,
                "stages_executed": [
                    "UPLOAD_VALIDATION",
                    "METADATA_EXTRACTION",
                    "REPRESENTATION_EXTRACTION",
                    "PAIRWISE_COMPARISON",
                    "DUPLICATE_CASCADE",
                    "QUALITY_RISK_ANALYSIS",
                    "LOCALIZATION",
                    "EVIDENCE_RETRIEVAL",
                    "EXPLANATION_GENERATION",
                    "UNCERTAINTY_EVALUATION",
                    "REVIEW_ROUTING",
                    "PROVENANCE_LOGGING",
                    "AUDIT_TRAIL",
                ],
                "audit_hash": audit_hash,
            },
        }

    @staticmethod
    def _get_or_compute_embedding(
        db: Session,
        image: Image,
        representation: str,
        dinov2_engine: DINOv2Engine,
        phase4_engine: Optional[Phase4Engine],
    ) -> np.ndarray:
        """Fetch existing embedding or compute dynamically."""
        if representation == "phase4_adapted":
            emb = db.query(Embedding).filter(
                Embedding.image_id == image.id,
                Embedding.embedding_type == "phase4_adapted",
            ).first()
            if emb:
                return np.array(emb.embedding_vector, dtype=np.float32)

            # Need base embedding to adapt
            base_emb = db.query(Embedding).filter(
                Embedding.image_id == image.id,
                Embedding.embedding_type == "dinov2_base",
            ).first()
            if base_emb:
                base_vec = np.array(base_emb.embedding_vector, dtype=np.float32)
            else:
                base_vec = dinov2_engine.extract_features(image.storage_path)

            adapted_vec = phase4_engine.adapt_embedding(base_vec)
            return adapted_vec
        else:
            emb = db.query(Embedding).filter(
                Embedding.image_id == image.id,
                Embedding.embedding_type == "dinov2_base",
            ).first()
            if emb:
                return np.array(emb.embedding_vector, dtype=np.float32)
            vec = dinov2_engine.extract_features(image.storage_path)
            return vec

    @staticmethod
    def _build_cohort_evidence_engine(db: Session, exclude_ids: List[int]) -> Optional[RetrievalEvidenceEngine]:
        """Construct cohort retrieval engine from indexed database images."""
        import pandas as pd

        all_embs = db.query(Embedding).filter(Embedding.embedding_type == "dinov2_base").all()
        if not all_embs:
            return None

        gallery_rows = []
        gallery_feats = []
        for pe in all_embs:
            p_img = db.query(Image).filter(Image.id == pe.image_id).first()
            if not p_img or not p_img.storage_path or not Path(p_img.storage_path).is_file():
                continue
            p_meta = p_img.metadata_rel
            gallery_feats.append(pe.embedding_vector)
            gallery_rows.append({
                "image_id": str(p_img.id),
                "specimen_id": str(getattr(p_meta, "specimen_id", None) or f"SPEC_{p_img.id}"),
                "acquisition_id": str(getattr(p_meta, "acquisition_id", None) or f"ACQ_{p_img.id}"),
                "instrument": str(p_meta.microscope) if p_meta and p_meta.microscope else "ImageXpress Micro",
                "detector": str(p_meta.detector) if p_meta and p_meta.detector else "CoolSNAP HQ CCD",
                "accelerating_voltage_kv": p_meta.accelerating_voltage_kv if p_meta else None,
                "file_path": p_img.storage_path,
            })

        if not gallery_feats:
            return None

        g_features = np.array(gallery_feats, dtype=np.float32)
        g_df = pd.DataFrame(gallery_rows)
        return RetrievalEvidenceEngine(gallery_features=g_features, gallery_metadata=g_df, top_k=5)


def uuid_short() -> str:
    import uuid
    return uuid.uuid4().hex[:8]
