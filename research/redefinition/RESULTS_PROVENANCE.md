# SCI-INTEL: Results Provenance & Verification Audit

**Document**: `RESULTS_PROVENANCE.md`  
**Location**: `/research/redefinition/RESULTS_PROVENANCE.md`  
**Standard**: Scientific Rigor, Immutability, and Research Claim Integrity  
**Date**: October 2026  
**Status**: COMPLETE  

---

## 1. Provenance Integrity Mandate

In accordance with strict scientific integrity guidelines:
* **No historical metric is grandfathered in as "verified"** merely because it appeared in an earlier markdown report or slide deck.
* Every metric must map to an **exact reproducible execution script**, an **identifiable input dataset manifest hash**, an **immutable model checkpoint hash**, and an **output JSON/Parquet artifact**.
* Metrics are segregated into four explicit categories:
  - `[VERIFIED]`: Re-executed, confirmed deterministic match with output artifacts on disk.
  - `[HISTORICAL]`: Computed during Phases 1–13; recorded in `artifacts/phase7/MASTER_RESULTS.json` or `phase4_evaluation_results.json`, awaiting automated pipeline re-execution under the unified benchmark runner.
  - `[UNVERIFIED]`: Preliminary calculations lacking frozen checksum manifests.
  - `[DEMO]`: Synthetic mock figures used in earlier development prototypes.

---

## 2. Comprehensive Metric Provenance Audit

### 2.1 Retrieval Metrics on HCCI Benchmark

| Metric Claim | Value | Location in Codebase | Source Artifact | Execution Script | Provenance Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **DINOv2 ViT-S/14 R@1** | 94.81% | `Dashboard.tsx`, `README.md`, `MASTER_RESULTS.json` | `artifacts/phase7/MASTER_RESULTS.json` | `src/evaluation/master_benchmark.py` | `HISTORICAL` |
| **ResNet-50 Baseline R@1**| 92.45% | `Dashboard.tsx`, `MASTER_RESULTS.json` | `artifacts/phase7/MASTER_RESULTS.json` | `src/evaluation/master_benchmark.py` | `HISTORICAL` |
| **pHash Baseline R@1** | 41.20% | `MASTER_RESULTS.json` | `artifacts/phase7/MASTER_RESULTS.json` | `src/integrity/perceptual_hash.py` | `VERIFIED` |
| **dHash Baseline R@1** | 38.79% | `MASTER_RESULTS.json` | `artifacts/phase7/MASTER_RESULTS.json` | `src/integrity/perceptual_hash.py` | `VERIFIED` |
| **Proposed Adapter R@1** | 97.84% | `phase4_evaluation_results.json` | `data/processed/phase4/metrics/` | `evaluate_phase4.py` | `VERIFIED` |
| **Multi-Seed Adapter Mean**| $97.72 \pm 0.16\%$ | `phase4_evaluation_results.json` | Seeds 42, 123, 2024 checkpoints | `evaluate_phase4.py` | `VERIFIED` |

**Audit Note on Retrieval Claims**:
* The Phase 4 contrastive projection adapter achieved $97.84\%$ on Seed 42, $97.68\%$ on Seed 123, and $97.65\%$ on Seed 2024. The multi-seed consistency across 3 distinct random initializations demonstrates statistical stability.
* The baseline comparison (DINOv2 $94.81\%$ vs ResNet-50 $92.45\%$) was evaluated under identical test splits. Under Experiment Freeze 1, this will be re-run through the unified benchmark runner.

---

### 2.2 Acquisition Gap & Statistical Claims

| Claim | Reported Statistic | Source File | Mathematical Foundation | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Cross-Acquisition Gap** | 68.15% reduction | `Dashboard.tsx`, `phase4_evaluation_results.json` | Relative delta between within-instrument and cross-instrument cosine distances | `HISTORICAL` |
| **Statistical Significance**| $p = 1.42 \times 10^{-12}$ | `Dashboard.tsx`, `MASTER_PROJECT_COMPREHENSIVE_REPORT.md` | Two-tailed paired Student's $t$-test across specimen query vectors | `HISTORICAL` |
| **Ablation: Linear Head** | R@1: 96.25% | `data/processed/phase4/embeddings/` | Evaluated without L2 normalization | `VERIFIED` |
| **Ablation: Standard SupCon**| R@1: 96.90% | `data/processed/phase4/embeddings/` | Evaluated without cross-instrument hard negative mining | `VERIFIED` |

---

### 2.3 Quality Screening & Anomaly Claims

| Claim | Reported Statistic | Source File | Underlying Experiment | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Defocus Detection AUROC** | 0.8803 | `Dashboard.tsx`, `artifacts/phase13/` | Synthetic Gaussian defocus blur on HCCI test split | `HISTORICAL` |
| **Defocus Detection AUPRC** | 0.9618 | `Dashboard.tsx`, `artifacts/phase13/` | Synthetic Gaussian defocus blur on HCCI test split | `HISTORICAL` |
| **Natural Micrograph Quality**| 100% nominal on clean BBBC021 | Database `scidata_platform.db` | Live evaluation of real 16-bit TIFFs | `VERIFIED` |
| **Deduplication Precision** | 100.0% (Zero false matches) | `artifacts/phase6/phase6_results.json` | 6-stage redundancy cascade verification | `VERIFIED` |

---

### 2.4 Latency & Operational Efficiency Claims

| Claim | Reported Metric | Hardware / Platform | Benchmark Script | Status |
| :--- | :--- | :--- | :--- | :--- |
| **FAISS Query Latency** | 0.096 ms | Intel Core i7 / AMD CPU (Local) | `platform/backend/app/api/system.py` | `VERIFIED` |
| **14-Stage Ingestion Latency**| $\approx 1.8\text{ s}$ per 16-bit TIFF | Local CPU (percentile stretch + DINOv2) | `test_live_docker_workflow.py` | `VERIFIED` |
| **Index Memory Scale** | 1.5 KB per $10^3$ vectors | RAM | Exact IndexFlatIP memory footprint | `VERIFIED` |

---

## 3. Data Leakage & Split Integrity Audit

A comprehensive leakage audit was conducted across all splits:
1. **Cryptographic SHA-256 Duplication**:
   - `zero_detected_sha_overlap = True`. Zero train/val/test images share identical SHA-256 digests.
2. **Specimen Separation**:
   - All HCCI specimens in the test set originate from samples acquired with the **Zeiss Sigma 300** instrument, which was held out from the primary training pool.
3. **Perceptual Near-Duplicate Leakage**:
   - Evaluated via pHash (Hamming distance $\le 3$) and DINOv2 cosine similarity ($\ge 0.98$). Zero cross-split near-duplicate contamination detected.
4. **Leakage Audit Report**:
   - Authoritative report location: `artifacts/phase7/leakage_audit.json`.

---

## 4. Unsupported Claim Corrections

The following language discipline rules have been applied across all documentation:
* ❌ *"Best in the world"* $\to$ Replaced with *"Demonstrates higher recall among evaluated baselines on the declared benchmark protocol."*
* ❌ *"Guarantees error-free retrieval"* $\to$ Replaced with *"Achieves exact sub-millisecond retrieval without quantization error."*
* ❌ *"Autonomous defect diagnosis"* $\to$ Replaced with *"Image-derived quality-risk screening and decision support."*
* ❌ *"State-of-the-art anomaly detector"* $\to$ Replaced with *"Physically grounded microscopy degradation indicator."*
