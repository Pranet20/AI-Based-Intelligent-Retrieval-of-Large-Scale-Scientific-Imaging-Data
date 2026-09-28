"""Image management, upload, metadata, and analytics endpoints."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import RoleChecker, get_current_user_payload
from app.db.models import (
    DuplicateProfile,
    Embedding,
    Image,
    ImageMetadata,
    QualityProfile,
)
from app.db.session import get_db
from app.ml.faiss_engine import FAISSEngine
from app.ml.novelty_engine import NoveltyEngine
from app.services.audit import AuditService
from app.services.ingestion import IngestionService
from app.services.provenance import ProvenanceService

router = APIRouter(prefix="/images", tags=["Images"])


@router.get("")
def list_images(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    query = db.query(Image)
    if project_id:
        query = query.filter(Image.project_id == project_id)
    if status:
        query = query.filter(Image.processing_status == status)
    total = query.count()
    images = query.order_by(Image.id.desc()).offset(offset).limit(limit).all()

    items = []
    for img in images:
        meta = img.metadata_rel
        qp = img.quality_profile
        dp = img.duplicate_profile
        items.append({
            "id": img.id,
            "project_id": img.project_id,
            "original_filename": img.original_filename,
            "sha256": img.sha256,
            "width": img.width,
            "height": img.height,
            "file_size": img.file_size,
            "processing_status": img.processing_status,
            "created_at": img.created_at,
            "quality_label": qp.quality_label if qp else "UNKNOWN",
            "composite_quality_risk": qp.composite_quality_risk if qp else 0.0,
            "duplicate_status": dp.duplicate_status if dp else "UNKNOWN",
            "microscope": meta.microscope if meta else None,
        })
    return {"total": total, "items": items}


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    project_id: Optional[int] = Form(None),
    microscope: Optional[str] = Form(None),
    detector: Optional[str] = Form(None),
    accelerating_voltage_kv: Optional[float] = Form(None),
    magnification: Optional[float] = Form(None),
    pixel_size_nm: Optional[float] = Form(None),
    payload: Dict[str, Any] = Depends(get_current_user_payload),
    db: Session = Depends(get_db),
):
    allowed_mimes = {"image/png", "image/jpeg", "image/tiff", "application/octet-stream"}
    if file.content_type and file.content_type not in allowed_mimes:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported MIME type '{file.content_type}'. Allowed: {sorted(list(allowed_mimes))}"
        )

    file_bytes = await file.read()
    manual_meta = {}
    if microscope: manual_meta["microscope"] = microscope
    if detector: manual_meta["detector"] = detector
    if accelerating_voltage_kv: manual_meta["accelerating_voltage_kv"] = accelerating_voltage_kv
    if magnification: manual_meta["magnification"] = magnification
    if pixel_size_nm: manual_meta["pixel_size_nm"] = pixel_size_nm

    try:
        image_record = IngestionService.ingest_file(
            db=db,
            file_bytes=file_bytes,
            original_filename=file.filename,
            project_id=project_id,
            manual_metadata=manual_meta if manual_meta else None,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "id": image_record.id,
        "original_filename": image_record.original_filename,
        "sha256": image_record.sha256,
        "processing_status": image_record.processing_status,
        "message": "Image ingested and analyzed successfully."
    }


@router.get("/{id}")
def get_image_detail(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    meta = img.metadata_rel
    qp = img.quality_profile
    dp = img.duplicate_profile

    return {
        "id": img.id,
        "project_id": img.project_id,
        "original_filename": img.original_filename,
        "storage_path": img.storage_path,
        "thumbnail_path": img.thumbnail_path,
        "sha256": img.sha256,
        "mime_type": img.mime_type,
        "width": img.width,
        "height": img.height,
        "file_size": img.file_size,
        "processing_status": img.processing_status,
        "created_at": img.created_at,
        "metadata": {
            "microscope": meta.microscope if meta else None,
            "detector": meta.detector if meta else None,
            "accelerating_voltage_kv": meta.accelerating_voltage_kv if meta else None,
            "magnification": meta.magnification if meta else None,
            "pixel_size_nm": meta.pixel_size_nm if meta else None,
            "beam_current_na": meta.beam_current_na if meta else None,
            "dwell_time_us": meta.dwell_time_us if meta else None,
            "working_distance_mm": meta.working_distance_mm if meta else None,
            "chamber_pressure_pa": meta.chamber_pressure_pa if meta else None,
            "metadata_source": meta.metadata_source if meta else "unknown",
            "metadata_completeness": meta.metadata_completeness if meta else 0.0,
        } if meta else None,
        "quality": {
            "laplacian_variance": qp.laplacian_variance if qp else None,
            "edge_density": qp.edge_density if qp else None,
            "shannon_entropy": qp.shannon_entropy if qp else None,
            "dynamic_range": qp.dynamic_range if qp else None,
            "clipping_ratio": qp.clipping_ratio if qp else None,
            "high_freq_fft_ratio": qp.high_freq_fft_ratio if qp else None,
            "composite_quality_risk": qp.composite_quality_risk if qp else 0.0,
            "quality_label": qp.quality_label if qp else "NOMINAL",
        } if qp else None,
        "duplicate": {
            "duplicate_status": dp.duplicate_status if dp else "NO_DECLARED_REDUNDANCY_DETECTED",
            "matched_image_id": dp.matched_image_id if dp else None,
            "similarity_score": dp.similarity_score if dp else None,
            "match_stage": dp.match_stage if dp else None,
        } if dp else None,
    }


@router.get("/{id}/file")
def get_image_file(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.storage_path:
        raise HTTPException(status_code=404, detail="Image file not found")
    file_path = Path(img.storage_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image file missing from storage")
    return FileResponse(file_path, media_type=img.mime_type)


@router.get("/{id}/thumbnail")
def get_image_thumbnail(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.thumbnail_path:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    thumb_path = Path(img.thumbnail_path)
    if not thumb_path.is_file():
        raise HTTPException(status_code=404, detail="Thumbnail missing from storage")
    return FileResponse(thumb_path, media_type="image/png")


@router.get("/{id}/metadata")
def get_metadata(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.metadata_rel:
        raise HTTPException(status_code=404, detail="Metadata not found")
    m = img.metadata_rel
    return {
        "image_id": img.id,
        "microscope": m.microscope,
        "detector": m.detector,
        "accelerating_voltage_kv": m.accelerating_voltage_kv,
        "magnification": m.magnification,
        "pixel_size_nm": m.pixel_size_nm,
        "beam_current_na": m.beam_current_na,
        "dwell_time_us": m.dwell_time_us,
        "working_distance_mm": m.working_distance_mm,
        "chamber_pressure_pa": m.chamber_pressure_pa,
        "metadata_source": m.metadata_source,
        "metadata_completeness": m.metadata_completeness,
        "raw_metadata_json": m.raw_metadata_json,
    }


class MetadataUpdateRequest(BaseModel):
    microscope: Optional[str] = None
    detector: Optional[str] = None
    accelerating_voltage_kv: Optional[float] = None
    magnification: Optional[float] = None
    pixel_size_nm: Optional[float] = None
    beam_current_na: Optional[float] = None
    dwell_time_us: Optional[float] = None
    working_distance_mm: Optional[float] = None
    chamber_pressure_pa: Optional[float] = None


@router.put("/{id}/metadata")
def update_metadata(
    id: int,
    meta_in: MetadataUpdateRequest,
    payload: Dict[str, Any] = Depends(RoleChecker(["CURATOR", "ADMIN"])),
    db: Session = Depends(get_db),
):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.metadata_rel:
        raise HTTPException(status_code=404, detail="Image or metadata not found")

    m = img.metadata_rel
    update_data = meta_in.model_dump(exclude_unset=True)

    for field, val in update_data.items():
        setattr(m, field, val)

    m.metadata_source = "curator_edited"

    fields = [
        m.microscope,
        m.detector,
        m.accelerating_voltage_kv,
        m.magnification,
        m.pixel_size_nm,
        m.beam_current_na,
        m.dwell_time_us,
        m.working_distance_mm,
        m.chamber_pressure_pa,
    ]
    m.metadata_completeness = float(sum(f is not None for f in fields) / len(fields))

    db.commit()
    db.refresh(m)

    user_id = int(payload.get("sub")) if payload and "sub" in payload else None

    # Record provenance event
    ProvenanceService.record_event(
        db=db,
        image_id=img.id,
        event_type="METADATA_UPDATE",
        parameters={
            "updated_fields": list(update_data.keys()),
            "new_completeness": m.metadata_completeness,
            "source": m.metadata_source,
        },
    )

    # Record audit log
    AuditService.log_action(
        db=db,
        action="METADATA_UPDATE",
        resource_type="image_metadata",
        user_id=user_id,
        resource_id=m.id,
        parameters={"image_id": img.id, "updated_fields": list(update_data.keys())},
    )

    return {
        "image_id": img.id,
        "microscope": m.microscope,
        "detector": m.detector,
        "accelerating_voltage_kv": m.accelerating_voltage_kv,
        "magnification": m.magnification,
        "pixel_size_nm": m.pixel_size_nm,
        "beam_current_na": m.beam_current_na,
        "dwell_time_us": m.dwell_time_us,
        "working_distance_mm": m.working_distance_mm,
        "chamber_pressure_pa": m.chamber_pressure_pa,
        "metadata_source": m.metadata_source,
        "metadata_completeness": m.metadata_completeness,
    }


@router.get("/{id}/quality")
def get_quality(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.quality_profile:
        raise HTTPException(status_code=404, detail="Quality profile not found")
    qp = img.quality_profile
    return {
        "image_id": img.id,
        "laplacian_variance": qp.laplacian_variance,
        "edge_density": qp.edge_density,
        "shannon_entropy": qp.shannon_entropy,
        "dynamic_range": qp.dynamic_range,
        "clipping_ratio": qp.clipping_ratio,
        "high_freq_fft_ratio": qp.high_freq_fft_ratio,
        "composite_quality_risk": qp.composite_quality_risk,
        "quality_label": qp.quality_label,
        "disclaimer": "image-derived quality-risk indicators; not direct physical sensor calibrations",
    }


@router.get("/{id}/integrity")
def get_integrity(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.duplicate_profile:
        raise HTTPException(status_code=404, detail="Duplicate profile not found")
    dp = img.duplicate_profile
    return {
        "image_id": img.id,
        "sha256": img.sha256,
        "phash": dp.phash,
        "dhash": dp.dhash,
        "duplicate_status": dp.duplicate_status,
        "matched_image_id": dp.matched_image_id,
        "similarity_score": dp.similarity_score,
        "match_stage": dp.match_stage,
    }


@router.get("/{id}/novelty")
def get_novelty(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    emb = db.query(Embedding).filter(Embedding.image_id == id, Embedding.embedding_type == "dinov2_base").first()
    if not emb:
        raise HTTPException(status_code=400, detail="Image has no embedding")

    import numpy as np
    vec = np.array(emb.embedding_vector)
    novelty_engine = NoveltyEngine()
    res = novelty_engine.evaluate_novelty(vec)
    res["image_id"] = img.id
    return res


@router.get("/{id}/similar")
def get_similar_images(id: int, top_k: int = 10, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    emb = db.query(Embedding).filter(Embedding.image_id == id, Embedding.embedding_type == "dinov2_base").first()
    if not emb:
        raise HTTPException(status_code=400, detail="Image has no embedding")

    import numpy as np
    vec = np.array(emb.embedding_vector)
    faiss_engine = FAISSEngine()
    search_res = faiss_engine.search(vec, top_k=top_k + 1)

    out = []
    for cand_id, sim in search_res:
        if cand_id == id:
            continue  # Exclude query image
        cand_img = db.query(Image).filter(Image.id == cand_id).first()
        if cand_img:
            meta = cand_img.metadata_rel
            dp = cand_img.duplicate_profile
            out.append({
                "rank": len(out) + 1,
                "image_id": cand_img.id,
                "original_filename": cand_img.original_filename,
                "similarity": sim,
                "duplicate_status": dp.duplicate_status if dp else "NO_DECLARED_REDUNDANCY_DETECTED",
                "microscope": meta.microscope if meta else None,
                "magnification": meta.magnification if meta else None,
            })
        if len(out) >= top_k:
            break
    return out
