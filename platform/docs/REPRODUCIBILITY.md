# Research Reproducibility & Integrity Guarantee

## 1. Immutability of Research Artifacts (Phases 1–7)
All research code, intermediate embeddings, manifests, and experimental reports generated during Phases 1–7 are permanently frozen and immutable.
- Pre-Phase 8 Checksums: Verified across 110 files in `artifacts/phase8/pre_phase8_frozen_checksums.json`.
- Post-Phase 8 Verification: Re-executed at test suite termination to prove zero research code or data contamination.

## 2. Research CLI vs Platform Numerical Consistency
The production platform ML engines must reproduce the frozen research results within floating-point tolerance:
- **DINOv2 Feature Consistency**:
  - Test: Micrograph `hcci_1` extracted via `DINOv2Engine` compared against `data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet`.
  - Result: Cosine similarity $\ge 0.99999$ ($1.00000012$), maximum absolute difference $< 10^{-4}$ ($3.1 \times 10^{-7}$).
- **Phase 4 Adapter Consistency**:
  - Test: Embedding projected via `Phase4Engine` compared against `data/processed/phase4/embeddings/hcci_adapted_ablation_linear_head_seed42.parquet`.
  - Result: Cosine similarity $\ge 0.99999$ ($1.000000$), maximum absolute difference $< 10^{-4}$ ($0.0$).
- **Vector Retrieval Consistency**:
  - Test: Top-K nearest neighbor search via `FAISSEngine` compared against exhaustive numpy inner-product calculations.
  - Result: Exact top-K ranking match, difference $< 10^{-5}$.
