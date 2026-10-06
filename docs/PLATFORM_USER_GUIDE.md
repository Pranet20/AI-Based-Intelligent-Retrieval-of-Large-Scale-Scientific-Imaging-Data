# SCI-INTEL Platform User Guide
## AI-Powered Scientific Imaging Intelligence Platform for Scanning Electron Microscopy

---

## 1. Overview of the SCI-INTEL Platform

The **SCI-INTEL** platform is an enterprise-grade scientific imaging intelligence system designed for materials science, nanolithography, and electron microscopy laboratories. It combines self-supervised visual representation foundation models (DINOv2 ViT-S/14) with specialized acquisition-aware retrieval adapters (Phase 4), deterministic multi-stage duplicate detection, image-derived quality-risk indicators, and human-in-the-loop curator workbenches.

### Key Architectural Pillars
- **Dual Representation System**:
  - *DINOv2 Base*: General perceptual similarity, focus/blur screening, patch-level pseudo-attention localization.
  - *Phase 4 Adapter*: Specialized microscopy projection head reducing accelerating voltage and detector acquisition gaps.
- **Cascaded Integrity Architecture**: Bit-level SHA-256 deduplication, perceptual hashing (pHash/dHash), neural feature matching, and SSIM structural verification.
- **Cryptographic Provenance**: Immutable SHA-256 chained event audit logging across all data ingestion and curator actions.
- **Zero Diagnosis Claims**: Strictly provides image-derived quality indicators and suggested triage prioritization.

---

## 2. Researcher Quickstart Guide

