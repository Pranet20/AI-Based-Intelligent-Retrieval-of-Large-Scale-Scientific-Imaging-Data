# Scientific Platform Project Structure & Classification Audit

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Status:** COMPLETE & AUDITED  

---

## 1. Classification Categories & Legend

Every file and directory in this research repository is audited and assigned an immutable operational status:

| Tag | Meaning | Handling Policy |
| :--- | :--- | :--- |
| **FROZEN** | Cryptographically verified research artifact (Phases 1–9) | Byte-for-byte immutable; checksum-enforced; never modified. |
| **GENERATED** | Output created by benchmark scripts or build pipelines | Derived automatically from frozen data and deterministic scripts. |
| **REPRODUCIBLE** | Deterministic computational pipeline, test suite, or tool | Runnable end-to-end to recreate evaluation tables or runtime models. |
| **EXTERNAL** | Upstream dependencies, libraries, or third-party datasets | Managed via pinned dependency specifications; not authored in-repo. |
| **NOT REDISTRIBUTABLE** | Proprietary or restricted raw microscopy image files | Quarantined; excluded from git and release packages; manifest only. |
| **DOCUMENTATION ONLY** | Explanatory narrative, manuscript drafts, or architectural specs | Version-controlled text, figures, and protocols for peer review. |

---

## 2. Comprehensive Directory Architecture & Component Breakdown

