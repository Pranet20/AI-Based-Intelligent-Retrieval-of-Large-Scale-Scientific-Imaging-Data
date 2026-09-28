# Phase 15 Retrieval Uncertainty & Calibration Protocol

**Document Version:** 1.0.0-phase15  
**Date:** 2026-09-27  
**Scope:** Principled Uncertainty Quantification for Scientific Micrograph Retrieval  
**Hypothesis Evaluated:** H3 (Discriminative power of calibrated uncertainty vs. raw ranking margin)

---

## 1. Scientific Objective

In Phase 13, the raw score margin heuristic ($\Delta S = S_1 - S_2$) demonstrated near-random discriminative power for predicting retrieval correctness ($\text{AUROC} = 0.5146$) due to angular score compression in dense self-supervised ViT space. 

This protocol benchmarks two principled alternatives against the raw margin heuristic:
1. **Method 1: Baseline Margin Heuristic ($\Delta S$):** Difference in cosine similarity between top-1 and top-2 retrieved candidates.
2. **Method 2: Latent Distance-to-Reference Distribution ($D_{\text{ref}}$):** Euclidean distance in the 384-dimensional normalized latent space between query vector $q$ and the nearest reference cluster centroid $\mu_k$:
   $$D_{\text{ref}}(q) = \min_k \|q - \mu_k\|_2$$
3. **Method 3: Temperature-Scaled Softmax Entropy ($H_T$):** Softmax distribution over top-10 candidate similarities with temperature $T = 0.1$:
   $$p_i = \frac{\exp(S_i / T)}{\sum_{j=1}^{10} \exp(S_j / T)}, \quad H_T(q) = -\sum_{i=1}^{10} p_i \log p_i$$

---

## 2. Evaluation Cohort & Ground-Truth Definition

- **Evaluation Cohort:** 212 held-out Zeiss GeminiSEM test queries ($N = 201$ correct top-1 retrievals, $N = 11$ false nearest neighbor errors).
- **Evaluation Metrics:** Area Under the Receiver Operating Characteristic curve (AUROC) for distinguishing correct from incorrect retrievals, Area Under the Precision-Recall Curve (AUPRC), and Brier calibration error.
- **Falsification Criterion for H3:** If neither alternative exceeds the baseline margin AUROC ($0.5146$), hypothesis H3 is falsified.
