# DOCKER RUNTIME MANUAL EXECUTION PROTOCOL

**Document**: Phase 1–20 Master Final Completion — Docker Runtime Verification Protocol  
**Operational Status**: `DOCKER_RUNTIME_NOT_EXECUTED` (Automated execution blocked: Windows named pipe `//./pipe/dockerDesktopLinuxEngine` unavailable)  
**Configuration Verified**: `docker compose config` PASSED (0 errors, valid compose specification)  

---

## 1. Why Automation Cannot Complete This Step
In the current workstation environment, the Docker Desktop client CLI is installed (v29.1.3), but the Docker Desktop daemon / background Linux engine service is stopped or not launched by the host OS. Because starting Windows desktop background GUI services requires interactive host administrator privileges, container execution cannot be completed automatically in this headless session.

---

## 2. Prerequisites
1. Windows 10/11 64-bit or Ubuntu 22.04 LTS.
2. Docker Desktop running with WSL2 backend or native Docker Engine daemon (`systemctl status docker`).
3. Port availability: `5432` (PostgreSQL), `8000` (FastAPI backend), `3000` (Frontend / Web UI).
4. Minimum 4 GB RAM allocated to Docker VM.

---

## 3. Step-by-Step Execution Commands

### Step 1: Launch Docker Engine
Ensure Docker Desktop is open and showing "Engine running" in green. Verify communication:
```bash
docker version
docker info
```

### Step 2: Validate Compose Configuration
From the project root:
```bash
docker compose config
```
Expected output: valid rendered YAML specification for `backend`, `frontend`, and `postgres` services.

### Step 3: Build Container Images
```bash
docker compose build --no-cache
```
Expected output:
- `scidata-postgres`: pulled `postgres:15.6-alpine`
- `scidata-backend`: built `scientific-platform-api:v2.0.0` from `platform/docker/Dockerfile.backend`
- `scidata-frontend`: built `scientific-platform-web:v2.0.0` from `platform/docker/Dockerfile.frontend`

### Step 4: Launch the Microservice Stack
```bash
docker compose up -d
```
Expected output:
```text
[+] Running 4/4
 ✔ Network miniproject_default       Created
 ✔ Container scidata-postgres        Healthy
 ✔ Container scidata-backend         Started
 ✔ Container scidata-frontend        Started
```

### Step 5: Container Status & Health Verification
```bash
docker compose ps
```
Expected table:
| Name | Image | Status | Ports |
|---|---|---|---|
| `scidata-postgres` | `postgres:15.6-alpine` | Up (healthy) | 0.0.0.0:5432->5432/tcp |
| `scidata-backend` | `scientific-platform-api:v2.0.0` | Up (healthy) | 0.0.0.0:8000->8000/tcp |
| `scidata-frontend` | `scientific-platform-web:v2.0.0` | Up | 0.0.0.0:3000->80/tcp |

---

## 4. Smoke Test & Health Check Verification

### Health Endpoints
```bash
# Backend health
curl -f http://localhost:8000/api/v1/health
# Expected: {"status":"healthy","database":"connected","vector_index":"loaded"}

# Backend readiness
curl -f http://localhost:8000/api/v1/readiness
# Expected: {"ready":true,"model":"dinov2_vits14"}

# Frontend UI HTTP response
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK
```

### In-Container Database Schema Verification
```bash
docker compose exec postgres psql -U scidata_user -d scidata_platform -c "\dt"
```
Expected tables: `micrographs`, `metadata_catalog`, `provenance_events`, `curation_queue`, `experiments`, `audit_logs`.

---

## 5. Troubleshooting & Failure Handling
- **Port Conflict (5432 / 8000)**: If local PostgreSQL is running on host, update `docker-compose.yml` port mapping to `5433:5432`.
- **Database Connection Refused**: Ensure `depends_on.postgres.condition: service_healthy` is present.
- **Out of Memory during PyTorch load**: Increase Docker Desktop memory allocation to >= 6 GB.

---

## 6. Required Evidence to Capture for Publication
1. Terminal screenshot showing `docker compose ps` with all containers `healthy`.
2. Terminal output of `curl http://localhost:8000/api/v1/health`.
3. Browser screenshot of `http://localhost:3000` showing the live dashboard.
4. Export container logs: `docker compose logs > docker_execution.log`.
