import io
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
import numpy as np
from PIL import Image as PILImage
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.config import settings
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
from src.ingestion.reader import ScientificImageReader

logger = logging.getLogger("scidata.images")
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


def _format_image_detail(img: Image) -> Dict[str, Any]:
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


def _get_sample_dir() -> Path:
    candidates = [
        Path("BBBC021_v1_images_Week10_40111/Week10_40111"),
        Path("../BBBC021_v1_images_Week10_40111/Week10_40111"),
        Path("../../BBBC021_v1_images_Week10_40111/Week10_40111"),
        Path("C:/Users/Pranet/Downloads/Mini Project/BBBC021_v1_images_Week10_40111/Week10_40111"),
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c.resolve()
    return candidates[0]


@router.get("/samples/available")
def list_available_samples():
    sample_dir = _get_sample_dir()
    if not sample_dir.exists():
        return {"samples": []}
    files = [f for f in os.listdir(sample_dir) if f.lower().endswith(('.tif', '.tiff', '.png', '.jpg'))]
    samples_info = []
    for f in sorted(files)[:25]:
        st = os.stat(os.path.join(sample_dir, f))
        channel = "DAPI Nuclei (w1)" if "_w1" in f else ("Tubulin Cytoskeleton (w2)" if "_w2" in f else ("Actin Microfilaments (w4)" if "_w4" in f else "Fluorescence Channel"))
        samples_info.append({
            "filename": f,
            "channel": channel,
            "size_bytes": st.st_size,
            "size_mb": round(st.st_size / (1024 * 1024), 2)
        })
    return {"samples": samples_info}


@router.post("/samples/ingest")
def ingest_sample(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    filename = payload.get("filename")
    if not filename:
        raise HTTPException(status_code=400, detail="Sample filename required")
    filename = os.path.basename(filename)
    sample_dir = _get_sample_dir()
    file_path = sample_dir / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Sample file not found on disk")

    with open(file_path, "rb") as f:
        file_bytes = f.read()

    channel = "DAPI Nuclei" if "_w1" in filename else ("Tubulin Cytoskeleton" if "_w2" in filename else ("Actin Microfilaments" if "_w4" in filename else "Fluorescence"))
    manual_meta = {
        "microscope": "Widefield Fluorescence (IXM)",
        "detector": "sCMOS High-QE",
        "magnification": 200.0,
        "pixel_size_nm": 325.0,
        "accelerating_voltage_kv": 0.0,
        "stain": channel,
        "metadata_source": "BBBC021 Assay Benchmark"
    }

    try:
        image_record = IngestionService.ingest_file(
            db=db,
            file_bytes=file_bytes,
            original_filename=filename,
            project_id=payload.get("project_id"),
            manual_metadata=manual_meta
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    res = _format_image_detail(image_record)
    res["message"] = f"Sample micrograph '{filename}' ingested, quality-assessed, and indexed successfully."
    return res


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

    res = _format_image_detail(image_record)
    res["message"] = "Micrograph ingested, quality-assessed, and indexed successfully."
    return res


@router.get("/{id}")
def get_image_detail(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    return _format_image_detail(img)


@router.get("/{id}/file")
def get_image_file(id: int, raw: bool = False, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.storage_path:
        raise HTTPException(status_code=404, detail="Image file not found")
    file_path = Path(img.storage_path)
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Image file missing from storage")

    if raw:
        return FileResponse(file_path, media_type=img.mime_type, filename=img.original_filename)

    # For browser rendering: check if high-contrast display PNG exists
    disp_path = settings.THUMBNAILS_PATH / f"{img.sha256}_display.png"
    if disp_path.is_file():
        return FileResponse(disp_path, media_type="image/png")

    if file_path.suffix.lower() in [".tif", ".tiff"]:
        try:
            arr, _ = ScientificImageReader.load_array(file_path)
            p_low, p_high = np.percentile(arr, (0.5, 99.8))
            norm = np.clip((arr - p_low) / max(1.0, (p_high - p_low)) * 255.0, 0, 255).astype(np.uint8)
            disp_im = PILImage.fromarray(norm, mode="L" if norm.ndim == 2 else None)
            disp_path.parent.mkdir(parents=True, exist_ok=True)
            disp_im.save(disp_path, "PNG")
            return FileResponse(disp_path, media_type="image/png")
        except Exception as e:
            logger.error(f"On-the-fly display PNG generation error: {e}")

    return FileResponse(file_path, media_type=img.mime_type)


@router.get("/{id}/thumbnail")
def get_image_thumbnail(id: int, db: Session = Depends(get_db)):
    img = db.query(Image).filter(Image.id == id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")

    thumb_path = Path(img.thumbnail_path) if img.thumbnail_path else None
    if thumb_path and thumb_path.is_file():
        return FileResponse(thumb_path, media_type="image/png")

    expected_thumb = settings.THUMBNAILS_PATH / f"{img.sha256}_thumb.png"
    if expected_thumb.is_file():
        img.thumbnail_path = str(expected_thumb)
        db.commit()
        return FileResponse(expected_thumb, media_type="image/png")

    if img.storage_path and Path(img.storage_path).is_file():
        try:
            arr, _ = ScientificImageReader.load_array(img.storage_path)
            p_low, p_high = np.percentile(arr, (0.5, 99.8))
            norm = np.clip((arr - p_low) / max(1.0, (p_high - p_low)) * 255.0, 0, 255).astype(np.uint8)
            im = PILImage.fromarray(norm, mode="L" if norm.ndim == 2 else None)
            expected_thumb.parent.mkdir(parents=True, exist_ok=True)
            im.thumbnail((256, 256))
            im.save(expected_thumb, "PNG")
            img.thumbnail_path = str(expected_thumb)
            db.commit()
            return FileResponse(expected_thumb, media_type="image/png")
        except Exception as e:
            logger.error(f"On-the-fly thumbnail generation failed: {e}")

    # Fallback to a solid neutral placeholder PNG so browser never loops
    fallback = PILImage.new("RGBA", (256, 256), (15, 23, 42, 255))
    buf = io.BytesIO()
    fallback.save(buf, "PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")


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


@router.get("/{id}/analysis")
def get_image_analysis(id: int, db: Session = Depends(get_db)):
    """Deep scientific pixel-level and frequency-level analysis."""
    img = db.query(Image).filter(Image.id == id).first()
    if not img or not img.storage_path or not Path(img.storage_path).is_file():
        raise HTTPException(status_code=404, detail="Image file not found")

    try:
        arr, _ = ScientificImageReader.load_array(img.storage_path)
        # Compute 32-bin pixel intensity histogram
        hist, bin_edges = np.histogram(arr, bins=32)
        bins_data = [
            {"range": f"{int(bin_edges[i])}-{int(bin_edges[i+1])}", "count": int(hist[i]), "pct": float(hist[i]/arr.size*100)}
            for i in range(len(hist))
        ]

        # Nuclei / Spot detection estimate
        from scipy import ndimage
        thresh = float(np.percentile(arr, 88.0))
        mask = arr > thresh
        labeled, num_features = ndimage.label(mask)
        foreground_pct = float(np.sum(mask) / arr.size * 100)

        # Quantile intensity statistics
        p0, p1, p25, p50, p75, p99, p100 = np.percentile(arr, [0, 1, 25, 50, 75, 99, 100])

        # 2D Fourier energy ring analysis (High-frequency ratio)
        fft = np.fft.fft2(arr.astype(float))
        fft_shift = np.fft.fftshift(fft)
        magnitude_spectrum = np.log(np.abs(fft_shift) + 1.0)
        h, w = arr.shape[:2]
        center = (h // 2, w // 2)
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        max_r = min(center)
        high_freq_mask = dist_from_center > (max_r * 0.5)
        high_freq_energy = float(np.sum(np.abs(fft_shift)[high_freq_mask]) / (np.sum(np.abs(fft_shift)) + 1e-9) * 100)

        # Gradient / Edge density
        gy, gx = np.gradient(arr.astype(float))
        grad_mag = np.sqrt(gx**2 + gy**2)
        mean_edge_intensity = float(np.mean(grad_mag))

        return {
            "image_id": img.id,
            "filename": img.original_filename,
            "dimensions": f"{img.width} × {img.height}",
            "dtype": str(arr.dtype),
            "bit_depth": 16 if "16" in str(arr.dtype) else (32 if "32" in str(arr.dtype) else 8),
            "total_pixels": int(arr.size),
            "quantiles": {
                "min": float(p0),
                "p1": float(p1),
                "p25": float(p25),
                "median": float(p50),
                "p75": float(p75),
                "p99": float(p99),
                "max": float(p100),
                "mean": round(float(np.mean(arr)), 2),
                "std": round(float(np.std(arr)), 2),
                "dynamic_range": float(p100 - p0),
            },
            "histogram": bins_data,
            "spot_detection": {
                "estimated_cell_nuclei_count": int(num_features),
                "threshold_intensity": round(thresh, 1),
                "foreground_coverage_pct": round(foreground_pct, 2),
            },
            "frequency_analysis": {
                "high_frequency_energy_pct": round(high_freq_energy, 2),
                "mean_gradient_edge_strength": round(mean_edge_intensity, 2),
                "shannon_entropy_bits": round(float(img.quality_profile.shannon_entropy if img.quality_profile else 0.0), 3),
                "laplacian_focus_variance": round(float(img.quality_profile.laplacian_variance if img.quality_profile else 0.0), 2),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis computation failed: {str(e)}")

