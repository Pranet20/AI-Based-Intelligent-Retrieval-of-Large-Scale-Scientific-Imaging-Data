# Master Final Multimodal Evidence & Confounder Audit (Phase 15)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Reconciling Multimodal Retrieval Results and Scoping Hypothesis H1  
**Status:** `EMPIRICALLY_VERIFIED_AND_SCOPED`

---

## 1. Complete Multimodal Architecture Benchmark Suite

| Architecture ID | Model Description | Inputs | Empirical R@1 | Empirical MRR | Empirical P@5 | Performance Delta vs Visual |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| **B0** | **Visual-Only (DINOv2 ViT-S/14)** | Micrograph ($d=384$) | **0.9481** | **0.9658** | **0.8708** | **Baseline Reference** |
| **B1** | Metadata-Only | 7 Scalar Features | 0.0519 | 0.3443 | 0.0632 | -0.8962 (-89.6%) |
| **B2** | Linear Late Fusion ($\alpha = 0.5$) | Image + 7 Scalars | 0.6274 | 0.7289 | 0.5981 | -0.3207 (-32.1%) |
| **B3** | Non-Linear Gated MLP | Image + 7 Scalars | 0.5896 | 0.7034 | 0.5745 | -0.3585 (-35.8%) |
| **B4** | Learned Cross-Attention | Image + 7 Scalars | 0.6132 | 0.7180 | 0.5858 | -0.3349 (-33.5%) |

---

## 2. Mandatory Language Scoping & Hypothesis H1 Verdict

> [!IMPORTANT]
> **Claim Scoping Directives:**
> 1. Do **NOT** assert that *"metadata is universally harmful"* or that *"multimodal representation is flawed in microscopy"*.
> 2. The precise, scientifically bounded statement is:  
>    **"The evaluated acquisition metadata configurations did not improve retrieval under the tested benchmark."**
> 3. Do **NOT** call Hypothesis H1 *"universally falsified"*. The proper wording is:  
>    **"Hypothesis H1 was not supported under the evaluated datasets, metadata variables, architectures, and benchmark protocol."**
> 4. Physical Mechanism Framing: Instrument acquisition parameters act as empirical confounders because identical accelerating voltages and beam currents are routinely utilized to image dissimilar metallurgical phases.
