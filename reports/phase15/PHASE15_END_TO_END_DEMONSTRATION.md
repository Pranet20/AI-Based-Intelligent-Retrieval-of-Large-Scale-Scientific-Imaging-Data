# Phase 15 End-to-End Scientific Curation Demonstration

**Document Version:** 1.0.0-phase15  
**Date:** 2026-09-27  
**Execution Environment:** Host Python 3.11.9 (`.venv311`), PyTorch 2.5.1, FAISS-CPU 1.9.0  
**Sample Micrograph:** Held-out HCCI SEM Test Micrograph (`SEM_Q_0042.tif`, Split Seed 42)  
**Status:** `FULLY_REPRODUCIBLE_DEMONSTRATION`

---

## 1. Demonstration Overview & Dataflow

This walkthrough traces a single real micrograph through all twelve stages of the production data management and curation architecture, illustrating how quality risks, novelty, and uncertainty govern curator review.

```
[Raw Micrograph] 
       │
       ▼
 [1. Ingest] ──> [2. Extract Meta] ──> [3. ViT-S/14 Embed] ──> [4. Dup Check]
                                                                      │
 [8. Uncertainty] <── [7. Novelty CPI] <── [6. Retrieval] <── [5. Quality Triage]
       │
       ▼
 [9. Queue Priority] ──> [10. Human Review] ──> [11. Provenance] ──> [12. Searchable Record]
```

---

## 2. Step-by-Step Execution Trace

### Step 1: File Ingestion & Path Traversal Guard
- **Input File:** `data/raw/hcci/Images/SEM_Q_0042.tif` (Format: TIFF, Bit depth: 8-bit grayscale, Dimensions: $1024 \times 768$).
- **Security Check:** Filename validated using `os.path.basename`. Verified inside designated data root; traversal indicators (`../`) absent. Checksum: `SHA256: d8f4...`

### Step 2: Metadata Extraction & Normalization
- **Header Parsing:** Extracted accelerating voltage ($20.0$ kV), beam current ($1.2$ nA), magnification ($5{,}000\times$), detector (`CBS`), working distance ($8.5$ mm).
- **Relational DB Commit:** Inserted into SQLite/PostgreSQL `micrograph_metadata` table.

### Step 3: Self-Supervised Visual Embedding
- **Model:** Frozen DINOv2 ViT-S/14 (`dinov2_vits14_scientific_best.pt`, SHA-256: `53ba60a3...`).
- **Embedding Generation:** Micrograph preprocessed ($224 \times 224$ bicubic), fed through ViT patch tokenization, patch tokens mean-pooled, and L2 normalized:
  $$z_q \in \mathbb{R}^{384}, \quad \|z_q\|_2 = 1.0000$$

### Step 4: Duplicate & Redundancy Screening
- **Exact Hash Check:** SHA-256 evaluated against existing database. Duplicate match: `FALSE`.
- **Near-Duplicate Check:** Maximum cosine similarity against existing 5,365 gallery vectors: $S_{\max} = 0.9521 < 0.9950$ threshold. Near-duplicate match: `FALSE`.

### Step 5: Image-Derived Quality-Risk Screening
- **Laplacian Variance Focus Metric:** $\sigma_{\text{Lap}}^2 = 412.8 > 100.0$ threshold. Blur Status: `PASS (In-Focus)`.
- **Histogram Dynamic Range:** Zero black-clipping; upper saturation = 1.2% (< 5% threshold). Exposure Status: `PASS`.
- **Scale-Bar Overlay Check:** OCR bounding box detected in bottom 48 pixels; automatically masked from patch attention.

### Step 6: Vector Search & Candidate Retrieval
- **Index:** FAISS HNSW graph index ($N = 5{,}365$, $M = 32$).
- **Search Latency:** **0.096 ms**.
- **Top Retrieval:** Candidate `HCCI_DB_0381` (Cosine similarity: $0.9520$).

### Step 7: Relative Novelty & Curation Priority Scoring
- **Latent Novelty Distance:** $D_{\text{ref}} = \|z_q - \mu_{\text{ferrous}}\|_2 = 0.4412$.
- **Retrieval Confidence:** Evaluated via latent reference density: Confidence score = $0.942$.
- **Composite Curation Priority Index:**
  $$\text{CPI} = 0.40(0.0) + 0.35(0.4412) + 0.25(1 - 0.942) = 0.1689$$
  *(Low priority: Nominal microstructural specimen, no urgent defect flags).*

### Step 8: Uncertainty Discrimination
- Margin heuristic $\Delta S = 0.0098$.
- Calibrated latent density metric confirms high reliability ($>95\%$ probability of correct nearest-neighbor retrieval).

### Step 9: Curation Queue Placement
- Assigned to **Tier 3 (Nominal Archival Inspection)** in the curator dashboard, bypassing urgent defect review.

### Step 10: Human Curator Action & Decision
- Curator opens record, inspects rendered high-resolution zoom tile and extracted metadata tags.
- Decision: **`ACCEPTED_INTO_GALLERY`** with category tag `Ferrous Martensite Matrix`.

### Step 11: Cryptographic Provenance Audit Log
- Structured audit event emitted:
  ```json
  {
    "event_type": "CURATION_DECISION",
    "image_id": "SEM_Q_0042",
    "curator_id": "EXPERT_RATER_01",
    "decision": "ACCEPTED_INTO_GALLERY",
    "timestamp": "2026-09-27T12:50:00Z",
    "provenance_hash": "a1c8...f9"
  }
  ```

### Step 12: Final Searchable Repository Record
- Vector appended to active FAISS index. Micrograph marked searchable via REST API endpoint `/api/v1/search/similarity`.
