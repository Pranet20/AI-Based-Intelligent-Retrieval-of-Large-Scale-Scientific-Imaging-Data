"""Idempotent 14-Step Scientific Image Ingestion Pipeline."""

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from PIL import Image as PILImage
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import (
    DuplicateProfile,
    Embedding,
    Image,
    ImageMetadata,
    ModelVersion,
    QualityProfile,
)
from app.ml.dinov2_engine import DINOv2Engine
from app.ml.duplicate_engine import DuplicateEngine
from app.ml.faiss_engine import FAISSEngine
from app.ml.novelty_engine import NoveltyEngine
from app.ml.phase4_engine import Phase4Engine
from app.services.audit import AuditService
from app.services.provenance import ProvenanceService
from src.ingestion.reader import ScientificImageReader


class IngestionError(ValueError):
    """Raised when ingestion validation fails."""
    pass


class IngestionService:
    """Orchestrates end-to-end scientific image ingestion."""

    @classmethod
    def ingest_file(
        cls,
        db: Session,
        file_bytes: bytes,
        original_filename: str,
        project_id: Optional[int] = None,
        manual_metadata: Optional[Dict[str, Any]] = None,
    ) -> Image:
        # Step 1: Security validations (Path traversal, unsafe characters, extension & size)
        if ".." in original_filename or "/" in original_filename or "\\" in original_filename or ":" in original_filename:
            raise IngestionError(f"Path traversal or unsafe filename detected: {original_filename}")
        clean_filename = Path(original_filename).name
        ext = Path(clean_filename).suffix.lower()
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise IngestionError(f"Unsupported file extension '{ext}'. Allowed: {settings.ALLOWED_EXTENSIONS}")
        if len(file_bytes) > settings.MAX_UPLOAD_SIZE_BYTES:
            raise IngestionError(f"File size {len(file_bytes)} exceeds limit of {settings.MAX_UPLOAD_SIZE_BYTES} bytes.")

        # Step 2: SHA-256 computation
        sha256_hash = hashlib.sha256(file_bytes).hexdigest()

        # Step 3: Idempotency check
        existing_image = db.query(Image).filter(Image.sha256 == sha256_hash).first()
        if existing_image:
            return existing_image

        # Step 4: Immutable original storage
        settings.ORIGINALS_PATH.mkdir(parents=True, exist_ok=True)
        storage_rel_path = f"platform/storage/originals/{sha256_hash}{ext}"
        storage_path = Path(storage_rel_path)
        if not storage_path.exists():
            with open(storage_path, "wb") as f:
                f.write(file_bytes)

        # Step 5: Read dimensions and metadata
        arr, raw_meta = ScientificImageReader.load_array(storage_path)
        height, width = int(arr.shape[0]), int(arr.shape[1])
        mime_type = "image/tiff" if ext in [".tif", ".tiff"] else ("image/png" if ext == ".png" else "image/jpeg")

        # Step 6: Create Image record
        image_record = Image(
            project_id=project_id,
            original_filename=clean_filename,
            storage_path=str(storage_path),
            sha256=sha256_hash,
            mime_type=mime_type,
            width=width,
            height=height,
            file_size=len(file_bytes),
            processing_status="PROCESSING",
        )
        db.add(image_record)
        db.commit()
        db.refresh(image_record)

        # Log UPLOAD provenance
        ProvenanceService.record_event(
            db, image_record.id, "UPLOAD",
            {"original_filename": clean_filename, "file_size": len(file_bytes), "sha256": sha256_hash}
        )

        # Log UPLOAD audit
        AuditService.log_action(
            db=db,
            action="UPLOAD",
            resource_type="images",
            resource_id=image_record.id,
            parameters={"original_filename": clean_filename, "file_size": len(file_bytes), "sha256": sha256_hash},
        )

        # Step 7: Scientific Metadata extraction
        raw_meta = raw_meta or {}

        # Intelligent extraction from tags or known dataset filename protocols (e.g. BBBC021 / HCCI / SEM)
        is_bbbc = "week" in clean_filename.lower() or "bbbc" in clean_filename.lower() or ext in [".tif", ".tiff"]
        default_microscope = "Molecular Devices ImageXpress Micro" if is_bbbc else None
        default_detector = "Photometrics CoolSNAP HQ CCD" if is_bbbc else None
        default_mag = 20.0 if is_bbbc else None
        default_pixel_size = 650.0 if is_bbbc else None
        default_dwell = 120000.0 if is_bbbc else None

        extracted_microscope = raw_meta.get("microscope") or raw_meta.get("Microscope") or (manual_metadata.get("microscope") if manual_metadata else default_microscope)
        extracted_detector = raw_meta.get("detector") or raw_meta.get("Detector") or (manual_metadata.get("detector") if manual_metadata else default_detector)
        extracted_voltage = raw_meta.get("accelerating_voltage_kv") or raw_meta.get("Voltage") or (manual_metadata.get("accelerating_voltage_kv") if manual_metadata else None)
        extracted_mag = raw_meta.get("magnification") or raw_meta.get("Magnification") or (manual_metadata.get("magnification") if manual_metadata else default_mag)
        extracted_pixel_size = raw_meta.get("pixel_size_nm") or raw_meta.get("PixelSize") or (manual_metadata.get("pixel_size_nm") if manual_metadata else default_pixel_size)
        extracted_current = raw_meta.get("beam_current_na") or (manual_metadata.get("beam_current_na") if manual_metadata else None)
        extracted_dwell = raw_meta.get("dwell_time_us") or (manual_metadata.get("dwell_time_us") if manual_metadata else default_dwell)
        extracted_wd = raw_meta.get("working_distance_mm") or (manual_metadata.get("working_distance_mm") if manual_metadata else None)
        extracted_press = raw_meta.get("chamber_pressure_pa") or (manual_metadata.get("chamber_pressure_pa") if manual_metadata else None)

        meta_source = "embedded" if raw_meta else ("manual" if manual_metadata else ("inferred_protocol" if is_bbbc else "unknown"))
        # Calculate completeness
        fields = [extracted_microscope, extracted_detector, extracted_voltage, extracted_mag, extracted_pixel_size, extracted_current, extracted_dwell, extracted_wd, extracted_press]
        completeness = float(sum(f is not None for f in fields) / len(fields))

        meta_record = ImageMetadata(
            image_id=image_record.id,
            microscope=str(extracted_microscope) if extracted_microscope else None,
            detector=str(extracted_detector) if extracted_detector else None,
            accelerating_voltage_kv=float(extracted_voltage) if extracted_voltage is not None else None,
            magnification=float(extracted_mag) if extracted_mag is not None else None,
            pixel_size_nm=float(extracted_pixel_size) if extracted_pixel_size is not None else None,
            beam_current_na=float(extracted_current) if extracted_current is not None else None,
            dwell_time_us=float(extracted_dwell) if extracted_dwell is not None else None,
            working_distance_mm=float(extracted_wd) if extracted_wd is not None else None,
            chamber_pressure_pa=float(extracted_press) if extracted_press is not None else None,
            metadata_source=meta_source,
            metadata_completeness=completeness,
            raw_metadata_json=raw_meta,
        )
        db.add(meta_record)
        db.commit()

        ProvenanceService.record_event(
            db, image_record.id, "METADATA_EXTRACTION",
            {"source": meta_source, "completeness": completeness}
        )

        # Step 8: High-Contrast Display & Thumbnail generation
        settings.THUMBNAILS_PATH.mkdir(parents=True, exist_ok=True)
        thumb_path = settings.THUMBNAILS_PATH / f"{sha256_hash}_thumb.png"
        disp_path = settings.THUMBNAILS_PATH / f"{sha256_hash}_display.png"
        try:
            # Contrast-stretch scientific array (16-bit, float, or 8-bit) to web-renderable PNG
            if arr.ndim == 2:
                p_low, p_high = np.percentile(arr, (0.5, 99.8))
                if p_high > p_low:
                    norm = np.clip((arr - p_low) / (p_high - p_low) * 255.0, 0, 255).astype(np.uint8)
                else:
                    norm = np.clip(arr, 0, 255).astype(np.uint8)
                disp_im = PILImage.fromarray(norm, mode="L")
            elif arr.ndim == 3 and arr.shape[2] in (3, 4):
                p_low, p_high = np.percentile(arr, (0.5, 99.8))
                if p_high > p_low:
                    norm = np.clip((arr - p_low) / (p_high - p_low) * 255.0, 0, 255).astype(np.uint8)
                else:
                    norm = np.clip(arr, 0, 255).astype(np.uint8)
                disp_im = PILImage.fromarray(norm)
            else:
                norm = np.clip(arr, 0, 255).astype(np.uint8)
                disp_im = PILImage.fromarray(norm)

            disp_im.save(disp_path, "PNG")
            thumb_im = disp_im.copy()
            thumb_im.thumbnail((256, 256))
            thumb_im.save(thumb_path, "PNG")

            image_record.thumbnail_path = str(thumb_path)
            db.commit()
        except Exception as e:
            logger.error(f"Thumbnail/display generation error: {e}")

        # Step 9: Quality-risk analysis
        from app.ml.quality_engine import QualityEngine
        q_results = QualityEngine.evaluate_quality(storage_path)
        q_profile = QualityProfile(
            image_id=image_record.id,
            laplacian_variance=q_results["laplacian_variance"],
            edge_density=q_results["edge_density"],
            shannon_entropy=q_results["shannon_entropy"],
            dynamic_range=q_results["dynamic_range"],
            clipping_ratio=q_results["clipping_ratio"],
            high_freq_fft_ratio=q_results["high_freq_fft_ratio"],
            composite_quality_risk=q_results["composite_quality_risk"],
            quality_label=q_results["quality_label"],
        )
        db.add(q_profile)
        db.commit()

        ProvenanceService.record_event(
            db, image_record.id, "QUALITY_ANALYSIS",
            {"composite_quality_risk": q_results["composite_quality_risk"], "label": q_results["quality_label"]}
        )

        # Step 10: Extract Embeddings (DINOv2 & Phase 4)
        dino_engine = DINOv2Engine()
        dino_vec = dino_engine.embed_image(storage_path)

        phase4_engine = Phase4Engine()
        adapt_vec = phase4_engine.adapt_embedding(dino_vec)

        # Retrieve model version IDs
        m_dino = db.query(ModelVersion).filter(ModelVersion.model_id == "dinov2_vits14_phase2").first()
        m_phase4 = db.query(ModelVersion).filter(ModelVersion.model_id == "phase4_acquisition_adapter_seed42").first()

        emb_dino = Embedding(
            image_id=image_record.id,
            model_id=m_dino.id if m_dino else 1,
            embedding_type="dinov2_base",
            embedding_vector=dino_vec.tolist(),
            l2_normalized=True,
        )
        emb_phase4 = Embedding(
            image_id=image_record.id,
            model_id=m_phase4.id if m_phase4 else 2,
            embedding_type="phase4_adapted",
            embedding_vector=adapt_vec.tolist(),
            l2_normalized=True,
        )
        db.add(emb_dino)
        db.add(emb_phase4)
        db.commit()

        ProvenanceService.record_event(
            db, image_record.id, "EMBEDDING_GENERATION",
            {"dino_dim": len(dino_vec), "adapted_dim": len(adapt_vec)},
            model_version="dinov2_vits14"
        )

        # Step 11: Exact & Near Duplicate Detection
        dup_hashes = DuplicateEngine.compute_hashes(storage_path)
        # Query existing profiles to compare
        other_images = db.query(Image).filter(Image.id != image_record.id).all()
        candidates = []
        for other in other_images:
            other_dp = db.query(DuplicateProfile).filter(DuplicateProfile.image_id == other.id).first()
            other_emb = db.query(Embedding).filter(Embedding.image_id == other.id, Embedding.embedding_type == "dinov2_base").first()
            other_ad = db.query(Embedding).filter(Embedding.image_id == other.id, Embedding.embedding_type == "phase4_adapted").first()
            candidates.append({
                "id": other.id,
                "storage_path": other.storage_path,
                "sha256": other.sha256,
                "phash": other_dp.phash if other_dp else None,
                "dhash": other_dp.dhash if other_dp else None,
                "dinov2_vector": np.array(other_emb.embedding_vector) if other_emb else None,
                "adapted_vector": np.array(other_ad.embedding_vector) if other_ad else None,
            })

        dup_res = DuplicateEngine.check_duplicate_against_candidates(
            storage_path,
            sha256_hash,
            dup_hashes["phash"],
            dup_hashes["dhash"],
            dino_vec,
            adapt_vec,
            candidates,
        )
        dup_profile = DuplicateProfile(
            image_id=image_record.id,
            phash=dup_hashes["phash"],
            dhash=dup_hashes["dhash"],
            duplicate_status=dup_res["duplicate_status"],
            matched_image_id=dup_res["matched_image_id"],
            similarity_score=dup_res["similarity_score"],
            match_stage=dup_res["match_stage"],
        )
        db.add(dup_profile)
        db.commit()

        ProvenanceService.record_event(
            db, image_record.id, "DUPLICATE_ANALYSIS",
            {"status": dup_res["duplicate_status"], "stage": dup_res["match_stage"]}
        )

        # Step 12: FAISS Indexing
        faiss_engine = FAISSEngine()
        faiss_engine.add_vector(image_record.id, dino_vec)

        ProvenanceService.record_event(
            db, image_record.id, "INDEXING",
            {"index_type": "IndexFlatIP", "total_indexed": faiss_engine.index.ntotal}
        )

        # Step 13: Novelty Scoring
        novelty_engine = NoveltyEngine()
        nov_res = novelty_engine.evaluate_novelty(dino_vec)

        # Step 14: Ready status
        image_record.processing_status = "READY"
        db.commit()
        db.refresh(image_record)

        AuditService.log_action(
            db=db,
            action="IMAGE_PROCESSING",
            resource_type="images",
            resource_id=image_record.id,
            parameters={"status": "READY", "sha256": sha256_hash},
        )

        return image_record
