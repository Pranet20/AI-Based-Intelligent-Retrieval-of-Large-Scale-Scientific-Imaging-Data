# SCI-INTEL Canonical Research Evidence Manifest

**Platform:** SCI-INTEL — Scientific Imaging Intelligence Platform  
**Repository:** `Pranet20/AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data`  
**Classification:** FROZEN SCIENTIFIC EVIDENCE SOURCE OF TRUTH  
**Immutability Policy:** Strictly immutable. All metrics are derived from executed experiments and cryptographic hashes.

---

## 1. Phase 1 — Dataset Ingestion, Normalization & Immutability Freeze

### 1.1 Active Micrograph Population
The evaluated scientific corpus comprises **6,085 active micrographs** distributed across three physical microscopy repositories:
- **HCCI (High-Carbon Chromium Bearing Steel):** 774 micrographs in PNG format (AISI 52100 metallurgical specimens: As-Cast, Water-Quenched, Air-Cooled).
- **Carinthia SEM:** 4,591 micrographs in JPEG format (Materials engineering defect archive).
- **BBBC021v1 (Broad Bioimage Benchmark Collection):** 720 micrographs in uncompressed 16-bit TIFF format (MCF-7 cultured human breast cancer cell line).

### 1.2 Benchmark Partitions
- **HCCI Partitioning:**
  - Training Split: 427 micrographs
  - Validation Split: 135 micrographs
  - Held-out Test Split: 212 micrographs (Zeiss Sigma 300 acquisitions)
- **Known Specimen Limitation:** The same metallurgical specimen classes occur across train, validation, and test splits under varying instrument capture configurations. The benchmark evaluates cross-acquisition and cross-instrument retrieval robustness; it does **not** evaluate generalization to completely unseen metallurgical specimens.

### 1.3 Cryptographic Verification
- **Phase 1 Manifest Hash:** `6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5`
- **Phase 1 Test Suite:** 232 / 232 passed

---

## 2. Phase 2 — Visual Foundation Representations & Retrieval Benchmark

### 2.1 Model Specifications
- **Visual Foundation Encoder:** DINOv2 ViT-S/14 (384-dimensional representation space).
- **Projection Adapter Architecture:** Linear projection head with L2-normalized outputs ($384 \to 384$).

### 2.2 Frozen Phase 4 Model Checkpoints
- **Seed 42 Checkpoint SHA-256:** `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`
- **Seed 123 Checkpoint SHA-256:** `391fd18c95599a6956018be60b6dc8780be4b8154b899f7807c1c3950a0a931f`
- **Seed 2024 Checkpoint SHA-256:** `c5ebbc7187dd1e643fb4e59ee77b0ab4b49e8aacd9cb4647733a92258e0d8f7b`
- **Training Manifest SHA-256:** `42339ff6f53b3e76617cb99876cf10a0d2ac95545f07b716ea9c84cc2ced3258`
- **Split Manifest SHA-256:** `bb81b268d241245b8fde478a0c201333cf3e7fed47e3c4d7410f40033b9b7727`

### 2.3 Evaluated Retrieval Performance (Top-5 Accuracy)
| Model / Method | Top-5 Retrieval Accuracy |
| :--- | :---: |
| pHash (Perceptual Hash) | 0.971698 |
| dHash (Difference Hash) | 0.948113 |
| ResNet-50 (Pretrained) | 0.981132 |
| DINOv2 ViT-S/14 (Zero-Shot) | 0.985849 |
| Phase 4 Adapted (Seed 42) | 0.995283 |
| Phase 4 Adapted (Seed 123) | 0.990566 |
| Phase 4 Adapted (Seed 2024) | 0.990566 |
| **3-Seed Ensemble Mean** | **0.992138** |

- **Phase 2 Retrieval Result Hash:** `83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361`
- **Phase 2 Test Suite:** 238 / 238 passed

---

## 3. Protocol M vs. Protocol U Formal Distinction

The evaluation framework defines two non-interchangeable retrieval protocols that must never be merged or treated as contradictory:

### 3.1 Protocol M: Masked Exclusion (Intra-Acquisition Discriminability)
- **Protocol Definition:** Distractor micrographs sharing identical acquisition configurations are masked from the gallery. Evaluates fine-grained intra-condition morphology discrimination.
- **Results:**
  - Recall@1: `0.9481`
  - Mean Reciprocal Rank (MRR): `0.9658`

