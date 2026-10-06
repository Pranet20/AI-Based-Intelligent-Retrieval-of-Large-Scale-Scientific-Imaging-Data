# SCI-INTEL Live Platform Demonstration Runbook
## Operational Execution Guide for Live Demonstrations and Reviewer Audits

---

## 1. Prerequisites & Environment Setup

### System Prerequisites
- **Operating System**: Windows 10/11, macOS 12+, or Ubuntu 22.04 LTS.
- **Python Runtime**: Python 3.11.x with active virtual environment (`.venv311`).
- **Node.js Runtime**: Node.js 18.x or 20.x with `npm`.
- **Repository Location**: Root directory of `AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data`.

---

## 2. Server Startup Sequence

### Step 1: Start Backend ASGI Server
Open a terminal in the project root:

```powershell
# Activate Python 3.11 environment
.\.venv311\Scripts\Activate.ps1

# Set PYTHONPATH and start FastAPI service
$env:PYTHONPATH = "platform/backend;."
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

*Expected console confirmation*:
```
[Startup Diagnostic] Database connection parameters: {'dialect': 'sqlite', 'driver': 'pysqlite', ...}
[Startup Diagnostic] Database connection verified (SELECT 1 succeeded).
[Startup Diagnostic] Authoritative models cryptographically verified and registered:
  - Model [dinov2]: model_id=dinov2_vits14_phase2, dim=384, hash=torch_hub_facebookresearch_dinov2_vits14, active=True
  - Model [phase4]: model_id=phase4_acquisition_adapter_seed42, dim=384, hash=53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62, active=True
[Startup Diagnostic] MODEL_STATUS: LOADED | CHECKPOINT_STATUS: VERIFIED | CHECKPOINT_SHA256: 53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62
INFO: Application startup complete.
```

### Step 2: Verify Readiness & Health Probes
In a secondary terminal, verify backend health:

```powershell
curl http://127.0.0.1:8000/api/v1/health
# Expected: {"status":"healthy","database":"connected","faiss_index_count":...,"version":"1.0.0"}

curl http://127.0.0.1:8000/api/v1/readiness
# Expected: {"status":"READY","checks":{"database":"READY","storage":"READY","model_checkpoint":"READY","faiss_engine":"READY"}}
```

### Step 3: Start Frontend Development Server
In a third terminal:

```powershell
cd platform/frontend
npm start
```

*Expected confirmation*:
Browser automatically opens to `http://localhost:3000`.

---

## 3. Live Demonstration Walkthrough

Follow these sequential steps during a live review:

### Step 1: Initial Login & Telemetry Dashboard (`http://localhost:3000`)
1. Log in with demo curator credentials:
   - **Username**: `admin`
   - **Password**: `admin123`
2. Point out the **Research Benchmark Cards**:
   - DINOv2 Foundation $R@1$: $0.585$
   - Acquisition Gap Reduction: $+23.4\%$
   - Workload Reduction: $44.5\%$
3. Highlight live database metrics and system readiness indicators.

### Step 2: Ingestion & Autonomous 14-Step Profiling (`/upload`)
1. Click **Ingestion & Upload** in the navigation menu.
2. Select the **Sample Gallery** tab.
3. Click **Ingest Sample** on any sample micrograph (e.g. `Week10_40111_s1_w1_DAPI.tif`).
4. Watch the progress dialog complete in $< 1\text{ second}$.
5. Automatically view the newly indexed micrograph in `/images/{id}`.

### Step 3: Deep Canvas Viewer & Spectral Inspection (`/images/{id}`)
1. Use the interactive canvas:
   - Click and drag to pan across the specimen.
   - Use the slider or `+` / `-` buttons to zoom into subcellular features.
   - Toggle color lookup tables (Cyan, Green, Thermal).
2. Hover over any pixel to view the **Pixel Inspector HUD** showing coordinates $(x, y)$ and intensity value.
3. Review the **Quality Indicators Breakdown**:
   - Focus Variance ($\sigma^2_{\nabla^2}$), Edge Density, Shannon Entropy, Dynamic Range, Clipping, and High-Frequency FFT energy.
4. Review the **Cryptographic Provenance Trail** at the bottom of the page, demonstrating immutable event logging.

### Step 4: Acquisition-Aware Retrieval Probing (`/search`)
1. Click **Vector Search** in the navigation bar.
2. Enter Query Micrograph ID `1`.
3. Set **Representation Architecture** to `Phase 4 Adapter (Acquisition-Aware)`.
4. Click **Execute Search**.
5. Observe sub-15ms FAISS retrieval results with normalized cosine similarities.
6. Click **Compare** on the top match to open the **Side-by-Side Micrograph Comparison Modal**, highlighting identical specimen morphology despite disparate acquisition settings.

### Step 5: Rapid Curator Workbench Triage (`/reviews`)
1. Navigate to **Curator Workbench**.
2. Explain the scientific priority formula:
   $$\text{Priority} = 0.50 \cdot \text{Risk} + 0.30 \cdot (\text{Novelty} / 100) + 0.20 \cdot \mathbb{I}_{\text{Redundant}}$$
3. Select the highest priority queue item.
4. Press keyboard shortcut `1` to select **ACCEPT / KEEP**.
5. Enter a brief justification: *"Verified focal sharpness across granular specimen field."*
6. Click **Submit Review Decision**.
7. Confirm that the triage item is marked `COMPLETED` and audit logs are recorded.

### Step 6: Model Registry Checkpoint Verification (`/models`)
1. Navigate to **Models View**.
2. Confirm the green verification shield on `Phase 4 Acquisition Adapter`.
3. Verify that the displayed SHA-256 matches:
   `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`
4. Test the **Interactive Feature Extractor** to render the $14 \times 14$ pseudo-attention patch grid.

---

## 4. Demonstration Verification Checklist

- [x] Backend starts with zero warnings or errors.
- [x] Readiness probe returns HTTP 200 with `status: READY`.
- [x] Sample micrograph ingests cleanly in $< 1\text{ second}$.
- [x] DINOv2 and Phase 4 representations generate distinct 384-d vectors.
- [x] FAISS IndexFlatIP executes retrieval queries in $< 15\text{ ms}$.
- [x] Side-by-side comparison displays accurate parameter diffs.
- [x] Review submission successfully commits to SQLite database.
- [x] Provenance trail reflects all operations chronologically.

---

## 5. Teardown and Clean Shutdown

To stop the demonstration servers:
1. In the frontend terminal, press `Ctrl+C` to terminate the Webpack dev server.
2. In the backend terminal, press `Ctrl+C` to cleanly exit Uvicorn ASGI runtime.
3. Temporary test artifacts created during testing can be purged if desired (`platform/storage/test_scidata.db`).
