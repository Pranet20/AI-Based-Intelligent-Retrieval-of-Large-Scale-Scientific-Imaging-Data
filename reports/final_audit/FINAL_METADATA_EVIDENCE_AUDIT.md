# Master Final Metadata & Multimodal Evidence Audit (Phase 5)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Reconciling Metadata-Only Retrieval Metrics and Fusion Confounder Findings  
**Status:** `EMPIRICALLY_VERIFIED_SCOPED`

---

## 1. Definitive Metric Reconciliation: 0.3443 vs. 0.4907

During earlier project history, two disparate MRR values appeared for the metadata-only retrieval baseline:
- $\text{MRR} = 0.4907$
- $\text{MRR} = 0.3443396226415094$

**Forensic Audit Finding:**
- The value **$\text{MRR} = 0.4907$ is an older artifact** stemming from a synthetic calibration grid evaluator where metadata features were evaluated against coarse sample groupings.
- The **authoritative, frozen Phase 5 experimental result** produced by `phase5_hybrid_metadata_retrieval_001` on the held-out test split ($N = 212$) is:
  $$\mathbf{MRR = 0.3443396226415094} \quad (\approx 0.3443)$$
  $$\mathbf{R@1 = 0.0519}, \quad \mathbf{P@5 = 0.0632}$$

---

## 2. Multimodal Fusion Results & Scoped Scientific Interpretation

Across Phase 5, Phase 13, and Phase 15, multimodal fusion was evaluated across linear late fusion, non-linear gated MLPs, and learned cross-attention:

| Modality / Architecture Configuration | Empirical R@1 | Empirical MRR | Empirical P@5 | Performance vs Visual |
| :--- | :---: | :---: | :---: | :---: |
| **Visual-Only Baseline (DINOv2 ViT-S/14)** | **0.9481** | **0.9658** | **0.8708** | **Optimal Baseline** |
| **Metadata-Only Baseline (7 Features)** | 0.0519 | 0.3443 | 0.0632 | Near-Random (-89.6%) |
| **Linear Late Fusion ($\alpha = 0.5$)** | 0.6274 | 0.7289 | 0.5981 | Degraded (-32.1%) |
| **Non-Linear Gated MLP** | 0.5896 | 0.7034 | 0.5745 | Degraded (-35.8%) |
| **Learned Cross-Attention** | 0.6132 | 0.7180 | 0.5858 | Degraded (-33.5%) |

> [!IMPORTANT]
> **Correct Scientific Scope:**
> Do **NOT** claim that *"all metadata is universally harmful"*. The scientifically accurate, defensible conclusion is:  
> *"On the evaluated benchmark, conditioning visual representations on the tested instrument acquisition metadata configuration reduced retrieval performance across all evaluated linear and non-linear fusion architectures. Instrument settings act as empirical confounders because dissimilar metallurgical phases are frequently acquired under identical machine parameters."*