### 3.2 Protocol U: Unmasked Distractors (Cross-Acquisition Robustness)
- **Protocol Definition:** Unconstrained retrieval where distractors from differing instruments and capture geometries remain in the candidate set.
- **Results:**
  - **DINOv2 ViT-S/14 Baseline:**
    - Recall@1: `0.1321`
    - Recall@5: `0.9858`
    - Recall@10: `1.0000`
    - MRR: `0.5200`
    - Precision@5: `0.6160`
  - **Phase 4 Adapted (Seed 42):**
    - Recall@1: `0.1321` | Recall@5: `0.9953` | Recall@10: `1.0000` | MRR: `0.5230`
  - **Phase 4 Adapted (Seed 123):**
    - Recall@1: `0.1462` | Recall@5: `0.9906` | Recall@10: `1.0000` | MRR: `0.5214`
  - **Phase 4 Adapted (Seed 2024):**
    - Recall@1: `0.1557` | Recall@5: `0.9906` | Recall@10: `1.0000` | MRR: `0.5338`
  - **3-Seed Multi-Run Ensemble Mean:**
    - Recall@1: `0.1447` | Recall@5: `0.9921` | Recall@10: `1.0000` | MRR: `0.5261` | Precision@5: `0.6327`

---

## 4. Phase 3 — Acquisition-Aware Similarity Gap Analysis

### 4.1 Embedding Space Geometry
Evaluated on the $N=55$ matched query cohort across varying accelerating voltages and detector sensors:
- **DINOv2 ViT-S/14 Baseline:**
  - Within-Acquisition Cosine Similarity: `0.7811`
  - Cross-Acquisition Cosine Similarity: `0.5794`
  - Observed Acquisition Gap ($\Delta_{\text{baseline}}$): **`0.2016`**
- **Phase 4 Adapted Representation:**
  - Within-Acquisition Cosine Similarity: `0.9085`
  - Cross-Acquisition Cosine Similarity: `0.8404`
  - Observed Acquisition Gap ($\Delta_{\text{adapted}}$): **`0.0681`**

### 4.2 Statistical Significance
- **Gap Reduction:** **`66.23%`** (Query-level mean reduction: `66.40%`).
- **Wilcoxon Signed-Rank Test:** $W = 21743$, $p = 5.03 \times 10^{-36}$.
- **Paired Cohen's Effect Size:** $d_z = 2.19$ (Large effect).
- **Multi-Seed Individual Gaps:**
  - Seed 42: $\Delta = 0.0791$ (`60.76%` reduction)
  - Seed 123: $\Delta = 0.0598$ (`70.35%` reduction)
  - Seed 2024: $\Delta = 0.0654$ (`67.57%` reduction)
  - Mean Across Seeds: $\Delta = 0.0681$ (`66.23%` reduction)
- **Scientific Phrasing:** The adaptation *"reduced the observed acquisition-geometry similarity gap under the evaluated protocol."* It must not be described as complete or universal invariance.
- **Phase 3 Test Suite:** 248 / 248 passed

---

## 5. Phase 4 — Quality Screening, Localization & Calibration

### 5.1 Controlled Synthetic Benchmark
- Total Synthetic Samples: $N = 2,750$ (derived from 250 pristine parents across 11 balanced artifact categories).
- Binary Classification Test Split: $N = 1,100$ (100 Nominal Pristine, 1,000 Quality-Risk).

### 5.2 Screening Model Performance
| Model / Feature Set | AUROC | AUPRC | F1 Score | Balanced Accuracy |
| :--- | :---: | :---: | :---: | :---: |
| DINOv2 ViT-S/14 Representations | **0.8582** | **0.9841** | **0.9632** | **0.7036** |
| Handcrafted Quality Features | 0.8281 | 0.9808 | 0.9518 | 0.5085 |
| Phase 4 Adapted Representations | 0.8230 | 0.9792 | 0.9587 | 0.6645 |

- **Validation Operating Threshold ($\tau = 0.900$):**
  - Specificity: `0.8200` | Balanced Accuracy: `0.7545` | Matthews Correlation Coefficient (MCC): `0.3054`
- **11-Class Fine-Grained Identification (DINOv2 Logistic Classifier):**
  - Macro F1: `0.6837` | Weighted F1: `0.6837`

### 5.3 Spatial Localization Evaluation ($N = 500$)
- Macro Intersection-over-Union (IoU): **`0.4454`**
- Dice Similarity Coefficient: **`0.5103`**
- Pixel Precision: `0.5259` | Pixel Recall: `0.4957`
- Bounded Description: Strictly designated as a **model-derived suspicious region**, not physical defect confirmation.