`	ext
c:/Users/Pranet/Downloads/Mini Project/
├── artifacts/                           [FROZEN / GENERATED] Authoritative experimental outputs and audit logs
│   ├── phase5/                          [FROZEN] Phase 5 metrics, score calibrators, and retrieval tables
│   ├── phase6/                          [FROZEN] Phase 6 duplicate detection, novelty, and quality benchmarks
│   ├── phase7/                          [FROZEN] Phase 7 unified benchmark tables, figures, and metadata
│   ├── phase8/                          [FROZEN] Phase 8 platform test verification and closure checksums
│   ├── phase9/                          [FROZEN] Phase 9 manuscript audit registries and reconciliation records
│   ├── pre_phase9/                      [FROZEN] Pre-Phase 9 gap audits and consistency registries
│   └── phase10/                         [GENERATED / RELEASE] Reproducibility manifests, registries, and scans
├── configs/                             [FROZEN / REPRODUCIBLE] Immutable experiment and dataset specifications
│   ├── datasets.yaml                    [FROZEN] Configuration for 6 microscopy datasets
│   ├── deduplication.yaml               [FROZEN] Thresholds and parameters for duplicate cascade
│   ├── paths.yaml                       [FROZEN] Standard directory path bindings
│   ├── phase2.yaml                      [FROZEN] DINOv2 feature extraction hyperparameters
│   ├── phase3.yaml                      [FROZEN] FAISS vector indexing and search evaluation configuration
│   ├── phase4.yaml                      [FROZEN] Acquisition adaptation contrastive learning hyperparameters
│   ├── phase5.yaml                      [FROZEN] Hybrid metadata fusion grid and calibration weights
│   ├── phase6.yaml                      [FROZEN] Anomaly, duplicate, and quality screening parameters
│   ├── phase7.yaml                      [FROZEN] Statistical evaluation, CI bootstrap, and ablation plan
│   ├── phase7_experiments.yaml          [FROZEN] Unified registry of 18 peer-reviewed research experiments
│   ├── quality.yaml                     [FROZEN] Physical image quality indicator thresholds
│   └── reproducibility.yaml             [FROZEN] Random seed registry and hardware constraints
├── data/                                [EXTERNAL / NOT REDISTRIBUTABLE / FROZEN]
│   ├── raw/                             [EXTERNAL / NOT REDISTRIBUTABLE] Third-party raw microscopy archives
│   │   ├── carinthia/                   [NOT REDISTRIBUTABLE] 4,591 SEM industrial defect images (Zenodo 10715190)
│   │   └── hcci/                        [NOT REDISTRIBUTABLE] 774 physical SEM metallurgy images (Zenodo 21931379)
│   ├── manifests/                       [FROZEN / REPRODUCIBLE] Cryptographically hashed image metadata manifests
│   │   ├── carinthia_manifest.parquet   [FROZEN] Verified manifest for 4,591 Carinthia images
│   │   ├── hcci_manifest.parquet        [FROZEN] Verified manifest for 774 physical HCCI images
│   │   └── hcci_manifest.csv            [FROZEN] Tabular export of HCCI metadata and acquisition conditions
│   ├── processed/                       [FROZEN / GENERATED] Pre-computed features, indices, and checkpoints
│   │   ├── embeddings/                  [FROZEN] Pre-extracted DINOv2 ViT-S/14 embeddings (384-d, L2 normalized)
│   │   ├── indexes/                     [FROZEN] Pre-built FAISS vector indices (IndexFlatIP, IVF, HNSW)
│   │   └── phase4/                      [FROZEN] Linear adapter checkpoints (seed 42, 123, 2024), splits, metrics
│   ├── annotations/                     [FROZEN] Ground truth label mappings and defect taxonomies
│   └── benchmarks/                      [FROZEN] Benchmark evaluation partition definitions
├── platform/                            [REPRODUCIBLE] Production research web application
│   ├── backend/                         [REPRODUCIBLE] FastAPI REST backend application
│   │   ├── app/                         [REPRODUCIBLE] Core API endpoints, ML engines, security, db models
│   │   └── requirements.txt             [REPRODUCIBLE] Backend Python dependencies
│   ├── frontend/                        [REPRODUCIBLE] React 18 / TypeScript / Tailwind web interface
│   │   ├── src/                         [REPRODUCIBLE] Components, pages, state management, API client
│   │   ├── package.json                 [REPRODUCIBLE] NPM dependencies and build scripts
│   │   └── tsconfig.json                [REPRODUCIBLE] TypeScript compilation options
│   ├── docker/                          [REPRODUCIBLE] Multi-stage container definitions
│   │   ├── Dockerfile.backend           [REPRODUCIBLE] Python 3.11 FastAPI container
│   │   ├── Dockerfile.frontend          [REPRODUCIBLE] Multi-stage Node/Nginx frontend container
│   │   └── nginx.conf                   [REPRODUCIBLE] Reverse proxy routing configuration
│   ├── storage/                         [GENERATED] Local runtime storage (indexes, thumbnails, SQLite test db)
│   └── tests/                           [REPRODUCIBLE] Platform integration test suite (28 tests)
├── reports/                             [DOCUMENTATION ONLY / FROZEN] Scientific reports and manuscript deliverables
│   ├── dataset_audit/                   [FROZEN] Phase 1 forensic dataset integrity and count reconciliation
│   ├── figures/                         [FROZEN] Publication-ready vector diagrams and confusion matrices
│   ├── phase2/                          [FROZEN] DINOv2 baseline retrieval benchmark reports and tables
│   ├── phase3/                          [FROZEN] FAISS vector indexing latency and recall trade-off reports
│   ├── phase4/                          [FROZEN] Acquisition adapter training, ablation, and generalization reports
│   ├── phase5/                          [FROZEN] Hybrid metadata fusion benchmark and calibration reports
│   ├── phase6/                          [FROZEN] Multi-track duplicate, anomaly, and quality screening reports
│   ├── phase7/                          [FROZEN] Unified peer-review manuscript benchmark and statistical CIs
│   ├── phase8/                          [FROZEN] Platform integration closure audit and parity verification
│   ├── phase9/                          [FROZEN] Complete 17-part academic publication manuscript package
│   └── phase10/                         [GENERATED] Reproducibility audit, release manifests, and environmental specs
├── scripts/                             [REPRODUCIBLE] Python CLI tools, evaluation runners, and automation
│   ├── data/                            [REPRODUCIBLE] Deterministic dataset download and acquisition helpers
│   ├── validation/                      [REPRODUCIBLE] Dataset, image format, and metadata integrity validators
│   ├── reproduce/                       [REPRODUCIBLE] End-to-end experiment reproduction and smoke-test CLI
│   ├── audit_phase5_data.py             [FROZEN] Phase 5 forensic audit script
│   ├── audit_phase6_data.py             [FROZEN] Phase 6 forensic audit script
│   ├── evaluate_phase4.py               [FROZEN] Phase 4 evaluation pipeline
│   ├── generate_phase2_report.py        [FROZEN] Phase 2 report generator
│   ├── generate_phase3_report.py        [FROZEN] Phase 3 report generator
│   ├── generate_phase4_report.py        [FROZEN] Phase 4 report generator
│   ├── generate_phase5_report.py        [FROZEN] Phase 5 report generator
│   ├── generate_phase6_report.py        [FROZEN] Phase 6 report generator
│   ├── generate_phase7_publication_assets.py [FROZEN] Phase 7 asset and figure generator
│   ├── run_full_audit.py                [FROZEN] Phase 1 integrity audit runner
│   ├── run_phase5.py                    [FROZEN] Phase 5 execution runner
│   ├── run_phase6.py                    [FROZEN] Phase 6 execution runner
│   └── train_phase4.py                  [FROZEN] Phase 4 adapter training script
├── src/                                 [REPRODUCIBLE] Core research Python package (scidata-platform)
│   ├── cli/                             [REPRODUCIBLE] Research CLI entry points
│   ├── core/                            [REPRODUCIBLE] Configuration loaders, loggers, seed controllers
│   ├── data/                            [REPRODUCIBLE] Adapters, loaders, and preprocessing pipelines
│   ├── deduplication/                   [REPRODUCIBLE] Perceptual hash cascades and redundancy graph clustering
│   ├── models/                          [REPRODUCIBLE] DINOv2 wrapper, linear adapter, and projection heads
│   ├── quality/                         [REPRODUCIBLE] Laplacian variance, clipping, and dynamic range metrics
│   ├── search/                          [REPRODUCIBLE] FAISS index builder and exact/ANN similarity search
│   └── utils/                           [REPRODUCIBLE] Metrics calculators, bootstrap CIs, statistical tests
├── tests/                               [REPRODUCIBLE] Research test suite (190 test cases)
├── release/                             [GENERATED] Clean, standalone open-source distribution package
├── .env.example                         [DOCUMENTATION ONLY] Environment variable template
├── docker-compose.yml                   [REPRODUCIBLE] Full platform orchestration definition
├── pyproject.toml                       [REPRODUCIBLE] Python build system, package metadata, and dependencies
├── requirements.txt                     [REPRODUCIBLE] Pinned root Python dependencies
├── requirements-lock.txt                [REPRODUCIBLE] Fully resolved Python environment lockfile
├── environment.yml                      [REPRODUCIBLE] Conda environment specification
├── LICENSE                              [DOCUMENTATION ONLY] Open-source MIT License
├── CITATION.cff                         [DOCUMENTATION ONLY] Machine-readable citation metadata
├── CITATION.md                          [DOCUMENTATION ONLY] Human-readable academic citation guide
├── DATASET_CITATIONS.md                 [DOCUMENTATION ONLY] Formal citations for all external research datasets
├── REPRODUCE.md                         [DOCUMENTATION ONLY] Step-by-step reproduction instructions
└── README.md                            [DOCUMENTATION ONLY] Project overview and getting started guide
`

