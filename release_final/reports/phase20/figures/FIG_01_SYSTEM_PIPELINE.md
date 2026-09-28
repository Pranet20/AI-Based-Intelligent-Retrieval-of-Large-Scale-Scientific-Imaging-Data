# Figure 1: End-to-End Scientific Image Platform Architecture

**Caption**: Architectural block diagram showing ingestion provenance, quality screening, DINOv2 feature extraction, HNSW indexing, decoupled metadata filtering, and curation triage.

**Figure Type**: Mermaid Flowchart

```mermaid
graph TD
    A[Raw Micrograph Ingestion] --> B[Cryptographic SHA-256 & Audit Trail]
    A --> C[Tenengrad Focus Screening]
    A --> D[DINOv2 ViT-S/14 Feature Extraction 384-d]
    D --> E[FAISS HNSW Vector Index]
    B --> F[Relational Metadata Store]
    F --> G[Decoupled Inverted Index]
    E --> H[Hybrid Query Engine]
    G --> H
    H --> I[Latent Distance Screening D_ref]
    I --> J[Human Curator Active Queue]
```
