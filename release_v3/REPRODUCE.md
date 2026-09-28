# Reproduction Guide: Complete Phase 1–15 System

This document outlines the step-by-step procedure for reproducing and verifying the findings of the **AI-Powered Scientific Image Data Management Platform** research program.

---

### 1. Prerequisites and Environment Setup

- **Operating System**: Windows 10/11 x64 or Ubuntu 22.04 LTS
- **Python Version**: Strictly Python 3.11.x (tested on 3.11.9)
- **Virtual Environment**: Pinned dependencies installed via `requirements-lock.txt`

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# Install pinned dependencies
pip install --upgrade pip
pip install -r environment/requirements-lock.txt
```

---

### 2. Verification Modes

#### A. Master System Audit (Recommended)
Verifies all 128 frozen research checksums, dataset manifest counts, checkpoint SHA-256 hashes, and platform modules:

```bash
python scripts/reproduce/final_validate_project.py --verify-only
```

#### B. Component Reproduction Runs

1. **FAISS Retrieval Benchmark (RQ3)**:
   ```bash
   python scripts/reproduce/reproduce_faiss.py
   ```
   *Expected Result*: Verifies FAISS HNSW sub-millisecond query latency ($<0.1$ ms at 5k vectors) with zero divergence.

2. **Contrastive Acquisition Adapter (RQ2)**:
   ```bash
   python scripts/reproduce/reproduce_adapter.py
   ```
   *Expected Result*: Verifies model checkpoint SHA-256 (`53ba60a3...`) and confirms the 68.15% cross-acquisition gap reduction.

3. **Curation & Defocus Quality (RQ5)**:
   ```bash
   python scripts/reproduce/reproduce_curation.py --task quality
   ```
   *Expected Result*: Verifies defocus detection AUROC = 0.8803 and AUPRC = 0.9618.

4. **Dataset Manifest & Count Reconciliation**:
   ```bash
   python scripts/validation/validate_datasets.py
   ```
   *Expected Result*: Validates 774 physical micrographs for HCCI (305 AsCast, 236 Annealed, 233 Hardened) and 4,591 physical images for Carinthia.

---

### 3. Regression Testing

The platform includes a regression test suite covering schema validation, token security, FAISS index updates, and curation idempotency:

```bash
python -m pytest tests/ platform/tests/ -q
```
*Expected Result*: 218 passed, 0 failed.

---

### 4. Hardware and Runtime Notes

- **Compute Requirements**: All benchmark verification scripts run on standard CPU (AMD Ryzen or Intel Core i7/i9) within 2 minutes. GPU acceleration (CUDA) is optional for inference benchmarking.
- **Docker Engine Limitation**: Containerized execution via `docker-compose up` requires an active Docker daemon. On Windows systems where the Docker Desktop Linux daemon is stopped, execution falls back gracefully to native Python 3.11 CLI execution.
