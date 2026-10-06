# Historical Result Reconciliation & Retrieval Protocol Separation

**Project:** AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images  
**Standard:** IEEE Scientific Reproducibility & Protocol Transparency Standards  
**Status:** RECONCILED & AUTHORITATIVE  

---

## 1. Executive Summary

During development across Phases 1–6, multiple retrieval metrics were recorded under differing operational protocols. To ensure scientific rigor and publication integrity, this document explicitly reconciles all numerical values appearing across git logs, exploratory notes, and preliminary manuscripts.

---

## 2. Definitive Reconciliation Table

| Metric Value | Protocol Designation | Target Variable | Status | Context & Explanation |
|:---:|:---:|:---|:---:|:---|
| **0.9481** | **Protocol M** | Retrieval Recall@1 | **HISTORICAL / NON-AUTHORITATIVE** | Preliminary exploratory benchmark where same-acquisition gallery images were masked out. Superseded by frozen Protocol U. |
| **0.9658** | **Protocol M** | Retrieval MRR | **HISTORICAL / NON-AUTHORITATIVE** | Paired with Recall@1 = 0.9481 under masked exclusion. Superseded by frozen Protocol U. |
| **0.1321** | **Protocol U** | Frozen DINOv2 Recall@1 | **AUTHORITATIVE** | Evaluated on frozen 212 test queries under Protocol U (unmasked distractors retained). |
| **0.9858** | **Protocol U** | Frozen DINOv2 Recall@5 | **AUTHORITATIVE** | Evaluated on frozen 212 test queries under Protocol U. |
| **0.5200** | **Protocol U** | Frozen DINOv2 MRR | **AUTHORITATIVE** | Frozen DINOv2 MRR under unmasked distractors. |
| **0.1447** | **Protocol U** | Phase-4 Ensemble Recall@1 | **AUTHORITATIVE** | 3-seed ensemble Recall@1 on frozen 212 test queries. |
| **0.9921** | **Protocol U** | Phase-4 Ensemble Recall@5 | **AUTHORITATIVE** | 3-seed ensemble Recall@5 under Protocol U (+0.63% over DINOv2). |
| **0.5261** | **Protocol U** | Phase-4 Ensemble MRR | **AUTHORITATIVE** | 3-seed ensemble MRR under Protocol U. |
| **0.2016** | **Protocol U** | DINOv2 Acquisition Gap $\Delta_{\text{geom}}$ | **AUTHORITATIVE** | Within-acquisition (0.7811) minus cross-acquisition (0.5794) cosine similarity. |
| **0.0681** | **Protocol U** | Phase-4 Mean Acquisition Gap $\Delta_{\text{geom}}$ | **AUTHORITATIVE** | Within-acquisition (0.9085) minus cross-acquisition (0.8404) cosine similarity across 3 seeds. |
| **66.23%** | **Protocol U** | Population Mean Gap Reduction | **AUTHORITATIVE** | $\frac{0.2016 - 0.0681}{0.2016} \times 100\% = 66.23\%$; Wilcoxon $p = 5.03 \times 10^{-36}, d_z = 2.19$. |
| **66.40%** | **Protocol U** | Query-Level Mean Gap Reduction | **AUTHORITATIVE** | Arithmetic mean of individual paired gap reduction percentages across 212 queries. |
| **0.8582** | **Phase 4 Synthetic** | DINOv2 Artifact AUROC | **AUTHORITATIVE** | Controlled synthetic artifact screening on 1,100 test micrographs. |
| **0.8230** | **Phase 4 Synthetic** | Phase-4 Adapted Artifact AUROC | **AUTHORITATIVE** | Controlled synthetic artifact screening across 3 seeds (mean). |
| **0.6837** | **Phase 4 Synthetic** | DINOv2 Artifact Macro F1 | **AUTHORITATIVE** | 11-class artifact screening Macro F1 (+5.14% over Phase-4 adapted). |
| **0.6323** | **Phase 4 Synthetic** | Phase-4 Adapted Macro F1 | **AUTHORITATIVE** | 11-class artifact screening Macro F1 across 3 seeds (mean). |
| **0.8803** | **Exploratory** | Uncalibrated Confidence Mean | **SUPERSEDED** | Historical uncalibrated confidence score; superseded by temperature-scaled calibration. |
| **0.9825** | **Exploratory** | Preliminary Single-Class AUROC | **SUPERSEDED** | Historical binary artifact detection; superseded by 11-class multiclass screening. |

---

## 3. Mandatory Protocol Separation Notice

> [!IMPORTANT]
> **Mandatory Manuscript Notice:** The Protocol-U retrieval results reported in the final publication (DINOv2 R@5 = 0.9858, Phase-4 R@5 = 0.9921) must not be compared directly with the historical Protocol-M result (R@1 = 0.9481, MRR = 0.9658) because the two protocols differ fundamentally in same-acquisition exclusion. Protocol M artificially excluded intra-acquisition distractors, whereas Protocol U evaluates realistic multi-instrument galleries containing both intra- and cross-acquisition candidate images.
