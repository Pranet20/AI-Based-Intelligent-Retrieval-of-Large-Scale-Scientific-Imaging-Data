# Platform Architecture & Database Reproducibility Specification

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Document ID:** PLATFORM-REPRO-2026-v1.0  
**Verification Date:** September 2026  

---

## 1. System Overview & Platform Architecture

The SciData Platform converts the frozen Phase 1–7 scientific core into a production-grade web application:
- **Backend Framework:** FastAPI (v0.141.1) running with Uvicorn on Python 3.11.
- **Frontend Framework:** React 18 with TypeScript, Tailwind CSS, and Lucide React icons.
- **Database Engine:** SQLAlchemy ORM with SQLite for unit testing/local development, and PostgreSQL 15+ for multi-user production.
- **Vector Search Engine:** FAISS IndexFlatIP (exact inner product search) and IndexHNSWFlat (approximate nearest neighbors).
- **Security & Authorization:** JWT Bearer authentication with Role-Based Access Control (`ADMIN`, `CURATOR`, `RESEARCHER`).

---

## 2. Database Schema & Tables

The schema is defined in `platform/backend/app/db/models.py` and exported as SQL DDL in `artifacts/phase8/database_schema.sql`.

### 2.1 Core Entities
1. **`users`:** User accounts with bcrypt-hashed passwords and roles.
   - `id` (INTEGER PRIMARY KEY)
   - `username` (VARCHAR(50), UNIQUE, NOT NULL)
   - `email` (VARCHAR(100), UNIQUE, NOT NULL)
   - `hashed_password` (VARCHAR(255), NOT NULL)
   - `role` (VARCHAR(20), DEFAULT 'RESEARCHER')
   - `is_active` (BOOLEAN, DEFAULT TRUE)
   - `created_at` (TIMESTAMP WITH TIME ZONE)

2. **`projects`:** Research groupings and access control boundaries.
   - `id` (INTEGER PRIMARY KEY)
   - `name` (VARCHAR(100), NOT NULL)
   - `description` (TEXT)
   - `created_by` (INTEGER REFERENCES users(id))
   - `created_at` (TIMESTAMP WITH TIME ZONE)

3. **`images`:** Scientific image records with normalized metadata.
   - `id` (INTEGER PRIMARY KEY)
   - `project_id` (INTEGER REFERENCES projects(id))
   - `image_id` (VARCHAR(100), UNIQUE, NOT NULL)
   - `original_filename` (VARCHAR(255), NOT NULL)
   - `storage_path` (VARCHAR(500), NOT NULL)
   - `thumbnail_path` (VARCHAR(500))
   - `sha256_hash` (VARCHAR(64), UNIQUE, NOT NULL)
   - `format` (VARCHAR(20), NOT NULL)
   - `width` (INTEGER), `height` (INTEGER), `channels` (INTEGER)
   - `voltage_kv` (FLOAT), `magnification` (FLOAT), `detector` (VARCHAR(50))
   - `status` (VARCHAR(20), DEFAULT 'ACTIVE')
   - `created_at` (TIMESTAMP WITH TIME ZONE)

4. **`embeddings`:** High-dimensional vector representations.
   - `id` (INTEGER PRIMARY KEY)
   - `image_id` (INTEGER REFERENCES images(id))
   - `model_name` (VARCHAR(50), NOT NULL) — e.g. `dinov2_vits14`, `phase4_adapted`
   - `embedding_dim` (INTEGER, NOT NULL) — 384
   - `vector_data` (BLOB / BYTEA)
   - `l2_normalized` (BOOLEAN, DEFAULT TRUE)
   - `created_at` (TIMESTAMP WITH TIME ZONE)

