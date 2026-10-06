# SCI-INTEL Interactive Platform Demonstration Guide
## Multi-Scenario Live Demonstration Runbook for Scientific Evaluation

---

## 1. Demonstration Personas

1. **Dr. Elena Vance (Staff Microscopist & Materials Scientist)**
   - *Goals*: Rapidly upload high-resolution SEM micrographs, verify acquisition parameters, query across instruments, and detect microstructural homology regardless of detector settings.
2. **Marcus Chen (Senior Scientific Data Curator)**
   - *Goals*: Screen incoming specimen datasets for blur, contrast saturation, and duplicate acquisitions; rapidly triage submissions with keyboard shortcuts; document scientific justifications with tamper-evident audit trails.
3. **Dr. Arthur Pendelton (Director of Central Electron Microscopy Facility)**
   - *Goals*: Inspect laboratory throughput, verify model checkpoint provenance and cryptographic integrity, audit compliance with IEEE reproducibility standards, and ensure zero unvalidated clinical or diagnostic claims.

---

## 2. Live Demonstration Scenarios

### Scenario 1: New Micrograph Ingestion and Auto-Profiling
- **Persona**: Dr. Elena Vance
- **Objective**: Ingest an uncataloged 16-bit SEM micrograph and demonstrate the automated 14-step synchronous analysis pipeline.
- **Step-by-Step Actions**:
  1. Navigate to `/upload`.
  2. Under the **Sample Gallery** tab, select benchmark sample `Week10_40111_s1_w1_DAPI.tif`.
  3. Enter manual acquisition parameters:
     - Microscope: `Molecular Devices ImageXpress Micro`
     - Detector: `Photometrics CoolSNAP HQ CCD`
     - Accelerating Voltage: `15.0 kV`
     - Magnification: `200.0x`
     - Pixel Size: `650.0 nm`
  4. Click **Ingest Sample** (or drag and drop your own microstructural image).
- **Expected Visual Output**:
  - Ingestion progress bar completes synchronously within $< 800\text{ ms}$.
  - Success banner: *"Sample micrograph ingested, quality-assessed, and indexed successfully."*
  - Automatically routes to Deep Micrograph Detail (`/images/{id}`).
- **Scientific Narrative & Talking Points**:
  - *"Notice that SCI-INTEL immediately computes the bit-level SHA-256 hash, stores the raw 16-bit original immutably, and generates an 8-bit percentile-stretched display image so high-contrast features render perfectly in standard web browsers."*

---

### Scenario 2: Acquisition-Aware Retrieval (Cross-Voltage Matching)
- **Persona**: Dr. Elena Vance
- **Objective**: Demonstrate retrieval across different accelerating voltages using the frozen Phase 4 acquisition adapter versus standard visual embeddings.
- **Step-by-Step Actions**:
  1. Navigate to `/search`.
  2. Input query image ID `1`.
  3. First search with `DINOv2 Foundation (Visual Quality)` selected. Observe top 5 matches.
  4. Switch **Representation Architecture** dropdown to `Phase 4 Adapter (Acquisition-Aware)`.
  5. Click **Execute Search**.
- **Expected Visual Output**:
  - Latency indicator: `Query executed in < 15.00 ms via exact FAISS IndexFlatIP`.
  - Mode badge updates to: `frozen_phase4_acquisition_adapter`.
  - Results table lists candidates with cosine similarity scores, composite risk badges, and instrument metadata.
- **Scientific Narrative & Talking Points**:
  - *"While standard visual models match micrographs based on surface contrast and detector brightness, our frozen Phase 4 adapter projects embeddings into an acquisition-invariant subspace, bridging the cross-voltage similarity gap by up to 23.4% without any learned fusion."*

---

### Scenario 3: Quality-Risk Detection and Spatial Localization
- **Persona**: Marcus Chen
- **Objective**: Inspect an image flagged for high quality risk and review the multi-indicator decomposition and patch-level pseudo-attention grid.
- **Step-by-Step Actions**:
  1. Navigate to `/curation` and click the **Quality-Risk Flagged** filter tab.
  2. Select an image with composite quality risk $\ge 0.60$.
  3. In the detail view (`/images/{id}`), observe the **Quality Indicators Card**:
     - Focus Variance, Edge Density, Shannon Entropy, Dynamic Range, Clipping Ratio, FFT High-Frequency Ratio.
  4. Switch to the **Frequency Spectrum** tab.
  5. Navigate to `/models`, select the image, and click **Extract Features & Attention**.
