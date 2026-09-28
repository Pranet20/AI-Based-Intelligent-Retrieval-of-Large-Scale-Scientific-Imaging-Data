# MASTER REPRODUCIBILITY GUIDE (FINAL RELEASE)

**Project**: AI-Powered Scientific Image Data Management Platform  
**Target Release**: `release_final/` (v4.0.0-final)  
**Status**: `VERIFIED_REPRODUCIBLE`  

---

## 1. Quickstart Environment Setup
```bash
# Clone repository
git clone <repo-url>
cd "Mini Project"

# Activate Python 3.11 virtual environment
.venv311\Scripts\activate  # Windows
# source .venv/bin/activate # Linux

# Install dependencies
pip install -r requirements.txt
```

## 2. Automated Regression Verification (190 Tests)
```bash
pytest tests/ -q
```
Expected output: `190 passed in ~20s`.

## 3. End-to-End Pipeline Reproduction Commands
- **Feature Extraction**:
  ```bash
  python scripts/extract_embeddings.py --dataset hcci --model dinov2_vits14
  ```
- **FAISS Index Construction**:
  ```bash
  python scripts/build_hnsw_index.py --dim 384 --hnsw-m 16 --ef-search 128
  ```
- **Benchmark Evaluation**:
  ```bash
  python scripts/evaluate_retrieval.py --benchmark hcci
  ```
- **Host Serving Launch**:
  ```bash
  uvicorn src.api.main:app --host 127.0.0.1 --port 8000
  ```

## 4. Reproducibility Classification
- **Automatically Reproducible**: Feature extraction, FAISS HNSW indexing, zero-shot retrieval benchmarks, focus/quality screening, duplicate cascade, database cascades, RBAC authorization, and host load testing.
- **Conditionally Reproducible**: Docker container execution (requires starting Docker Desktop daemon).
- **Requires External Accounts / Cloud**: Terraform cloud provisioning and public Kubernetes deployment.
- **Requires Physical Hardware**: Silicon Drift Detector (SDD) live EDS spectral acquisition.
- **Requires Human Participants**: External double-blinded expert mineralogist review.
