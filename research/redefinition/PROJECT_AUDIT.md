# SCI-INTEL: Complete Repository Architecture & Engineering Audit

**Audit Date**: October 2026  
**Auditor**: Lead Research Engineer, Scientific-Software Architect, and IEEE Research Reproducibility Lead  
**Scope**: Full codebase audit across `platform/backend/`, `platform/frontend/`, `src/`, `data/`, `experiments/`, `reports/`, `artifacts/`, `configs/`, `docker-compose.yml`, and `.github/workflows/`  
**Status**: COMPLETE — PHASE 0 MILESTONE  

---

## 1. Executive Summary

This comprehensive audit evaluates the existing codebase for the project formerly titled *"AI-Based Intelligent Retrieval of Large-Scale Scientific Imaging Data"* and establishes the baseline for its transformation into **SCI-INTEL: Scientific Imaging Intelligence Platform**.

### Key Findings
1. **Strong Functional Foundation**: The core software stack (FastAPI 0.110+, React 18, PostgreSQL 15 / SQLite, FAISS exact index, DINOv2 ViT-S/14 representation) is functional. The test suite currently collects **224 tests with 100% pass rate** (`224 passed in 41.99s`).
2. **Empirical Dataset Inventory on Disk**:
   - **HCCI**: 774 real PNG electron micrographs on disk (with 6 macOS `._` junk files identified and filtered). Accompanied by metadata in `data/raw/hcci/Metadata_All_Samples.xlsx` and `data/manifests/hcci_manifest.csv`.
   - **Carinthia**: 4,591 mineral/rock SEM images in JPEG format on disk, with corresponding manifest in `data/manifests/carinthia_manifest.csv`.
   - **BBBC021**: 721 uncompressed 16-bit multi-channel scientific fluorescence micrographs (Week 10 40111) on disk.
   - **Archives**: Large zip archives present in root (`data.zip` [4.4 GB], `HCCI Dataset .zip` [4.1 GB], `BBBC021.zip` [845 MB], `10715190.zip` [130 MB]).
3. **ML Models & Checkpoints on Disk**:
   - `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` (1.70 MB, SHA-256: `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`)
   - `data/processed/phase4/checkpoints/best_checkpoint_seed123.pt` (3.40 MB)
   - `data/processed/phase4/checkpoints/best_checkpoint_seed2024.pt` (3.40 MB)
   - `platform/storage/indexes/faiss_exact_flatip.index` (Exact inner-product FAISS index for 384-D L2-normalized embeddings)
4. **Primary Architectural Deficits for Publication-Grade Platform**:
   - **Lack of Anomaly Localization**: The system currently provides only global scalar quality metrics and anomaly scores; spatial patch-level attention heatmaps or anomaly bounding are missing.
   - **Absence of Systematic Corrective Action & Evidence Chain**: While quality risks are detected, there is no structured, deterministic rule engine linking detected anomaly $\to$ reference images $\to$ physical cause $\to$ suggested operator corrective actions.
   - **Missing Uncertainty & Abstention Layer**: No calibrated abstention mechanism (Expected Calibration Error [ECE], selective prediction thresholds) exists when the model is uncertain or when an out-of-distribution (OOD) micrograph is presented.
   - **Duplicated Release Trees**: The root contains `release/`, `release_v4/`, and `release_final/`, which clone entire subsets of the backend and reports, increasing maintenance overhead and drift risk.
   - **Historical Metrics vs. Real-Time Verified Metrics**: Several dashboard UI widgets previously displayed frozen historical claims rather than dynamically computed and verified results.

---

## 2. Complete Architecture Map

```
                                  [ SCIENTIFIC MICROGRAPH ]
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │   Ingestion & Preprocessing   │
                             │  (Reader, SHA-256, 16-Bit     │
                             │   Percentile Contrast Stretch)│
                             └───────────────┬───────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │  Scientific Metadata Parser   │
                             │  (EXIF, TIFF Tags, Protocol)  │
                             └───────────────┬───────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │  Foundation Vision Encoder    │
                             │  (DINOv2 ViT-S/14, 384-D)     │
                             └───────────────┬───────────────┘
                                             │
                     ┌───────────────────────┴───────────────────────┐
                     │                                               │
                     ▼                                               ▼
     ┌───────────────────────────────┐               ┌───────────────────────────────┐
     │   Retrieval Subsystem         │               │     Quality Subsystem         │
     │  - Phase 4 Acquisition        │               │  - 6 Physical Indicators      │
     │    Projection Adapter         │               │    (Laplacian, Shannon, etc.) │
     │  - Exact FAISS IndexFlatIP    │               │  - Multi-Stage Duplicate &    │
     │  - Specimen Identity Search   │               │    Redundancy Cascade         │
     │  - Cross-Acquisition Filter   │               │  - Anomaly Screening (Global) │
     └───────────────┬───────────────┘               └───────────────┬───────────────┘
                     │                                               │
                     └───────────────────────┬───────────────────────┘
                                             │
                                             ▼
     ┌───────────────────────────────────────────────────────────────────────────────┐
     │                     NEW SCI-INTEL EXTENSION SUBSYSTEMS                        │
     │  ┌───────────────────────┐ ┌───────────────────────┐ ┌───────────────────────┐│
     │  │ Anomaly Localization  │ │   Evidence & Action   │ │ Uncertainty & OOD     ││
     │  │ (ViT Patch Energy Map)│ │  (Deterministic Rule) │ │ (Selective Abstention)││
     │  └───────────────────────┘ └───────────────────────┘ └───────────────────────┘│
     └───────────────────────────────────────┬───────────────────────────────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │   Platform Storage & API      │
                             │  (FastAPI REST, SQLite/PG,    │
                             │   Audit Logs, Provenance Graph│
                             └───────────────┬───────────────┘
                                             │
                                             ▼
                             ┌───────────────────────────────┐
                             │   Workstation UI (React/TS)   │
                             │  (Bit-by-Bit Inspector,       │
                             │   Dark/Light Tokens, Scientist│
                             │   Review Workspace)           │
                             └───────────────────────────────┘
```

