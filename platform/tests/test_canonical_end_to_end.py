"""Canonical 20-step end-to-end integration workflow test."""

from datetime import datetime, timezone
import io
import json
from pathlib import Path
import numpy as np
from PIL import Image as PILImage
from starlette.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.models import (
    AuditLog,
    DuplicateProfile,
    Embedding,
    Image,
    ImageMetadata,
    Project,
    ProvenanceEvent,
    QualityProfile,
    ReviewItem,
    User,
)


def test_canonical_20_step_lifecycle(db_session):
    """Execute and record the complete 20-step scientific image data management lifecycle."""
    step_results = {}
    db = db_session

    try:
        with TestClient(app) as client:
            # Step 1: CREATE USER
            username = f"canonical_user_{int(datetime.now(timezone.utc).timestamp())}"
            reg_res = client.post(
                "/api/v1/auth/register",
                json={
                    "username": username,
                    "email": f"{username}@research.org",
                    "password": "CanonicalPassword123!",
                    "role": "CURATOR",
                },
            )
            assert reg_res.status_code == 200, reg_res.text
            user_data = reg_res.json()
            user_token = user_data["access_token"]
            step_results["1_create_user"] = {"status": "SUCCESS", "username": username, "role": user_data["role"]}

            # Step 2: LOGIN
            login_res = client.post(
                "/api/v1/auth/login",
                data={"username": username, "password": "CanonicalPassword123!"},
            )
            assert login_res.status_code == 200, login_res.text
            auth_token = login_res.json()["access_token"]
            headers = {"Authorization": f"Bearer {auth_token}"}
            step_results["2_login"] = {"status": "SUCCESS", "token_type": "bearer"}

            # Step 3: CREATE PROJECT
            proj_res = client.post(
                "/api/v1/projects",
                json={"name": "End-to-End Validation Study", "description": "Automated pipeline lifecycle test"},
                headers=headers,
            )
            assert proj_res.status_code == 200, proj_res.text
            proj_id = proj_res.json()["id"]
            step_results["3_create_project"] = {"status": "SUCCESS", "project_id": proj_id}

            # Prepare controlled synthetic SEM fixture
            fixture_arr = (np.random.RandomState(12345).rand(256, 256) * 255).astype(np.uint8)
            img_buf = io.BytesIO()
            PILImage.fromarray(fixture_arr).save(img_buf, format="PNG")
            img_bytes = img_buf.getvalue()

            # Step 4: UPLOAD IMAGE
            upload_res = client.post(
                "/api/v1/images/upload",
                files={"file": ("canonical_sem_sample.png", img_bytes, "image/png")},
                data={
                    "project_id": proj_id,
                    "microscope": "Thermo Scientific Apreo 2 SEM",
                    "detector": "Trinity T1",
                    "accelerating_voltage_kv": 15.0,
                    "magnification": 50000.0,
                    "pixel_size_nm": 2.2,
                },
                headers=headers,
            )
            assert upload_res.status_code == 200, upload_res.text
            upload_data = upload_res.json()
            image_id = upload_data["id"]
            step_results["4_upload_image"] = {"status": "SUCCESS", "image_id": image_id}

            # Step 5: SHA-256
            image_rec = db.query(Image).filter(Image.id == image_id).first()
            assert image_rec is not None
            assert len(image_rec.sha256) == 64
            step_results["5_sha256"] = {"status": "SUCCESS", "sha256": image_rec.sha256}

            # Step 6: STORE IMMUTABLE ORIGINAL
            orig_path = Path(image_rec.storage_path)
            assert orig_path.exists()
            assert orig_path.stat().st_size == len(img_bytes)
            step_results["6_store_immutable_original"] = {"status": "SUCCESS", "path": str(orig_path)}

            # Step 7: EXTRACT METADATA
            meta_rec = db.query(ImageMetadata).filter(ImageMetadata.image_id == image_id).first()
            assert meta_rec is not None
            assert meta_rec.microscope == "Thermo Scientific Apreo 2 SEM"
            assert meta_rec.accelerating_voltage_kv == 15.0
            step_results["7_extract_metadata"] = {
                "status": "SUCCESS",
                "completeness": meta_rec.metadata_completeness,
                "source": meta_rec.metadata_source,
            }

            # Step 8: CREATE THUMBNAIL
            thumb_path = Path(image_rec.thumbnail_path)
            assert thumb_path.exists()
            step_results["8_create_thumbnail"] = {"status": "SUCCESS", "path": str(thumb_path)}

            # Step 9: QUALITY ANALYSIS
            qp = db.query(QualityProfile).filter(QualityProfile.image_id == image_id).first()
            assert qp is not None
            assert 0.0 <= qp.composite_quality_risk <= 1.0
            step_results["9_quality_analysis"] = {
                "status": "SUCCESS",
                "composite_quality_risk": qp.composite_quality_risk,
                "label": qp.quality_label,
            }

            # Step 10 & 11: EXACT & NEAR DUPLICATE CHECK
            dp = db.query(DuplicateProfile).filter(DuplicateProfile.image_id == image_id).first()
            assert dp is not None
            step_results["10_exact_duplicate_check"] = {"status": "SUCCESS", "phash_computed": dp.phash is not None}
            step_results["11_near_duplicate_check"] = {"status": "SUCCESS", "duplicate_status": dp.duplicate_status}

            # Step 12: DINO EMBEDDING
            dino_emb = db.query(Embedding).filter(Embedding.image_id == image_id, Embedding.embedding_type == "dinov2_base").first()
            assert dino_emb is not None
            assert len(dino_emb.embedding_vector) == 384
            step_results["12_dino_embedding"] = {"status": "SUCCESS", "dim": 384, "normalized": dino_emb.l2_normalized}

            # Step 13: PHASE 4 EMBEDDING
            phase4_emb = db.query(Embedding).filter(Embedding.image_id == image_id, Embedding.embedding_type == "phase4_adapted").first()
            assert phase4_emb is not None
            assert len(phase4_emb.embedding_vector) == 384
            step_results["13_phase4_embedding"] = {"status": "SUCCESS", "dim": 384}

            # Step 14: FAISS INDEX
            from app.ml.faiss_engine import FAISSEngine
            faiss_engine = FAISSEngine()
            assert faiss_engine.index.ntotal >= 1
            step_results["14_faiss_index"] = {"status": "SUCCESS", "total_indexed": faiss_engine.index.ntotal}

            # Step 15: NOVELTY
            nov_res = client.get(f"/api/v1/images/{image_id}/novelty", headers=headers)
            assert nov_res.status_code == 200, nov_res.text
            nov_data = nov_res.json()
            step_results["15_novelty"] = {
                "status": "SUCCESS",
                "novelty_score": nov_data["novelty_score"],
                "novelty_percentile": nov_data["novelty_percentile"],
            }

            # Step 16: IMAGE PROFILE
            profile_res = client.get(f"/api/v1/images/{image_id}", headers=headers)
            assert profile_res.status_code == 200, profile_res.text
            profile_data = profile_res.json()
            step_results["16_image_profile"] = {
                "status": "SUCCESS",
                "filename": profile_data["original_filename"],
                "processing_status": profile_data["processing_status"],
            }

            # Step 17 & 18: SEARCH & RETRIEVE TOP-K
            search_res = client.post(
                "/api/v1/search",
                data={"image_id": image_id, "top_k": 5},
                headers=headers,
            )
            assert search_res.status_code == 200, search_res.text
            search_data = search_res.json()
            step_results["17_search"] = {"status": "SUCCESS", "mode": search_data["retrieval_mode"]}
            step_results["18_retrieve_top_k"] = {"status": "SUCCESS", "results_count": search_data["total_results"]}

            # Step 19: REVIEW QUEUE
            queue_res = client.get("/api/v1/curation/review-queue", headers=headers)
            assert queue_res.status_code == 200, queue_res.text
            queue_items = queue_res.json()
            step_results["19_review_queue"] = {"status": "SUCCESS", "queue_length": len(queue_items)}

            # Step 20: HUMAN REVIEW
            rev_res = client.post(
                "/api/v1/curation/reviews",
                json={
                    "image_id": image_id,
                    "decision": "KEEP",
                    "comment": "Validated nominal SEM micrograph with full metadata completeness.",
                },
                headers=headers,
            )
            assert rev_res.status_code == 200, rev_res.text
            rev_data = rev_res.json()
            step_results["20_human_review"] = {
                "status": "SUCCESS",
                "decision": rev_data["decision"],
                "algorithmic_recommendation": rev_data["algorithmic_recommendation"],
            }

            # Verification: PROVENANCE
            provs = db.query(ProvenanceEvent).filter(ProvenanceEvent.image_id == image_id).all()
            prov_types = [p.event_type for p in provs]
            assert "UPLOAD" in prov_types
            assert "QUALITY_ANALYSIS" in prov_types
            assert "REVIEW" in prov_types
            step_results["provenance_verification"] = {"status": "SUCCESS", "event_count": len(provs), "events": prov_types}

            # Verification: AUDIT LOG
            audits = db.query(AuditLog).all()
            audit_actions = [a.action for a in audits]
            assert "UPLOAD" in audit_actions
            assert "HUMAN_REVIEW_SUBMITTED" in audit_actions
            step_results["audit_log_verification"] = {"status": "SUCCESS", "total_audit_events": len(audits)}

            # Save results artifact
            out_path = Path("artifacts/phase8/end_to_end_results.json")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "experiment_id": "phase8_scientific_image_platform_001",
                        "validation_timestamp": datetime.now(timezone.utc).isoformat(),
                        "steps_completed": 20,
                        "overall_status": "SUCCESS",
                        "steps": step_results,
                    },
                    f,
                    indent=2,
                )
    finally:
        db.close()
