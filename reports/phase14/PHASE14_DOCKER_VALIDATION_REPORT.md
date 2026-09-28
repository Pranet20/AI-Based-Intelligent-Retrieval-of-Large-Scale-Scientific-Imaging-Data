# Phase 14 Docker Runtime Validation & Environment Disclosure Report

**Document Version:** 1.0.0-phase14  
**Date:** 2026-09-27  
**Host Platform:** Windows 11 AMD64  
**Docker CLI Version:** 29.1.3 (build f52814d)  
**Docker Compose Version:** v2.40.3-desktop.1  
**Validation Status:** `DOCKER_VALIDATION_NOT_EXECUTED`  
**Associated Audit Table:** `reports/phase14/PHASE14_PLATFORM_RUNTIME_AUDIT.csv`

---

## 1. Executive Summary

This report documents the container runtime audit performed under Phase 14. The objective was to evaluate containerized deployment and reproducibility of the platform stack (FastAPI backend, PostgreSQL database, and FAISS indexing services).

In strict adherence to the non-negotiable principle of scientific honesty, **no live container runtime execution is claimed**. While the Docker CLI and Docker Compose CLI binaries are installed on the host system, the background Docker Desktop engine daemon is inactive (`open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`).

Consequently, live container runtime validation is formally designated:

```
===============================================================================
                       DOCKER RUNTIME STATUS:
                   DOCKER_VALIDATION_NOT_EXECUTED
===============================================================================
```

---

## 2. Command Probing Diagnostics

| Probed Command | Returncode | Observed Output | Diagnostic Interpretation |
| :--- | :---: | :--- | :--- |
| `docker --version` | 0 | `Docker version 29.1.3, build f52814d` | Client CLI available |
| `docker compose version` | 0 | `Docker Compose version v2.40.3-desktop.1` | Compose plugin available |
| `docker info` | 1 | `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine` | Background daemon service not running |

---

## 3. 20-Point Container Lifecycle Check Mapping

| Check ID | Container Lifecycle Dimension | Evaluation Standard | Host Status | Scheduled Resolution |
| :---: | :--- | :--- | :---: | :--- |
| **C-01** | Docker Image Build | Build multi-stage Python 3.11-slim image | NOT_EXECUTED | Linux CI/CD cloud staging |
| **C-02** | Compose Configuration | Parse and validate service dependency graph | STATIC_VALID | Validated syntactically |
| **C-03** | PostgreSQL Startup | Healthcheck on port 5432 with schema init | NOT_EXECUTED | Staging environment |
| **C-04** | FastAPI Startup | Uvicorn worker initialization on port 8000 | NOT_EXECUTED | Staging environment |
| **C-05** | Frontend/Nginx Startup | Static asset serving and reverse proxy | NOT_EXECUTED | Staging environment |
| **C-06** | Internal Networking | Inter-container DNS resolution (`web` $\leftrightarrow$ `db`) | NOT_EXECUTED | Staging environment |
| **C-07** | Database Initialization | Alembic migration on startup | NOT_EXECUTED | Staging environment |
| **C-08** | API Health Endpoint | `GET /health` returns HTTP 200 JSON | NOT_EXECUTED | Staging environment |
| **C-09** | Authentication | Bearer token generation via `/auth/login` | NOT_EXECUTED | Staging environment |
| **C-10** | JWT Validation | Guard verification on protected routes | NOT_EXECUTED | Staging environment |
| **C-11** | RBAC Enforcement | Scope checks (`read`, `curate`, `admin`) | NOT_EXECUTED | Staging environment |
| **C-12** | Metadata Creation/Update | Ingest sample TIFF and extract header | NOT_EXECUTED | Staging environment |
| **C-13** | Provenance Logging | Structured audit event recorded to disk | NOT_EXECUTED | Staging environment |
| **C-14** | Research Retrieval | Query FAISS index within container | NOT_EXECUTED | Staging environment |
| **C-15** | Model Checkpoint Loading | Verify SHA-256 match on container load | NOT_EXECUTED | Staging environment |
| **C-16** | Container Restart | `docker restart` preserves state | NOT_EXECUTED | Staging environment |
| **C-17** | Database Persistence | Data retained across container recreate | NOT_EXECUTED | Staging environment |
| **C-18** | Application Persistence | Embeddings retained in mounted volume | NOT_EXECUTED | Staging environment |
| **C-19** | Graceful Shutdown | SIGTERM handled cleanly within 10s | NOT_EXECUTED | Staging environment |
| **C-20** | Clean Recovery | Self-healing on unhandled exception | NOT_EXECUTED | Staging environment |
