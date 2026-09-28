# Scientific Software & Execution Environment Specification

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Document ID:** ENV-SPEC-2026-v1.0  
**Verification Date:** September 2026  

---

## 1. Executive Summary & Runtime Architecture

This document specifies the exact hardware, operating system, and software stack required to reproduce all frozen research benchmarks (Phases 1–7), the production web platform (Phase 8), and the academic manuscript deliverables (Phase 9).

The environment relies on **Python 3.11.x** for all machine learning and scientific computing pipelines, **Node.js 20+** for the web frontend, and optional **PostgreSQL 16+** with **Docker / Docker Compose** for multi-container deployment.

---

## 2. Core Python Computational Stack (Exact Frozen Versions)

All experiments were executed and frozen using the virtual environment `.venv311`. Dependency versions were captured directly from the running environment:

| Software / Library | Frozen Version | Required / Minimum | Role & Operational Scope |
| :--- | :--- | :--- | :--- |
| **Python** | `3.11.9` | `>=3.11, <3.12` | Core scientific execution runtime |
| **PyTorch (`torch`)** | `2.14.0+cpu` | `>=2.0.0` | Deep feature inference & adapter training |
| **TorchVision (`torchvision`)** | `0.29.0+cpu` | `>=0.15.0` | Vision preprocessing & tensor transformation |
| **DINOv2 Base Model** | `ViT-S/14` (384-d) | Torch Hub cache | Pinned frozen foundation vision backbone |
| **FAISS (`faiss-cpu`)** | `1.15.1` | `>=1.7.4` | Vector indexing (IndexFlatIP, IVF, HNSW) |
| **NumPy (`numpy`)** | `2.4.6` | `>=1.25.0` | Numerical linear algebra & matrix processing |
| **SciPy (`scipy`)** | `1.17.1` | `>=1.10.0` | Calibration, empirical CDF, statistical tests |
| **Pandas (`pandas`)** | `3.0.6` | `>=2.0.0` | Manifest querying, tabular analysis, Parquet I/O |
| **scikit-learn (`scikit-learn`)** | `1.9.1` | `>=1.2.0` | Anomaly detectors, isolation forest, ROC curves |
| **Pillow (`pillow`)** | `12.3.0` | `>=10.0.0` | Raster image loading and decoding |
| **ImageHash (`imagehash`)** | `4.3.2` | `>=4.3.0` | Perceptual hashing (aHash, pHash, dHash, wHash) |
| **Tifffile (`tifffile`)** | `2026.3.3` | `>=2024.1.1` | Scientific 16-bit TIFF microscopy decoding |
| **PyArrow (`pyarrow`)** | `25.0.1` | `>=14.0.0` | High-throughput columnar Parquet storage |
| **PyYAML (`pyyaml`)** | `6.0.3` | `>=6.0` | Configuration parser |
| **Pydantic (`pydantic`)** | `2.13.5` | `>=2.0.0` | Data schema validation & config typing |
| **Pydantic Settings** | `2.15.0` | `>=2.0.0` | Environment variable management |
| **FastAPI (`fastapi`)** | `0.141.1` | `>=0.110.0` | REST API backend server |
| **Uvicorn (`uvicorn`)** | `0.54.0` | `>=0.28.0` | ASGI production application server |
| **SQLAlchemy (`sqlalchemy`)** | `2.1.1` | `>=2.0.0` | ORM & database session management |
| **PyJWT (`pyjwt`)** | `2.15.0` | `>=2.8.0` | Role-Based Access Control (RBAC) tokens |
| **Passlib (`passlib`)** | `1.7.4` | `>=1.7.4` | Password hashing (bcrypt algorithm) |
| **Matplotlib (`matplotlib`)** | `3.11.2` | `>=3.7.0` | Publication vector figure rendering |
| **OpenPyXL (`openpyxl`)** | `3.1.5` | `>=3.1.0` | Forensic metadata reconciliation (.xlsx) |
| **Pytest (`pytest`)** | `9.1.1` | `>=8.0.0` | Test runner (218 unit/integration tests) |
| **Ruff (`ruff`)** | `0.16.9` | `>=0.3.0` | Fast Python code linter and formatter |

