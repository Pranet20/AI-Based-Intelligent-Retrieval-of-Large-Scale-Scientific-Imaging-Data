# Post-Phase-11 Audit Revised Manuscript — Section 9: Limitations & Threats to Validity

**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase11_revised_limitations_v110`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Section 9 (Post-Phase-11 Audit Revision)  

---

# 9. Limitations & Threats to Validity

To preserve absolute scientific rigor and transparently bound our findings, we document six primary limitations:

1. **Modest Corpus Size & Single-Alloy Focus:** The in-domain metallurgical benchmark (HCCI) contains 774 physical micrographs across 3 macroscopic heat-treatment conditions of a single alloy family (High-Chromium Cast Iron). While dense across 67 acquisition permutations, total image volume is modest relative to web-scale computer vision datasets. The generalizability of the contrastive adaptation head across multi-alloy families (e.g., aluminum, titanium, superalloys) remains an open empirical question requiring multi-center validation.
2. **Missing Upstream Samples in Source Archive:** Micrograph sample indices 10, 20, and 30 were omitted from the author-deposited Zenodo archive prior to ingestion; our manifest accurately registers the 774 physical files, defusing potential discrepancy allegations.
3. **Absence of Co-Registered Physical ROIs:** Because individual micrographs possess unique `roi_id` values (`roi_1` to `roi_777`), evaluations measure cross-acquisition alloy condition invariance rather than registered pixel-to-pixel alignment across identical microstructural coordinates. In multiphase alloys with heterogeneous carbide distributions, local phase fractions naturally vary between fields of view.
4. **Metadata Heterogeneity Across External Repositories:** External scientific archives (such as Carinthia semiconductor micrographs) lack embedded TIFF acquisition parameter tags, precluding cross-dataset multimodal fusion benchmarks.
5. **Synthetic Quality Evaluations:** Quality risk indicators were validated on $N = 120$ controlled synthetic degradations (defocus blur, sensor noise, detector clipping); natural review queue candidates represent algorithmic outlier rankings rather than certified expert clinical or metallurgical defect labels.
6. **Docker Runtime Verification Limitation:** While local host-level Python 3.11 tests pass 218/218 with bit-exact numerical parity ($L_\infty < 1.0 \times 10^{-6}$), multi-container Docker deployment is documented and syntactically configured but was certified as `DOCKER_VALIDATION_NOT_EXECUTED` due to host daemon inactivity during the closure audit.
