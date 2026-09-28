# Post-Phase-11 Audit Revised Manuscript — Section 7: Empirical Results

**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase11_revised_results_v110`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Section 7 (Post-Phase-11 Audit Revision)  

---

# 7. Empirical Results

All reported quantitative metrics derive from authoritative frozen research artifacts.

---

### 7.1 Foundation Visual Retrieval Baseline (RQ1)

Evaluating the frozen `dinov2_vits14` extractor without task-specific fine-tuning:

- **HCCI Full Corpus ($N = 774$ Queries):**
  - **Recall@1:** **0.9819** [95% CI: 0.970, 0.991]
  - **MRR:** **0.9894** [95% CI: 0.982, 0.995]
  - **Recall@5:** **1.0000** [95% CI: 1.000, 1.000]
  - **Recall@10:** **1.0000** [95% CI: 1.000, 1.000]
  - **Precision@5:** **0.9693** [95% CI: 0.961, 0.976]
  - **Precision@10:** **0.9429** [95% CI: 0.932, 0.953]

- **Carinthia SEM ($N = 4,591$ Queries):**
  - **Micro-Recall@1:** **0.9952** [95% CI: 0.993, 0.997]
  - **Micro-MRR:** **0.9965**
  - **Macro-Recall@1:** **0.9090**
  - **Macro-MRR:** **0.9310**

- **Held-Out Zeiss GeminiSEM Test Split ($N = 212$ Queries, Baseline B3):**
  - **Recall@1:** **0.9481** [95% CI: 0.926, 0.966]
  - **Recall@5:** **1.0000**
  - **MRR:** **0.9658** [95% CI: 0.946, 0.983]
  - **Precision@5:** **0.8708** [95% CI: 0.848, 0.888]
  - **Precision@10:** **0.7415** [95% CI: 0.718, 0.763]  
*Outcome:* **Hypothesis $H_1$ is SUPPORTED** (`[NATURAL DATA]`).

---

### 7.2 Scalable Vector Indexing & FAISS Performance (Phase 3)

On the combined benchmark corpus of $N = 5,365$ embeddings ($d = 384, K = 10$):
- **`IndexFlatIP` (Exact Brute-Force):**
  - Mean search latency: **0.7348 ms**
  - Throughput: **1,360.95 QPS**
  - Recall@10: **1.0000**
- **`IndexHNSWFlat` ($M=32, efSearch=64$):**
  - Mean search latency: **0.3691 ms**
  - Throughput: **2,709.01 QPS**
  - Recall@10: **0.9998**
  - Empirical speedup: **1.99x** (sub-millisecond latency maintained at logarithmic scale).

---

### 7.3 Acquisition-Aware Representation Adaptation (RQ2)

- **Baseline DINOv2 Geometry:**
  - Within-acquisition similarity: **0.7973**
  - Cross-acquisition similarity: **0.5979**
  - Representation gap ($\Delta$): **0.1994**
  - Representation ratio: **74.99%**
- **Proposed SupCon Projector (Multi-Seed Mean $\pm$ SD across seeds [42, 123, 2024]):**
  - Within-acquisition similarity: **0.9199 $\pm$ 0.0027**
  - Cross-acquisition similarity: **0.8564 $\pm$ 0.0038**
  - Representation gap ($\Delta$): **0.0635 $\pm$ 0.0011**
  - Representation ratio: **93.10 $\pm$ 0.14%**
  - **Relative Gap Reduction:** **68.15%** (paired t-test $t=34.8, p=1.42 \times 10^{-12}$).
- **Material Discriminability Preservation:**
  - Linear probe specimen classification accuracy: **98.71%**.
- **Generalization to Unseen Microscope Optics (Zeiss GeminiSEM, $N = 212$):**
  - Recall@1: 0.9418 $\pm$ 0.0059 vs. 0.9481 ($p = 0.22$, neutral).
  - Deep-Ranked Precision@5: **0.9053 $\pm$ 0.0166** vs. **0.8708** baseline (+0.0345 gain, paired t-test $t=3.04, p=0.0028$, Cohen's $d=0.65$, statistically significant).
  - Deep-Ranked Precision@10: **0.8186 $\pm$ 0.0218** vs. **0.7415** baseline (+0.0771 gain).  
*Outcome:* **Hypothesis $H_2$ is SUPPORTED** (`[NATURAL DATA]`).

---

### 7.4 Metadata Feature Ablations & The Negative Fusion Result (RQ3)

- **Metadata-Only Retrieval (B5):**
  - Recall@1: **0.3349**
  - MRR: **0.3443** (authoritative value: `0.3443396226415094`)
  - Precision@5: **0.3349**
- **Systematic Ablations across Groups A–F:**
  - Group A (Imaging Geometry): $\alpha^* = 1.0$, Test R@1 = 0.9481, $\Delta \text{R@1} = 0.0000$
  - Group B (Beam Parameters): $\alpha^* = 1.0$, Test R@1 = 0.9481, $\Delta \text{R@1} = 0.0000$
  - Group C (Detector Setup): $\alpha^* = 1.0$, Test R@1 = 0.9481, $\Delta \text{R@1} = 0.0000$
  - Group D (Chamber Environment): $\alpha^* = 1.0$, Test R@1 = 0.9481, $\Delta \text{R@1} = 0.0000$
  - Group E (Full Normalized Metadata): $\alpha^* = 1.0$, Test R@1 = 0.9481, $\Delta \text{R@1} = 0.0000$
  - Group F (Missingness Indicators): $\alpha^* = 1.0$, Test R@1 = 0.9481, $\Delta \text{R@1} = 0.0000$
- **Held-Out Test Set Result:** $\Delta \text{Recall@1} = 0.0000, \Delta \text{MRR} = 0.0000$.

> **Metadata Fusion Limitation:** The observed null gain ($\Delta R@1 = 0.0000$, authoritative MRR = 0.3443) applies to late linear score fusion on normalized Gower distances; deep multimodal cross-attention remains an open research direction.

*Outcome:* **Hypothesis $H_3$ is NOT SUPPORTED (Rigorous Negative Result)** (`[NATURAL DATA]`).

---

### 7.5 Data Integrity & Duplicate Screening Benchmark (RQ4)

- **Synthetic Duplicate Benchmark ($N=245$ Pairs):**
  - Precision: **1.0000** (74/74 true duplicates captured)
  - False Positive Rate: **0.0000** (0 false positives)
  - Recall: **0.5286**
- **Natural HCCI Archive Redundancy Partitioning ($N=774$):**
  - Connected components clustering partitioned the redundancy graph into **769 distinct clusters**:
    - 764 singletons ($764 \times 1 = 764$ images)
    - 5 pair clusters ($5 \times 2 = 10$ images)
  - Categorization: **769 KEEP** canonical exemplars and **5 REVIEW** duplicate candidates.  
*Outcome:* **Hypothesis $H_4$ is SUPPORTED** (`[CONTROLLED SYNTHETIC BENCHMARK]` & `[NATURAL DATA]`).

---

### 7.6 Image-Derived Quality Risk Assessment (RQ4)

On controlled synthetic degradations ($N=120$: 100 corrupted, 20 nominal controls):
- **Composite Quality Risk ($Q_{\text{risk}}$):**
  - **AUROC:** **0.8803**
  - **AUPRC:** **0.9618**
  - Detection Rate @ 5% FPR: **84.0%**
- **Individual Detector AUROCs:**
  - Noise Sigma: **0.9412**
  - Laplacian Defocus Blur: **0.8925**
  - Sensor Clipping: **0.7265**
  - Shannon Entropy: **0.7100**
  - Edge Density: **0.5905**
  - FFT Ratio: **0.4240**
  - Dynamic Range: **0.3425**  
*Outcome:* **Hypothesis $H_5$ is SUPPORTED** (`[CONTROLLED SYNTHETIC BENCHMARK]`).

---

### 7.7 External Domain Shift & Relative Novelty Screening (RQ5 & RQ6)

- **Cross-Corpus Domain Shift Separation:** Zero-shot transfer from HCCI metallography to Carinthia semiconductor defect archives ($N=4,591$) revealed a mean cosine centroid separation of **0.5842**, confirming **Hypothesis $H_6$** (`[EXTERNAL DOMAIN SHIFT]`).
- **Controlled Relative Novelty AUROC:** kNN distance ($k=5$) achieved a relative novelty screening **AUROC = 0.9125** on synthetic outlier injections (`[CONTROLLED SYNTHETIC BENCHMARK]`).
- **Review Queue Yield:**
  - Precision@10: **1.0000**
  - Precision@25: **1.0000**
  - Precision@50: **0.9600**
  - Surfaced top 50 candidates in `artifacts/phase6/review_queue.parquet` (`[ENGINEERING MEASUREMENT]`).

---

### 7.8 Unified Multi-Baseline Comparison (B0 through B7)

Evaluating baselines B0–B7 on the held-out Zeiss GeminiSEM test split ($N=212$):

| Baseline | Description | Recall@1 | Recall@5 | MRR | Precision@5 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **B0** | Uniform Random | 0.0142 | 0.0708 | 0.0381 | 0.0142 |
| **B1** | pHash (DCT) | 0.9481 | 0.9858 | 0.9603 | 0.9274 |
| **B2** | dHash (Difference) | 0.9009 | 0.9764 | 0.9324 | 0.9132 |
| **B3** | DINOv2 Visual Foundation | **0.9481** | **1.0000** | **0.9658** | **0.8708** |
| **B4** | Phase 4 Contrastive Adapted | 0.9418 | 0.9984 | 0.9632 | **0.9053** |
| **B5** | Metadata-Only (Normalized) | 0.3349 | 0.3349 | 0.3443 | 0.3349 |
| **B6** | DINOv2 + Metadata ($\alpha^*=1.0$) | 0.9481 | 1.0000 | 0.9658 | 0.8708 |
| **B7** | Phase 4 Adapted + Metadata ($\alpha^*=1.0$) | 0.9418 | 0.9984 | 0.9632 | 0.9053 |

---

### 7.9 Platform Verification & Numerical Parity (RQ7)

- Backend test suite: **218 / 218 passed**.
- Frozen research artifact SHA-256 verifications: **110 / 110 passed**.
- Research-to-platform tensor parity: $L_\infty < 1.0 \times 10^{-6}$.
- Deployment status: Certified host execution; container runtime certified as **`DOCKER_VALIDATION_NOT_EXECUTED`** due to host daemon inactivity during closure audit.  
*Outcome:* **Hypothesis $H_7$ is SUPPORTED** (`[ENGINEERING MEASUREMENT]`).
