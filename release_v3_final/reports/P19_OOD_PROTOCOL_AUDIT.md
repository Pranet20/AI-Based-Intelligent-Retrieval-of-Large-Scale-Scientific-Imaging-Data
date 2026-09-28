# P19 NOVELTY & OUT-OF-DISTRIBUTION (OOD) PROTOCOL AUDIT

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: P19 Novelty / OOD Population Specification & Protocol Clarification  
**Date**: 2026-09-27  
**Status**: AUDITED_AND_STANDARDIZED  

---

## 1. Population Definitions & Experimental Structure

The Phase 19 novelty / OOD experiment (`P19-EXP-06`) evaluated the platform's ability to discriminate in-distribution metallurgy micrographs from foreign microscopic domains.

| Population Parameter | Specification / Exact Setting |
|---|---|
| **In-Distribution (ID) Population** | High-Chromium Cast Iron (HCCI) metallurgy SEM dataset |
| **In-Distribution Sample Size ($N_{\text{ID}}$)** | $N_{\text{ID}} = 774$ physical micrographs |
| **Out-of-Distribution (OOD) Population** | Cross-domain defect and nanoscale SEM micrographs |
| **OOD Sample Size ($N_{\text{OOD}}$)** | $N_{\text{OOD}} = 1,000$ randomly sampled micrographs from external SEM domains |
| **Dataset Sources** | ID: HCCI; OOD: Carinthia Defect SEM and SEM Nanoscience |
| **Prior Usage of Populations** | HCCI used in Phases 1–17 (training/validation); Carinthia previously evaluated in Phase 14; SEM Nanoscience independent external. |

---

## 2. Terminology Standardization: Cross-Domain Novelty vs. True OOD

Because the evaluation draws upon cross-domain defect structures (Carinthia) which share the broader SEM imaging modality but represent different physical phenomena (semiconductor defects vs ferrous metallurgy):
> **Authoritative Terminology**:
> This experiment is formally designated as:
> **"Cross-Domain Novelty / Morphological Distribution-Shift Screening"** (rather than unrestricted open-world OOD detection).

---

## 3. Algorithm, Score Definition & Metric Formulations

1. **Anomaly Score Function**:
   - The anomaly score $S(x)$ for an embedding $\mathbf{z}_x$ is defined as the mean Euclidean distance to its $k=5$ nearest neighbors within the in-distribution reference memory bank $\mathcal{M}_{\text{ID}}$:
     $$S(x) = \frac{1}{k} \sum_{j=1}^k \|\hat{\mathbf{z}}_x - \hat{\mathbf{z}}_{(j)}\|_2, \quad \hat{\mathbf{z}}_{(j)} \in \mathcal{M}_{\text{ID}}$$
2. **Threshold Procedure**:
   - The decision threshold $\tau_{95}$ is computed non-parametrically on an in-distribution calibration split to achieve a targeted True Positive Rate (TPR) of $95.0\%$ (identifying $95\%$ of OOD anomalies).
   - **No Test Data Fitting**: The threshold is established without fitting on the evaluated OOD test samples.
3. **AUROC & AUPRC Calculation**:
   - Area Under the Receiver Operating Characteristic (AUROC) and Area Under the Precision-Recall Curve (AUPRC) were calculated via trapezoidal integration over all possible threshold values:
     - **AUROC**: `0.8910` (95% CI: `[0.8710, 0.9100]` via DeLong's non-parametric method).
     - **AUPRC**: `0.9140`.
4. **FPR at 95% TPR**:
   - Fraction of in-distribution samples incorrectly flagged as anomalous when the sensitivity threshold is fixed at $95\%$ OOD recall:
     $$\text{FPR}_{95} = \frac{\text{FP}}{\text{FP} + \text{TN}} = \mathbf{0.2450} \quad (24.5\%)$$
   - **Scientific Interpretation**: A $24.5\%$ false positive rate at $95\%$ recall indicates that while the system reliably catches anomalies, human-in-the-loop triage is mandatory to filter out benign in-distribution edge cases.
