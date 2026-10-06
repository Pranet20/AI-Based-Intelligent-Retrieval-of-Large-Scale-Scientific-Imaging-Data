# IEEE Manuscript Figures Specification & Reproduction Map
**Target Manuscript**: Complete Figure Suite (Figures 1 – 8)  
**Storage Directories**: `paper/figures/` and `paper/scripts/`  

---

## 1. Figure Portfolio Overview

```
FIGURE 1: End-to-End Scientific Platform Architecture (Three-Tier Enterprise Topology)
FIGURE 2: Multi-Stage Cryptographic Scientific Ingestion & Feature Pipeline
FIGURE 3: DINOv2 Latent Representation Space & In-Memory FAISS Vector Retrieval
FIGURE 4: Acquisition-Geometry Robustness: The Cross-Acquisition Similarity Gap & Mitigation
FIGURE 5: Visual vs Metadata Retrieval: PR Curves & Late Fusion Alpha Grid Evaluation
FIGURE 6: Archival Hygiene: Quality-Risk Screening, Redundancy Graph, and Novelty Triage
FIGURE 7: Human-in-the-Loop Curation Workbench & Cryptographic Provenance Trail
FIGURE 8: Multi-Container Production Docker Deployment Topology
```

---

## 2. Detailed Figure Specifications

### FIGURE 1: Overall System Architecture
- **Type**: Architectural Flowchart Diagram (Vector / Mermaid / TikZ)
- **Content**: Illustrates interaction between the React 18 client, Nginx reverse proxy gateway, FastAPI backend microservices, FAISS vector index, and PostgreSQL ACID storage.
- **Source Specification**: `paper/SYSTEM_ARCHITECTURE.md`

### FIGURE 2: Scientific Image Ingestion Pipeline
- **Type**: Process Pipeline Diagram
- **Content**: Step-by-step depiction of multipart upload, magic byte MIME sniffing, chunked streaming SHA-256 computation, metadata parsing, DINOv2 inference, quality-risk profiling, and atomic index commit.
- **Source Specification**: `reports/FINAL_INGESTION_AUDIT.md`

### FIGURE 3: DINOv2 + FAISS Retrieval Architecture
- **Type**: Latent Space Embedding Projection & Retrieval Schematic
- **Content**: Depicts patch extraction ($14 \times 14$), self-attention transformer forward pass, L2 hypersphere normalization, and sub-millisecond inner-product search in `IndexFlatIP`.
- **Source Data**: `reports/phase2/` evaluation logs

### FIGURE 4: Acquisition-Geometry Evaluation
- **Type**: Empirical Scatter / Bar Chart
- **Content**: Shows cosine similarity distributions across varied tilt angles ($0^\circ, 15^\circ, 30^\circ, 45^\circ$) before and after affine projection alignment, illustrating the 42.3% similarity gap reduction.
- **Source Data**: `reports/phase4/figures/pca_phase2_vs_phase4.png` and `reports/phase4/figures/retrieval_comparison.png`

### FIGURE 5: Metadata vs Visual Retrieval Comparison
- **Type**: Precision-Recall & Alpha Grid Search Curves
- **Content**: Dual-panel plot: (a) Precision-Recall curves comparing Visual Baseline (AUC=0.9658) against Metadata-Only (AUC=0.3443); (b) Late fusion validation grid search demonstrating optimal convergence at $\alpha^* = 1.0$.
- **Source Data**: `reports/phase5/figures/fig3_validation_alpha_grid.png` and `reports/phase5/figures/fig4_methods_comparison.png`

### FIGURE 6: Quality-Risk & Redundancy Workflow
- **Type**: Multi-Panel Triage Diagnostic Plot
- **Content**: (a) ROC curve for image-derived quality-risk screening ($\text{AUROC} = 0.8803$); (b) Precision-Recall curve for duplicate screening ($F_1 = 0.9810$); (c) Redundancy graph component distribution ($764$ singletons, $5$ pairs).
- **Source Data**: `reports/phase6/figures/fig2_synthetic_duplicate_roc.png` and `reports/phase6/figures/fig3_redundancy_graph_components.png`

### FIGURE 7: Platform UI & Curation Workflow
- **Type**: Micrograph Triage Interface Screen Capture
- **Content**: Side-by-side duplicate diff viewer, interactive quality badge visualizer, and curator decision recording modal (`KEEP`, `MERGE`, `REJECT`).
- **Source Data**: `platform/frontend/src/` component mockups and live UI render

### FIGURE 8: End-to-End Deployment Architecture
- **Type**: Production Network & Container Topology Diagram
- **Content**: Multi-container Docker Compose layout showing isolated bridge network, port bindings (`127.0.0.1:5432`, `8000`, `3000`), non-root security boundaries, and persistent named volumes.
- **Source Specification**: `docker-compose.yml` and `reports/FINAL_DOCKER_RUNTIME_VALIDATION.md`
