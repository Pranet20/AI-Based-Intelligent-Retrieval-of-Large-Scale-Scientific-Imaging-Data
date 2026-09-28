# Master Final Failure Mode & Artifact Catalog

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Exhaustive Cross-Phase Inventory of Evaluated Failure Modes and Mitigations

---

## 1. Master Failure Taxonomy Table

| Failure ID | Failure Description | Empirical Evidence | Affected Subsystem | Severity | Implemented Mitigation | Remaining Limitation |
| :---: | :--- | :--- | :--- | :---: | :--- | :--- |
| **FAIL-01** | Carbide / Void Morphological Ambiguity | 4 of 11 errors in held-out SEM test set | Visual Embedding | High | Multi-scale patch contextual pooling | Requires EDS elemental spectroscopy for physical separation |
| **FAIL-02** | BSE Detector Contrast Clipping | 3 of 11 errors in held-out SEM test set | Quality Screening | Medium | Histogram saturation rejection in Phase 6 | Unmitigated on raw corrupted inputs |
| **FAIL-03** | Beam Drift & Astigmatism Striping | 2 of 11 errors in held-out SEM test set | Quality Screening | High | Automated blur and edge-jitter screening | Cannot restore physically distorted scans |
| **FAIL-04** | Scale-Bar & Overlay Attention Incursion | 2 of 11 errors in held-out SEM test set | Token Preprocessing | Medium | Automated OCR bounding box masking | Marginal text incursions outside standard crop margins |
| **FAIL-05** | Minority-Class Neighborhood Dilution | 10 of 22 errors in Carinthia LOO benchmark | Vector Retrieval | High | Class-balanced macro evaluation reporting | Dense majority clusters (Class 3) envelop sparse margins |
| **FAIL-06** | Directional Scratch Feature Overlap | 4 of 22 errors in Carinthia LOO benchmark | Visual Embedding | Medium | Multi-scale structural feature aggregation | 1D high-aspect edge tokens share curvature |
| **FAIL-07** | Acquisition Metadata Confounding | R@1 drops from 0.9481 to 0.5896 under fusion | Multimodal Fusion | Critical | Metadata relegated to relational SQL filtering | Dense representation must remain purely image-derived |
| **FAIL-08** | DINOv2 Latent Angular Compression | Score margin AUROC = 0.5146 (near-random) | Uncertainty Triage | High | Replaced margin with Latent Distance $D_{\text{ref}}$ (AUROC = 0.7412) | Dense space cosine similarities tightly clustered (>0.90) |
| **FAIL-09** | Severe Objective Focal Drift (Defocus) | R@1 drops to 0.4528 (48% retention) | Acquisition Robustness| Critical | Laplacian variance blur gate ($\sigma_{\text{Lap}}^2 < 100$) | Ingestion must discard or flag severe defocus scans |
| **FAIL-10** | Cross-Modality Distribution Shift (TEM) | Zero-shot R@1 = 0.7642 (vs 0.9481 SEM) | Cross-Domain | High | Supervised contrastive fine-tuning (R@1 restored to 0.9104) | Cannot expect direct zero-shot transfer across SEM/TEM |
