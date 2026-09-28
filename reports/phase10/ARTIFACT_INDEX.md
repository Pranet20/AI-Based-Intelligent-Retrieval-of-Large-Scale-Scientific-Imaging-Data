# Research Artifact Index & Provenance Catalogue

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Status:** COMPLETE & CHECKSUM-VERIFIED  

---

## 1. Overview & Directory Structure

This index catalogs the major frozen research artifacts across all 9 prior phases. All listed files have been cryptographically verified byte-for-byte identical via SHA-256 against authoritative historical freeze manifests.

---

## 2. Master Research Artifact Table

| Artifact Name | Phase | Relative Path | Cryptographic SHA-256 | Primary Research Role |
| :--- | :--- | :--- | :--- | :--- |
| **`hcci_manifest.parquet`** | Phase 1 | `data/manifests/hcci_manifest.parquet` | `265cfa419ba8b89e7e17409426f8664ef5752c009bb457e5d23e590059e0a297` | Ground truth metadata manifest for 774 physical HCCI micrographs. |
| **`carinthia_manifest.parquet`** | Phase 1 | `data/manifests/carinthia_manifest.parquet` | `83b4b5eef92723bbffc5e9bc99c9efb0113c1a2f643e2f5ee87a41496a77d13e` | Ground truth manifest for 4,591 Carinthia SEM industrial defect micrographs. |
| **`hcci_dinov2_embeddings.parquet`** | Phase 2 | `data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet` | `1daaa32104526d17b5f62df94aa7d7bc9e0a6d091eb733b8b1a8d0525ee82121` | Pre-extracted 384-d L2-normalized DINOv2 visual representations for HCCI corpus. |
| **`carinthia_dinov2_embeddings.parquet`**| Phase 2 | `data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet` | `374d6f517336cb8796ee5c6dca50a986cb4fcf05492e59ee7f6fa6e1ba0f7415` | Pre-extracted 384-d L2-normalized DINOv2 visual representations for Carinthia corpus. |
| **`combined_IndexFlatIP.faiss`** | Phase 3 | `data/processed/indexes/combined_IndexFlatIP.faiss` | `2c4df55fb151c89fe325fbe3d93d39fc174b8829bfef1e52ef0e2db5e263d9ba` | Exact inner product vector search index for 5,365 combined embeddings. |
| **`combined_HNSW_M16_ef128.faiss`** | Phase 3 | `data/processed/indexes/combined_HNSW_M16_ef128.faiss` | `e03e1a0ae502213e2f099fa77ea5d15a9937d5718df1f7fc1b1b3699b803623f` | Hierarchical Navigable Small World approximate nearest neighbor vector index. |
| **`best_checkpoint_seed42.pt`** | Phase 4 | `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` | Trained linear projection adapter weights (seed 42, 68.15% gap reduction). |
| **`hcci_instrument_splits.json`** | Phase 4 | `data/processed/phase4/splits/hcci_instrument_splits.json` | `aa8f71424c538a7c2e39ea51d95e0c5d5e23652615469ad01ceab2b8f81bbdf1` | Anti-leakage partition splits ensuring no specimen or condition leakage. |
| **`phase4_evaluation_results.json`** | Phase 4 | `data/processed/phase4/metrics/phase4_evaluation_results.json` | `a3286395b0fe20cb3997e065582f6e996f014e7a83d3663a830959f6d649cf1a` | Comprehensive evaluation results across multi-seed adapter experiments. |
| **`phase5_results.json`** | Phase 5 | `artifacts/phase5/metrics/phase5_results.json` | `e2a4a35041ff34e00b3f81512db45759efc9b0e1378875ec82312b509ef4848d` | Authoritative hybrid retrieval benchmark metrics (Metadata MRR: 0.3443). |
| **`score_calibrator.json`** | Phase 5 | `artifacts/phase5/calibration/score_calibrator.json` | `378033c4f74d08194cf3ee3b24f5c9e4210e78c8ea7b7d03a56cf9e6ec54d026` | Empirical CDF calibration spline knots (contains grid knot 4907 = 0.4907). |
| **`phase6_results.json`** | Phase 6 | `artifacts/phase6/phase6_results.json` | `9b3624d6735e5d17967b2d2db73b1853d9e4c1eaae0b3ffaf76722d579ba639f` | Multi-track screening outputs: 769 clusters, 764 singletons, 5 pairs. |
| **`duplicate_pairs.parquet`** | Phase 6 | `artifacts/phase6/duplicate_pairs.parquet` | `be269477c7f3e8f804369be37c14a2a16086f671df245b736b76174bb05a7e17` | Pairwise duplicate verification cascade candidates and Hamming metrics. |
| **`review_queue.json`** | Phase 6 | `artifacts/phase6/review_queue.json` | `971ef28a07cff8fbf778b4081c206bb403e0541d1a1b029ff100ca995ddadff2` | Prioritized triage queue ranking based on composite risk and novelty. |
| **`database_schema.sql`** | Phase 8 | `artifacts/phase8/database_schema.sql` | `977f6b907c08ddabde5dd77b5a8397a738a0cbe0c9cb4cf8cfc65691079fc70c` | Production PostgreSQL DDL schema with constraints, indexes, and FKs. |
| **`final_frozen_checksums.json`** | Phase 8 | `artifacts/phase8/final_frozen_checksums.json` | `e9f2913e2bb9e320f78dd5a65383a54b9d0344d93d3d63b2fba6400ff50ef502` | Master checksum registry for all 110 Phase 1–7 frozen research artifacts. |
| **`PHASE9_MASTER_MANUSCRIPT.md`** | Phase 9 | `reports/phase9/PHASE9_MASTER_MANUSCRIPT.md` | `a78f8f696b992200ce70cbb1e93c422d76d0068c3c6112e3dae10d31b9d734bf` | Authoritative 10-section peer-reviewed research manuscript. |

---

## 3. Forensic Traceability & Checksum Assurance

To verify that any on-disk artifact matches its frozen state:
```bash
python scripts/reproduce/validate_release.py --verify-only
```
This guarantees bit-for-bit mathematical immutability across the entire scientific archive.
