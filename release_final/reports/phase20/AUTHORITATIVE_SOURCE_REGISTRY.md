# AUTHORITATIVE SOURCE REGISTRY & EVIDENCE TRACEABILITY MATRIX

**Project**: AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Document**: Phase 20 Authoritative Evidence Registry  
**Date**: 2026-09-27  
**Status**: PERMANENTLY_FROZEN  

---

## 1. Executive Registry of Core Scientific Domains

| Research Dimension | Authoritative Source Artifact | Phase | Key Invariant Metric | Verified Value | Scope / Boundary | Documented Limitation |
|---|---|---|---|---|---|---|
| **Dataset Counts** | `data/manifests/hcci_manifest.parquet`, `carinthia_manifest.parquet` | Phase 1 & 2 | Image Counts ($N$) | HCCI: 774; Carinthia: 4,591; SEM Nano: 21,169 | Micrographs with verified headers | Restricted raw distribution |
| **Model Architecture** | `reports/phase20/MODEL_CARD_DINOV2.md` | Phase 2 | Parameter Count | 22,056,576 parameters | Vision Transformer (ViT-S/14) | Frozen pretrained backbone |
| **Embedding Dimension** | `data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet` | Phase 2 | Latent Feature Dim ($D$) | 384 dimensions ($L_2$-normalized) | Penultimate [CLS] token | Unit hypersphere projection |
| **Phase 2 Retrieval** | `experiments/phase3/results/phase3_representation_benchmark_metrics.json` | Phase 3 | R@1 / MRR / P@5 | R@1=0.9481, MRR=0.9658, P@5=0.8708 | In-domain ferrous metallurgy | Baseline representation |
| **FAISS Query Latency** | `reports/phase3/latency_benchmark.csv` | Phase 3 | Query Latency (ms) | 0.096 ms (5k) to 0.317 ms (100k) | HNSW index (M=16, efSearch=128) | Synthetic vector scale |
| **Phase 4 Adaptation** | `data/processed/phase4/training_summary.json` | Phase 4 | Bias Gap Reduction | 68.15% ($p = 1.42 \times 10^{-12}$) | Supervised contrastive head | Scoped to same-specimen pairs |
| **Phase 5 Metadata** | `reports/phase9/PHASE9_FINAL_MRR_VERIFICATION_REPORT.md` | Phase 9 | Authoritative MRR | MRR = 0.3443396 (R@1 = 0.0519) | Unnormalized instrument logs | Late fusion degraded R@1 |
| **Phase 6 Integrity** | `artifacts/phase6/curation_summary.json` | Phase 6 | Focus AUROC / Duplicates | AUROC = 0.8803; 0 exact duplicates | Tenengrad gradient energy | 769 natural clusters |
| **Phase 7 Benchmark** | `experiments/phase3/results/phase3_representation_benchmark_metrics.json` | Phase 7 | Multi-Seed R@1 | R@1 = 0.9418 ± 0.0059 | Held-out instrument split | Contrastive projection |
| **Phase 13 Baselines** | `experiments/phase13/p13_exp01_multimodal_fusion/p13_exp01_metrics.json` | Phase 13 | Multimodal Ablation | Gated MLP: 0.5896; Cross-Attn: 0.6132 | Complex neural fusion | H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol |
| **Phase 14 Cross-Domain** | `reports/phase14/PHASE14_CROSS_DOMAIN_RESULTS.csv` | Phase 14 | Cross-Domain LOO R@1 | Micro R@1=0.9952, Macro R@1=0.9090 | Carinthia defect SEM (6 classes) | Class imbalance penalty |
| **Phase 15 Multimodal** | `reports/final_closure/FINAL_CLOSURE_MATRIX.csv` | Phase 15 | Late Fusion vs Visual | Visual: 0.9481 vs Fusion: 0.6274 | Inverted metadata index | Visual-first retained |
| **Phase 16 Production** | `reports/final_closure/PHASE18_LOAD_TEST_REPORT.md` | Phase 16 | Synthetic Throughput | Peak: 67.61 req/s (0 errors / 600 reqs) | Host-side FastAPI TestClient | Not cloud certification |
| **Phase 17 Intelligence** | `reports/phase17/PHASE17_INTELLIGENCE_VALIDATION_REPORT.md` | Phase 17 | Explainability & Provenance | 100% provenance event audit logging | Modular curator workbench | Synthetic EDS stubs only |
| **Phase 18 Readiness** | `reports/phase18/PHASE18_SECURITY_AUDIT.md` | Phase 18 | RBAC & Backup RTO | 5/5 RBAC passed; Restore: 0.0077 s | Host infrastructure specs | Cloud/Docker not executed |
| **Phase 19 Validation** | `reports/phase19/PHASE19_EXPERIMENT_REGISTRY.json` | Phase 19 | External Transfer | Micro R@1=0.9952; Nanoscience MMD^2=0.3120 | Zero-shot unadapted DINOv2 | Minority class drop-off |
| **Human Review** | `reports/final_closure/P19_HUMAN_VALIDATION_PROTOCOL_AUDIT.md` | Phase 19 | Actionability Yield | 91.67% yield (110/120); Cohen's $\kappa=0.8420$ | Double-blinded review | Zero label leakage |
| **Uncertainty Signal** | `reports/final_closure/P19_UNCERTAINTY_CALIBRATION_AUDIT.md` | Phase 19 | $D_{\text{ref}}$ Separation | In-domain: 0.2410 vs External: 0.5120 | Continuous geometric distance | Calibration not claimed |
| **Dataset Rights** | `reports/final_closure/FINAL_DATASET_RIGHTS_MATRIX.csv` | Phase 19 | Governance Status | 1 Fully Open (CC BY 4.0); 7 Restricted | Redistribution compliance | Manifest-only redistribution |
| **Limitations** | `reports/final_closure/FINAL_LIMITATIONS.md` | Phase 19 | Declared Count | 6 Substantive Limitations | Platform-wide operational boundaries | Permanent boundary register |
| **Reproducibility** | `reports/final_closure/PERMANENT_RELEASE_FREEZE.md` | Phase 20 | Test & Checksum Pass Rate | 190/190 tests passed; 145/145 historical | Independent two-pass verify | Zero historical mutations |
| **Final Claims** | `reports/phase19/FINAL_CLAIM_EVIDENCE_GRAPH_V3.json` | Phase 20 | Graph Claim Status | 22 claims mapped; 0 unsupported | Complete claim traceability | CLIP/ResNet descriptive only |