### 5.4 Uncertainty & Calibration
- Expected Calibration Error (ECE): `0.3333`
- Brier Score: `0.4821`
- **Selective Prediction Coverage:**
  - Confidence $\tau \ge 0.20$: Coverage `77.00%`, Selective Accuracy `78.28%`
  - Confidence $\tau \ge 0.40$: Coverage `29.73%`, Selective Accuracy `99.08%`
  - Confidence $\tau \ge 0.60$: Coverage `9.73%`, Selective Accuracy `100.00%` (Abstention rate = `90.27%`)
- **Carinthia Defect SEM Screening ($N = 100$):**
  - AUROC: `1.0000` | AUPRC: `1.0000` | FPR: `0.0000` (Designated as *cross-domain distribution-shift screening*).
- **Phase 4 Test Suite:** 30 / 30 passed (cumulative repo: 278 / 278)

---

## 6. Phase 5 — Grounded Evidence & Explanation Engine

### 6.1 Architectural Modules (`src/evidence/`)
- `schemas.py`: Pydantic data contracts for risk profiles, bounding boxes, evidence cohorts, and action codes.
- `quality_risk_engine.py`: Multi-metric risk indicator calculator.
- `localization_engine.py`: Patch-level saliency and bounding box generator.
- `retrieval_evidence_engine.py`: Gallery peer matcher across $N=55$ cohort context.
- `explanation_generator.py`: Deterministic operational microscope parameter mapper.
- `evidence_aggregator.py`: End-to-end evidence pack synthesizer.

### 6.2 Thresholds & Benchmark Latency
- **Threshold Container:** `phase5-thresholds-v1.0`
- **Threshold Hash:** `a894676be938dc85b08e2cbf1fba453a25cb73a886a1dfae9e3a09722361665a`
- **Benchmark Inference Latency:** `23.40 ms/image` (mean), `28.30 ms` (P95).
- **Evidence Master Seal:** `93e5520120356ec584771eda2a94b9889af9f932de1556674b8c7c4df2141996`
- **Phase 5 Test Suite:** 36 / 36 passed

---

## 7. Phase 6 — Integrated Scientific Evaluation

### 7.1 Hypothesis Validation
- **Hypothesis $H_1$ (Acquisition Bias Reduction):** CONFIRMED. Embedding gap reduced by 66.23% ($0.2016 \to 0.0681$, $p = 5.03 \times 10^{-36}$, $d_z = 2.19$); Top-5 retrieval preserved and improved from 0.9858 to 0.9921.
- **Hypothesis $H_2$ (Dual Representation Efficacy):** *"Supported at the architectural-composition level."* Dual representations (DINOv2 for screening; Phase 4 for retrieval) operate effectively without learned parameter fusion.

### 7.2 Evidence Cohort Integrity ($N = 55$)
- Valid Evidence Availability: **100.0%**
- Same-Specimen Cross-Acquisition Matching: **100.0%**
- Cross-Instrument Retrieval: **100.0%**
- Quality-Compatible Evidence: **100.0%**
- Duplicate Contamination: **0.0%**
- Missing Provenance Events: **0.0%**
- Deterministic Ranking Consistency: **100.0%**

### 7.3 Pipeline Component Latency Breakdown
| Pipeline Stage | Latency (ms) |
| :--- | :---: |
| Image Preprocessing | 0.35 |
| Dual Representation Generation | 3.12 |
| Quality Risk Screening | 2.45 |
| Spatial Localization | 8.84 |
| Evidence Cohort Retrieval | 4.22 |
| Explanation & Aggregation | 4.42 |
| **Total Pipeline Latency** | **23.40 ms** (P95: **28.30 ms**) |

- **Phase 6 Master Seal:** `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780`
- **Phase 6 Test Suite:** 57 / 57 passed (cumulative repo: 371 / 371)

---

## 8. Authoritative Phase Seals & Checksums

| Phase | Cryptographic Master Seal / Hash |
| :--- | :--- |
| **Phase 1 Manifest** | `6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5` |
| **Phase 2 Retrieval** | `83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361` |
| **Phase 4 Checkpoint (seed 42)** | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` |
| **Phase 5 Threshold Container** | `a894676be938dc85b08e2cbf1fba453a25cb73a886a1dfae9e3a09722361665a` |
| **Phase 6 Master Seal** | `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780` |
| **Phase 7 Master Seal** | `25a2dbf5571054aae7370c7ab62ab11a85af8a8a0298256dabb15dd59fb72719` |
| **Phase 8 Corrected Master Seal** | `89dae3adb2b51e0a40aa076f3c0e4ffa9ac97fa01f7d25c6d90d5128486bb377` |
| **Phase 9 ISBI Master Seal** | `8a2e7ad6132161482a287f106dc91ba814c84223dc88b0d0cad3ff17c1810162` |
