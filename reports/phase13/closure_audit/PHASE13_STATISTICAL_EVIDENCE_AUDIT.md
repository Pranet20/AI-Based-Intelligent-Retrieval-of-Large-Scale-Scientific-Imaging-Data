# Phase 13 Statistical Evidence & Methodology Audit

**Document Version:** 1.0.0-closure  
**Audit Date:** 2026-09-27  
**Scope:** Statistical Validation of All Phase 13 Quantitative Claims  
**Audit Status:** `STATISTICALLY_DEFENSIBLE_WITH_SCOPING`

---

## 1. Executive Summary

This audit examines the statistical integrity, sample independence assumptions, test validity, and reporting rigor of all quantitative benchmarks introduced in Phase 13.

**Key Determinations:**
1. **Sample Independence Boundary:** In all retrieval benchmarks ($N = 212$ queries), individual micrographs are evaluated as image-level retrieval instances. They are **not** treated as independent physical metallurgical specimens, preventing unit-of-analysis inflation.
2. **Appropriate Avoidance of Unsound Hypothesis Tests:** Global ranking metrics ($R@1$, $MRR$, $P@5$) are reported as population descriptive parameters over the benchmark set; no misleading two-sample t-tests are fabricated.
3. **Formal Statistical Inference Confirmed:** Where inferential statistics are reported (Cohen's Kappa $\kappa = 0.842$, $95\%$ CI: $[0.758, 0.926]$ and margin AUROC $0.5146$), standard errors, confidence intervals, and test assumptions are mathematically verified.

---

## 2. Statistical Audit Inventory Table

| Experiment ID | Empirical Claim / Metric | Sample Size ($N$) | Unit of Analysis | Grouping / Split | Statistical Method / Test | Reported Statistic & Value | Confidence Interval / SE | Statistical Verdict |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| **P13-EXP-01** | ResNet-50 vs DINOv2 Retrieval | 212 queries / 5,365 gallery | Query micrograph | Split seed 42 | Exact top-$k$ ranking evaluation | R@1: 0.9481 vs 0.9245; MRR: 0.9658 vs 0.9542 | N/A (Descriptive population) | **VALID** |
| **P13-EXP-02** | Token Pooling Ablations | 212 queries | Query micrograph | Split seed 42 | Ablation ranking comparison | R@1: Full (0.9481), Patch (0.9151), CLS (0.8774) | N/A (Descriptive) | **VALID** |
| **P13-EXP-03** | Multimodal Gated MLP Fusion | 212 queries | Query micrograph | Split seed 42 | Non-linear ranking evaluation | R@1: 0.5896 vs 0.9481 ($\Delta = -0.3585$) | N/A (Descriptive) | **VALID (Negative Result)** |
| **P13-EXP-04** | Cross-Domain TEM Transfer | 100 queries / 1,100 gallery | Micrograph | Split 80/20 | Cosine similarity ranking | Zero-shot R@1 = 0.7642; Fine-tuned = 0.9104 | N/A (Descriptive) | **VALID (Scoped)** |
| **P13-EXP-05** | Robustness Perturbations | 212 queries $\times$ 5 conditions | Perturbed query | Split seed 42 | Perturbation sensitivity curve | R@1: Clean (0.9434) to Defocus (0.4528, 48% retention) | N/A (Descriptive) | **VALID (Controlled)** |
| **P13-EXP-06** | FAISS Vector Search Scaling | 100 queries $\times$ 5 scales | Search query run | Synthetic expansion | Mean search latency over 100 runs | Latency: 0.096ms to 0.317ms; Speedup: 1.55x to 15.64x | N/A (Engineering benchmark) | **VALID (Stress Test)** |
| **P13-EXP-07** | Forensic Failure Taxonomy | 11 error queries | Failed query | Split seed 42 | Categorical frequency analysis | 4 Carbide (36.4%), 3 BSE (27.3%), 2 Drift (18.2%), 2 Scale (18.2%) | N/A (Total failure census) | **VALID** |
| **P13-EXP-08** | Expert Human Curation Agreement | 100 triage micrographs | Curated image | 4 strata ($n=25$ each) | Pairwise Cohen's Kappa ($k=2$) | $\kappa = 0.842$, raw agreement = 91.0% | $SE = 0.0428$, 95% CI: $[0.758, 0.926]$ ($p < 0.0001$) | **VALID** |
| **P13-EXP-09** | Uncertainty Margin Calibration | 212 queries | Margin $\Delta S$ | Split seed 42 | Receiver Operating Characteristic (ROC) | AUROC = 0.5146; High-conf Acc = 95.28% | N/A (Non-parametric ROC) | **VALID (Negative Result)** |

---

## 3. Methodological Boundaries & Guidance for V2 Manuscript

1. **Micrograph Replicates vs Physical Specimens:**  
   Because multiple SEM fields of view originate from the same metallurgical sample mount, claims of generalized material properties are prohibited. Micrograph retrieval measures visual representation robustness, not specimen-level material variance.
2. **Controlled Perturbations vs Field Microscope Variations:**  
   The synthetic perturbations in P13-EXP-05 provide controlled mathematical stress-testing. They must be cited as *controlled synthetic perturbations* rather than field instrumentation measurements.
3. **Engineering Scalability vs Corpus Growth:**  
   The 100K-vector benchmark in P13-EXP-06 evaluated vector indexing mechanisms under synthetic replicated embeddings. It demonstrates algorithmic sub-millisecond retrieval scaling, but must not be conflated with a 100,000-sample real microscopy archive.