- **Expected Visual Output**:
  - 32-bin intensity histogram showing severe exposure clipping at pixel limits ($0$ or $255$).
  - 2D Fourier energy ring plot illustrating decay in high-frequency spectral bands.
  - $14 \times 14$ pseudo-attention patch heat-map highlighting regions of anomalous blur or artifact distortion.
- **Scientific Narrative & Talking Points**:
  - *"SCI-INTEL decomposes quality into 6 deterministic indicators. The composite risk score transparently reports optical and signal degradation without pretending to diagnose physical specimen defects."*

---

### Scenario 4: Near-Duplicate Detection and Cluster Resolution
- **Persona**: Marcus Chen
- **Objective**: Identify a micrograph redundant with an existing archive specimen and inspect the matching stage.
- **Step-by-Step Actions**:
  1. Navigate to `/curation` and click **Redundancies Detected**.
  2. Open any asset marked `EXACT_DUPLICATE` or `POTENTIAL_NEAR_DUPLICATE`.
  3. Inspect the **Integrity & Redundancy Profile**.
- **Expected Visual Output**:
  - Redundancy badge clearly displays `POTENTIAL_NEAR_DUPLICATE` with matched image ID.
  - Match Stage displays `STAGE_3_PERCEPTUAL_PHASH` or `STAGE_1_FILE_SHA256`.
  - pHash and dHash 64-bit binary signatures are displayed with Hamming distance $\le 10$.
- **Scientific Narrative & Talking Points**:
  - *"Our multi-stage cascade prevents redundant micrographs from polluting downstream retrieval benchmarks, testing exact bitstream SHA-256 first, then decoded pixel hashes, perceptual hashes, and SSIM structural similarity."*

---

### Scenario 5: Curator Workbench Triage (Keyboard-Driven Workflow)
- **Persona**: Marcus Chen
- **Objective**: Execute rapid expert triage using the priority-ranked queue and hotkey controls.
- **Step-by-Step Actions**:
  1. Navigate to `/reviews`.
  2. Observe the priority queue ordered by:
     $$\text{Priority} = 0.50 \cdot \text{Risk} + 0.30 \cdot (\text{Novelty} / 100) + 0.20 \cdot \mathbb{I}_{\text{Redundant}}$$
  3. Select the top item in the queue.
  4. Press keyboard key `1` (or click **ACCEPT / KEEP**).
  5. In the rationale text box, type: *"Nominal focal contrast verified across cellular membranes."*
  6. Press **Submit Review Decision**.
- **Expected Visual Output**:
  - Review queue updates instantly; item is marked `COMPLETED` and removed from the active triage queue.
  - Audit notification confirms the decision is immutably committed.
- **Scientific Narrative & Talking Points**:
  - *"In large facilities processing thousands of micrographs weekly, curators can triage the entire queue using hotkeys 1 through 6, saving over 40% of manual review time while maintaining strict audit compliance."*

---

### Scenario 6: Provenance Trail Audit and Verification
- **Persona**: Dr. Arthur Pendelton
- **Objective**: Verify end-to-end auditability and cryptographically chained event records.
- **Step-by-Step Actions**:
  1. Navigate to any micrograph detail page (`/images/{id}`).
  2. Scroll to the **Cryptographic Provenance Trail** timeline.
  3. Expand the event details for `UPLOAD`, `QUALITY_ANALYSIS`, `EMBEDDING_GENERATION`, and `REVIEW`.
- **Expected Visual Output**:
  - Chronological event timeline showing exact timestamps, user IDs, software version (`v1.0.0`), model version, and JSON parameters.
- **Scientific Narrative & Talking Points**:
  - *"Every state transition in SCI-INTEL is immutably recorded in a append-only ledger. Reviewers and auditors can verify the exact software and model version that touched every individual micrograph."*

---

