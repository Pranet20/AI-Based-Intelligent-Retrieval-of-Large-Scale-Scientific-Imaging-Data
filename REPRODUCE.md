# Scientific Reproduction Guide

This guide details the exact step-by-step procedures to replicate the software environment, dataset validation, experimental benchmarks (Phases 1–7), the production web platform (Phase 8), and the academic manuscript claims (Phase 9).

---

## 1. Prerequisites & System Requirements

- **Operating System:** Linux (Ubuntu 22.04+), Windows 10/11 (64-bit), or macOS.
- **Python:** Python 3.11.x strictly required (`python >=3.11, <3.12`).
- **Node.js:** Node.js v18+ (tested on v24.12.0) and npm 9+.
- **Hardware:** x86_64 CPU (minimum 8 cores recommended), 16 GB RAM (32 GB recommended), 25 GB free disk space.
- **Acceleration:** CPU only (all benchmarks verified without CUDA).
- **Optional Services:** PostgreSQL 15+ and Docker / Docker Compose.

---

## 2. Repository Setup

Clone or extract the repository archive into your workspace:
```bash
git clone https://github.com/scidata-platform/scidata-platform.git
cd scidata-platform
```

---

## 3. Python Environment Setup

Create and activate a clean Python 3.11 virtual environment:

### Linux / macOS:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Windows (PowerShell):
```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

To install the exact frozen lockfile:
```bash
pip install -r requirements-lock.txt
```

Install local package in editable mode:
```bash
pip install -e .
```

---

## 4. Frontend Environment Setup

```bash
cd platform/frontend
npm install --package-lock-only
npm install
cd ../..
```

---

## 5. Dataset Acquisition

In compliance with data rights (see `reports/phase10/DATA_REDISTRIBUTION_POLICY.md`), raw microscopy images must be acquired from their source repositories:

### 5.1 HCCI SEM Dataset (Zenodo 21931379)
```bash
python scripts/data/download_hcci.py
```
*(If automated download is restricted, follow the prompt to place `HCCI Dataset .zip` in the root and re-run).*

### 5.2 Carinthia SEM Defect Dataset (Zenodo 10715190)
```bash
python scripts/data/download_carinthia.py
```
*(Places `10715190.zip` into `data/raw/carinthia/`).*

### 5.3 Additional Benchmarks (Optional)
- SEM Nanoscience: `python scripts/data/download_sem_nanoscience.py --variant 100_percent`
- atomagined: `python scripts/data/download_atomagined.py`
- cigRockSEM: `python scripts/data/download_cigrocksem.py`
- MicroAl: `python scripts/data/download_microal.py`

---

## 6. Dataset Validation

Run the automated dataset and manifest validator:
```bash
python scripts/validation/validate_datasets.py
```
Expected output:
- `data/manifests/hcci_manifest.parquet`: 774 records matched on disk.
- `data/manifests/carinthia_manifest.parquet`: 4,591 records matched on disk.
- Machine-readable report: `artifacts/phase10/dataset_validation_report.json`.

---

## 7. Model Acquisition & Checkpoint Verification

The foundation vision backbone (`dinov2_vits14`) downloads automatically via Torch Hub.
Verify that the Phase 4 linear projection adapter checkpoint matches the authoritative frozen hash:
```bash
python scripts/reproduce/reproduce_adapter.py --eval
```
Expected Checkpoint SHA-256:
```text
53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62
```

---

## 8. Phase 2: DINOv2 Baseline Retrieval Reproduction

```bash
python scripts/reproduce/reproduce_retrieval.py --model dinov2
```
Expected Metrics (HCCI full corpus, $N=774$):
- **Recall@1:** `0.9819`
- **Recall@5:** `0.9884`
- **MRR:** `0.9894`
- **Precision@5:** `0.9693`

---

## 9. Phase 3: FAISS Vector Indexing Reproduction

```bash
python scripts/reproduce/reproduce_faiss.py
```
Expected Metrics:
- **IndexFlatIP Latency:** ~0.73 ms
- **IndexHNSW Latency:** ~0.37 ms
- **Observed Speedup:** ~1.99x
- **Agreement Recall@10:** 1.0000

---

## 10. Phase 4: Acquisition-Aware Adaptation Reproduction

```bash
python scripts/reproduce/reproduce_adapter.py --eval
```
Expected Authoritative Metrics (Evaluated protocol, N=55 cohort):
- **Baseline Within:** `0.7811` | **Baseline Cross:** `0.5794` (Gap: `0.2016`)
- **Adapted Within:** `0.9085` | **Adapted Cross:** `0.8404` (Gap: `0.0681`)
- **Gap Reduction:** `66.23%` (Query-level: `66.40%`, Wilcoxon $W = 21743$, $p = 5.03 \times 10^{-36}$, paired Cohen's $d_z = 2.19$)


---

## 11. Phase 5: Hybrid Metadata Retrieval Reproduction

```bash
python scripts/reproduce/reproduce_metadata.py --mode metadata_only
```
Expected Authoritative Metrics (Held-out test split, $N=212$):
- **Recall@1:** `0.3349`
- **MRR:** `0.3443` (Exact: `0.3443396226415094`)
- **Late Fusion Delta:** `0.0000` (Optimal $\alpha^* = 1.0$)

---

## 12. Phase 6: Duplicate, Anomaly & Curation Reproduction

```bash
# Redundancy Graph Connected Components:
python scripts/reproduce/reproduce_curation.py --task redundancy_graph

