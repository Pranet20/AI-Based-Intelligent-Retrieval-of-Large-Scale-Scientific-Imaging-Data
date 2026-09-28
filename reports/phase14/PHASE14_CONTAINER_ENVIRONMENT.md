# Phase 14 Container Environment Specification

**Document Version:** 1.0.0-phase14  
**Date:** 2026-09-27  
**Host Hardware:** Intel Core i7 / 8 vCPUs, 16 GB RAM  
**Host OS:** Windows 11 Enterprise (AMD64)  
**Docker Engine Status:** INACTIVE (Docker Desktop engine named pipe not active)

---

## 1. Local Host Environment Parameters

- **Python Interpreter:** Python 3.11.9 (`.venv311\Scripts\python.exe`)
- **PyTorch Engine:** 2.5.1+cpu
- **FAISS Engine:** 1.9.0 (CPU vector index)
- **FastAPI Framework:** 0.115.0
- **SQLAlchemy ORM:** 2.0.35
- **Pydantic Validation:** 2.9.2

---

## 2. Container Assets & Digests

The repository includes complete multi-container orchestration configs:
- **Dockerfile:** Multi-stage build based on `python:3.11-slim`, non-root execution (`uid=10001`). Checksum: `1a3d3905357ee16bb41b4898f9be225e07e24de4b2e7c3f7d89d1d4a29df5ffc`.
- **docker-compose.yml:** Defines `db` (PostgreSQL 15-alpine), `web` (FastAPI backend), `worker` (async processing queue), and volume bindings for persistent storage. Checksum: `90760a6b4ff58d86c49f1d9afc2df82f1d0983ec92a8649150c10090d72779fc`.
- **requirements.txt:** Pinned dependency specification. Checksum: `479390172fc705e62b760266ed659eb6ab617465ef552d480790ae242da42f0f`.
- **Container Checksums Registry:** [`PHASE14_CONTAINER_CHECKSUMS.json`](file:///c:/Users/Pranet/Downloads/Mini%20Project/reports/phase14/PHASE14_CONTAINER_CHECKSUMS.json).
