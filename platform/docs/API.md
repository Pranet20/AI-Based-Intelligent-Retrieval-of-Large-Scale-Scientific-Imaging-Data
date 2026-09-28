# SciData Platform REST API Specification

The SciData Platform exposes a comprehensive RESTful API under `/api/v1`. Interactive OpenAPI documentation is accessible at `/docs`.

## Authentication & Identity (`/auth`)
- `POST /api/v1/auth/token`: OAuth2 password flow returning JWT access token.
- `GET /api/v1/auth/me`: Retrieve current authenticated user profile and assigned role.

## Project Management (`/projects`)
- `GET /api/v1/projects`: List all accessible research projects with image counts.
- `POST /api/v1/projects`: Register a new scientific project.
- `GET /api/v1/projects/{id}`: Detailed project metadata and summary.

## Micrograph Ingestion & Lifecycle (`/images`)
- `POST /api/v1/images/upload`: Execute the 14-step idempotent ingestion pipeline for scientific images (.png, .tif, .tiff).
- `GET /api/v1/images`: Filterable list of indexed micrographs.
- `GET /api/v1/images/{id}`: Full image profile including metadata, quality indicators, duplicate cascade status, and relative novelty.

## Retrieval & Search (`/search`)
- `POST /api/v1/search/vector`: Exact FAISS `IndexFlatIP` retrieval using 384-D visual embeddings.
- `POST /api/v1/search/hybrid`: Hybrid visual similarity combined with scientific metadata filters (Phase 5 fusion).

## Data Integrity & Curation (`/curation`)
- `GET /api/v1/curation/review-queue`: Prioritized triage queue sorted by composite diagnostic risk.
- `POST /api/v1/curation/reviews`: Submit curator review decision (KEEP, REVIEW_LATER, DUPLICATE, LOW_QUALITY, INTERESTING_NOVEL, INCORRECT_METADATA).
- `GET /api/v1/curation/reviews`: Audit log of completed human reviews.

## Authoritative Models (`/models`)
- `GET /api/v1/models`: List registered models with architecture, dimension, and verified weights SHA-256 hashes.

## Provenance & Auditing (`/provenance`)
- `GET /api/v1/provenance/image/{id}`: Complete cryptographic event history for an image.
- `GET /api/v1/provenance/audit-logs`: Append-only governance audit log.

## System Diagnostics (`/system` & `/health`)
- `GET /api/v1/health`: Liveness and readiness probe with DB and FAISS status.
- `GET /api/v1/version`: Pinned model versions and schema versions.
- `GET /api/v1/dashboard/stats`: Dynamically aggregated database metrics (no hardcoded metrics).
