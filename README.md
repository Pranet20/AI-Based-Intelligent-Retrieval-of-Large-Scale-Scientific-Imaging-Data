# AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images (SCI-INTEL)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![Tests: 479 Passed](https://img.shields.io/badge/Tests-479%20Passed-brightgreen.svg)]()
[![Frozen Records: 128/128 Verified](https://img.shields.io/badge/Frozen%20Records-128%2F128%20Verified-blue.svg)](reports/final_audit/FINAL_HISTORICAL_IMMUTABILITY_REPORT.md)
[![Status: Ready For Paper Writing](https://img.shields.io/badge/Status-READY__FOR__PAPER__WRITING-brightgreen.svg)](artifacts/final/FINAL_APPLICATION_RELEASE_REPORT.md)
[![IEEE Paper Package](https://img.shields.io/badge/IEEE%20Paper%20Package-Complete-blue.svg)](paper/)

> **Full Project Title:** AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images  
> **Platform Name:** SCI-INTEL — Scientific Imaging Intelligence Platform  
> **Repository Owner:** Pranet20  
> **Current Platform Gate:** `READY_FOR_PAPER_WRITING`  
> **Final Release Report:** [artifacts/final/FINAL_APPLICATION_RELEASE_REPORT.md](artifacts/final/FINAL_APPLICATION_RELEASE_REPORT.md) | **Evidence Summary:** [artifacts/final/research_evidence_summary.json](artifacts/final/research_evidence_summary.json)

---

## 1. Overview & Research Motivation

Scientific imaging repositories—particularly Scanning Electron Microscopy (SEM), Transmission Electron Microscopy (TEM), and High-Content Automated Fluorescence Imaging—face four fundamental data curation challenges:
1. **Instrument Acquisition Bias:** Cross-instrument and cross-session variations (accelerating voltage, dwell time, detector sensor, optical gain) dominate naive visual distance metrics, causing identical specimen morphology captured under differing conditions to diverge in representation space.
2. **Metadata Decoupling & Incompleteness:** Critical optical and instrument parameters are frequently omitted, inconsistent, or stripped during data publication.
3. **Unindexed Data Redundancy & Quality Degradation:** Repositories accumulate unindexed near-duplicate captures, out-of-focus micrographs, dynamic range truncation, and saturation defects without automated computational screening.
4. **Lack of Grounded Interpretability:** Automated triage models typically issue black-box verdicts without actionable, parameter-mapped recommendations for microscope operators or scientific curators.

The **SCI-INTEL** platform provides an end-to-end, publication-grade scientific imaging intelligence system that resolves these challenges through:
- Self-supervised foundation vision representations (DINOv2 ViT-S/14).
- Supervised contrastive acquisition adaptation (Phase 4 linear projection adapter).
- Transparent computational image-derived quality screening (focus variance, entropy, saturation, clipping).
- Patch-level spatial localization of model-derived suspicious regions.
- Grounded comparable reference evidence retrieval ($N=55$ cohort context).
- Deterministic, parameter-targeted corrective action recommendations.
- Principled entropy- and margin-based uncertainty abstention gates.
- An interactive, scientist-facing web workbench with cryptographic provenance and audit logging.

---

## 2. Core Research Questions (RQ1–RQ5)

The scientific foundation and experimental validation of SCI-INTEL are structured around five core research questions:

- **RQ1 (Acquisition-Robust Retrieval — Protocol M vs. Protocol U):** Can supervised contrastive acquisition adaptation compress the cross-instrument embedding gap under Unmatched Acquisition conditions (Protocol U) without degrading fine-grained intra-acquisition discriminability under Matched Acquisition conditions (Protocol M)?
- **RQ2 (Computational Quality-Risk Screening):** Can transparent image-derived quality indicators (Laplacian focus variance, saturation/dark clipping, Shannon entropy, dynamic range) reliably flag compromised micrographs without relying on proprietary microscope hardware telemetry?
- **RQ3 (Spatial Localization & Principled Uncertainty Abstention):** Can model-derived suspicious region localization combined with entropy- and margin-based uncertainty estimation identify corrupted regions and trigger reliable automated abstention?
- **RQ4 (Grounded Evidence Retrieval & Suggested Corrective Action):** Does retrieving comparable cross-acquisition reference micrographs ($N=55$ cohort context) enable deterministic mapping to actionable microscope operational parameter adjustments?
- **RQ5 (Human-in-the-Loop Scientific Curation):** Does integrating quality-risk triage, localization overlays, and grounded evidence into a unified curation workbench reduce human inspection fatigue while preserving scientific data integrity?

---

## 3. Key Scientific Findings & Benchmark Results

All numerical results below are cryptographically frozen, independently audited, and verified across all project phases:

| Research Question | Metric / Evaluation Protocol | Baseline / Prior | Platform Result | Statistical Significance / Population |
| :--- | :--- | :--- | :--- | :--- |
| **RQ1: Foundation Retrieval Baseline** | HCCI Recall@1 (Visual Baseline) | `0.0210` (pHash) | **`0.9819`** (DINOv2) | Full corpus ($N=774$) |
| **RQ1: Protocol U (Cross-Acquisition Gap)** | Mean Cross-Condition Embedding Gap | `0.2016` (Unadapted) | **`0.0681`** (Adapted) | **`66.23%` Gap Reduction** ($p = 5.03 \times 10^{-36}$, $d_z = 2.19$, $N=55$) |
| **RQ1: Protocol M (Matched Acquisition)** | Intra-Instrument Discriminability | `1.0000` | **`1.0000`** | Preserved discriminability without performance degradation |
| **RQ1: Held-out Test Transfer** | Held-out Zeiss P@5 | `0.8708` (Baseline) | **`0.9053`** (Adapted) | Paired $t$-test: $p = 0.0028$, Cohen's $d = 0.65$ |
| **RQ2: Quality Degradation Screening** | Image-Derived Quality Risk AUROC | N/A | **`0.8803`** | Controlled benchmark ($N=120$), AUPRC = `0.9618` |
| **RQ2: Multi-Stage Redundancy Screening** | Synthetic Duplicate AUROC | N/A | **`0.9998`** | False Positive Rate = `0.0000` |
| **RQ3: Suspicious Region Localization** | Spatial Saliency Threshold | N/A | **`0.50` Saliency** | Strictly bounded as *Model-Derived Suspicious Region* |
| **RQ3: Principled Abstention Gate** | Abstention Trigger Criteria | N/A | **Conf < 0.45 or Entropy > 0.85** | Principled deferral to human specialist review |
| **RQ4: Grounded Evidence Retrieval** | Comparable Micrograph Cohort | N/A | **$N=55$ Cohort** | Cross-acquisition & same-specimen peers retrieved |
| **RQ4: Deterministic Action Mapping** | Corrective Recommendation Mapping | N/A | **100% Deterministic** | 10 mapped categories to microscope parameter targets |
| **Platform: Query Retrieval Latency** | End-to-End REST Search Latency | IndexFlatIP: 0.73 ms | **Mean `23.40 ms`** (P95 `28.30 ms`) | Complete REST API pipeline across $N=55$ cohort |
| **Platform: Vector Index Acceleration** | FAISS HNSW vs IndexFlatIP Speedup | 0.73 ms / query | **0.37 ms / query** | **`1.99x` Speedup** ($100\%$ Recall@10) |

---

## 4. Platform Architecture & Repository Structure

```text
├── artifacts/
│   └── final/           # Master application release report, evidence summary, and seal
├── configs/             # Immutable YAML experiment and dataset specifications
├── data/
│   ├── manifests/       # Normalized Parquet/CSV image metadata manifests
│   ├── processed/       # Pre-extracted DINOv2 embeddings, FAISS indices, checkpoints
│   └── raw/             # Third-party microscopy imagery (local only; not redistributed)
├── platform/
│   ├── backend/         # FastAPI REST API (JWT/RBAC, Ingestion, Curation, Evidence)
│   │   └── app/
│   │       ├── api/     # Endpoints: auth, images, search, curation, provenance, admin
│   │       ├── core/    # Security, configuration, role-based access control
│   │       ├── db/      # SQLAlchemy ORM models, migrations, and database session
│   │       ├── ml/      # FAISS vector index, DINOv2 loader, Phase 4 adapter engine
│   │       └── services/# Ingestion, audit logging, provenance graph builder
│   ├── frontend/        # React 18 / TypeScript interactive web user interface
│   │   └── src/
│   │       ├── api/     # Typed API client with response normalization
│   │       ├── components/ # Micrograph viewers, HUD overlays, charts, layout
│   │       └── pages/   # Dashboard, Search, Explorer, ImageDetail, Workbench, Admin
│   ├── docker/          # Multi-stage Docker container definitions & compose stacks
│   ├── storage/         # Local runtime data storage and SQLite/PostgreSQL models
│   └── tests/           # 55 platform integration, API, security, and lifecycle tests
├── reports/             # Comprehensive phase audit reports and IEEE submission package
├── scripts/
│   ├── data/            # Deterministic dataset acquisition scripts
│   ├── validation/      # Dataset schema and image file integrity validators
│   └── reproduce/       # One-command reproduction CLI and benchmark runners
├── src/                 # Reusable Python research library (`scidata-platform`)
│   ├── evidence/        # Quality-risk engine, localization, evidence retrieval, explanation
│   ├── ingestion/       # Scientific TIFF/PNG/JPEG reader and metadata normalizer
│   └── quality/         # Handcrafted pixel-level focus, dynamic range, and entropy metrics
└── tests/               # 424 unit, regression, and historical freeze tests
```

---

## 5. Quick Start & Execution

### 5.1 Docker Compose Deployment (Recommended)
The multi-container stack runs PostgreSQL 15, the FastAPI backend, and the React frontend via Nginx reverse proxy:
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Build and launch services in background
docker compose up -d

# 3. Verify container health status (all 3 healthy)
docker compose ps
```
- **Web User Interface**: `http://localhost:3000`
- **Interactive OpenAPI / Swagger**: `http://localhost:8000/docs`
- **Liveness Health Check**: `http://localhost:8000/api/v1/health`
- **Deep Readiness Probe**: `http://localhost:8000/api/v1/readiness`

### 5.2 Local Development Environment (Python 3.11 & Node.js)
```bash
# Python 3.11 virtual environment setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -e .

# Launch Backend
python scripts/run_backend.py
# (Runs on http://127.0.0.1:8000)

# Launch Frontend (in a separate terminal)
cd platform/frontend
npm install
npm start
# (Runs on http://localhost:3000)
```

### 5.3 Automated Verification & Test Suite Execution
The repository includes a comprehensive, verified 479-test automated test suite:
- **Research Test Suite:** 424 passed tests (`pytest tests/`)
- **Platform & Integration Suite:** 55 passed tests (`pytest platform/tests/`)
- **Combined Total:** 479 passed / 0 failed / 0 skipped

```bash
# Verify all 128 frozen research checksums (immutability check)
python scripts/reproduce/final_validate_project.py --verify-only

# Run platform test suite (55 tests)
pytest platform/tests/ -v

# Run canonical 17-stage scientific workflow test
pytest platform/tests/test_canonical_scientific_flow.py -v

# Run full research test suite (424 tests)
pytest tests/ -v

# Run combined 479-test suite
pytest tests/ platform/tests/ -q

# Test production frontend build
cd platform/frontend && npm run build
```

> **Note on Test Count Reconciliation:** Early Phase 8 project reporting documented a 218-test baseline (190 research + 28 platform tests). Subsequent implementation of Phase 5 (evidence and explanation engines), Phase 6 (integrated scientific evaluation), Phase 7–9 (closure audits), and Phase 10 (platform closure and canonical end-to-end integration tests) expanded the verified test suite to 479 passed tests.

---

## 6. End-to-End Scientific Curation Workflow

The platform implements the complete 17-stage scientific imaging curation workflow:
1. **AUTHENTICATE (LOGIN):** JWT/RBAC secure access with granular roles (`ADMIN`, `CURATOR`, `RESEARCHER`).
2. **INGEST & UPLOAD:** Multi-format ingestion supporting 16-bit uncompressed TIFF, PNG, and JPEG.
3. **VALIDATE & STORE:** MIME validation, dimension extraction, and SHA-256 cryptographic hashing.
4. **METADATA EXTRACTION:** Extraction of microscope model, detector sensor, accelerating voltage, magnification, and completeness scores.
5. **REPRESENTATION EXTRACTION:** Foundation embedding extraction via frozen DINOv2 ViT-S/14 (384-d).
6. **QUALITY-RISK SCREENING:** Automated calculation of Laplacian focus variance, Shannon entropy, dynamic range, clipping ratios, and composite risk scoring.
7. **SPATIAL LOCALIZATION:** Multi-scale patch-level anomaly saliency mapping with model-derived suspicious region envelopes.
8. **SIMILARITY RETRIEVAL:** Vector search with explicit representation selection (DINOv2 vs. Phase 4 Acquisition-Adapted).
9. **EVIDENCE RETRIEVAL:** Retrieval of comparable reference gallery peers demonstrating same-specimen or cross-acquisition visual comparison ($N=55$ cohort context).
10. **EXPLANATION GENERATION:** Structured explanation breakdown without unsupported causal assertions.
11. **SUGGESTED CORRECTIVE ACTION:** Deterministic mapping to operational microscopy parameter adjustments (`beam_current`, `dwell_time`, `stigmation`, `gain`).
12. **UNCERTAINTY & ABSTENTION:** Entropy- and margin-based uncertainty evaluation with automated abstention gates for high-uncertainty captures.
13. **HUMAN SPECIALIST REVIEW:** Active curation queue sorting captures by risk and novelty for domain expert inspection.
14. **CURATION DECISION:** Recording expert decisions (`KEEP`, `REVIEW_LATER`, `DUPLICATE`, `LOW_QUALITY`) with review notes.
15. **SECURITY AUDIT LOGGING:** Immutable database logging of all curation actions, parameters, and user IDs.
16. **PROVENANCE GRAPH TRACKING:** Bidirectional cryptographic provenance recording parentage, transformations, and model checkpoints.
17. **EXPORT & AUDIT:** One-click export of complete scientific curation packages and cryptographic verification seals.

---

## 7. Data Redistribution & Rights Governance

This project adheres strictly to scientific research ethics and data rights:
- **Raw Images:** Not redistributed in release packages. Users acquire raw data directly from official public depositors (e.g., Broad Bioimage Benchmark Collection BBBC021).
- **Derived Features:** Vector embeddings, normalized cryptographic manifests, and trained adapter checkpoints are open and fully reproducible.

---

## 8. License & Citation

- **Software License:** [MIT License](LICENSE) (see [SOFTWARE_LICENSE.md](reports/phase10/SOFTWARE_LICENSE.md)).
- **Citation:** Please cite this software and associated research using [CITATION.cff](CITATION.cff) or [CITATION.md](CITATION.md).
- **Dataset Attribution:** When utilizing external datasets, cite the original depositors as documented in [DATASET_CITATIONS.md](DATASET_CITATIONS.md).
