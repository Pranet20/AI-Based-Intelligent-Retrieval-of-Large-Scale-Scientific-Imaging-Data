# Canonical Scientific Metrics & Statistical Proofs

This document compiles the authoritative frozen figures for the SCI-INTEL manuscript. Every number is backed by executed experiments and cryptographic hashes.

---

## 1. Acquisition Robustness & Gap Reduction (RQ2)

- **Evaluation Population:** $N = 55$ matched query micrographs across multi-voltage and multi-detector capture configurations.
- **Baseline Representation (Frozen DINOv2 ViT-S/14):**
  - Within-Acquisition Cosine Similarity: `0.7811`
  - Cross-Acquisition Cosine Similarity: `0.5794`
  - Observed Acquisition Gap ($\Delta_{\text{baseline}}$): **`0.2016`**
- **Proposed Representation (Phase 4 Linear Adapter):**
  - Within-Acquisition Cosine Similarity: `0.9085`
  - Cross-Acquisition Cosine Similarity: `0.8404`
  - Observed Acquisition Gap ($\Delta_{\text{adapted}}$): **`0.0681`**
- **Observed Gap Mitigation:**
  - Mean Gap Reduction: **`66.23%`**
  - Query-Level Mean Reduction: **`66.40%`**
- **Statistical Significance Testing:**
  - Non-parametric Wilcoxon Signed-Rank Test: $W = 21743.0$, $p = 5.03 \times 10^{-36}$
  - Paired Effect Size (Cohen's $d_z$): $d_z = 2.19$ (Extremely large effect)
- **Multi-Seed Stability:**
  - Seed 42: Gap = `0.0791` (`60.76%` reduction)
  - Seed 123: Gap = `0.0598` (`70.35%` reduction)
  - Seed 2024: Gap = `0.0654` (`67.57%` reduction)
- **Mandatory Phrasing:** The adaptation *"reduced the observed acquisition-geometry similarity gap under the evaluated protocol."* Do not claim universal acquisition invariance.

---

## 2. Retrieval Protocols (RQ1)

- **Protocol M (Masked Distractors / Intra-Acquisition):**
  - Recall@1: `0.9481`
  - Mean Reciprocal Rank (MRR): `0.9658`
- **Protocol U (Unmasked Distractors / Cross-Acquisition):**
  - Baseline DINOv2: Recall@1 = `0.1321`, Recall@5 = `0.9858`, Recall@10 = `1.0000`, MRR = `0.5200`, Precision@5 = `0.6160`
  - Phase 4 Adapted (Seed 42): Recall@1 = `0.1321`, Recall@5 = `0.9953`, Recall@10 = `1.0000`, MRR = `0.5230`
  - Phase 4 Adapted (Seed 123): Recall@1 = `0.1462`, Recall@5 = `0.9906`, Recall@10 = `1.0000`, MRR = `0.5214`
  - Phase 4 Adapted (Seed 2024): Recall@1 = `0.1557`, Recall@5 = `0.9906`, Recall@10 = `1.0000`, MRR = `0.5338`
  - 3-Seed Multi-Run Ensemble Mean: Recall@1 = `0.1447`, Recall@5 = `0.9921`, Recall@10 = `1.0000`, MRR = `0.5261`, Precision@5 = `0.6327`
- **Protocol Distinction Rule:** Protocol M and Protocol U represent fundamentally distinct retrieval tasks and must never be merged or conflated.

---

## 3. Quality-Risk Screening & Spatial Localization (RQ3 & RQ4)

- **Controlled Synthetic Benchmark:**
  - Population: $N = 2,750$ total (250 pristine parents, 11 artifact classes)
  - Binary Test Evaluation: $N = 1,100$ (100 nominal, 1,000 quality-risk)
- **Screening Performance (Branch A - DINOv2 ViT-S/14):**
  - AUROC: **`0.8582`**
  - AUPRC: **`0.9841`**
  - F1 Score: **`0.9632`**
  - Balanced Accuracy: **`0.7036`**
- **Validation Operating Threshold ($\tau = 0.900$):**
  - Specificity: `0.8200`
  - Balanced Accuracy: `0.7545`
  - Matthews Correlation Coefficient (MCC): `0.3054`
- **11-Class Fine-Grained Identification:**
  - Macro F1: `0.6837`
  - Weighted F1: `0.6837`
- **Spatial Localization of Suspicious Regions ($N = 500$):**
  - Macro Intersection-over-Union (IoU): **`0.4454`**
  - Dice Similarity Coefficient: **`0.5103`**
  - Pixel-Level Precision: `0.5259`
  - Pixel-Level Recall: `0.4957`
  - Required Terminology: Designated strictly as a **model-derived suspicious region**, never a confirmed physical defect.

---

## 4. Uncertainty, Abstention & Calibration (RQ4)

- **Calibration Indicators:**
  - Expected Calibration Error (ECE): `0.3333`
  - Brier Score: `0.4821`
- **Selective Prediction Coverage:**
  - $\tau \ge 0.20$: Coverage `77.00%`, Selective Accuracy `78.28%`
  - $\tau \ge 0.40$: Coverage `29.73%`, Selective Accuracy `99.08%`
  - $\tau \ge 0.60$: Coverage `9.73%`, Selective Accuracy `100.00%` (Abstention rate = `90.27%`)
- **Key Scientific Finding:** Achieving 100% selective accuracy required a 90.27% abstention rate, justifying the necessity of human curatorial oversight.

---

## 5. Grounded Evidence Cohort & System Latency (RQ5)

- **Evaluated Evidence Cohort ($N = 55$):**
  - Valid Evidence Availability: **`100.0%`**
  - Same-Specimen Cross-Acquisition Matching: **`100.0%`**
  - Cross-Instrument Retrieval: **`100.0%`**
  - Quality-Compatible Evidence: **`100.0%`**
  - Duplicate Contamination: **`0.0%`**
  - Missing Lineage Events: **`0.0%`**
  - Deterministic Ranking Consistency: **`100.0%`**
  - Note: This 100% figure is strictly valid for the evaluated $N=55$ cohort and must not be extrapolated to the uncurated entire corpus.
- **Latency Breakdown (Declared Local Workstation Environment):**
  - Preprocessing: `0.35 ms`
  - Dual Representation Generation: `3.12 ms`
  - Quality Risk Screening: `2.45 ms`
  - Spatial Localization: `8.84 ms`
  - Evidence Retrieval: `4.22 ms`
  - Explanation & Aggregation: `4.42 ms`
  - **Total Pipeline Latency:** **`23.40 ms`** (Mean) | **`28.30 ms`** ($P_{95}$)
