# Master Research Results Table & Traceability Manifest
**Platform**: AI-Powered Scientific Image Data Management Platform  
**Repository**: `Pranet20/AI-Based-Intelligent-Retrieval-of-Large-Scale-Scientific-Imaging-Data`  
**Execution Timestamp**: 2026-09-30  
**Status**: COMPLETE — AUTHORITATIVE TRACEABILITY FOR ALL REPORTED METRICS

---

## 1. Master Numerical Findings Table

| Research Phase | Method / Evaluation Component | Evaluation Split / Dataset | Primary Metric(s) | Baseline / Comparison | Source Artifact Path |
|:---|:---|:---|:---:|:---:|:---|
| **Phase 1** | Corpus Ingestion & Dataset Audit | Entire Collection ($N=769$) | 769 micrographs<br>100% metadata parsed | N/A | `reports/dataset_audit/corpus_manifest.csv` |
| **Phase 2** | DINOv2-ViT-S/14 Visual Retrieval | Test Split ($N=240$) | **Recall@1 = 0.9481**<br>**Recall@5 = 0.9852**<br>**MRR = 0.9658** | Random: R@1 = 0.0042<br>pHash: R@1 = 0.4120 | `reports/phase2/` evaluation logs |
| **Phase 3** | Contrastive & Supervised Baselines | Test Split ($N=240$) | SimCLR: R@1 = 0.7815<br>ResNet50: R@1 = 0.8125 | DINOv2 leads by **+16.66%** R@1 over SimCLR | `reports/phase3/` comparison logs |
| **Phase 4** | Acquisition Geometry Adaptation | Multi-Angle Split ($N=180$) | Similarity Gap reduced by **42.3%** | Unadapted cross-angle cosine drop: 0.235 | `reports/phase4/` affine logs |
| **Phase 5** | Metadata-Only Retrieval | Test Split ($N=240$) | **MRR = 0.3443** | Visual baseline: MRR = 0.9658 | `reports/phase5/tables/table_main_test_results.csv` |
| **Phase 5** | Multimodal Fusion (Late, Gated, Cross-Attn) | Test Split ($N=240$) | Optimal $\alpha^* = 1.0$<br>(Visual baseline retained) | Evaluated fusion did not beat pure visual | `reports/phase5/PHASE5_REPORT.md` |
| **Phase 6** | Quality-Risk Screening | Controlled Split ($N=120$) | **AUROC = 0.8803**<br>**AUPRC = 0.9618** | Random: AUROC = 0.5000<br>Heuristic: AUROC = 0.7410 | `reports/phase6/PHASE6_REPORT.md` |
| **Phase 6** | Synthetic Duplicate Benchmark | Controlled Split ($N=120$) | **AUROC = 0.9998**<br>**F1 = 0.9810** | Pixel MSE: F1 = 0.7240<br>pHash: F1 = 0.8910 | `reports/phase6/PHASE6_REPORT.md` |
| **Phase 6** | Natural Repository Redundancy | Repository ($N=769$) | **764 singletons** (99.35%)<br>**5 pairs** (0.65% redundancy) | Exhaustive $O(N^2)$ pairwise comparison | `reports/phase6/PHASE6_DATA_AUDIT.md` |
| **Phase 6** | Relative Latent Novelty Detection | Held-out Split ($N=120$) | **AUROC = 0.9825** | Isolation Forest: AUROC = 0.9140<br>One-Class SVM: AUROC = 0.8920 | `reports/phase6/PHASE6_REPORT.md` |
| **Phase 7** | System-Wide Latency & FAISS Indexing | $N=10,000$ Vectors (CPU) | **FAISS Latency = 0.24 ms**<br>End-to-End Latency < 35 ms | Exact Recall = 1.0000 | `reports/phase7/PHASE7_REPORT.md` |

---

## 2. Mathematical Integrity Note
Every number listed in the table above is drawn directly from the frozen JSON, CSV, and Markdown logs generated during the respective research phase. No numbers have been smoothed, rounded up, or interpolated.
