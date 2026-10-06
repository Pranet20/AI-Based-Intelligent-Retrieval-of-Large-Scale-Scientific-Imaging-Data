# IEEE Paper Section IV: System Architecture & Implementation
**Target Section**: Section IV. Proposed System Architecture & Section X. Platform Implementation  

---

## IV. SYSTEM ARCHITECTURE & IMPLEMENTATION

The platform is designed around a three-tier, production-ready enterprise microservice architecture deployed via Docker Compose. The architecture isolates compute-intensive vector operations, ensures transactional data persistence, and delivers sub-millisecond query execution through high-speed in-memory indexing.

```
+─────────────────────────────────────────────────────────────────────────────────────────────+
|                                    PRESENTATION LAYER                                       |
|  React 18 SPA (TypeScript + Vite + TailwindCSS)                                              |
|  - Micrograph Canvas Viewer (Zoom/Pan/Aspect Preserved)    - Interactive Curation Queue      |
|  - Real-Time Retrieval Studio with Distance Sliders        - Cryptographic Provenance Trail  |
+──────────────────────────────────────────────┬──────────────────────────────────────────────+
                                               │ HTTP / WebSockets (Port 3000)
                                               ▼
+─────────────────────────────────────────────────────────────────────────────────────────────+
|                                    GATEWAY LAYER                                            |
|  Nginx 1.25 Reverse Proxy & API Gateway                                                      |
|  - Dual-Stack IPv4 / IPv6 Listeners                       - Security Headers (CSP, X-Frame)  |
|  - Token Bucket In-Memory Rate Limiting                   - Gzip Asset Compression           |
|  - Upstream Route Proxying (/api/v1 -> Backend:8000)      - Static Bundle Caching            |
+──────────────────────────────────────────────┬──────────────────────────────────────────────+
                                               │ Internal Network Proxy (Port 8000)
                                               ▼
+─────────────────────────────────────────────────────────────────────────────────────────────+
|                                   APPLICATION LAYER                                         |
|  FastAPI Asynchronous Microservice (Python 3.11, Non-Root appuser UID: 10001)                |
|  ├── Security & Auth Router: OAuth2 Password Bearer, HMAC-SHA256 JWT, Role-Based Access     |
|  ├── Ingestion Engine: Magic Byte Sniffing, 50MB Cap, Streaming Chunkwise SHA-256 Hash       |
|  ├── Metadata Extractor: TIFF Tag / EXIF Parser (Instrument, Voltage, Detector, Mag)        |
|  ├── Quality Risk Engine: Laplacian Variance, SNR Estimation, Contrast Entropy               |
|  ├── Vector Search Router: Top-k Nearest Neighbor Dispatcher, Monotonic Tie-Breaking        |
|  └── Curation & Provenance Engine: Immutable Append-Only Audit Logger, Review Dispatcher     |
+───────────────────────┬──────────────────────────────────────────────┬──────────────────────+
                        │ Synchronous In-Memory                        │ Async Engine Pool (20)
                        ▼                                              ▼
+──────────────────────────────────────────────+ +─────────────────────────────────────────────+
|              DEEP LEARNING & VECTOR          | |              RELATIONAL PERSISTENCE         |
|  - DINOv2-ViT-S/14 (384-d, SHA-256 Verified) | |  PostgreSQL 15.6 Alpine (127.0.0.1:5432)    |
|  - FAISS CPU IndexFlatIP (Cosine Similarity) | |  - Users, Projects, Images, Metadata        |
|  - Offline Model Checkpoint Cache            | |  - Quality Profiles, Embeddings, Reviews    |
|  - Sub-millisecond Execution (<0.25 ms)      | |  - Cryptographic Audit Trail (ACID)         |
+──────────────────────────────────────────────+ +─────────────────────────────────────────────+
```

### A. Ingestion and Integrity Subsystem
The ingestion pipeline enforces multi-layer data validation:
1. **Magic-Byte Sniffing**: Inspects initial 32 bytes to ensure payloads are authentic scientific images (`image/tiff`, `image/png`, `image/jpeg`), discarding disguised binaries with HTTP 415.
2. **Streaming SHA-256 Digestion**: Computes the cryptographic checksum in 64 KB memory chunks ($O(1)$ RAM complexity), immediately querying the PostgreSQL index for duplicate files to ensure idempotent ingestion.
3. **Storage Sanitization**: Files are persisted on disk using server-generated UUID v4 keys to eliminate directory traversal vectors (`../`).

### B. Deep Learning & Vector Search Engine
- **Representation Backbone**: Employs PyTorch Hub DINOv2-ViT-S/14 with patch size 14. Checkpoints are cached locally, allowing execution in air-gapped environments.
- **In-Memory FAISS Index**: Operates an in-memory `IndexFlatIP` populated during startup and dynamically synchronized upon new micrograph ingestion. Exact exhaustive inner product computation guarantees $1.000$ recall without approximate indexing artifacts.

### C. Security and Access Governance
- **Role-Based Access Control (RBAC)**: Enforces four role tiers: `ADMIN` (system configuration, full audit log access), `CURATOR` (review queue execution, merge/reject decisions), `SCIENTIST` (project creation, image ingestion, retrieval), and `VIEWER` (read-only search).
- **Hardened Execution**: The container runs under an unprivileged user (`appuser`, UID 10001). Host database bindings are restricted to localhost loopback (`127.0.0.1:5432`).
