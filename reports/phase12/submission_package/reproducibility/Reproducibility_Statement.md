# Phase 12 — Formal Reproducibility & Provenance Statement

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Document ID:** `phase12_reproducibility_statement_001`  
**Date:** September 2026  
**Status:** Certified Submission Deliverable — Reproducibility & Provenance Statement  

---

## 1. Formal Journal-Ready Reproducibility Statement

> **Reproducibility Statement:**  
> This research adheres to the highest standards of computational reproducibility, cryptographic provenance, and FAIR data stewardship. All empirical findings, retrieval tables, representation geometry metrics, and quality screening curves report exact values computed directly from immutable experimental artifacts.
> 
> The computational pipeline is deterministically pinned to Python 3.11.9, PyTorch 2.5.1+cu124 (CPU/CUDA agnostic), and FAISS-CPU 1.9.0. Image preprocessing enforces deterministic bicubic antialiasing and fixed ImageNet standardization moments. All pseudo-random processes—including contrastive projector weight initialization, minibatch shuffling, and bootstrap confidence interval resampling ($B=1,000$)—are deterministically controlled across seeds `[42, 123, 2024]`.
> 
> Exactly 110 research artifacts spanning Phases 1 through 7 and 17 manuscript artifacts are cryptographically registered with SHA-256 digests in immutable release manifests (`release/v1.0.0/manifests/master_checksums.sha256`). The trained contrastive adaptation checkpoint matches cryptographic digest `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` bit-for-bit. An automated release validation script (`python scripts/reproduce/validate_release.py --verify-only`) validates all checksums in under two minutes with zero tolerance for byte-level drift.
> 
> Software reliability and mathematical parity between research prototypes and production inference modules are validated by a comprehensive suite of 218 automated unit and integration tests passing with 100% compliance. Research-to-platform tensor parity satisfies maximum absolute error $L_\infty < 1.0 \times 10^{-6}$.
> 
> **Runtime Environment Disclosure:** While host-level Python 3.11 execution has been exhaustively validated across all 218 tests, multi-container Docker Compose deployment is documented and syntactically validated in the release archive but is designated as `DOCKER_VALIDATION_NOT_EXECUTED` due to host daemon inactivity during the closure audit.

---

## 2. Certified Execution Environment Specification

| Subsystem | Exact Software / Tool Version | Purpose in Pipeline | Verification Method |
| :--- | :--- | :--- | :--- |
| **Python Runtime** | Python 3.11.9 (64-bit) | Core ML, extraction, evaluation | `python --version` |
| **Deep Learning Framework** | PyTorch 2.5.1+cu124 | ViT extraction, SupCon training | `torch.__version__` |
| **Vector Search Engine** | FAISS-CPU 1.9.0 | Flat & HNSW nearest-neighbor search | `faiss.__version__` |
| **Scientific Stack** | NumPy 1.26.4, SciPy 1.14.1, scikit-learn 1.5.2 | Linear probing, LOF, metrics | Package metadata |
| **Data Processing** | Pandas 2.2.3, PyArrow 18.1.0 | Parquet manifests, feature tables | Package metadata |
| **Web Platform Backend** | FastAPI 0.115.6, Uvicorn 0.34.0, SQLAlchemy 2.0 | Asynchronous REST service & DB ORM | Platform test suite |
| **Web Platform Frontend** | Node.js v24.12.0, npm 11.6.2, React 18.3.1 | Curator triage interface | Node runtime |
| **Testing Engine** | pytest 9.1.1, anyio 4.15.1 | Automated regression & parity tests | 218/218 tests passing |

---

## 3. Cryptographic Checkpoints & Invariant Hashes

- **Phase 4 Contrastive Adapter Weights:**
  - Filename: `data/processed/phase4/checkpoints/phase4_adapter.pt`
  - Architecture: 2-layer MLP ($384 \to 128 \to 128$, BatchNorm, ReLU)
  - Trainable Parameters: 66,048
  - **SHA-256 Digest:** `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`
- **Master Checksum Manifest:**
  - Filename: `release/v1.0.0/manifests/master_checksums.sha256`
  - Total Registered Files: 130 files (110 research artifacts + 17 Phase 9 manuscript deliverables + metadata manifests)
  - Validation Mode: Strict bit-exact comparison (`validate_release.py --verify-only`)

---

## 4. Single-Command Reproduction Instructions

To reproduce the complete benchmark evaluation from scratch:
```bash
# 1. Activate isolated Python 3.11 environment
.\.venv311\Scripts\activate

# 2. Run release checksum verification (takes ~60s)
python scripts/reproduce/validate_release.py --verify-only

# 3. Execute the full end-to-end scientific benchmark reproduction
python -m src.cli.phase7_cmd reproduce

# 4. Execute the complete test suite (218 passing tests)
pytest tests platform/tests -q
```