---

## 3. Existing Functionality Map

### 3.1 Backend Application (`platform/backend/app/`)
* **`api/auth.py`**: JWT-based authentication, PBKDF2/bcrypt hashing, login, registration, role checks (`ADMIN`, `CURATOR`, `RESEARCHER`).
* **`api/images.py`**:
  * `POST /api/v1/images/upload`: Micrograph ingestion with 16-bit percentile dynamic range stretching, SHA-256 computation, metadata normalization.
  * `GET /api/v1/images`: Paginated image listing with project filtering.
  * `GET /api/v1/images/{id}`: Full image detail including metadata, quality profile, and duplicate profile.
  * `GET /api/v1/images/{id}/file`: Contrast-stretched display PNG serving (or raw TIFF via `?raw=true`).
  * `GET /api/v1/images/{id}/thumbnail`: On-the-fly thumbnail generation.
  * `GET /api/v1/images/{id}/analysis`: Deep pixel analytics (32-bin intensity histogram, connected-component nuclei counting, 2D FFT spectral energy ring metrics).
  * `GET /api/v1/images/samples/available`: Dynamic catalog of local BBBC021 benchmark micrographs.
  * `POST /api/v1/images/samples/ingest`: 1-click automated sample micrograph ingestion.
* **`api/search.py`**:
  * `POST /api/v1/search/vector`: Exact FAISS inner-product retrieval (top-K cosine similarity).
  * `POST /api/v1/search/hybrid`: Combined vector + structured metadata filtering.
* **`api/models.py`**:
  * `GET /api/v1/models`: Model registry listing.
  * `POST /api/v1/models/extract-features`: Live 384-D vector extraction and $14 \times 14$ ViT patch energy grid generation.
  * `POST /api/v1/models/compare-features`: Real-time cross-micrograph cosine similarity calculation.
* **`api/system.py`**:
  * `GET /api/v1/admin/audit-logs`: Provenance and audit trail inspection.
  * `POST /api/v1/admin/run-diagnostics`: Live subsystem latency benchmark (DB, FAISS, Checkpoint hash, IOPS).
* **`api/curation.py` & `projects.py`**: Review queue, curator decisions (`APPROVE`, `FLAG`, `QUARANTINE`), project scoping.

### 3.2 Machine Learning Modules (`src/` & `platform/backend/app/ml/`)
* **`src/representation/dinov2_encoder.py`**: DINOv2 ViT-S/14 encoder via PyTorch Hub with frozen backbone.
* **`src/adaptation/phase4_model.py` & `projection_head.py`**: Linear projection adapter ($384 \to 384$) with L2 normalization for acquisition-robustness.
* **`src/integrity/quality_indicators.py`**: Six physically grounded microscopy degradation indicators:
  1. Laplacian Variance ($\sigma^2_{\text{Laplacian}}$) for focus/blur.
  2. Edge Density (Sobel mean gradient magnitude).
  3. Shannon Entropy (information richness of pixel distribution).
  4. Dynamic Range ($99^{\text{th}} - 1^{\text{st}}$ percentile spread).
  5. Clipping / Saturation Ratio ($0$ and $255$ pixel fractions).
  6. High-Frequency Spectral Energy Ratio (2D FFT energy above $0.25 \times \text{Nyquist}$).
* **`src/integrity/duplicate_cascade.py`**: 6-stage redundancy cascade (Exact SHA-256, pHash, dHash, embedding cosine, combined threshold).
* **`src/retrieval/faiss_index.py`**: Exact IndexFlatIP FAISS engine for sub-millisecond retrieval.

