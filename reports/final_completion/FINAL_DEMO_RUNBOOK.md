# Master Final Live Demonstration Runbook

**Project**: AI-Powered Scientific Image Data Management Platform  
**Target Environment**: Local Host (`127.0.0.1`)  
**Backend API**: `http://127.0.0.1:8000` (FastAPI / Swagger docs at `/docs`)  
**Frontend Dashboard**: `http://127.0.0.1:3000` (React 18 Web UI)  
**Duration**: 10–15 Minutes  

---

## 1. Pre-Demonstration Service Launch

Open two separate PowerShell terminals from the repository root:

### Terminal 1: Backend API Service
```powershell
$env:PYTHONPATH = "platform/backend;."
.\.venv311\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Expected Output*: `Authoritative models cryptographically verified and registered. Application startup complete.`

### Terminal 2: Frontend Web Dashboard
```powershell
cd platform/frontend
npm start
```
*Expected Output*: `Compiled successfully! Web application running at http://localhost:3000.`

---

## 2. Deterministic 10-Step Demonstration Script

| Step | Action & Route | Description & System Operation | Verifiable Output |
| :---: | :--- | :--- | :--- |
| **1** | **Authentication** (`/login`) | Log in as Researcher (`researcher_user` / `test-only-placeholder`) or Curator (`curator_user` / `test-only-placeholder`). | JWT token issued, RBAC permissions initialized in session. |
| **2** | **Dashboard** (`/dashboard`) | View live system telemetry, registered repositories, and indexed FAISS vectors. | Real-time counters matching SQLite/PostgreSQL relational counts. |
| **3** | **Project Selection** (`/projects`) | Select target scientific collection (`Benchmark Project` or `HCCI Mineralogy`). | Project ID bound to session context. |
| **4** | **Micrograph Upload** (`/upload`) | Upload synthetic or open test micrographs (TIFF / PNG format). | Real-time SHA-256 digest computation; provenance event logged. |
| **5** | **Metadata Extraction** | Inspect extracted instrument parameters (voltage, detector, working distance). | Completeness score calculated ($0.88$); metadata persisted. |
| **6** | **Embedding Extraction** | Frozen DINOv2 ViT-S/14 transforms image into 384-dimensional $L_2$-normalized vector. | Deterministic class token (`[CLS]`) embedding generated. |
| **7** | **Vector Search** (`/search`) | Query by visual image to retrieve nearest semantic candidates via FAISS HNSW. | Sub-millisecond retrieval (< 0.5 ms), Top-5 candidates with similarity scores. |
| **8** | **Decoupled Filtering** | Apply categorical filter (`detector = 'BSE' AND voltage >= 15kV`) in search sidebar. | Decoupled inverted index scopes candidates without visual embedding degradation. |
| **9** | **Integrity Screening** | View automated quality flags: Defocus risk (Tenengrad) and near-duplicate alerts. | Micrographs routed to triage queue based on risk thresholds. |
| **10**| **Curator Review** (`/reviews`)| Curator inspects flagged specimen, records verdict (`KEEP`, `LOW_QUALITY`, `DUPLICATE`). | Immutable audit trail updated with curator ID, timestamp, and rationale. |

---

## 3. Failure Recovery & Reset Procedure
If local state needs to be reset between demonstration sessions:
```powershell
# Reset test database
Remove-Item platform/storage/test_scidata.db -ErrorAction SilentlyContinue
# Re-run automated regression suite
.\.venv311\Scripts\pytest tests/ platform/tests/ -q
```
