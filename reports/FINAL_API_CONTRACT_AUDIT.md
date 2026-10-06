# Final API Contract Audit
**Platform**: AI-Powered Scientific Image Data Management Platform  
**Repository**: `Pranet20/AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data`  
**Execution Timestamp**: 2026-09-30  
**Status**: AUDITED & CANONICALIZED (PASS)

---

## 1. Executive Summary
A comprehensive endpoint audit was conducted across FastAPI routers, OpenAPI specifications, frontend API client bindings, and automated tests. All routes strictly adhere to REST conventions under the `/api/v1` namespace with comprehensive Pydantic v2 validation.

---

## 2. Canonical API Route Structure

All API routes are served under the canonical `/api/v1` prefix:

### 2.1. Authentication (`/api/v1/auth`)
- `POST /api/v1/auth/register` — User registration with role assignment (`ADMIN`, `CURATOR`, `RESEARCHER`, `VIEWER`)
- `POST /api/v1/auth/login` — OAuth2-compliant login returning JWT bearer access token
- `GET /api/v1/auth/me` — Protected profile probe for the authenticated subject

### 2.2. Projects (`/api/v1/projects`)
- `GET /api/v1/projects` — List all projects with dynamic image counts
- `POST /api/v1/projects` — Create new research project (authenticated)
- `GET /api/v1/projects/{id}` — Project details and associated image inventory

### 2.3. Images & Ingestion (`/api/v1/images`)
- `GET /api/v1/images` — Paginated list of images filtered by project and status
- `POST /api/v1/images/upload` — Ingestion endpoint (multipart file, microscope metadata, SHA-256 idempotency check)
- `GET /api/v1/images/{id}` — Deep image details (metadata, quality metrics, duplicate profile, novelty)
- `GET /api/v1/images/{id}/file` — Serve original image binary
- `GET /api/v1/images/{id}/thumbnail` — Serve optimized WebP/PNG thumbnail

### 2.4. Visual & Multimodal Retrieval (`/api/v1/search`)
- `POST /api/v1/search/vector` — Visual nearest-neighbor retrieval using DINOv2 / FAISS IndexFlatIP
- `POST /api/v1/search/hybrid` — Calibrated retrieval baseline (alpha=1.0 under frozen baseline)

### 2.5. Curation Workbench (`/api/v1/curation`)
- `GET /api/v1/curation/review-queue` — Diagnostic risk-sorted queue of pending micrographs
- `POST /api/v1/curation/reviews` — Record human curation decision (`KEEP`, `DUPLICATE`, `LOW_QUALITY`, `REVIEW_LATER`, `INTERESTING_NOVEL`, `INCORRECT_METADATA`)
- `GET /api/v1/curation/reviews` — List historical completed review actions

### 2.6. Model Registry (`/api/v1/models`)
- `GET /api/v1/models` — List active models (DINOv2 ViT-S/14 baseline and Phase 4 adapter)
- `GET /api/v1/models/{model_id}` — Model metadata, embedding dimension, weights hash

### 2.7. Provenance & Audit (`/api/v1/provenance`, `/api/v1/admin`)
- `GET /api/v1/provenance/{image_id}` — Complete cryptographic lifecycle history of an image
- `GET /api/v1/admin/audit-logs` — Administrative audit log viewer (RBAC protected: `ADMIN` only)

### 2.8. System & Observability (`/api/v1`)
- `GET /api/v1/health` — Liveness probe (database connectivity, FAISS vector count)
- `GET /api/v1/readiness` — Deep readiness probe (database, storage, model checkpoints, vector index)
- `GET /api/v1/version` — Semantic platform and model versioning metadata
- `GET /api/v1/dashboard/stats` — Live database-derived metrics
- `GET /api/v1/research/dashboard` — Research metrics and dataset counts
- `GET /openapi.json` — OpenAPI 3.0 specification

---

## 3. Client & Contract Validation
- Client request types in `platform/frontend/src/api/` match backend schemas 100%.
- Automated schema validation verifies 0 breaking contract discrepancies.