5. **`curation_records`:** Automated and human curation decisions.
   - `id` (INTEGER PRIMARY KEY)
   - `image_id` (INTEGER REFERENCES images(id))
   - `quality_risk_score` (FLOAT)
   - `novelty_outlier_score` (FLOAT)
   - `redundancy_cluster_id` (INTEGER)
   - `redundancy_role` (VARCHAR(20)) — `CANONICAL_KEEP` vs `REVIEW_DUPLICATE`
   - `human_review_status` (VARCHAR(20), DEFAULT 'PENDING') — `APPROVED`, `FLAGGED`, `REJECTED`
   - `reviewed_by` (INTEGER REFERENCES users(id))
   - `reviewed_at` (TIMESTAMP WITH TIME ZONE)

6. **`audit_logs`:** Append-only cryptographic provenance ledger.
   - `id` (INTEGER PRIMARY KEY)
   - `timestamp` (TIMESTAMP WITH TIME ZONE)
   - `user_id` (INTEGER REFERENCES users(id))
   - `action` (VARCHAR(50), NOT NULL) — `INGEST`, `METADATA_UPDATE`, `CURATION_DECISION`, `LOGIN`
   - `resource_type` (VARCHAR(50), NOT NULL)
   - `resource_id` (INTEGER)
   - `parameters` (JSON)
   - `previous_hash` (VARCHAR(64))

---

## 3. Database Initialization & Migration

### 3.1 SQLite (Local Quick-Start & Testing)
Tables are initialized automatically on startup via SQLAlchemy metadata reflection:
```python
from app.db.models import Base
from app.db.session import engine
Base.metadata.create_all(bind=engine)
```

### 3.2 PostgreSQL Production Initialization
Execute the authoritative SQL DDL:
```bash
psql -U scidata_user -d scidata_platform -f artifacts/phase8/database_schema.sql
```

---

## 4. Authentication & Role-Based Access Control (RBAC)

Three hierarchical roles are strictly enforced via endpoint dependency injection:
- **`ADMIN`:** Full access to user management, system diagnostics, and audit logs.
- **`CURATOR`:** Access to human review queues, triage decisions, and metadata corrections.
- **`RESEARCHER`:** Read access, image search, project creation, and image uploads.

### API Security Endpoints:
- `POST /api/v1/auth/register` — Create user account
- `POST /api/v1/auth/login` — Authenticate and receive signed JWT
- `GET /api/v1/auth/me` — Inspect current session claims

---

## 5. Image Ingestion & 14-Step Processing Pipeline

When an image is submitted via `POST /api/v1/images/upload`:
1. MIME type validation (`.tif`, `.tiff`, `.png`, `.jpg`, `.jpeg`).
2. Payload size check (maximum 50 MB).
3. Compute SHA-256 and perceptual hashes.
4. Exact duplicate check against existing database hashes.
5. Save original file to `platform/storage/originals/<hash>.<ext>`.
6. Generate 224x224 RGB thumbnail in `platform/storage/thumbnails/`.
7. Extract instrument metadata (TIFF tags, EXIF, or sidecar JSON).
8. Compute physical image quality indicators (Laplacian variance, clipping, dynamic range).
9. Evaluate composite quality risk score.
10. Extract 384-d feature vector via frozen DINOv2 engine.
11. Compute L2 normalization on embedding.
12. Add embedding to live FAISS vector index.
13. Populate database records in a single transactional unit.
14. Emit immutable audit log event with operator ID and timestamp.

---

## 6. Vector Similarity Search & Metadata Filtering

- **Endpoint:** `POST /api/v1/search/similarity`
- **Request Parameters:**
  - `query_image_id` OR `query_file`: Input probe
  - `top_k`: Number of results (default 10)
  - `filters`: Optional metadata constraints (`voltage_kv_min`, `voltage_kv_max`, `detector`, `project_id`)
  - `use_adapted_model`: Toggle baseline DINOv2 vs Phase 4 linear projection adapter
- **Execution:**
  1. FAISS returns candidate top-N indices via cosine similarity (IndexFlatIP).
  2. SQL filtering applies metadata constraints and project boundary masks.
  3. Hybrid score fusion applies calibrated confidence ranking.
  4. Response returns ranked items with similarity scores, thumbnails, and metadata attributes.
