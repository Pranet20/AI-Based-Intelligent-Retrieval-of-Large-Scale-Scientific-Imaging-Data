# P19 UNCERTAINTY & LATENT-DISTANCE SIGNAL AUDIT

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: Audit of Uncertainty Quantification & $D_{\text{ref}}$ Calibration Terminology  
**Date**: 2026-09-27  
**Status**: AUDITED_AND_RECLASSIFIED  

---

## 1. Mathematical Definition of $D_{\text{ref}}$

$D_{\text{ref}}$ is a continuous geometric distance metric defined in the unit-normalized latent embedding space $\mathcal{Z} \subset \mathbb{R}^{384}$. 

For a given query image embedding $\hat{\mathbf{z}}_x$ and a curated in-distribution reference corpus $\mathcal{R}_{\text{in}}$, $D_{\text{ref}}(x)$ is defined as the minimum Euclidean distance to any exemplar in the reference set:
$$D_{\text{ref}}(x) = \min_{\mathbf{r} \in \mathcal{R}_{\text{in}}} \|\hat{\mathbf{z}}_x - \hat{\mathbf{r}}\|_2$$

Because vectors are $L_2$-normalized, $D_{\text{ref}}(x) = \sqrt{2 - 2 \max_{\mathbf{r}} \langle \hat{\mathbf{z}}_x, \hat{\mathbf{r}} \rangle} \in [0, 2]$.

---

## 2. Forensic Audit of Calibration Claims

| Audit Criterion | Verification Finding | Technical Interpretation |
|---|---|---|
| **What is $D_{\text{ref}}$?** | Latent embedding-space distance to nearest reference vector | Continuous geometric proximity metric |
| **Probability Conversion** | Not mapped via Platt scaling, isotonic regression, or temperature scaling | Remained a continuous distance in $[0, 2]$ |
| **Target Variable** | Empirical distribution membership / top-1 retrieval error | Correlated with retrieval error, but not a direct likelihood |
| **ECE Calculation ($0.0480$)** | Binned retrieval correctness across 10 quantile bins based on distance rank | Measures empirical error monotonicity, not formal Bayesian confidence |
| **Independent Calibration Split** | Evaluated directly on external benchmarks without dedicated calibration parameter fitting | Descriptive heuristic rather than fitted parametric model |

---

## 3. Required Terminology Corrections

Because $D_{\text{ref}}$ is a geometric distance signal rather than a formally fitted and calibrated posterior probability distribution:

1. **Replaced Terminology**:
   - The term *"Calibrated Uncertainty Estimation"* is **formally retired**.
2. **Authoritative Terminology**:
   - The capability is reclassified as:
     > **"Latent-Distance Uncertainty Signal Evaluation"** or **"Embedding-Space Proximity Discrimination"**
3. **Formal Claim Status**:
   - Reclassified as:
     > **"Latent-distance discrimination supported; formal probability calibration not claimed."**
4. **Retained Empirical Values**:
   - Mean in-distribution $D_{\text{ref}} = 0.2410 \pm 0.0650$
   - Mean external Carinthia $D_{\text{ref}} = 0.5120 \pm 0.1180$ (**2.12x reference distance separation**)
   - Mean external SEM Nanoscience $D_{\text{ref}} = 0.4850 \pm 0.1040$ (**2.01x reference distance separation**)
   - Monotonic error alignment across 10 quantiles confirmed.
