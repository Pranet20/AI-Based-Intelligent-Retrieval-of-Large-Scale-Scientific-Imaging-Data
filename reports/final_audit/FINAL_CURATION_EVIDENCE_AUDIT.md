# Master Final Redundancy, Quality, and Novelty Curation Audit (Phase 6)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Data Redundancy Cascades, Quality-Risk Screening, and Embedding Novelty  
**Status:** `EMPIRICALLY_VERIFIED_SCOPED`

---

## 1. Redundancy & Duplicate Screening Audit

- **Physical Dataset Evaluated:** HCCI SEM Micrograph Archive ($N = 774$).
- **Exact Hash Duplicates:** Exactly **0** byte-for-byte duplicate images.
- **Natural Redundancy Cascade (Four-Stage Filter):**
  - Resulting Clusters: **769 distinct clusters**
  - Singletons: **764 singletons**
  - Near-Duplicate Pairs: **5 pairs** (micrographs of the same field with trivial stage jitter)
- **Synthetic Validation Benchmark:** 140 positive near-duplicate pairs, 105 negative pairs. Measured Precision: **1.0000**, Recall: **0.9929**, F1: **0.9964**.
- **Mandatory Phrasing:** The manuscript must state *"no detected redundancy under the declared four-stage cascade"*, never *"no duplicates exist"*.

---

## 2. Image-Derived Quality-Risk Screening

- **Focus Quality Indicator:** Laplacian focus variance $\sigma_{\text{Lap}}^2$ against synthetic blur degradation.
- **Authoritative ROC Metrics:** **AUROC = 0.8803**, **AUPRC = 0.9618**.
- **Mandatory Terminology:** Must remain framed as **"image-derived quality-risk indicators"**, not direct physical microscope focus measurements.

---

## 3. Novelty Screening vs Domain Shift

- **Novelty Metric:** Distance-to-reference centroid in normalized feature space ($D_{\text{ref}}$).
- **Mandatory Terminology:** Framed as **"relative embedding-space novelty"**. Distribution shifts between distinct microscopy datasets (e.g. Carinthia vs HCCI, centroid cosine = 0.4018) must be characterized as **macro domain shift**, never mislabeled as anomalies.