### 3.3 Database Layer (`platform/backend/app/db/`)
* **Database File**: `platform/storage/scidata_platform.db` (SQLite for local dev/testing) and PostgreSQL support for Docker.
* **Tables (14 active)**:
  - `users`: User identity and RBAC.
  - `images`: Image catalog (ID, SHA-256, path, dimensions, file size).
  - `image_metadata`: Acquisition parameters (microscope, voltage, magnification, detector, pixel size, completeness).
  - `embeddings`: 384-D float vectors with L2 normalization flag.
  - `quality_profiles`: 6 physical indicators and composite risk score.
  - `duplicate_profiles`: Perceptual hashes and match stages.
  - `model_versions`: Model registry metadata and checkpoint hashes.
  - `audit_logs` & `provenance_events`: Immutable action and transformation tracking.
  - `review_items`, `retrieval_queries`, `retrieval_results`, `projects`, `processing_runs`.

---

## 4. File-by-File Status & Action Matrix

| Category | Path / Module | Current Status | Recommended Action |
| :--- | :--- | :--- | :--- |
| **Core Representation** | `src/representation/dinov2_encoder.py` | Active, tested | **Preserve & Wrap** in unified `EmbeddingService` |
| **Acquisition Adapter** | `src/adaptation/phase4_model.py` | Active, tested | **Preserve & Validate** with multi-seed evaluation |
| **Acquisition Checkpoints** | `data/processed/phase4/checkpoints/*.pt` | Active on disk | **Preserve & Verify** against frozen SHA-256 |
| **Quality Engine** | `src/integrity/quality_indicators.py` | Active, updated | **Preserve & Extend** with anomaly categories |
| **Redundancy Cascade** | `src/integrity/duplicate_cascade.py` | Active, tested | **Preserve & Link** to evidence graph |
| **Retrieval Engine** | `src/retrieval/faiss_index.py` | Active, tested | **Preserve & Extend** with quality-aware filters |
| **Backend API** | `platform/backend/app/api/` | Active, verified | **Preserve & Refactor** (add evidence/anomaly endpoints) |
| **Backend Core** | `platform/backend/app/core/config.py` | Active, robust | **Preserve & Decouple** hardcoded paths |
| **Frontend Core** | `platform/frontend/src/` | Active, compiles clean | **Redesign UI** into minimal scientific workstation |
| **Legacy Release Dirs** | `release/`, `release_v4/`, `release_final/` | Stale copies | **Archive** to `research/archive/legacy_releases/` |
| **Outdated Scripts** | `scripts/phase16/` through `phase20/` | One-off scripts | **Archive** to `research/archive/historical_scripts/` |
| **Unverified Reports** | Historical Phase 10-13 markdown reports | Static claims | **Reconcile** against rerun experimental artifacts |

---

## 5. Technical Debt & Deficit Inventory

1. **Hardcoded Metric Displays in UI**:
   - `platform/frontend/src/pages/Dashboard.tsx` previously contained hardcoded historical metric strings (`94.81%`, `68.15%`, `0.096 ms`) rather than fetching them dynamically from the backend research registry.
2. **Path Dependency & Portability**:
   - Several utility scripts in `scripts/reproduce/` assume absolute Windows paths (`C:\Users\Pranet\...`) rather than resolving paths dynamically relative to repository root or `configs/paths.yaml`.
3. **Redundant Code Trees**:
   - The repository currently contains three duplicate release trees: `release/`, `release_v4/`, and `release_final/`. Each contains duplicate copies of backend and reports. These must be archived to ensure a single source of truth in `platform/` and `src/`.
4. **Missing Scientific Intelligence Features**:
   - **Patch-Level Spatial Anomaly Localization**: The quality engine scores images globally, but cannot yet render an overlay heatmap highlighting *where* high-frequency loss or clipping occurs.
   - **Deterministic Corrective Action Engine**: The platform lacks a formal recommendation rule engine that maps detected degradation patterns $\to$ microscopy instrument causes $\to$ actionable operator procedures.
   - **Uncertainty & Abstention Calibration**: The system forces a decision on all micrographs rather than offering an `"UNCERTAIN — HUMAN REVIEW REQUIRED"` abstention pathway based on prediction confidence and OOD distance.
5. **Database Driver Edge Cases**:
   - FastAPI backend uses SQLite locally and PostgreSQL in Docker. Differences in JSON column querying must remain insulated through the SQLAlchemy ORM layer.

---

## 6. Audit Verdict

* **Engineering Infrastructure**: **HEALTHY & READY**. All 224 unit/integration tests pass, Docker configurations are present, and API endpoints are responsive.
* **Scientific Readiness**: **REQUIRES REDEFINITION & RE-EXECUTION**. Historical numbers in reports must be cleanly separated from reproducible experimental runs.
* **Next Immediate Step**: Proceed with **DATASET_INVENTORY.md**, **EXPERIMENT_INVENTORY.md**, **MODEL_INVENTORY.md**, **RESULTS_PROVENANCE.md**, **TECHNICAL_DEBT.md**, **MIGRATION_PLAN.md**, and **PROJECT_REDEFINITION.md**.
