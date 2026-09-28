# Master Final Cross-Domain Task & Evaluation Audit (Phase 14)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Rigorous Task Definition, Metric Interpretation, and Class Imbalance De-biasing  
**Status:** `EMPIRICALLY_VERIFIED_AND_SCOPED`

---

## 1. Cross-Domain Dataset Scale & Distribution

- **Source In-Domain Corpus (HCCI):** $N = 774$ ferrous metallurgy SEM micrographs across varying kV, current, and detector modes.
- **Target Evaluation Corpus (Carinthia):** $N = 4,591$ industrial semiconductor SEM micrographs across six defect classes.
- **Domain Centroid Divergence:**
  $$\text{Cosine Similarity} = \mathbf{0.4018}, \quad \text{Euclidean Distance} = \mathbf{1.0938}$$
  Confirming substantial macro-level distribution shift between the two material categories.

---

## 2. Task Definition Rigor: Classification vs Acquisition Invariance

> [!IMPORTANT]
> **Task Distinction:**
> - The **HCCI In-Domain Benchmark** evaluates **same-specimen / different-acquisition retrieval** (retrieving the identical metallurgical specimen under different accelerating voltage, detector, or magnification).
> - The **Carinthia Benchmark** evaluates **leave-one-out nearest-neighbor defect classification** (determining whether the nearest neighbor in embedding space shares the same defect category tag).
> 
> The manuscript must **never conflate** the 0.9952 micro R@1 on Carinthia with the 0.9481 R@1 on HCCI. They represent fundamentally different retrieval tasks.

---

## 3. Class Imbalance & Macro vs Micro Metric De-Biasing

The Carinthia dataset exhibits severe class imbalance, with Class 3 (planar substrate) accounting for **87.3%** of the entire repository ($4{,}008 / 4{,}591$).

| Class ID | Defect Category Name | Class Count ($N$) | Population Share | Leave-One-Out R@1 | Absolute Errors |
| :---: | :--- | :---: | :---: | :---: | :---: |
| **Class 1** | Pin-hole Defect | 55 | 1.20% | **0.8545** | 8 |
| **Class 2** | Surface Scratch | 8 | 0.17% | **0.8750** | 1 |
| **Class 3** | Planar Substrate (Majority) | 4,008 | 87.30% | **0.9988** | 5 |
| **Class 4** | Particulate Contaminant | 289 | 6.29% | **0.9758** | 7 |
| **Class 5** | Interfacial Discoloration | 4 | 0.09% | **0.7500** | 1 |
| **Class 6** | Etch Trench Void | 227 | 4.95% | **1.0000** | 0 |
| **Overall** | **Micro-Averaged Metric** | **4,591** | **100.0%** | **0.9952** | **22** |
| **Overall** | **Macro-Averaged Metric** | **4,591** | **6 classes**| **0.9090** | **22** |

*Reporting Mandate:* In all publications, the **macro-averaged Recall@1 (0.9090)** must be presented alongside micro metrics to truthfully reflect representation quality on minority defect classes.
