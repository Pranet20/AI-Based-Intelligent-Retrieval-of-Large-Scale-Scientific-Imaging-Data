# Scientific Contribution Lock

The manuscript locks exactly four core contributions. No extraneous claims may be introduced during drafting.

---

## Authoritative Contributions

### Contribution 1: Acquisition-Aware Scientific Microscopy Retrieval
Formulation and evaluation of a contrastive linear projection adapter operating on frozen visual foundation representations (DINOv2 ViT-S/14), demonstrating a **66.23% reduction in the observed acquisition-geometry similarity gap** ($p = 5.03 \times 10^{-36}$, $d_z = 2.19$) across varying accelerating voltages (5–20 kV) and secondary electron detector geometries on metallurgical SEM micrographs.

### Contribution 2: Image-Derived Quality-Risk Screening & Localization
An independent screening framework that quantifies image degradation risks (AUROC = 0.8582, AUPRC = 0.9841) and localizes model-derived suspicious regions (Macro IoU = 0.4454, Dice = 0.5103) coupled with uncertainty-based selective abstention (90.27% abstention required to achieve 100% precision).

### Contribution 3: Grounded Evidence Retrieval & Operational Explanation
An evidence retrieval mechanism that links degraded micrographs to comparable high-quality reference peers ($N=55$ cohort context, 100% valid evidence availability) and generates deterministic, operational corrective actions (e.g., beam re-alignment, astigmatism correction, re-acquisition requests).

### Contribution 4: Reproducible Provenance-Aware Platform Architecture
A full-stack, research-grade software platform (SCI-INTEL) integrating the complete 17-stage research lifecycle, dual-representation vector indexing (FAISS), multi-image duplicate analysis, and append-only tamper-evident audit logging with sub-30 ms latency ($23.40\text{ ms}$ mean, $28.30\text{ ms } P_{95}$) verified by 509 automated tests.

---

## Strict Non-Claims (Forbidden Language)

The manuscript MUST NOT make the following claims under any circumstances:

1. **NO Clinical or Diagnostic Claims:** Do not claim medical diagnosis, clinical pathology validation, or prognostic accuracy.
2. **NO Physical Defect Confirmation:** Model-derived suspicious regions and bounding boxes reflect visual and statistical saliency anomalies; they are not confirmed physical material defects.
3. **NO Expert Validation Claims:** Do not claim prospective expert reader, microscopist, or metallurgist validation.
4. **NO Universal Invariance:** Do not claim universal acquisition invariance or complete bias elimination. The system reduced the observed gap under the evaluated protocols.
5. **NO State-of-the-Art / Best-Method Claims:** Do not describe SCI-INTEL or any module as the "best existing method", "optimal combination", or "state-of-the-art".
6. **NO Guaranteed Evidence:** Do not generalize 100% evidence availability beyond the evaluated $N=55$ cohort.
7. **NO Perfect Duplicate Detection:** Duplicate cascade combines exact hashes and SSIM/MAE heuristics; it is not theoretically error-free.
8. **NO Autonomous Decisions:** Human curatorial review remains the sole authoritative decision-maker; the platform only suggests and routes actions.
