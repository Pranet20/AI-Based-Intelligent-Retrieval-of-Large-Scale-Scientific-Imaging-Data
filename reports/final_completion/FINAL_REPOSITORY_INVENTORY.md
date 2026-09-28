# Master Final Repository Inventory

**Project**: AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`  
**Distribution**: `release_final/`  
**Audit Date**: 2026-09-28  

---

## 1. Directory Structure & Major Components

```
AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data/
├── .github/
│   └── workflows/ci.yml         # 5/5 Passing GitHub Actions CI/CD Pipeline
├── configs/                     # System, model, and dataset configuration YAMLs
├── data/
│   ├── manifests/               # Dataset metadata manifests (zero raw proprietary images)
│   └── synthetic/               # Synthetic micrographs for automated testing and demo
├── demo/                        # Deterministic demonstration runbooks
├── docs/                        # Model cards, data cards, API references, reproducibility guides
├── platform/
│   ├── backend/                 # FastAPI REST API, SQLAlchemy DB, JWT/RBAC auth, model serving
│   ├── frontend/                # React 18, TypeScript, React Router v6 dashboard
│   ├── docker/                  # Backend & Frontend production Dockerfiles
│   └── tests/                   # Platform end-to-end and security audit tests (14 files)
├── release_final/               # Sealed, reproducible open-source release package (416 files)
├── reports/
│   ├── final_completion/        # Authoritative operational, security, and governance audits
│   └── phase20/                 # IEEE paper package, B.Tech thesis, tables, figures
├── scripts/
│   ├── reproduce/               # Frozen checksum & secret scan validation scripts
│   └── validation/              # Component and database integrity validators
├── src/
│   ├── adaptation/              # Phase 4 SupCon projection & cross-acquisition adaptation
│   ├── cli/                     # Click CLI entry point (`python -m src.cli.main`)
│   ├── datasets/                # Scientific dataset adapters & registry
│   ├── deduplication/           # Exact (MD5) & Perceptual (pHash) redundancy cascade
│   ├── integrity/               # Quality screening, novelty detection, review queue
│   ├── metadata/                # Schema validation & normalizer
│   ├── models/                  # DINOv2 visual backbone & linear projection models
│   ├── quality/                 # Reference-free Tenengrad focus & quality estimators
│   ├── representation/          # Embedding extractors & preprocessors
│   ├── retrieval/               # FAISS HNSW & decoupled inverted index search
│   └── utils/                   # Logging, reproducibility, and versioning utilities
├── tests/                       # Research unit & regression test suite (30 files)
├── CITATION.cff                 # Canonical citation specification
├── docker-compose.yml           # Multi-container orchestration (backend, frontend, postgres)
├── pyproject.toml               # Python packaging, pytest configuration, package metadata
├── requirements.txt             # Pinned core production dependencies
└── README.md                    # Comprehensive repository documentation
```

---

## 2. Component Directory & Function Matrix

| Component | Files / Entry Points | Primary Purpose | Test Coverage |
| :--- | :--- | :--- | :--- |
| **Visual Backbone** | `src/representation/dinov2_encoder.py` | Frozen DINOv2 ViT-S/14 384-d L2 normalized embeddings | `tests/test_phase2_*.py` |
| **Acquisition Adapter**| `src/adaptation/projection_head.py` | Linear projection reducing cross-acquisition gap by 68.15% | `tests/test_phase4_*.py` |
| **Vector Database** | `src/retrieval/faiss_index.py` | FAISS HNSW graph index (ef=128, M=16, latency < 0.32 ms) | `tests/test_phase3_faiss.py` |
| **Metadata Engine** | `src/metadata/schema.py`, `normalizer.py` | Inverted categorical scoping resolving the Metadata Paradox | `tests/test_phase5_*.py` |
| **Integrity Screening**| `src/quality/metrics.py`, `src/deduplication/` | Tenengrad focus gate (AUROC 0.8803) & pHash duplicate cascade | `tests/test_phase6_*.py` |
| **Backend REST API** | `platform/backend/app/main.py` | FastAPI server with JWT, RBAC, Prometheus metrics, audit DAG | `platform/tests/` |
| **Frontend UI** | `platform/frontend/src/App.tsx` | React 18 / TypeScript interactive curation workbench | Compiled in CI |
| **CLI Suite** | `src/cli/main.py` | Command-line administration (`dataset`, `version`, `phase*`) | `tests/test_cli.py` |
| **Canonical Release**| `release_final/` | Clean distribution with 2-pass SHA-256 manifest verification | `final_validate_project.py` |
