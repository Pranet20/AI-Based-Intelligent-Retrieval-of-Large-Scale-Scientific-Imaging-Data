"""Model Registry API endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.models import ModelVersion
from app.db.session import get_db
from app.services.audit import AuditService

router = APIRouter(prefix="/models", tags=["Models"])


class ModelVersionResponse(BaseModel):
    id: int
    model_id: str
    version: str
    architecture: str
    embedding_dimension: int
    weights_hash: str
    preprocessing_version: str
    source: str
    is_active: bool


@router.get("", response_model=List[ModelVersionResponse])
def list_models(db: Session = Depends(get_db)):
    models = db.query(ModelVersion).all()
    AuditService.log_action(
        db=db,
        action="MODEL_ACCESS",
        resource_type="model_versions",
        parameters={"count": len(models)},
    )
    return [
        ModelVersionResponse(
            id=m.id,
            model_id=m.model_id,
            version=m.version,
            architecture=m.architecture,
            embedding_dimension=m.embedding_dimension,
            weights_hash=m.weights_hash,
            preprocessing_version=m.preprocessing_version,
            source=m.source,
            is_active=m.is_active,
        )
        for m in models
    ]


class FeatureExtractionRequest(BaseModel):
    image_id: int
    model_id: str = "dinov2_vits14_phase2"


class FeatureComparisonRequest(BaseModel):
    image_id_a: int
    image_id_b: int


@router.post("/extract-features")
def extract_model_features(req: FeatureExtractionRequest, db: Session = Depends(get_db)):
    """Interactive neural feature extraction on any micrograph."""
    import time
    from pathlib import Path
    import numpy as np
    from app.db.models import Image, Embedding
    from app.ml.dinov2_engine import DINOv2Engine
    from app.ml.phase4_engine import Phase4Engine

    img = db.query(Image).filter(Image.id == req.image_id).first()
    if not img or not img.storage_path or not Path(img.storage_path).is_file():
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Image not found")

    t0 = time.perf_counter()
    # Check if embedding already computed or compute live
    emb_type = "phase4_adapted" if "phase4" in req.model_id else "dinov2_base"
    emb = db.query(Embedding).filter(Embedding.image_id == img.id, Embedding.embedding_type == emb_type).first()
    
    if emb and emb.embedding_vector:
        vec = np.array(emb.embedding_vector, dtype=float)
    else:
        dino = DINOv2Engine()
        raw_vec = dino.embed_image(img.storage_path)
        if "phase4" in req.model_id:
            p4 = Phase4Engine()
            vec = p4.adapt_embedding(raw_vec)
        else:
            vec = raw_vec
    
    latency_ms = (time.perf_counter() - t0) * 1000.0

    # L2 norm and statistics
    l2_norm = float(np.linalg.norm(vec))
    variance = float(np.var(vec))
    active_dims = int(np.sum(np.abs(vec) > 0.05))

    # 14x14 pseudo-attention patch distribution
    patches = np.abs(vec[:196]) if len(vec) >= 196 else np.abs(vec)
    patch_grid = (patches / (np.max(patches) + 1e-9)).reshape((14, 14)).tolist()

    return {
        "image_id": img.id,
        "filename": img.original_filename,
        "model_id": req.model_id,
        "embedding_dimension": len(vec),
        "l2_norm": round(l2_norm, 4),
        "variance": round(variance, 6),
        "active_dimensions_count": active_dims,
        "active_dimensions_pct": round(active_dims / len(vec) * 100, 1),
        "latency_ms": round(latency_ms, 2),
        "vector_preview": [round(float(v), 4) for v in vec[:48]],
        "full_vector": [round(float(v), 5) for v in vec],
        "patch_attention_14x14": patch_grid,
    }


@router.post("/compare-features")
def compare_model_features(req: FeatureComparisonRequest, db: Session = Depends(get_db)):
    """Interactive cosine similarity probe between two micrographs."""
    import numpy as np
    from app.db.models import Image, Embedding
    from fastapi import HTTPException

    img_a = db.query(Image).filter(Image.id == req.image_id_a).first()
    img_b = db.query(Image).filter(Image.id == req.image_id_b).first()
    if not img_a or not img_b:
        raise HTTPException(status_code=404, detail="One or both images not found")

    emb_a = db.query(Embedding).filter(Embedding.image_id == img_a.id, Embedding.embedding_type == "dinov2_base").first()
    emb_b = db.query(Embedding).filter(Embedding.image_id == img_b.id, Embedding.embedding_type == "dinov2_base").first()

    if not emb_a or not emb_b:
        raise HTTPException(status_code=400, detail="Missing vector embeddings for comparison")

    va = np.array(emb_a.embedding_vector, dtype=float)
    vb = np.array(emb_b.embedding_vector, dtype=float)

    # Cosine similarity
    cos_sim = float(np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9))
    euclidean = float(np.linalg.norm(va - vb))

    return {
        "image_a": {"id": img_a.id, "filename": img_a.original_filename},
        "image_b": {"id": img_b.id, "filename": img_b.original_filename},
        "cosine_similarity": round(cos_sim, 4),
        "similarity_pct": round(max(0.0, cos_sim) * 100, 2),
        "euclidean_distance": round(euclidean, 4),
        "alignment_assessment": "High Morphological Homology" if cos_sim > 0.85 else ("Moderate Phenotypic Overlap" if cos_sim > 0.6 else "Distinct Phenotype / Modality"),
    }