# Quality Degradation Benchmark:
python scripts/reproduce/reproduce_curation.py --task quality

# Duplicate Cascade Benchmark:
python scripts/reproduce/reproduce_curation.py --task duplicate
```
Expected Metrics:
- **Redundancy Graph:** 769 clusters (764 singletons + 5 pairs of size 2) | 769 KEEP, 5 REVIEW
- **Quality Risk Benchmark ($N=120$):** AUROC = `0.8803`, AUPRC = `0.9618`
- **Duplicate Cascade:** AUROC = `0.9998`, AUPRC = `0.9999`

---

## 13. Phase 7: Master Publication Benchmark & Ablation

Run the publication asset and statistical test verification:
```bash
python -m pytest tests/test_phase7_benchmark_suite.py -v
```
All 11 Phase 7 tests must pass.

---

## 14. Phase 8: Platform Reproduction

### Backend Development Server:
```bash
uvicorn platform.backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
Swagger UI available at: `http://127.0.0.1:8000/docs`.

### Frontend Web Server:
```bash
cd platform/frontend
npm start
```
Web application available at: `http://localhost:3000`.

### Complete Test Regression Suite (218 Tests):
```bash
pytest tests platform/tests -v
```
Expected: `218 passed`.

---

## 15. One-Command Master Validation

To perform an automated validation of the entire release:
```bash
# Quick smoke validation:
python scripts/reproduce/validate_release.py --smoke

# Full validation including test suite:
python scripts/reproduce/validate_release.py --full

# Cryptographic checksum verification only:
python scripts/reproduce/validate_release.py --verify-only
```

---

## 16. Troubleshooting

- **Issue:** `torch.hub.load` fails due to network proxy.
  - **Solution:** Pre-download `dinov2_vits14` weights into `~/.cache/torch/hub/checkpoints/`.
- **Issue:** SQLite database locked during parallel tests.
  - **Solution:** Execute tests sequentially without `-n` parallel flags (`pytest tests platform/tests`).
- **Issue:** Missing raw images.
  - **Solution:** Checksums and embeddings are frozen; reproduction of metrics can be executed directly from `data/processed/embeddings/` without raw files.

---

## 17. Known Limitations

1. **Docker Runtime:** Dockerfile and Docker Compose definitions are provided and verified, but live daemon execution is classified as `DOCKER_VALIDATION_NOT_EXECUTED`.
2. **Metadata Fusion Flatness:** On the HCCI metallurgical benchmark, visual representations are sufficiently strong that late metadata fusion yields $\Delta R@1 = 0.0000$ (alpha=1.0).
3. **Third-Party Dataset Licenses:** Certain datasets (MicroAl, Carinthia) require separate author permissions or original source downloads.
