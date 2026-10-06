# SCI-INTEL: Experiment Registry & Research Question Inventory

**Document**: `EXPERIMENT_INVENTORY.md`  
**Location**: `/research/redefinition/EXPERIMENT_INVENTORY.md`  
**Standard**: IEEE Transactions on Pattern Analysis and Machine Intelligence / Open Science Guidelines  
**Date**: October 2026  
**Status**: COMPLETE HISTORICAL AUDIT & RE-EXECUTION BASELINE  

---

## 1. Research Questions & Evaluation Protocols

The platform investigates four primary research questions:

* **RQ1 (Representation Superiority)**: Does self-supervised foundation representation (DINOv2 ViT-S/14) outperform traditional supervised CNNs (ResNet-50) and perceptual hashes (pHash, dHash) on zero-shot scientific micrograph retrieval under identical evaluation splits?
* **RQ2 (Acquisition Robustness)**: Does contrastive acquisition projection adaptation (Phase 4) significantly reduce the cross-instrument acquisition geometry gap while preserving specimen identity across independent seeds?
* **RQ3 (Image Quality Risk Screening)**: Can physically grounded image indicators reliably detect and categorize focus blur, detector clipping, and signal degradation across controlled synthetic and natural microscopy datasets?
* **RQ4 (Multi-Stage Redundancy Efficiency)**: Does a hierarchical 6-stage redundancy cascade (Exact SHA-256 $\to$ pHash $\to$ dHash $\to$ DINOv2 Cosine) achieve near-instant deduplication with zero false dismissals?

---

## 2. Research Evidence Classification Standards

Every reported metric in the repository is strictly classified into one of four states:

1. **`VERIFIED RESULT`**: Directly executed and verified from an authoritative script with saved checkpoint, frozen dataset manifest hash, and reproducible output artifact.
2. **`HISTORICAL RESULT`**: Present in previous phase documentation/reports (Phases 1–13) but pending automated re-execution under the unified SCI-INTEL benchmark runner.
3. **`UNVERIFIED RESULT`**: Proposed or calculated under legacy or unconfirmed split conditions; cannot be cited in publication until verified.
4. **`DEMO RESULT`**: Synthetic or illustrative numbers used solely for interactive UI testing; strictly excluded from research claims.

---

## 3. Comprehensive Experiment Inventory

| Experiment ID | RQ | Method / Model | Dataset | Split | Evaluation Metric | Reported Value | Evidence Classification | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`EXP_RET_B0`** | RQ1 | Uniform Random Retrieval | HCCI | Held-out Zeiss | Recall@1 | 0.0013 | `VERIFIED RESULT` | COMPLETED |
| **`EXP_RET_B1`** | RQ1 | Perceptual Hash (pHash) | HCCI | Held-out Zeiss | Recall@1 | 0.4120 | `VERIFIED RESULT` | COMPLETED |
| **`EXP_RET_B2`** | RQ1 | Difference Hash (dHash) | HCCI | Held-out Zeiss | Recall@1 | 0.3879 | `VERIFIED RESULT` | COMPLETED |
| **`EXP_RET_B3`** | RQ1 | ResNet-50 Supervised | HCCI | Held-out Zeiss | Recall@1 | 0.9245 | `HISTORICAL RESULT`| COMPLETED |
| **`EXP_RET_B4`** | RQ1 | DINOv2 ViT-S/14 (Frozen) | HCCI | Held-out Zeiss | Recall@1 | 0.9481 | `HISTORICAL RESULT`| COMPLETED |
| **`EXP_RET_B5`** | RQ1 | DINOv2 + Metadata Fusion | HCCI | Held-out Zeiss | Recall@1 | 0.9612 | `HISTORICAL RESULT`| COMPLETED |
| **`EXP_ACQ_ROB`**| RQ2 | Phase 4 Adapter (Seed 42) | HCCI | Cross-Instrument | Recall@1 | 0.9784 | `VERIFIED RESULT` | COMPLETED |
| **`EXP_ACQ_GAP`**| RQ2 | Acquisition Gap Reduction | HCCI | Cross-Instrument | Gap Reduction | 68.15% ($p < 10^{-11}$) | `HISTORICAL RESULT`| COMPLETED |
| **`EXP_QUAL_SYN`**| RQ3 | Focus / Blur Detection | Synthetic | Controlled Perturbation | AUROC | 0.8803 | `HISTORICAL RESULT`| COMPLETED |
| **`EXP_QUAL_NAT`**| RQ3 | Natural Micrograph Risk | BBBC021 | 721 Micrographs | Normal Fraction | 96.8% | `VERIFIED RESULT` | COMPLETED |
| **`EXP_FAISS_LAT`**| MLOps | FAISS Exact IndexFlatIP | HCCI | 774 vectors | Latency | 0.096 ms | `VERIFIED RESULT` | COMPLETED |
| **`EXP_DEDUP_CAS`**| RQ4 | 6-Stage Cascade | HCCI | Full Dataset | Precision | 100.0% | `VERIFIED RESULT` | COMPLETED |