---

## 2. Comprehensive Claim Traceability Table

```text
CLAIM-RQ1: Supported | DINOv2 ViT-S/14 R@1=0.9481, MRR=0.9658 (vs ResNet-50 0.9245)
CLAIM-RQ2: Supported with Limitations | SupCon bias reduction 68.15% (p=1.42e-12, paired t-test)
CLAIM-RQ3: Supported | FAISS HNSW sub-millisecond search (0.096 to 0.317 ms)
CLAIM-RQ4: Supported | Authoritative metadata MRR=0.3443 on unnormalized logs
CLAIM-RQ5: Supported | Tenengrad focus AUROC=0.8803; 0 bitwise-exact duplicates on HCCI (769 natural clusters comprising 764 singleton clusters and 5 two-image near-duplicate/review clusters)
CLAIM-RQ6: Removed from Claims | Multimodal neural fusion degraded performance (H1 not supported)
CLAIM-RQ7: Supported | Active queue curation reduces workload by 41.2% (kappa=0.856)
CLAIM-P18-CLOUD: Not Executed | Host-side cloud-deployable architecture validated (zero cloud credentials)
CLAIM-P18-DOCKER: Not Executed | Container specifications validated on host (daemon inactive)
CLAIM-P18-LOAD: Supported with Limitations | Controlled host-side load test up to 250 requests (67.61 req/s peak)
CLAIM-P18-RBAC: Supported | 5/5 RBAC authorization and JWT security tests passed
CLAIM-P19-01: Supported with Limitations | Zero-shot Carinthia Micro R@1=0.9952, Macro R@1=0.9090
CLAIM-P19-02: Supported | MMD^2=0.3842 (Defect), 0.3120 (Nano), 0.5410 (TEM, p=0.0001)
CLAIM-P19-03: Supported with Limitations | Robust to noise (96.66%); breaks at blur sigma=3.0 (69.83%)
CLAIM-P19-04: Supported | Duplicate F1=0.9810, Focus AUROC=0.8640, Novelty AUROC=0.8910
CLAIM-P19-05: Supported | Focus quality screening generalizes out-of-domain without calibration
CLAIM-P19-06: Supported with Limitations | Embedding novelty detects shift; FPR at 95% TPR = 24.50%
CLAIM-P19-07: Supported with Limitations | Latent D_ref separation ratio 2.12x; probability calibration not claimed
CLAIM-P19-08: Supported | Double-blinded human curation review yield 91.67% (kappa=0.8420)
CLAIM-P19-09: Supported | Held-out batch ingestion at 14.80 img/s with 100% SHA-256 provenance
CLAIM-P19-10: Descriptive Only | DINOv2 Micro R@1=0.9952 vs CLIP 0.7840 and ResNet 0.6420 (inferential p demoted)
CLAIM-P19-EDS: Not Executed | Physical EDS validation not executed (synthetic stubs for engineering only)
```
