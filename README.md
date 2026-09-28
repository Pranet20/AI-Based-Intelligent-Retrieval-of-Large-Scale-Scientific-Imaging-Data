# AI-Powered Scientific Image Data Management Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3119/)
[![Tests: 218 Passed](https://img.shields.io/badge/Tests-218%20Passed-brightgreen.svg)]()
[![Frozen Records: 128/128 Verified](https://img.shields.io/badge/Frozen%20Records-128%2F128%20Verified-blue.svg)](file:///reports/final_audit/FINAL_HISTORICAL_IMMUTABILITY_REPORT.md)
[![Status: Final Audit](https://img.shields.io/badge/Status-PROJECT__FINALIZED__WITH__LIMITATIONS-blue.svg)](file:///reports/final_audit/FINAL_PROJECT_COMPLETION_REPORT.md)

> **Full Project Title:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
> **Final Authorized Status:** `PROJECT_FINALIZED_WITH_LIMITATIONS`  
> **Master Final Release:** [release_final/](file:///release_final/) | **Final Audit Suite:** [reports/final_audit/](file:///reports/final_audit/)

---

## 1. Overview & Research Motivation

Scientific imaging repositories—particularly Scanning Electron Microscopy (SEM) and Transmission Electron Microscopy (TEM)—face critical challenges:
1. **Instrument Acquisition Bias:** Cross-instrument variability (accelerating voltage, beam current, detector type) dominates standard visual distance metrics, causing identical physical specimens to appear dissimilar.
2. **Metadata Decoupling:** Crucial physical parameters are stripped or unstandardized during publication.
3. **Data Redundancy & Degradation:** Repositories accumulate unindexed near-duplicate micrographs, saturated exposures, or out-of-focus captures without automated quality screening.

This platform introduces an integrated, publication-grade scientific data management system combining self-supervised foundation vision features (DINOv2), supervised contrastive acquisition adaptation, multi-stage duplicate and anomaly curation, and production REST API search services.

---

## 2. Research Questions (RQ1–RQ7)

- **RQ1 (Foundation Baseline):** How effectively do frozen self-supervised foundation models (DINOv2) perform on domain-specific scientific microscopy retrieval compared to classical hashing baselines?
- **RQ2 (Acquisition Invariance):** Can a linear projection adapter trained with supervised contrastive loss compress the acquisition-induced embedding gap across differing electron microscopy operating conditions?
- **RQ3 (Metadata Fusion):** Does late fusion of normalized instrument metadata with deep visual features improve retrieval performance over vision alone?
- **RQ4 (Duplicate & Quality Screening):** Can a multi-stage perceptual hash cascade and image-derived quality indicators reliably identify redundant and degraded micrographs?
- **RQ5 (Outlier & Novelty Detection):** Can statistical and representation-based novelty estimators detect out-of-distribution defects and cross-corpus domain shifts?
- **RQ6 (Triage & Curation):** Does an automated composite-risk review queue accelerate expert human curation of problematic micrographs?
- **RQ7 (Platform Integration & Reproducibility):** Can the complete research pipeline be unified into a production-grade, reproducible web platform with cryptographic traceability?

---

## 3. Key Scientific Findings & Benchmark Results

| Experiment | Metric / Phenomenon | Baseline / Prior | Platform Result | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- |
| **RQ1: Foundation Retrieval** | HCCI Recall@1 | `0.0210` (pHash) | **`0.9819`** (DINOv2) | Full corpus ($N=774$) |
| **RQ2: Acquisition Adaptation**| Cross-Condition Gap | `0.1994` (Gap) | **`0.0635`** (Gap) | **`68.15%` Gap Reduction** ($p = 1.42 \times 10^{-12}$) |
| **RQ2: Held-out Test Transfer**| Held-out Zeiss P@5 | `0.8708` (Baseline)| **`0.9053`** (Adapted) | Paired $t$-test: $p = 0.0028$, Cohen's $d = 0.65$ |
| **RQ3: Hybrid Metadata** | Metadata-Only MRR | N/A | **`0.3443`** | Held-out test ($N=212$) |
| **RQ3: Late Fusion Delta** | $\Delta$ Recall@1 | N/A | **`0.0000`** | Visual dominance ($\alpha^* = 1.0$) |
| **RQ4: Duplicate Screening** | Synthetic Duplicate AUROC| N/A | **`0.9998`** | False Positive Rate = $0.0000$ |
| **RQ4: Natural HCCI Clusters** | Graph Partition | 774 Images | **769 Clusters** | 764 singletons + 5 pairs (769 KEEP, 5 REVIEW) |
| **RQ4: Quality Degradation** | Quality Risk AUROC | N/A | **`0.8803`** | Controlled benchmark ($N=120$), AUPRC = 0.9618 |
| **RQ7: Vector Search Speedup**| HNSW vs IndexFlatIP | 0.73 ms / query | **0.37 ms / query** | **`1.99x` Speedup** ($100\%$ Recall@10) |

---

## 4. Software Architecture

```text
├── configs/             # Immutable YAML experiment and dataset specifications
├── data/
│   ├── manifests/       # Normalized Parquet/CSV image metadata manifests
│   ├── processed/       # Pre-extracted DINOv2 embeddings, FAISS indices, checkpoints
│   └── raw/             # Third-party microscopy imagery (local only; not redistributed)
├── platform/
│   ├── backend/         # FastAPI REST API (JWT/RBAC, FAISS, Ingestion, Curation)
│   ├── frontend/        # React 18 / TypeScript interactive web user interface
│   ├── docker/          # Multi-stage Docker container definitions
│   └── storage/         # Local runtime data storage and SQLite/PostgreSQL models
├── reports/
│   ├── phase9/          # Complete 17-part academic publication manuscript package
│   └── phase10/         # Reproducibility audit, provenance, and environment specs
├── scripts/
│   ├── data/            # Deterministic dataset acquisition scripts
│   ├── validation/      # Dataset schema and image file integrity validators
│   └── reproduce/       # One-command reproduction CLI and benchmark runners
├── src/                 # Reusable Python research library (`scidata-platform`)
└── tests/               # 218 unit, integration, and platform regression tests
```

---

## 5. Quick Start & Installation

### 5.1 Python Environment (Python 3.11 Required)
```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -e .
```

### 5.2 One-Command Verification
Run the master verification tool to check your environment, checksums, and dataset manifests:
```bash
python scripts/reproduce/validate_release.py --smoke
```

### 5.3 Run Platform Web Application
```bash
# Terminal 1: Backend
uvicorn platform.backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Frontend
cd platform/frontend
npm start
```
- API Docs: `http://127.0.0.1:8000/docs`
- Web Dashboard: `http://localhost:3000`

---

## 6. Scientific Reproducibility & Reproduction Guide

To reproduce every experiment from scratch, consult the comprehensive [REPRODUCE.md](REPRODUCE.md) guide.

To verify all 218 test cases across the research pipeline and web platform:
```bash
pytest tests platform/tests -v
```

---

## 7. Data Redistribution & Rights Governance

This project adheres to strict research ethics and data rights:
- **Raw Images:** Not included in release archives. Users acquire raw data directly from official depositors (see [DATA_REDISTRIBUTION_POLICY.md](reports/phase10/DATA_REDISTRIBUTION_POLICY.md) and [DATASET_PROVENANCE.md](reports/phase10/DATASET_PROVENANCE.md)).
- **Derived Features:** Vector embeddings, cryptographic manifests, and trained adapter weights are open and included in releases.

---

## 8. License & Citation

- **Software License:** [MIT License](LICENSE) (see [SOFTWARE_LICENSE.md](reports/phase10/SOFTWARE_LICENSE.md)).
- **Citation:** Please cite this software and associated research using [CITATION.cff](CITATION.cff) or [CITATION.md](CITATION.md).
- **Dataset Attribution:** When utilizing external datasets, cite the original depositors as documented in [DATASET_CITATIONS.md](DATASET_CITATIONS.md).
