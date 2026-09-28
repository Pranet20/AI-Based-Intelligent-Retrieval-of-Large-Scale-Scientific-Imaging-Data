# MASTER API REFERENCE (VERSION 4.0.0)

**Base URL**: `http://127.0.0.1:8000/api/v1`  
**OpenAPI Specification**: `http://127.0.0.1:8000/docs`  

---

## 1. Authentication Endpoints
- `POST /auth/token`: OAuth2 password flow; returns HMAC-SHA256 JWT bearer token.
- `GET /auth/me`: Returns current authenticated user profile and assigned RBAC role.

## 2. Ingestion & Image Management
- `POST /images/upload`: Ingest micrograph (TIFF/PNG), compute SHA-256 digest, extract metadata tags.
- `GET /images/{image_id}`: Retrieve micrograph metadata, focus score, and storage URI.
- `GET /images/{image_id}/file`: Download raw micrograph bytes (subject to access control).

## 3. Vector Similarity & Retrieval
- `POST /retrieval/search`: Search Top-$K$ visually similar micrographs via FAISS HNSW.
  - Request: `{"image_id": 123, "top_k": 5, "filter_detector": "BSE", "filter_voltage_min": 15.0}`
  - Response: `{"query_id": 123, "latency_ms": 0.12, "candidates": [{"image_id": 456, "score": 0.9481}]}`

## 4. Quality & Integrity Screening
- `POST /quality/evaluate`: Compute Tenengrad gradient energy and dynamic range indicators.
- `POST /deduplication/check`: Run perceptual hash and cosine matching cascade.

## 5. Curation Workbench & Provenance
- `GET /curation/queue`: Retrieve triage queue of flagged low-quality or novel specimens.
- `POST /curation/review`: Submit curator decision (`KEEP`, `REVIEW_LATER`, `DUPLICATE`, `LOW_QUALITY`, `INTERESTING_NOVEL`).
- `GET /provenance/{image_id}`: Retrieve immutable DAG lineage events for micrograph.
