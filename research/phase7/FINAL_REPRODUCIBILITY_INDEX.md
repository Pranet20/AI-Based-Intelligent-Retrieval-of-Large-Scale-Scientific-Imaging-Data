# Phase 7 — Final Reproducibility Index & Evidence Registry

**Project:** AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images  
**Standard:** IEEE Scientific Reproducibility & FAIR Principles  
**Status:** REPRODUCIBLE & CRYPTOGRAPHICALLY SEALED  

---

## 1. Phase-Wise Evidence Ledger

| Phase | Description | Canonical Protocol | Results Artifact | Manifest / Split Reference | Cryptographic Seal | Status |
|:---:|:---|:---|:---|:---|:---|:---:|
| **Phase 1** | Dataset Ingestion & Partitioning Freeze | Ingestion Protocol 1 | `DATASET_FREEZE_REPORT.md` | `FINAL_IMAGE_MANIFEST.json` (6,085 imgs) | `6c2627c65fef8df0a78cd55f5b41dbc47fc3a043651bebb20a3d540765adbbe5` | **FROZEN / PASS** |
| **Phase 2** | Cross-Instrument Same-Specimen Retrieval | Protocol U Freeze 1 | `retrieval_results.csv` | `hcci_instrument_splits.json` (427/135/212) | `83b276d8d7e060a618adc6590c5891300a4e28298c86c82747f00a3dccd7f361` | **FROZEN / PASS** |
| **Phase 3** | Acquisition-Geometry Robustness Evaluation | Geometry Protocol 1 | `geometry_results.csv` | 212 paired queries across instruments | Verified in Phase 3 Seal | **FROZEN / PASS** |
| **Phase 4** | Quality Assessment & Controlled Anomaly Screening | Phase 4 Freeze 1 | `quality_metrics.csv` | `synthetic_manifest.csv` (2,750 imgs) | `3a5b7f6d376c11b472742a9c6abd43271cf1f539de39dfe66f3876e49dcb2947` | **FROZEN / PASS** |
| **Phase 5** | Scientific Evidence & Explanation Intelligence | Phase 5 Freeze 1 | `evidence_benchmark_results.json` | `phase5-thresholds-v1.0` config | `93e5520120356ec584771eda2a94b9889af9f932de1556674b8c7c4df2141996` | **FROZEN / PASS** |
| **Phase 6** | Integrated Evaluation & Documentation Freeze | Phase 6 Freeze 1 | `PHASE6_INTEGRATED_EVALUATION_REPORT.md` | $N=55$ evaluation cohort | `b416bb6179a754e841b859fe9552d3c7f3a3703558426bbbb4ce479f13bd2780` | **FROZEN / PASS** |
| **Phase 7** | Final Scientific Synthesis & Manuscript Preparation | Synthesis Protocol 1 | `SCI_INTEL_IEEE_MANUSCRIPT_DRAFT.docx` | Full repository synthesis | To be generated | **ACTIVE / READY** |

---

## 2. Model Checkpoint Provenance

All model representations are evaluated from frozen, immutable checkpoints:
1. **DINOv2 ViT-S/14**: Frozen Torch Hub checkpoint (`dinov2_vits14`), patch size 14, feature dimension 384. Weights frozen.
2. **Phase-4 Adapter (Seed 42)**: `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` (SHA-256 verified).
3. **Phase-4 Adapter (Seed 123)**: `data/processed/phase4/checkpoints/best_checkpoint_seed123.pt` (SHA-256 verified).
4. **Phase-4 Adapter (Seed 2024)**: `data/processed/phase4/checkpoints/best_checkpoint_seed2024.pt` (SHA-256 verified).
5. **No Learned Fusion Weights**: Zero fusion network weights exist; combination is strictly deterministic.
