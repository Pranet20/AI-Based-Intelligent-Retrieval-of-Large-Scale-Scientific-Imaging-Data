# Phase 13 Manuscript V2 Expansion Plan

**Document Version:** 1.0.0-phase13  
**Status:** DRAFTING / ROADMAP  
**Base Submitted Version:** v1.1.0-submission-ready (`reports/phase12/submission_package/`)  
**Target Submission Revision:** Journal Major Revision / Camera-Ready Extension (v2.0.0)

---

## 1. Overview & Rationale

While the frozen submission `v1.1.0-submission-ready` provides a complete, mathematically verified, and reproducible description of the scientific data management platform, proactive hardening in Phase 13 generates substantial empirical evidence to address anticipated reviewer inquiries. 

The V2 manuscript evolution integrates these new empirical results without modifying any submitted historical science:
1. **ResNet-50 Benchmark Integration:** Positions DINOv2 against the gold-standard supervised CNN architecture.
2. **Exhaustive Ablation & Fusion Analyses:** Documents the non-linear multimodal gated MLP findings, reinforcing the negative result.
3. **Hardware & Corpus Scaling:** Incorporates the 100,000-vector FAISS scaling curve and sub-millisecond response latency.
4. **Empirical Robustness:** Adds perturbation stress-testing (blur, noise, compression, scale-bars).
5. **Human Curation Validation:** Introduces the double-blind 100-sample triage protocol with Cohen's Kappa $\kappa = 0.842$.

---

## 2. Chapter-by-Chapter Integration Strategy

| Manuscript Section | V1 Submission Baseline | Proposed V2 Enhancement | Authoritative Evidence File |
| :--- | :--- | :--- | :--- |
| **Section 1: Introduction** | Focuses on SEM metadata chaos and visual retrieval gaps. | Expanded to frame the general challenge of multi-modal feature interference in scientific repositories. | `reports/phase13/manuscript_v2/01_INTRODUCTION_V2.md` |
| **Section 3: Representation Learning** | Compares ViT backbones (DINOv2 B3 vs B4). | Adds full comparative analysis against supervised ResNet-50 (R@1=0.9245 vs 0.9481). | `reports/phase13/PHASE13_VISUAL_BASELINE_REPORT.md` |
| **Section 4: Multimodal Fusion** | Linear late fusion results demonstrating degradation. | Adds non-linear gated MLP fusion evaluation (R@1=0.5896), confirming fundamental feature space divergence. | `artifacts/phase13/nonlinear_fusion_results.json` |
| **Section 5: Anomaly & Curation** | Algorithmic detector thresholds and ROC curves. | Integrates the 100-micrograph double-blind human curation study ($\kappa = 0.842$, 42.5s review time). | `reports/phase13/PHASE13_HUMAN_CURATION_RESULTS.md` |
| **Section 6: Systems & Scaling** | Ingestion pipeline architecture and test pass rates. | Adds FAISS HNSW scaling stress tests up to $N = 100{,}000$ (0.317 ms latency, 15.64x speedup). | `reports/phase13/PHASE13_PERFORMANCE_REPORT.md` |
| **Section 7: Discussion** | High-level synthesis. | Adds forensic failure analysis (11 top-1 errors) and score margin calibration limitations. | `reports/phase13/PHASE13_FAILURE_ANALYSIS.md` |

---

## 3. Immutability & Traceability Assurance

All V2 revisions will be staged strictly under `reports/phase13/manuscript_v2/`. The Phase 12 submission package (`reports/phase12/submission_package/`) remains completely untouched as the authoritative historical baseline.
