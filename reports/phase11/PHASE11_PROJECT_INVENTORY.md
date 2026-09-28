# Phase 11 — Project Inventory & Forensic Research Index

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Audit Scope:** Independent Scientific / Paper-Quality Audit (Phases 1–10)  
**Date:** September 2026  
**Auditor Persona:** Independent Senior Scientific Reviewer (TPAMI / TBD / TAI / Materials Informatics Standard)  

---

## 1. Executive Summary & Inventory Scope

This inventory catalogs the complete forensic baseline across all research phases (1–10), documenting every frozen research artifact, configuration file, manifest, dataset, report, model checkpoint, and release deliverable. All components listed under `FROZEN` are cryptographically verified via SHA-256 and treated as strictly read-only for this audit.

---

## 2. Research Artifacts Inventory (Phases 1–10)

| Phase | Artifact Name | Path | Type / Format | Status | Cryptographic Reference / Checksum | Relevance to Scientific Claims |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | HCCI Manifest (Parquet) | `data/manifests/hcci_manifest.parquet` | Columnar Data | `FROZEN` | `265cfa419ba8b89e...` | Ground-truth metadata and split mapping for 774 physical HCCI SEM images. |
| **Phase 1** | HCCI Manifest (CSV) | `data/manifests/hcci_manifest.csv` | Tabular Data | `FROZEN` | `990101 bytes` | Human-readable inspection format for metallurgy imaging conditions. |
| **Phase 1** | Carinthia Manifest | `data/manifests/carinthia_manifest.parquet` | Columnar Data | `FROZEN` | `83b4b5eef92723bb...` | Ground-truth defect labels for 4,591 industrial SEM defect images. |
| **Phase 1** | Count Reconciliation | `reports/dataset_audit/hcci_count_reconciliation.json` | JSON Audit | `FROZEN` | SHA-256 Verified | Reconciles 777 Excel records to 774 physical files (samples 10, 20, 30 missing). |
| **Phase 2** | HCCI DINOv2 Embeddings | `data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet` | Feature Vectors | `FROZEN` | `1daaa32104526d17...` | Foundation ViT-S/14 baseline embeddings (384-d, L2 normalized). |
| **Phase 2** | Carinthia Embeddings | `data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet` | Feature Vectors | `FROZEN` | `374d6f517336cb87...` | Foundation representations for defect classification and shift analysis. |
| **Phase 2** | Phase 2 Benchmark Report | `reports/phase2/PHASE2_REPORT.md` | Scientific Report | `FROZEN` | SHA-256 Verified | Authoritative baseline retrieval metrics (HCCI R@1=0.9819, MRR=0.9894). |
| **Phase 3** | Flat Vector Index | `data/processed/indexes/combined_IndexFlatIP.faiss` | Binary Index | `FROZEN` | `2c4df55fb151c89f...` | Exact brute-force inner product FAISS index (5,365 combined vectors). |
| **Phase 3** | HNSW Vector Index | `data/processed/indexes/combined_HNSW_M16_ef128.faiss` | Binary Graph | `FROZEN` | `e03e1a0ae502213e...` | Hierarchical graph index establishing 1.99x speedup at 1.000 recall. |
| **Phase 3** | Phase 3 Benchmark Report | `reports/phase3/PHASE3_REPORT.md` | Scientific Report | `FROZEN` | SHA-256 Verified | Vector search latency, memory footprint, and scaling trade-off benchmarks. |
| **Phase 4** | Adapter Checkpoint (Seed 42) | `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` | PyTorch Weights | `FROZEN` | `53ba60a317a140ce...fd0e62` | Trained linear adapter weights achieving 68.15% cross-acquisition gap reduction. |
| **Phase 4** | Adapter Checkpoint (Seed 123) | `data/processed/phase4/checkpoints/best_checkpoint_seed123.pt` | PyTorch Weights | `FROZEN` | `391fd18c95599a69...` | Multi-seed validation checkpoint for statistical variance quantification. |
| **Phase 4** | Adapter Checkpoint (Seed 2024)| `data/processed/phase4/checkpoints/best_checkpoint_seed2024.pt`| PyTorch Weights | `FROZEN` | `c5ebbc7187dd1e64...` | Multi-seed validation checkpoint for statistical variance quantification. |
| **Phase 4** | Instrument Splits | `data/processed/phase4/splits/hcci_instrument_splits.json` | JSON Split Map | `FROZEN` | `aa8f71424c538a7c...` | Strict cross-instrument partition (Helios Train, VEGA3 Val, Zeiss Test). |
| **Phase 4** | Phase 4 Evaluation Summary | `data/processed/phase4/metrics/phase4_evaluation_results.json` | JSON Metrics | `FROZEN` | `a3286395b0fe20cb...` | Core acquisition adaptation metrics across seeds and ablation heads. |
| **Phase 5** | Phase 5 Results | `artifacts/phase5/metrics/phase5_results.json` | JSON Metrics | `FROZEN` | `e2a4a35041ff34e0...` | Authoritative hybrid retrieval and metadata-only baseline (MRR=0.3443). |
| **Phase 5** | Score Calibrator | `artifacts/phase5/calibration/score_calibrator.json` | Calibration Knots| `FROZEN` | `378033c4f74d0819...` | Empirical CDF spline grid (contains knot 4907 = 0.4907). |
| **Phase 5** | Phase 5 Benchmark Report | `reports/phase5/PHASE5_REPORT.md` | Scientific Report | `FROZEN` | SHA-256 Verified | Comprehensive analysis of late fusion and visual dominance (Delta R@1=0.0). |
| **Phase 6** | Phase 6 Master Results | `artifacts/phase6/phase6_results.json` | JSON Metrics | `FROZEN` | `9b3624d6735e5d17...` | Multi-track screening: 769 clusters, 764 singletons, 5 pairs, quality AUROC=0.8803. |
| **Phase 6** | Redundancy Summary | `artifacts/phase6/redundancy_summary.parquet` | Columnar Data | `FROZEN` | `18669 bytes` | Graph connected components partition and canonical representative assignment. |
| **Phase 6** | Duplicate Pairs | `artifacts/phase6/duplicate_pairs.parquet` | Columnar Data | `FROZEN` | `39468 bytes` | Candidate near-duplicate pairs evaluated across 4-stage cascade. |
| **Phase 6** | Review Queue | `artifacts/phase6/review_queue.json` | JSON Queue | `FROZEN` | `23337 bytes` | Simulated prioritized triage queue ranking micrographs by composite risk. |
| **Phase 7** | Master Results JSON | `artifacts/phase7/MASTER_RESULTS.json` | JSON Metrics | `FROZEN` | SHA-256 Verified | Unified publication benchmark integrating RQ1–RQ7 results and bootstrap CIs. |
| **Phase 7** | Publication Tables (CSV) | `reports/phase7/tables/*.csv` | Tabular Data | `FROZEN` | 7 CSV Files | Statistical significance tests, ablations, and cross-phase comparative matrices. |
| **Phase 7** | Publication Figures | `reports/figures/pub_*.png` | Visualizations | `FROZEN` | 12 Vector Figures | High-resolution publication plots (ROC curves, PR curves, t-SNE embeddings). |
| **Phase 8** | Database DDL Schema | `artifacts/phase8/database_schema.sql` | SQL DDL | `FROZEN` | `977f6b907c08ddab...` | PostgreSQL schema defining entities, indexes, and audit log foreign keys. |
| **Phase 8** | Platform Integration Tests | `platform/tests/test_*.py` | Test Code | `FROZEN` | 28 Tests Passed | API endpoints, RBAC, FAISS synchronization, and idempotency tests. |
| **Phase 8** | Closure Checksums | `artifacts/phase8/final_frozen_checksums.json` | Cryptographic Log| `FROZEN` | `110 Artifacts` | 110/110 Phase 1–7 frozen research artifacts cryptographic reference. |
| **Phase 9** | Master Academic Manuscript | `reports/phase9/PHASE9_MASTER_MANUSCRIPT.md` | Academic Draft | `FROZEN` | `a78f8f696b992200...` | Complete 10-section publication manuscript prepared for peer review. |
| **Phase 9** | Claim Evidence Map | `reports/phase9/PHASE9_CLAIM_EVIDENCE_MAP.md` | Provenance Audit | `FROZEN` | SHA-256 Verified | Maps all 68 quantitative manuscript claims directly to frozen evidence files. |
| **Phase 9** | Quantitative Claim Registry | `artifacts/phase9/final_quantitative_claim_registry.csv`| Tabular Data | `FROZEN` | 68 Claim Rows | Granular parameter and metric registry supporting the master manuscript. |
| **Phase 9** | Reference Audit | `artifacts/phase9/final_reference_audit.csv` | Tabular Data | `FROZEN` | 26 References | Verified citations with DOIs and formal bibliographic metadata. |
| **Phase 10** | Release Package | `release/` | Release Archive | `RELEASE_READY`| 52 Files Hashed | Clean, standalone distribution directory containing manifests, configs, and CLI. |
| **Phase 10** | Reproducibility Manifest | `artifacts/phase10/REPRODUCTION_MANIFEST.yaml`| YAML Manifest | `RELEASE_READY`| SHA-256 Verified | Declarative specification of hardware, seeds, runtimes, and expected metrics. |
| **Phase 10** | Secret Scan Report | `artifacts/phase10/SECRET_SCAN_REPORT.md` | Security Report | `RELEASE_READY`| PASSED | Confirms 0 private keys, API tokens, passwords, or restricted image files. |
| **Phase 10** | Validation CLI | `scripts/reproduce/validate_release.py` | Executable CLI | `RELEASE_READY`| Verified | One-command automated reproducibility and checksum validation tool. |

