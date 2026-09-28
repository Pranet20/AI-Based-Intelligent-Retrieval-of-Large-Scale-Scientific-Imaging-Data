# Phase 13 — Cross-Domain Representation & Generalization Report

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 13 — Post-Submission Research Hardening  
**Document ID:** `phase13_cross_domain_report_001`  
**Date:** September 2026  
**Status:** Certified V2 Empirical Report  

---

## 1. Executive Summary & Reviewer Risk R4 Resolution

Reviewer Risk R4 asked whether the learned representations generalize beyond the cast iron metallurgy domain, and whether the system can distinguish between disparate scientific imaging distributions without semantic confusion.

To resolve this concern, Phase 13 evaluated cross-domain retrieval and manifold geometry between two open, independently acquired scanning electron microscopy archives:
1. **Primary In-Domain Archive:** High-Chromium Cast Iron (HCCI, $N=774$ physical micrographs, metallurgy).
2. **External Domain Shift Benchmark:** Carinthia SEM ($N=4,591$ PNG micrographs, semiconductor wafer manufacturing defects).

---

## 2. Cross-Domain Retrieval & Manifold Separation Matrix

| Evaluation Pathway | Source Domain $\to$ Query Target | Sample Size ($N$) | Evaluation Metric | Measured Value | Scientific Interpretation |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **In-Domain (Metallurgy)** | HCCI $\to$ HCCI | 774 | Recall@1 / MRR | **0.9819 / 0.9894** | Near-perfect zero-shot material retrieval |
| **In-Domain (Semiconductors)**| Carinthia $\to$ Carinthia | 4,591 | Micro-Recall@1 / MRR | **0.9952 / 0.9965** | Near-perfect defect morphology retrieval |
| **Cross-Domain Separation** | HCCI Centroid vs. Carinthia Centroid | Combined (5,365) | Centroid Cosine Distance | **0.5842** | Distinct, well-separated visual manifolds |
| **Cross-Domain Retrieval Crossover**| HCCI Query $\to$ Combined Pool | 774 queries | Cross-Domain False Match Rate | **0.0000 (0 / 774)** | Zero semiconductor images retrieved as metallurgy |
| **Cross-Domain Retrieval Crossover**| Carinthia Query $\to$ Combined Pool | 4,591 queries | Cross-Domain False Match Rate | **0.0000 (0 / 4,591)**| Zero metallurgy images retrieved as wafer defects |

---

## 3. Scientific Implications & Terminology Distinction

1. **Clear Domain Boundary:**  
   The cosine separation of **0.5842** demonstrates that self-supervised foundation representations naturally partition heterogeneous scientific imaging archives by physical domain without requiring fine-tuning or domain classifiers.
2. **Zero Semantic Crossover:**  
   When querying a unified multi-dataset index ($N=5,365$ embeddings), top-ranked retrieval results exhibit **0.0000 cross-domain false matches**: metallurgy queries retrieve exclusively metallurgy micrographs, and wafer defect queries retrieve exclusively wafer defects.
3. **Distribution Shift vs. Anomaly Distinction:**  
   In accordance with the Phase 11 terminology standard, Carinthia micrographs are recognized as **cross-corpus distribution shift** relative to HCCI, rather than "scientific anomalies." Treating cross-domain images as anomalies would mischaracterize distinct scientific disciplines as defective specimens.
