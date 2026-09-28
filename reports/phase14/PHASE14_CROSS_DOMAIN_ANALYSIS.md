# Phase 14 Cross-Domain Generalization Analysis

**Document Version:** 1.0.0-phase14  
**Date:** 2026-09-27  
**Status:** `EMPIRICALLY_VALIDATED`  
**Associated Results:** `reports/phase14/PHASE14_CROSS_DOMAIN_RESULTS.csv`

---

## 1. Executive Summary

This study evaluates the scientific generalizability of self-supervised DINOv2 ViT-S/14 representations across distinct scientific domains and microscopy modalities. 

**Key Empirical Findings:**
1. **Quantifiable Domain Shift:** The global centroid cosine similarity between the HCCI ferrous metallurgy domain and the Carinthia industrial defect domain is **0.4018** (Euclidean distance: **1.0938**), confirming substantial divergence in latent representation space between distinct materials regimes.
2. **Robust Zero-Shot Nearest-Neighbor Clustering in Target SEM Domain:** Across all 4,591 Carinthia industrial micrographs, unadapted DINOv2 representations achieve an overall micro-averaged Recall@1 of **0.9952** ($4{,}569 / 4{,}591$) and a macro-averaged Recall@1 of **0.9090** across the six defect categories under leave-one-out cross-validation.
3. **Class Imbalance Sensitivity:** While majority classes achieve near-perfect retrieval (Class 3: $99.88\%$; Class 6: $100.00\%$), ultra-minority classes exhibit lower recall (Class 5, $N=4$: $75.00\%$; Class 1, $N=55$: $85.45\%$), reflecting local neighborhood dilution in dense embedding space.
4. **Cross-Modality Transfer (SEM $\to$ TEM):** Zero-shot transfer from SEM to biological TEM demonstrates a baseline R@1 of **0.7642**, which is restored to **0.9104** via domain-targeted contrastive fine-tuning (+14.62% absolute improvement).

---

## 2. In-Depth Domain Shift Analysis

```
       HCCI Domain Centroid                Carinthia Domain Centroid
       (Ferrous Metallurgy)               (Industrial SEM Defects)
              [ • ] <----------------------------> [ • ]
                         Cosine Sim = 0.4018
                       Euclidean Dist = 1.0938
```

The low centroid similarity (0.4018) indicates that self-supervised embeddings naturally cluster by macro-domain rather than collapsing into a generic feature space. Within each domain, local microstructural geometry (e.g. etch pits, lamellae, particulate defects) governs nearest-neighbor distances.

---

## 3. Class-Averaged Retrieval Breakdown (Carinthia SEM)

| Defect Class ID | Description | Class Count ($N$) | Leave-One-Out R@1 | Error Count | Primary Misclassification Mode |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **Class 1** | Pin-hole Defect | 55 | **0.8545** | 8 | Retrieved Class 3 (sub-resolution pit) |
| **Class 2** | Surface Scratch | 8 | **0.8750** | 1 | Retrieved Class 4 (directional groove) |
| **Class 3** | Planar Substrate (Majority) | 4,008 | **0.9988** | 5 | Retrieved Class 4 |
| **Class 4** | Particulate Contaminant | 289 | **0.9758** | 7 | Retrieved Class 3 |
| **Class 5** | Interfacial Discoloration | 4 | **0.7500** | 1 | Retrieved Class 1 |
| **Class 6** | Etch Trench Void | 227 | **1.0000** | 0 | None (100% exact retrieval) |
| **Summary** | **Macro-Averaged** | **4,591** | **0.9090** | **22** | **Dilution by dominant Class 3** |

*Methodological Rigor:* The macro-average (0.9090) gives equal weight to all six defect classes, providing an uninflated assessment of representation quality on minority defect types.
