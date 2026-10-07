"""Visual & Multimodal Retrieval Endpoints with Dual Representation Support."""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
import numpy as np
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.security import get_optional_user_payload
from app.db.models import (
    DuplicateProfile,
    Embedding,
    Image,
    ImageMetadata,
    QualityProfile,
    RetrievalQuery,
    RetrievalResult,
)
from app.db.session import get_db
from app.ml.dinov2_engine import DINOv2Engine
from app.ml.faiss_engine import FAISSEngine
from app.ml.novelty_engine import NoveltyEngine
from app.ml.phase4_engine import Phase4Engine
from app.services.audit import AuditService
from app.services.provenance import ProvenanceService

router = APIRouter(prefix="/search", tags=["Retrieval"])


class SearchResultItem(BaseModel):
    rank: int
    image_id: int
    original_filename: str
    similarity_score: float
    duplicate_status: str
    quality_label: str
    composite_quality_risk: float
    novelty_score: Optional[float]
    metadata_summary: Dict[str, Any]


class SearchResponse(BaseModel):
    query_image_id: Optional[int]
    total_results: int
    results: List[SearchResultItem]
    retrieval_mode: str = "frozen_visual_dinov2_vit_s14"
    note: str = "Metadata weight alpha=1.0 under calibrated frozen baseline."


