# SciData Platform Architecture Specification

## 1. System Overview
SciData Platform is a production-grade research data management platform specifically engineered for scientific microscopy images. It integrates foundational visual representations, acquisition-aware metric learning, image-derived quality risk profiling, multi-stage deduplication cascades, exact vector retrieval, and human-in-the-loop curation review queues.

## 2. Layered Architecture

```
+-----------------------------------------------------------------------+
|                    Client Layer (React + TypeScript)                 |
|   Dashboard | Projects | Ingestion | Retrieval | Curation | Review   |
+-----------------------------------------------------------------------+
                                  |
                                  v
+-----------------------------------------------------------------------+
|                    API Gateway (FastAPI / REST / OpenAPI)             |
|   /auth | /projects | /images | /search | /curation | /models | /sys |
+-----------------------------------------------------------------------+
        |                    |                        |
        v                    v                        v
+---------------+    +-------------------+    +-------------------------+
| Relational DB |    | Immutable Storage |    | ML Retrieval & Analysis |
| PostgreSQL    |    | Originals / Thumbs|    | Exact FAISS IndexFlatIP |
| (14 Tables)   |    | Append-Only Blobs |    | DINOv2 ViT-S/14 (384-D) |
| SQLAlchemy ORM|    | SHA-256 Adherence |    | Phase 4 Linear Adapter  |
+---------------+    +-------------------+    +-------------------------+
```

## 3. Core Modules
- **`app.api`**: Modular REST endpoints with JWT role-based access control (ADMIN, RESEARCHER, REVIEWER).
- **`app.core`**: Security hashing, token verification, and immutable configuration settings.
- **`app.db`**: Relational models mapped to PostgreSQL schema (`artifacts/phase8/database_schema.sql`).
- **`app.ml`**: Encapsulated singleton ML engines:
  - `ModelRegistryService`: Cryptographic startup hash verification.
  - `DINOv2Engine`: Official Meta DINOv2 ViT-S/14 feature extraction (384-D L2 normalized).
  - `Phase4Engine`: Acquisition-aware linear projection adapter ($384 \to 384$).
  - `FAISSEngine`: Exact `IndexFlatIP` inner-product vector indexing and search.
  - `QualityEngine`: 6-indicator physical quality risk profiling.
  - `DuplicateEngine`: 6-stage duplicate detection cascade.
  - `NoveltyEngine`: Relative embedding-space novelty via k-NN distance.
- **`app.services`**:
  - `IngestionService`: Idempotent 14-step ingestion pipeline.
  - `ProvenanceService`: Cryptographic hash auditing and event logging.
  - `AuditService`: Append-only governance audit log.
