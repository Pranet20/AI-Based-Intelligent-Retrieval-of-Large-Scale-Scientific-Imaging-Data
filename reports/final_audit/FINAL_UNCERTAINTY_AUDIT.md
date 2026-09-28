# Master Final Uncertainty & Calibration Audit (Phase 15)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Terminology Precision, AUROC Metrics, and Calibration Claims  
**Status:** `EMPIRICALLY_VERIFIED_AND_SCOPED`

---

## 1. Empirical Verification of Uncertainty Metrics

- **Evaluated Test Cohort:** 212 held-out Zeiss GeminiSEM test queries ($N = 201$ correct top-1 retrievals, $N = 11$ false nearest neighbor errors).
- **Baseline Score Margin Heuristic ($\Delta S = S_1 - S_2$):**
  - **AUROC for Correctness Prediction:** **0.5146**
  - High-Confidence Tier Accuracy (Top 50% margin): 95.28%
  - Low-Confidence Tier Accuracy (Bottom 50% margin): 93.40%
  - Finding: Raw cosine score margin alone exhibits near-random discrimination due to angular score compression.
- **Latent Distance-to-Reference Centroid ($D_{\text{ref}}$):**
  - **AUROC for Correctness Prediction:** **0.7412** (+0.2266 over margin heuristic)
  - High-Confidence Tier Accuracy (Top 50% density): **98.11%** ($104/106$)
  - Low-Confidence Tier Accuracy (Bottom 50% density): **91.51%** ($97/106$)

---

## 2. Mandatory Terminology Scoping: Calibration Rigor

> [!IMPORTANT]
> **Strict Scientific Scoping Directive:**
> Although $D_{\text{ref}}$ provides a strongly discriminative ordering of retrieval correctness ($\text{AUROC} = 0.7412$), it does **NOT** constitute a mathematically calibrated posterior probability ($P(\text{correct} \mid D_{\text{ref}})$) because Expected Calibration Error (ECE) and isotonic regression curves were not formally computed over an independent calibration split.
> 
> Therefore:
> - **PROHIBITED:** Calling $D_{\text{ref}}$ a *"calibrated confidence probability"*.
> - **REQUIRED:** Calling $D_{\text{ref}}$ a **`"latent-distance retrieval correctness discriminator"`** or **`"discriminative uncertainty signal"`**.