@router.post("", response_model=SearchResponse)
@router.post("/vector", response_model=SearchResponse)
@router.post("/hybrid", response_model=SearchResponse)
async def search_images(
    request: Request,
    payload: Optional[Dict[str, Any]] = Depends(get_optional_user_payload),
    db: Session = Depends(get_db),
):
    """
    Search nearest visual neighbors by image_id or raw image upload.
    Supports both JSON payloads and Multipart/Urlencoded forms.
    Supports Dual Representation:
      - 'dinov2_base': General self-supervised foundation representation (FAISS IndexFlatIP).
      - 'phase4_adapted': Acquisition-aware representation using frozen Phase 4 adapter head.
    """
    content_type = request.headers.get("content-type", "")

    image_id: Optional[int] = None
    file = None
    top_k: int = 10
    representation: str = "dinov2_base"
    modality_filter: Optional[str] = None
    instrument_filter: Optional[str] = None
    metadata_query: Optional[Dict[str, Any]] = None

    if "application/json" in content_type:
        body = await request.json()
        image_id = body.get("query_image_id") or body.get("image_id")
        top_k = int(body.get("top_k", 10))
        representation = str(body.get("representation", "dinov2_base")).lower()
        modality_filter = body.get("modality_filter")
        instrument_filter = body.get("instrument")
        metadata_query = body.get("metadata_query")
    else:
        form = await request.form()
        if "image_id" in form and form["image_id"]:
            try:
                image_id = int(form["image_id"])
            except ValueError:
                image_id = None
        elif "query_image_id" in form and form["query_image_id"]:
            try:
                image_id = int(form["query_image_id"])
            except ValueError:
                image_id = None

        top_k = int(form.get("top_k", 10))
        file = form.get("file")
        representation = str(form.get("representation", "dinov2_base")).lower()
        modality_filter = form.get("modality_filter")
        instrument_filter = form.get("instrument")
        meta_raw = form.get("metadata_query")
        if meta_raw:
            if isinstance(meta_raw, str):
                try:
                    metadata_query = json.loads(meta_raw)
                except Exception:
                    metadata_query = None
            elif isinstance(meta_raw, dict):
                metadata_query = meta_raw

    # Merge metadata query filters if present
    if metadata_query and isinstance(metadata_query, dict):
        if not modality_filter and "modality" in metadata_query:
            modality_filter = metadata_query["modality"]
        if not instrument_filter and "instrument" in metadata_query:
            instrument_filter = metadata_query["instrument"]

    dino_engine = DINOv2Engine()
    faiss_engine = FAISSEngine()
    novelty_engine = NoveltyEngine()
    phase4_engine = Phase4Engine()

    q_vector: Optional[np.ndarray] = None
    query_img_record = None

    if representation == "phase4_adapted":
        try:
            phase4_engine._ensure_loaded()
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail=f"Phase 4 acquisition-aware representation is unavailable: {str(e)}",
            )
        is_phase4 = True
    elif representation == "dinov2_base":
        is_phase4 = False
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported representation '{representation}'. Allowed: ['dinov2_base', 'phase4_adapted']",
        )


    if image_id is not None:
        query_img_record = db.query(Image).filter(Image.id == image_id).first()
        if not query_img_record:
            raise HTTPException(status_code=404, detail="Query image_id not found")

        if is_phase4:
            emb = db.query(Embedding).filter(Embedding.image_id == image_id, Embedding.embedding_type == "phase4_adapted").first()
            if emb:
                q_vector = np.array(emb.embedding_vector, dtype=np.float32)
            else:
                base_emb = db.query(Embedding).filter(Embedding.image_id == image_id, Embedding.embedding_type == "dinov2_base").first()
                if not base_emb:
                    raise HTTPException(status_code=400, detail="Query image has no embedding")
                q_vector = phase4_engine.adapt_embedding(np.array(base_emb.embedding_vector, dtype=np.float32))
        else:
            emb = db.query(Embedding).filter(Embedding.image_id == image_id, Embedding.embedding_type == "dinov2_base").first()
            if not emb:
                raise HTTPException(status_code=400, detail="Query image has no embedding")
            q_vector = np.array(emb.embedding_vector, dtype=np.float32)

    elif file is not None:
        file_bytes = await file.read()
        import tempfile
        ext = Path(getattr(file, "filename", "temp.png")).suffix.lower() or ".png"
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        try:
            raw_dino = dino_engine.embed_image(tmp_path)
            if is_phase4:
                q_vector = phase4_engine.adapt_embedding(raw_dino)
            else:
                q_vector = raw_dino
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    else:
        raise HTTPException(status_code=400, detail="Must provide either image_id/query_image_id or file")

    # Ensure query vector is unit normalized
    q_norm = np.linalg.norm(q_vector)
    if q_norm > 1e-12:
        q_vector = q_vector / q_norm

    raw_candidates: List[tuple[int, float]] = []

    if is_phase4:
        # Acquisition-Aware Retrieval using Phase 4 representations
        target_embs = db.query(Embedding).filter(Embedding.embedding_type == "phase4_adapted").all()
        for cand_emb in target_embs:
            if query_img_record and cand_emb.image_id == query_img_record.id:
                continue
            cand_vec = np.array(cand_emb.embedding_vector, dtype=np.float32)
            c_norm = np.linalg.norm(cand_vec)
            if c_norm > 1e-12:
                cand_vec = cand_vec / c_norm
            sim = float(np.dot(q_vector, cand_vec))
            raw_candidates.append((cand_emb.image_id, sim))
        raw_candidates.sort(key=lambda x: x[1], reverse=True)
    else:
        # Visual Foundation Retrieval using exact FAISS IndexFlatIP
        search_top_k = max(top_k * 4, 20) + (1 if query_img_record else 0)
        raw_candidates = faiss_engine.search(q_vector, top_k=search_top_k)

    # Record RetrievalQuery in DB
    user_id = int(payload.get("sub")) if payload and "sub" in payload else None
    query_mode_label = "acquisition_aware_phase4" if is_phase4 else "visual_only_dinov2"
    if modality_filter or instrument_filter:
        query_mode_label += "_hybrid_filtered"

    rq = RetrievalQuery(
        user_id=user_id,
        query_image_id=query_img_record.id if query_img_record else None,
        query_mode=query_mode_label,
        top_k=top_k,
    )
    db.add(rq)
    db.commit()
    db.refresh(rq)

    results_list: List[SearchResultItem] = []
    rank_counter = 1

    for cand_id, sim in raw_candidates:
        if query_img_record and cand_id == query_img_record.id:
            continue

        cand_img = db.query(Image).filter(Image.id == cand_id).first()
        if not cand_img:
            continue

        meta = cand_img.metadata_rel
        qp = cand_img.quality_profile
        dp = cand_img.duplicate_profile

        # Apply metadata filters if specified
        if modality_filter:
            m_scope = (meta.microscope or "").lower() if meta else ""
            if modality_filter.lower() not in m_scope:
                continue

        if instrument_filter:
            det = (meta.detector or "").lower() if meta else ""
            m_scope = (meta.microscope or "").lower() if meta else ""
            if instrument_filter.lower() not in det and instrument_filter.lower() not in m_scope:
                continue

        meta_sum = {
            "microscope": meta.microscope if meta else None,
            "detector": meta.detector if meta else None,
            "voltage_kv": meta.accelerating_voltage_kv if meta else None,
            "magnification": meta.magnification if meta else None,
        }

        # Novelty score
        cand_emb = db.query(Embedding).filter(Embedding.image_id == cand_id, Embedding.embedding_type == "dinov2_base").first()
        nov_score = None
        if cand_emb:
            nov_res = novelty_engine.evaluate_novelty(np.array(cand_emb.embedding_vector))
            nov_score = nov_res["novelty_score"]

        item = SearchResultItem(
            rank=rank_counter,
            image_id=cand_img.id,
            original_filename=cand_img.original_filename,
            similarity_score=float(sim),
            duplicate_status=dp.duplicate_status if dp else "NO_DECLARED_REDUNDANCY_DETECTED",
            quality_label=qp.quality_label if qp else "NOMINAL",
            composite_quality_risk=qp.composite_quality_risk if qp else 0.0,
            novelty_score=nov_score,
            metadata_summary=meta_sum,
        )
        results_list.append(item)

        # Store in RetrievalResult
        rr = RetrievalResult(
            query_id=rq.id,
            rank=rank_counter,
            result_image_id=cand_img.id,
            similarity_score=float(sim),
            metadata_summary=meta_sum,
            duplicate_status=item.duplicate_status,
            novelty_score=nov_score,
        )
        db.add(rr)
        rank_counter += 1

        if len(results_list) >= top_k:
            break

    db.commit()

    if query_img_record:
        ProvenanceService.record_event(
            db=db,
            image_id=query_img_record.id,
            event_type="SEARCH",
            parameters={"top_k": top_k, "representation": representation, "results_found": len(results_list)},
        )

    AuditService.log_action(
        db=db,
        action="SEARCH",
        resource_type="retrieval_queries",
        user_id=user_id,
        resource_id=rq.id,
        parameters={
            "query_image_id": query_img_record.id if query_img_record else None,
            "top_k": top_k,
            "representation": representation,
            "results_returned": len(results_list),
        },
    )

    retrieval_mode_str = (
        "frozen_phase4_acquisition_adapter" if is_phase4 else "frozen_visual_dinov2_vit_s14"
    )
    note_str = (
        "Acquisition-aware retrieval using frozen Phase 4 adapter (SHA-256 verified)."
        if is_phase4
        else "Visual quality retrieval using frozen DINOv2 ViT-S/14 representation."
    )

    return SearchResponse(
        query_image_id=query_img_record.id if query_img_record else None,
        total_results=len(results_list),
        results=results_list,
        retrieval_mode=retrieval_mode_str,
        note=note_str,
    )