### System Requirements
- Modern Web Browser: Chrome 110+, Edge 110+, Firefox 115+, Safari 16+.
- Backend Server: Python 3.11+ running `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
- Frontend Server: Node 18+ running `npm start` (port 3000) or static nginx deployment.

```
http://localhost:3000
```

---

## 3. Step-by-Step Workflow Walkthrough

### Step 1: Account Setup and Authentication
1. Navigate to `/login` or `/register`.
2. Register a new researcher account with your institutional email and secure password (minimum 8 characters).
3. Upon registration, an HMAC-SHA256 JWT bearer token is automatically issued and saved to secure browser session storage.
4. User roles include `RESEARCHER`, `CURATOR`, and `ADMIN`. Curators and Admins have permission to submit review triage decisions and edit metadata.

### Step 2: Micrograph Ingestion (Single & Benchmark Batch)
1. Navigate to **Ingestion & Upload** (`/upload`).
2. **Interactive Upload**:
   - Drag and drop any 8-bit, 16-bit, or 32-bit TIFF, OME-TIFF, PNG, or JPEG image.
   - Enter optional instrument metadata: Microscope platform (e.g. *FEI Helios Nanolab*), Detector (e.g. *TLD SE / Inlens*), Accelerating Voltage ($5.0\text{ kV}$), Magnification ($25,000\times$), Pixel Size ($4.2\text{ nm}$).
   - Click **Ingest & Run Pipeline**.
3. **One-Click Benchmark Sample Ingestion**:
   - In the sample gallery tab, select pre-configured biological or SEM micrographs (e.g., BBBC021 fluorescence channels) and click **Ingest Sample** to automatically trigger synchronous 14-step processing.
4. The system synchronously:
   - Computes SHA-256 hash.
   - Generates contrast-stretched 8-bit display PNG and 256x256 thumbnail.
   - Extracts 6 image-derived quality indicators.
   - Computes DINOv2 and Phase 4 384-d embeddings.
   - Updates FAISS IndexFlatIP.
   - Computes nearest-neighbor novelty score.

### Step 3: Visual & Multimodal Retrieval
1. Navigate to **Vector & Hybrid Search** (`/search`).
2. Input a query micrograph ID (e.g., `1`) or upload a query file.
3. **Select Representation Architecture**:
   - `DINOv2 Foundation`: Optimizes for visual quality, general textures, and specimen structures.
   - `Phase 4 Adapter`: Optimizes for acquisition-aware retrieval across varying accelerating voltages ($5\text{ kV}$ vs $15\text{ kV}$).
4. **Hybrid Filtering (Optional)**:
   - Check **Enable Hybrid Visual + Scientific Metadata Filtering**.
   - Specify modality constraints (e.g. `SEM`, `BSE`, `IXM`) or instrument constraints.
5. Click **Execute Search**. Review top-$k$ matches with exact cosine similarity scores, composite risk badges, and redundancy status.
6. Click **Compare** to launch the side-by-side comparison modal displaying parameter differences and cross-acquisition insights.

### Step 4: Quality Screening and Anomaly Inspection
1. Navigate to **Data Integrity & Curation** (`/curation`).
2. Filter micrographs by **Quality-Risk Flagged** (composite risk $\ge 0.60$).
3. Click any micrograph to open the **Deep Micrograph Detail** (`/images/{id}`).
4. Inspect the quality metrics breakdown:
   - **Laplacian Focus Variance ($\sigma^2_{\nabla^2}$)**: Sensitivity to optical defocus and mechanical vibration.
   - **Sobel Edge Density**: Sharpness of granular or cellular boundaries.
   - **Shannon Information Entropy ($H$)**: Bit-depth utilization and information distribution.
   - **Clipping Ratio**: Sensor saturation or dynamic range loss at pixel extremes.
   - **2D Fourier High-Frequency Ratio**: Spectral energy decay in frequency ring bands.

### Step 5: Duplicate and Near-Duplicate Analysis
1. In `/curation`, filter by **Redundancies Detected**.
2. Examine the duplication status:
   - `EXACT_DUPLICATE`: Matched via identical bitstream SHA-256 or decoded pixel stream.
   - `POTENTIAL_NEAR_DUPLICATE`: Matched via perceptual hashing ($\text{pHash}/\text{dHash} \le 10$) and cosine similarity ($\ge 0.985$).
   - `NO_DECLARED_REDUNDANCY_DETECTED`: Micrograph confirmed unique within the indexed repository.

### Step 6: Curator Workbench and Review Workflow
1. Navigate to **Curator Workbench** (`/reviews`).
2. Micrographs are automatically sorted by the scientific priority score:
   $$\text{Priority} = 0.50 \cdot \text{Risk} + 0.30 \cdot (\text{NoveltyPercentile} / 100) + 0.20 \cdot \mathbb{I}_{\text{Redundant}}$$
3. Use the **Rapid Triage Panel** to assign a decision:
   - `KEEP` (`1`): Validated specimen asset accepted into archive.
   - `REVIEW_LATER` (`2`): Deferred for secondary review.
   - `DUPLICATE` (`3`): Redundant sample marked for archival suppression.
   - `LOW_QUALITY` (`4`): Flagged for severe blur, clipping, or artifact corruption.
   - `INTERESTING_NOVEL` (`5`): Noteworthy rare microstructure or out-of-distribution sample.
   - `INCORRECT_METADATA` (`6`): Acquisition parameter discrepancy flagged for instrumentation review.
4. Input curator justification notes and submit. The decision is committed with full audit tracking.

### Step 7: Multi-Image Scientific Comparison & Curation Workflow
1. Navigate to **Multi-Image Analysis** (`/multi-image`) via the sidebar navigation item.
2. **Cohort Selection**:
   - Drag and drop 2 or more micrographs (PNG, TIFF, JPEG) or click to browse.
   - Alternatively, click on available test samples to stage them immediately.
   - Minimum 2 micrographs are enforced; the cohort badge displays $N$ images and $N(N-1)/2$ pairwise combinations.
3. **Representation Configuration**:
   - Select either **DINOv2 Foundation** (ViT-B/14, 768-d) or **Phase 4 Acquisition-Aware** (fine-tuned projection adapter).
   - If Phase 4 is selected when weights are unavailable, the platform returns an explicit HTTP 503 error without silent fallback to preserve scientific integrity.
4. **Execution & Interactive Similarity Matrix**:
   - Click **Run Multi-Image Analysis** to trigger parallel Pipeline A (redundancy cascade) and Pipeline B (quality screening & localization).
   - Review the $N \times N$ interactive Similarity Matrix: diagonal displays 100%, and off-diagonal cells display similarity percentage and cascade decision (`DUPLICATE`, `NEAR_DUPLICATE`, `SIMILAR`, `DISTINCT`).
   - Click any matrix cell to immediately open the detailed **Side-by-Side Pair Comparison View**.
5. **Redundancy & Duplicate Groups (Pipeline A)**:
   - Evaluates multi-stage cascade: Stage 1 bitwise SHA-256 match, Stage 2 decoded pixel SHA-256 match, Stage 3/4 perceptual hash hamming distance ($\le 10$), and Stage 5 deep cosine similarity ($\ge 0.985$) with SSIM ($\ge 0.95$) and MAE ($\le 5.0$).
   - Groups redundant micrographs using graph clustering and elects a representative micrograph.
   - **Strict Scientific Advisory**: Redundancy detected — review before archival or removal. Automated deletion is strictly prohibited.
6. **Quality-Risk Screening & Suspicious Region Localization (Pipeline B)**:
   - Inspect handcrafted indicators: Focus Variance (Laplacian), Saturation / Dark Ratio, Dynamic Range, Shannon Entropy, RMS Contrast.
   - Toggle the **Model-Derived Suspicious Region Overlay** on any micrograph to inspect localized bounding boxes and saliency envelopes (*"Does not constitute confirmed physical defect"*).
   - Review the **Cohort Comparative Quality Ranking**: ranks micrographs from highest to lowest risk with comparative statement (*"Image X shows the strongest image-derived quality-risk signals among the analyzed images"*).
   - Comparative Corrective Action: when comparing a risk-flagged micrograph with a nominal reference peer, the platform suggests operational parameter adjustments (e.g., working distance, dwell time, accelerating voltage) derived from the cleaner reference.
7. **Human-in-the-Loop Review Routing**:
   - Select target micrograph and curator decision: `ACCEPT`, `FLAG`, `REQUEST_REACQUISITION`, `MARK_DUPLICATE`, `MARK_NOT_DUPLICATE`, `ADD_NOTE`.
   - Submit review action to record immutable provenance events and generate a cryptographic SHA-256 audit hash.

### Step 8: Provenance Exploration and Audit Trail
1. In the micrograph detail view (`/images/{id}`), scroll to the **Cryptographic Provenance Trail**.
2. Review chronological events (`UPLOAD`, `METADATA_EXTRACTION`, `QUALITY_ANALYSIS`, `EMBEDDING_GENERATION`, `INDEXING`, `MULTI_IMAGE_ANALYSIS`, `REVIEW_DECISION`).
3. Each event records the UTC timestamp, user identifier, software version (`v1.0.0`), and parameter JSON.

---

## 4. UI Controls & Keyboard Shortcuts

| Shortcut | Context | Action |
|:---|:---|:---|
| `+` / `-` | Deep Viewer (`ImageDetail`) | Zoom in / Zoom out |
| Click + Drag | Deep Viewer (`ImageDetail`) | Pan image across canvas |
| `R` | Deep Viewer (`ImageDetail`) | Reset zoom and pan to 100% |
| `1` | Curator Workbench (`/reviews`) | Triage: ACCEPT / KEEP |
| `2` | Curator Workbench (`/reviews`) | Triage: REVIEW LATER |
| `3` | Curator Workbench (`/reviews`) | Triage: FLAG DUPLICATE |
| `4` | Curator Workbench (`/reviews`) | Triage: FLAG LOW QUALITY |
| `5` | Curator Workbench (`/reviews`) | Triage: FLAG INTERESTING NOVELTY |
| `6` | Curator Workbench (`/reviews`) | Triage: FLAG METADATA ERROR |

---

## 5. FAQ and Troubleshooting

**Q: Why do 16-bit TIFF images look dark in standard web browsers?**  
A: Raw 16-bit TIFF images store pixel values from 0 to 65,535. Standard browser renderers cannot dynamically tone-map 16-bit ranges. SCI-INTEL automatically generates a high-contrast percentile-stretched 8-bit display PNG (`{sha256}_display.png`) during ingestion while preserving the bit-exact raw original for quantitative analysis.

**Q: How do I distinguish between visual similarity and acquisition similarity?**  
A: In `/search`, select **DINOv2 Foundation** to search purely on visual textures and structural patterns. Select **Phase 4 Adapter** when querying across different accelerating voltages ($5\text{ kV}$ vs $15\text{ kV}$) to retrieve images based on underlying specimen geometry rather than sensor-induced contrast shifts.

**Q: Can the quality score diagnose specimen pathology?**  
A: No. SCI-INTEL enforces strict scientific guardrails. The composite quality risk is an image-derived signal quality indicator assessing blur, noise, and dynamic range saturation; it must never be interpreted as a biological or clinical diagnosis.
