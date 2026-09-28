# Phase 14 Cross-Domain Generalization Failure Taxonomy

**Document Version:** 1.0.0-phase14  
**Date:** 2026-09-27  
**Scope:** Forensic Investigation of 22 Nearest-Neighbor Retrieval Errors in Target SEM Domain  
**Associated Results:** `reports/phase14/PHASE14_CROSS_DOMAIN_RESULTS.csv`

---

## 1. Executive Summary

In leave-one-out nearest-neighbor evaluation across the 4,591 micrographs of the Carinthia industrial SEM dataset, exactly **22 retrieval errors** were observed ($0.48\%$ micro error rate; $9.10\%$ macro error rate). This report establishes a structured failure taxonomy for these errors.

In strict compliance with scientific precision standards, non-causal language is maintained: failure modes are characterized as *associated with* or *consistent with* observed imaging characteristics rather than asserted as definitive causal factors.

---

## 2. Failure Mode Categorization

| Taxonomy ID | Failure Mode Description | Error Count | Share of Errors | Associated Imaging Characteristic | Possible Explanation |
| :---: | :--- | :---: | :---: | :--- | :--- |
| **GF-01** | Minority Neighborhood Dilution | 10 | 45.5% | Extreme sample size disparity (Class 5 $N=4$ vs Class 3 $N=4008$) | Consistent with sparse minority cluster margins being enveloped by the high-density baseline cluster |
| **GF-02** | Scale & Field-of-View Invariance | 6 | 27.3% | Sub-micron pin-holes (Class 1) imaged at low magnification | Associated with localized defects occupying $<1\%$ of the patch grid, allowing background texture to dominate |
| **GF-03** | Directional Feature Overlap | 4 | 18.2% | Scratch defects (Class 2) vs elongated particulate edges (Class 4) | Consistent with 1D high-aspect-ratio edge features sharing similar spatial orientation tokens |
| **GF-04** | Acquisition Contrast Shift | 2 | 9.1% | Planar substrate charging flares (Class 3) | Associated with localized high-intensity saturation mimicking particulate borders |
| **Total** | **All Evaluated Errors** | **22** | **100.0%** | **Cross-domain distribution shift** | **4,569 / 4,591 correct matches** |

---

## 3. Detailed Forensic Descriptions

### 3.1 GF-01: Minority Neighborhood Dilution (10/22 errors)
- **Observations:** In 10 instances (including 8 Class 1 pin-holes and 1 Class 5 discoloration), the nearest neighbor in embedding space belonged to the overwhelming majority Class 3 ($N = 4{,}008$).
- **Evidence Interpretation:** This pattern is consistent with representation density imbalance. Because Class 3 comprises 87.3% of the repository, the probability of an in-class neighbor in a sparse minority cluster (e.g. Class 5 with only 3 other instances in the entire database) is statistically constrained.
- **Recommended Remediation:** Class-balanced re-weighting or local density normalization during vector retrieval.

### 3.2 GF-02: Scale and Field-of-View Disparity (6/22 errors)
- **Observations:** Class 1 pin-hole defects imaged at lower magnification ($\le 2{,}500\times$) were misclassified into nominal substrate Class 3.
- **Evidence Interpretation:** In ViT-S/14 patch tokenization ($14 \times 14$ pixel patches), a tiny pin-hole of 5–8 pixels diameter contributes marginally to self-attention weights compared to the surrounding homogeneous substrate.

### 3.3 GF-03: Directional Feature Overlap (4/22 errors)
- **Observations:** Thin surface scratches (Class 2) retrieved elongated particulate contaminants (Class 4).
- **Evidence Interpretation:** Both classes produce sharp, linear high-frequency gradients. Without semantic multi-scale contextual aggregation, isotropic self-attention maps attend predominantly to the linear edge contrast.
