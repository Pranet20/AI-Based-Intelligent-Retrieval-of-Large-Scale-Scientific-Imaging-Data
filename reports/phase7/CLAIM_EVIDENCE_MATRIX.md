# Phase 7 — Comprehensive Claim-to-Evidence Matrix

**Experiment ID:** `phase7_publication_benchmark_001`  
**Purpose:** Formal publication-grade traceability mapping every scientific paper claim to its experimental protocol, dataset, metric, artifact path, evidence tag, and documented limitations.

---

| Claim # | Scientific Paper Claim | Target RQ | Dataset | Primary Metric | Authoritative Artifact | Evidence Tag | Documented Research Limitations |
| :---: | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| **C1** | Self-supervised DINOv2 provides robust zero-shot microscopy retrieval without task-specific tuning. | RQ1 | HCCI (Held-Out Zeiss Gemini) | Recall@1 = 0.9481, MRR = 0.9658, P@5 = 0.8708 | `artifacts/phase5/metrics/phase5_results.json` | `[NATURAL DATA]` | Pretrained externally; small general microscopy corpus compared to ImageNet. |
| **C2** | Acquisition-aware contrastive learning achieves a 68.2% measured reduction in within-vs-cross acquisition gap. | RQ2 | HCCI (Cross-Acquisition Pairs) | Gap: 0.1994 -> 0.0635, Ratio: 77.5% -> 93.1% | `reports/phase4/PHASE4_REPORT.md` | `[NATURAL DATA]` | Observational gap reduction; does not eliminate underlying physical optics variance. |
| **C3** | Generalization to unseen microscope optics improves deep-ranked precision (P@5 = 0.9053 vs. 0.8708). | RQ2 | HCCI (Held-Out Zeiss Gemini) | Precision@5 = 0.9053 +/- 0.0166 (p=0.0028) | `reports/phase4/PHASE4_REPORT.md` | `[NATURAL DATA]` | Evaluated across 3 alloy conditions; Zeiss instrument held-out but specimens share metallurgy. |
| **C4** | Late metadata fusion yields zero delta (Delta R@1 = 0.0) when visual features are saturated; optimal alpha=1.0. | RQ3 | HCCI (Validation & Test) | Delta R@1 = 0.0, Delta MRR = 0.0 across Groups A-F | `artifacts/phase5/metrics/phase5_results.json` | `[NATURAL DATA]` | Negative result; metadata does not improve saturated visual retrieval in HCCI. |
| **C5** | 4-stage cascade isolates duplicates with 100% precision and zero false positives across splits. | RQ4 | HCCI + Synthetic Benchmark | Cascade Prec = 1.000, FPR = 0.000, F1 = 0.6916 | `artifacts/phase6/phase6_results.json` | `[CONTROLLED SYNTHETIC BENCHMARK]` | Synthetic transformations are controlled mathematical approximations of real noise. |
| **C6** | Natural HCCI archive redundancy partitions into 769 clusters (764 singletons, 5 pairs) yielding 769 KEEP, 5 REVIEW. | RQ4 | HCCI (Full Corpus, N=774) | 769 KEEP (representatives), 5 REVIEW (duplicates) | `artifacts/phase6/redundancy_summary.parquet` | `[NATURAL DATA]` | Descriptive graph connected components; no human re-imaging ground truth. |
| **C7** | Image-derived quality indicators achieve AUROC=0.8803 and AUPRC=0.9742 on controlled synthetic degradations. | RQ4 | HCCI Synthetic Degradations (N=120) | Composite AUROC = 0.8803, AUPRC = 0.9742 | `artifacts/phase6/phase6_results.json` | `[CONTROLLED SYNTHETIC BENCHMARK]` | Statistical signal metrics; not direct physical sensor calibrations. |
| **C8** | Substantial domain shift separates SEM metallurgy from external semiconductor defect archives. | RQ5 | HCCI vs. Carinthia SEM | Mean Cosine Separation = 0.5842 to HCCI centroid | `reports/phase2/carinthia_evaluation_audit.json` | `[EXTERNAL DOMAIN SHIFT]` | Carinthia lacks acquisition header metadata; zero-shot shift analysis only. |
| **C9** | Diagnostic risk triage queue achieves 100% anomaly yield at top 10/25 inspection budgets. | RQ6 | Controlled Synthetic Review Queue | Precision@10 = 1.000, Precision@25 = 1.000 | `artifacts/phase6/phase6_results.json` | `[ENGINEERING MEASUREMENT]` | Evaluated against synthetic ground truth; natural queue reported as descriptive ranking. |
| **C10** | End-to-end framework and all reported experimental results reproduce bit-for-bit with 0 leakage. | RQ7 | All Registered Repositories | 84/84 checksum match, 10/10 leakage checks passed | `artifacts/phase7/frozen_checksums.json` | `[ENGINEERING MEASUREMENT]` | Single-platform automated reproduction script; hardware timing depends on CPU. |

---

### Integrity Notes on Evidence Classification
- `[NATURAL DATA]`: Measured directly on natural, unmanipulated micrographs collected from physical microscopes.
- `[CONTROLLED SYNTHETIC BENCHMARK]`: Rigorous controlled experiment with mathematically injected transformations and known ground truth.
- `[EXTERNAL DOMAIN SHIFT]`: Evaluation of representations under distribution shift across independent datasets without target retraining.
- `[ENGINEERING MEASUREMENT]`: Architectural, computational, and algorithmic performance properties (latency, yield, immutability).