---

## 3. Web Frontend & Tooling Stack

| Technology | Inspected Version | Minimum Requirement | Notes |
| :--- | :--- | :--- | :--- |
| **Node.js** | `v24.12.0` | `>=18.0.0` | Frontend build engine |
| **NPM** | `11.6.2` | `>=9.0.0` | Package manager |
| **React** | `^18.2.0` | `18.2.0` | Web UI framework |
| **TypeScript** | `^5.4.2` | `5.0.0` | Static typing compiler |
| **React Router** | `^6.22.3` | `6.0.0` | Client-side routing |
| **Lucide React** | `^0.359.0` | `0.300.0` | UI icon library |

---

## 4. Hardware, Operating System, and CUDA Constraints

### 4.1 Operating System
- **Tested & Verified:** Microsoft Windows 11 Enterprise / Pro (x86_64 architecture).
- **Compatible Platforms:** Ubuntu Linux 22.04 LTS / 24.04 LTS, macOS (Apple Silicon via CPU PyTorch fallback).
- **File System Requirements:** Case-insensitive or case-preserving file system supporting long path names and POSIX forward-slash normalization.

### 4.2 Compute Hardware & Acceleration
- **CPU:** Multi-core x86_64 (e.g. Intel Core i7/i9 or AMD Ryzen 7/9; minimum 8 cores recommended).
- **RAM:** Minimum 16 GB physical RAM (32 GB recommended for full Carinthia 4,591 embedding indexing in memory).
- **Storage:** Minimum 25 GB free disk space (to accommodate raw datasets, embeddings, indices, and checkpoints).
- **GPU / CUDA:** 
  - **CUDA Available:** `False` in verified benchmark execution.
  - **Acceleration Policy:** All reported benchmarks (Phases 1–9) were executed and validated strictly on **CPU** (`torch.cuda.is_available() == False`). This guarantees deterministic numerical parity across any standard workstation without requiring specialized proprietary hardware.

---

## 5. Foundation Model Cache Requirements

- **Model Identifier:** `dinov2_vits14` (Vision Transformer Small, patch size 14, 384 embedding dimensions, 22,056,576 parameters).
- **Torch Hub Repository:** `facebookresearch/dinov2`
- **Cache Location:** `~/.cache/torch/hub/facebookresearch_dinov2_main/`
- **Offline Mode:** If executing in air-gapped environments, the checkpoint `dinov2_vits14_pretrain.pth` (approx. 88 MB) must be pre-staged in `~/.cache/torch/hub/checkpoints/`.

---

## 6. Phase 4 Adapter Checkpoint Specification

- **File Path:** `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt`
- **Architecture:** Linear Projection Adapter (384 to 384) trained with SupCon loss.
- **Physical Size:** 1,780,127 bytes.
- **Authoritative Cryptographic SHA-256:**
  ```text
  53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62
  ```
- **Integrity Notice:** Any candidate hash differing from this exact 64-character hex sequence indicates file corruption or an invalid candidate seed.

---

## 7. External Services & Database Infrastructure

- **Development / Unit Testing Mode:** Local SQLite database (`platform/storage/scidata_platform.db` / `test_scidata.db`). Zero external daemon setup required.
- **Production Mode:** PostgreSQL 16+ running on `localhost:5432` (or containerized via Docker).
- **Docker Validation Status:** `DOCKER_VALIDATION_NOT_EXECUTED` (Docker CLI v29.1.3 present, daemon service currently inactive).

---

## 8. Required Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./platform/storage/scidata_platform.db` | Target database connection URI |
| `SECRET_KEY` | *(Set in `.env`)* | JWT signing secret (minimum 32 characters) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | JWT token lifetime (24 hours) |
| `BASE_STORAGE_PATH` | `platform/storage` | Root directory for platform uploaded data |
| `EXPECTED_PHASE4_HASH` | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` | Pinned checkpoint SHA-256 |
