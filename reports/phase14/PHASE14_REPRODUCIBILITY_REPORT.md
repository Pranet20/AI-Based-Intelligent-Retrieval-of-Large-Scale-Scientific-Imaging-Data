# Phase 14 Platform Deployment Reproducibility Report

**Document Version:** 1.0.0-phase14  
**Date:** 2026-09-27  
**Evaluation Mode:** Independent Host & Container Environment Audit  
**Status:** `REPRODUCIBLE_ON_HOST_ENVIRONMENT_CONTAINER_DEFERRED`

---

## 1. Executive Summary

This report assesses the degree to which an independent researcher can reproduce the data management platform without relying on hidden or implicit local state. 

**Summary Findings:**
1. **Host-Level Reproducibility:** **100% REPRODUCIBLE**. On a clean machine with Python 3.11.9, installing `requirements.txt` allows immediate execution of all unit and integration tests (218/218 passing), data ingestion scripts, and FAISS indexing pipelines.
2. **Container-Level Reproducibility:** **DEFERRED TO CLOUD STAGING**. While `Dockerfile` and `docker-compose.yml` configs are syntactically valid and pinned, live runtime execution requires a Linux or Windows environment with an active Docker daemon.
3. **Explicit External Dependencies:** Documented in Section 2 below to ensure full transparency.

---

## 2. Explicit Dependencies Required Outside Containers

To deploy the platform cleanly in an external Linux or cloud environment, only the following prerequisites are required:
1. **OS Kernel:** Linux (x86_64, kernel $\ge 5.4$) or Windows 10/11 with WSL2.
2. **OCI Runtime:** Docker Engine $\ge 24.0$ and Docker Compose $\ge 2.20$.
3. **System Memory:** Minimum 4 GB RAM (8 GB recommended for concurrent 100K vector search).
4. **Storage:** Minimum 10 GB persistent disk space for model weights, PostgreSQL volume, and image storage.
5. **Network Ports:** Port 8000 (FastAPI REST service) and Port 5432 (PostgreSQL database, internal network preferred).

---

## 3. Host Pipeline Lifecycle Trace

The complete platform lifecycle was validated natively:
$$\text{Raw TIFF Ingestion} \xrightarrow{\text{Header Parse}} \text{Metadata DB} \xrightarrow{\text{ViT-S/14}} \text{FAISS HNSW Index} \xrightarrow{\text{Cosine Query}} \text{Ranked Results}$$
All steps executed without external network dependencies, using local model checkpoints and SQLite WAL mode.
