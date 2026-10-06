# Phase 7 — Authoritative Evidence Index
## Comprehensive Audit and Provenance Traceability across Phases 1–6

**Generated:** 2026-10-06T06:29:46.540161+00:00
**Standard:** IEEE Research Reproducibility & Scientific Integrity Standards
**Status:** AUTHORITATIVE & FROZEN

---

## 1. Authoritative Evidence Catalog

| Phase | Artifact | Purpose | Dataset | Population | Protocol | Metric | Value | Hash (SHA-256) | Authority Status |
|:---:|:---|:---|:---|:---:|:---|:---|:---|:---|:---:|
| **1** | `FINAL_IMAGE_MANIFEST.json` | Master image index & metadata | HCCI, Carinthia, BBBC021 | 6,085 active micrographs | Dataset Ingestion Freeze 1 | Image count, SHA integrity | 6,085 verified | `6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5` | **AUTHORITATIVE** |
| **1** | `hcci_instrument_splits.json` | Instrument partition | HCCI | 774 SEM micrographs | Split Freeze 1 | Train / Val / Test counts | 427 / 135 / 212 | Verified in manifest | **AUTHORITATIVE** |
| **2** | `retrieval_results.csv` | Frozen cross-instrument retrieval | HCCI | 212 test queries, 100 gallery | Protocol U (unmasked distractors) | DINOv2 R@5 / MRR<br>Phase-4 R@5 / MRR | 0.9858 / 0.5200<br>0.9921 / 0.5261 | `83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361` | **AUTHORITATIVE** |
| **2** | Historical Protocol-M log | Retrieval with masked exclusion | HCCI | Historical test set | Protocol M (masked exclusion) | Historical R@1 / MRR | 0.9481 / 0.9658 | N/A (Superseded) | **HISTORICAL / NON-AUTHORITATIVE** |
| **3** | `geometry_results.csv` | Acquisition-geometry gap measurement | HCCI | 212 paired queries | Protocol U Geometry | DINOv2 Gap $\Delta$<br>Phase-4 Mean Gap $\Delta$<br>Gap Reduction | 0.2016<br>0.0681<br>66.23% ($p=5.03\times 10^{-36}$) | Verified in Phase 3 Seal | **AUTHORITATIVE** |
| **4** | `synthetic_manifest.csv` | Controlled synthetic artifact benchmark | HCCI | 2,750 micrographs | Phase 4 Synthetic Protocol | Artifact diversity, mask paths | 11 categories (250/cat) | `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947` | **AUTHORITATIVE** |
| **4** | `quality_metrics.csv` | Image-derived quality screening | HCCI | 1,100 test micrographs | Controlled Artifact Screening | DINOv2 Macro F1 / AUROC<br>Phase-4 Macro F1 / AUROC | 0.6837 / 0.8582<br>0.6323 / 0.8230 | Verified in Phase 4 Seal | **AUTHORITATIVE** |
| **4** | `localization_results.csv` | Spatial anomaly localization | HCCI | 500 test micrographs | Patch Saliency Slicing | Macro Mean IoU / Dice | 0.4454 / 0.5103 | `9654223242ced3fe9b3633a28958d85139f38dd9fc5b355fc545aab089117b45` | **AUTHORITATIVE** |
| **5** | `threshold_config.py` | Operational decision thresholds | Mathematical | 11-class simplex & entropy | Phase 5 Calibration | $\tau_{\text{conf}}, H_{\text{norm}}, \Delta$ | 0.40, 0.75, 0.10 | Version: `phase5-thresholds-v1.0` | **AUTHORITATIVE** |
| **5** | `PHASE5_EVIDENCE_HASH.txt` | Phase 5 Master Seal | HCCI | Multi-stage pipeline | Evidence Integrity Seal | Master Seal | `93e5520120356ec584771eda2a94b9889af9f932de1556674b8c7c4df2141996` | Verified | **AUTHORITATIVE** |
| **6** | `dual_representation_results.csv` | Modular composition comparison | HCCI | Test cohort | Architecture Evaluation | DINOv2 QC + Phase-4 Retrieval | Macro F1: 0.6837, R@5: 0.9921 | `e110106bb3562bebddb6c0eaf454e0860231914957b3bda3b4aeed694326220c` | **AUTHORITATIVE** |
| **6** | `counterfactual_evidence_results.csv` | Counterfactual evidence availability | HCCI | $N=55$ test queries | Conditions A, B, C | Condition B Availability | 100.0% (same-specimen peer) | `225cac12cfa7180ca6446eb43b37ae05ab5835c30e19f18d1e1511598283dd23` | **AUTHORITATIVE** |
| **6** | `latency_results.csv` | Stage-wise processing latency | HCCI | Serial ingestion pipeline | Benchmarking | Mean Complete Latency | 23.40 ms (P95: 28.30 ms) | `1a1b500848a1fe7225c523b2b5f6112459ae1f990d0d81b0c8887029bfcd0ca5` | **AUTHORITATIVE** |
| **6** | `PHASE6_FINAL_DOCUMENTATION_HASH.txt` | Phase 6 Documentation Seal | All | All Phase 6 artifacts | Documentation Freeze | Master Seal | `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780` | Verified | **AUTHORITATIVE** |

---

## 2. Policy on Historical & Superseded Values
- **Protocol-M Values (R@1 = 0.9481, MRR = 0.9658)**: Masked exclusion baseline from preliminary exploration; classified as **HISTORICAL / NON-AUTHORITATIVE**. Must not be directly compared with Protocol-U results.
- **Protocol-U Values (DINOv2 R@5 = 0.9858, Phase-4 R@5 = 0.9921)**: Authoritative frozen benchmark incorporating full unmasked distractors.
- **Registered Datasets (CIGRockSEM, SEM Nano)**: Classified as **NOT EVALUATED / REGISTERED ONLY**; excluded from manuscript empirical claims.