---

## 3. Configuration Inventory (`configs/`)

| Config File | Phase | Primary Purpose | Frozen Hyperparameters |
| :--- | :--- | :--- | :--- |
| `configs/datasets.yaml` | Phase 1 | Master registry for 6 scientific datasets | Dataset roles, modalities, source DOIs, and access statuses. |
| `configs/phase2.yaml` | Phase 2 | DINOv2 feature extraction parameters | Model: `dinov2_vits14`, dimension: 384, patch size: 14, batch size: 32. |
| `configs/phase3.yaml` | Phase 3 | FAISS vector index benchmarks | Metric: Inner Product, HNSW parameters ($M=16$, $efSearch \in \{16, 32, 64, 128\}$). |
| `configs/phase4.yaml` | Phase 4 | SupCon acquisition adapter training | Architecture: $384 \to 384$, $\tau=0.07$, epochs: 50, optimizer: AdamW, lr: $1e-4$. |
| `configs/phase5.yaml` | Phase 5 | Hybrid metadata fusion grid | Continuous/categorical weights, Gower distance, $\alpha$ grid $[0.0, 1.0]$. |
| `configs/phase6.yaml` | Phase 6 | Duplicate, quality, and novelty screening | Cascade thresholds ($H \le 12$, cosine $\ge 0.92$), isolation forest $k=5$. |
| `configs/phase7_experiments.yaml` | Phase 7 | Unified 18-experiment registry | Formal definition of experiments EXP_RET_B0 through EXP_REP_AUD (RQ1–RQ7). |
| `configs/reproducibility.yaml` | Phase 7 | Random seed bindings | Seeds: 42, 123, 2024. Hardware and CPU-only execution rules. |

---

## 4. Test Suite Inventory

- **Core Research Test Suite (`tests/`):** 190 tests covering dataset adapters, DINOv2 loading, FAISS search, adapter contrastive loss, metadata leakage protection, perceptual hashing, quality indicators, and Phase 7 benchmark validation.
- **Platform Test Suite (`platform/tests/`):** 28 tests covering FastAPI endpoints, JWT auth lifecycle, RBAC enforcement, PostgreSQL schema models, idempotent ingestion, and cryptographic parity.
- **Combined Test Status:** **218 / 218 PASSED** in 90.48s on Python 3.11.9.

---

## 5. Audit Traceability Matrix

Every scientific claim made in the manuscript ([PHASE9_MASTER_MANUSCRIPT.md](file:///c:/Users/Pranet/Downloads/Mini%20Project/reports/phase9/PHASE9_MASTER_MANUSCRIPT.md)) is referenced against this inventory. The subsequent sections of Phase 11 subject these artifacts to critical, skeptical peer-review evaluation.