### Scenario 7: Side-by-Side Micrograph Comparison
- **Persona**: Dr. Elena Vance
- **Objective**: Compare two micrographs side-by-side to assess cross-acquisition parameter differences.
- **Step-by-Step Actions**:
  1. In `/search`, click the **Compare** button on any retrieval match.
  2. Inspect the dual-image comparison window and parameter diff table.
- **Expected Visual Output**:
  - Synchronized side-by-side view showing Query vs Retrieved Match.
  - Parameter comparison table highlighting accelerating voltage ($15.0\text{ kV}$ vs $5.0\text{ kV}$), detector type, resolution, and composite quality risk diff.
- **Scientific Narrative & Talking Points**:
  - *"Microscopists can instantly identify whether similarity is driven by specimen morphology or acquisition geometry differences, enabling confident cross-laboratory study replication."*

---

### Scenario 8: Model Registry and Checkpoint Verification
- **Persona**: Dr. Arthur Pendelton
- **Objective**: Cryptographically verify authoritative model weights and system health.
- **Step-by-Step Actions**:
  1. Navigate to `/models`.
  2. Review the **Authoritative Model Registry**:
     - `DINOv2 ViT-S/14`: `384` dimensions, active status.
     - `Phase 4 Acquisition Adapter`: Checkpoint SHA-256 hash `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`.
  3. Navigate to `/settings` and review system diagnostics and master seal integrity.
- **Expected Visual Output**:
  - Green verification shields confirm model checkpoint hash exactly matches frozen research weights.
  - Master Seals for Phase 8 (`89dae3ad...`) and Phase 9 (`8a2e7ad6...`) confirmed valid.
- **Scientific Narrative & Talking Points**:
  - *"The platform strictly locks all model checkpoints to cryptographically sealed weights. Not a single floating-point parameter has shifted since our frozen evaluation, ensuring zero drift between research paper and production software."*

---

### Scenario 9: Multi-Image Scientific Comparison, Redundancy Grouping & Corrective Actions
- **Persona**: Marcus Chen & Dr. Elena Vance
- **Objective**: Execute multi-micrograph cohort comparison ($N \ge 2$), assess the pairwise redundancy cascade, inspect model-derived suspicious region envelopes, and route human-in-the-loop corrective actions.
- **Step-by-Step Actions**:
  1. Navigate to `/multi-image`.
  2. Select 3 or more micrographs via drag-and-drop or click available quick test samples.
  3. Confirm representation model: `DINOv2 Foundation` (or `Phase 4 Acquisition-Aware`).
  4. Click **Run Multi-Image Analysis**.
  5. Inspect the $N \times N$ interactive Similarity Matrix:
     - Click off-diagonal cell $(1, 2)$ to inspect side-by-side pair comparison.
     - Verify cascade metrics: Stage 1/2 file and decoded pixel SHA-256 matches, pHash/dHash hamming distances, deep cosine similarity, and SSIM.
  6. Review Redundancy Advisory:
     - Notice: *"Redundancy detected — review before archival/removal. Automated deletion is strictly prohibited."*
     - Inspect elected group representative.
  7. Inspect Pipeline B Quality & Spatial Localization:
     - Toggle **Model-Derived Suspicious Region Overlay** on flagged micrographs.
     - Review comparative quality statement: *"Image X shows the strongest image-derived quality-risk signals among the analyzed images."*
     - Inspect comparative corrective action: operational guidance referencing cleaner peers.
  8. Human Review Routing:
     - Select target micrograph and curator action (`REQUEST_REACQUISITION` or `ACCEPT`).
     - Enter justification note and click **Commit Review Action**.
     - Verify cryptographic audit hash generation and provenance ledger update.
- **Expected Visual Output**:
  - KPI cards populated: images analyzed, $N(N-1)/2$ pairwise pairs, duplicate/near-duplicate/similar counts, quality-risk flags.
  - Interactive matrix renders color-coded cells with live selection.
  - Side-by-side micrograph cards with quality status and comparative corrective action guidance.
  - Provenance audit hash generated and displayed.
- **Scientific Narrative & Talking Points**:
  - *"Rather than evaluating images in isolation, SCI-INTEL's multi-image comparison allows researchers to immediately detect redundant acquisitions across plates, compare defective scans against clean reference peers, and route structured corrective actions directly to the microscope operator."*