---

## 4. Experiment Detail Records

### Experiment Record: `EXP_ACQ_ROB` (Phase 4 Adaptation)
* **Experiment Name**: Acquisition-Robust Specimen Identity Retrieval
* **Version**: 4.0.0
* **Model**: DINOv2 ViT-S/14 with Linear Projection Head ($384 \to 384$, L2 norm)
* **Checkpoint Path**: `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt`
* **Checkpoint Hash (SHA-256)**: `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`
* **Dataset Manifest**: `data/manifests/hcci_manifest.parquet`
* **Split Configuration**: `data/processed/phase4/splits/hcci_instrument_splits.json`
* **Reproducibility Command**:
  ```bash
  python scripts/reproduce/reproduce_adapter.py --seed 42 --checkpoint data/processed/phase4/checkpoints/best_checkpoint_seed42.pt
  ```
* **Evaluation Output Artifact**: `data/processed/phase4/metrics/phase4_evaluation_results.json`
* **Metrics Recorded**:
  - Full Retrieval Recall@1: $0.9784$ (vs $0.9481$ baseline)
  - Full Retrieval Recall@5: $0.9948$
  - Full Retrieval Recall@10: $0.9987$
  - Full Retrieval MRR: $0.9856$
  - Cross-Instrument Mean Cosine Similarity: $0.842 \pm 0.031$ (vs $0.691 \pm 0.052$ baseline)

---

### Experiment Record: `EXP_RET_B4` (DINOv2 Baseline)
* **Experiment Name**: Zero-Shot Foundation Model Retrieval Baseline
* **Version**: 2.0.0
* **Model**: Frozen `dinov2_vits14` (384-D, PyTorch Hub)
* **Dataset**: HCCI (774 micrographs)
* **Artifact**: `data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet`
* **Evaluator**: `src/retrieval/evaluator.py`
* **Metrics Recorded**:
  - Recall@1: $0.9481$
  - Recall@5: $0.9845$
  - Precision@5: $0.8420$
  - MRR: $0.9632$
* **Status**: `HISTORICAL RESULT` $\to$ scheduled for automated re-run under Experiment Freeze 1.

---

### Experiment Record: `EXP_QUAL_NAT` (Microscopy Quality Indicators)
* **Experiment Name**: Natural 16-Bit Scientific Micrograph Quality Profiling
* **Version**: 6.1.0
* **Target Data**: BBBC021 Multi-Channel Micrographs (`Week10_40111`)
* **Evaluator**: `src/integrity/quality_indicators.py`
* **Indicators Computed**:
  - Focus Variance: Range $[19.0, 60.6]$
  - Shannon Entropy: Mean $5.27\text{ bits}$
  - Dynamic Range: Mean $141.0$ (normalized scale $[0, 255]$)
  - Clipping Ratio: $\le 0.0028$ ($< 0.3\%$)
  - High-Freq FFT Ratio: Mean $0.0027$
* **Composite Risk**: All evaluated real BBBC021 micrographs scored $\le 0.24$ (`NOMINAL`).
* **Status**: `VERIFIED RESULT` (verified live on disk).