---

## 3. Component Inventory Table

| Component Path | Primary Role | Assigned Status | Redistribution Policy |
| :--- | :--- | :--- | :--- |
| rtifacts/phase1-7/ | Frozen experimental evidence | FROZEN | Redistributable derived metrics & models |
| rtifacts/phase8/ | Platform closure evidence | FROZEN | Redistributable verification logs |
| rtifacts/phase9/ | Manuscript audit trails | FROZEN | Redistributable documentation |
| configs/ | Experiment parameters | FROZEN | Redistributable open configuration |
| data/raw/ | Microscopy image archives | EXTERNAL | **NOT REDISTRIBUTABLE (Original Source Only)** |
| data/manifests/ | Normalized metadata records | FROZEN | Redistributable research manifests |
| data/processed/embeddings/ | Precomputed vector representations | FROZEN | Redistributable derived scientific features |
| data/processed/checkpoints/ | Trained adapter weights | FROZEN | Redistributable research checkpoints |
| platform/backend/ | Production REST API server | REPRODUCIBLE | Redistributable open source (MIT) |
| platform/frontend/ | Web GUI interface | REPRODUCIBLE | Redistributable open source (MIT) |
| 
eports/phase9/ | Publication manuscript package | FROZEN | Redistributable academic manuscript |
| src/ | Scientific library modules | REPRODUCIBLE | Redistributable open source (MIT) |
| 	ests/ + platform/tests/ | Complete 218-test suite | REPRODUCIBLE | Redistributable test code |
