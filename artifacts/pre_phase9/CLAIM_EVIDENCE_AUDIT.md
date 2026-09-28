# Scientific Claim-to-Evidence Audit & Boundary Specification
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `pre_phase9_claim_evidence_audit_001`  
**Date:** September 2026  
**Status:** Authoritative Audit — Pre-Phase-9 Certification

---

## 1. Audit Framework & Evidence Taxonomy

To prevent scientific overclaiming, leakage, and circular reasoning in the forthcoming peer-reviewed manuscript (Phase 9), every formal scientific claim ($C_1$ through $C_{10}$) is subjected to a rigorous audit against physical experimental artifacts.

### Formal Evidence Classifications
1. **`[NATURAL DATA]`**: Directly evaluated on natural, physical electron microscopy acquisitions without artificial geometric or radiometric manipulations.
2. **`[CONTROLLED SYNTHETIC BENCHMARK]`**: Evaluated on controlled, mathematically injected degradations (defocus, noise, clipping) or geometric transformations with explicit ground-truth labels.
3. **`[EXTERNAL DOMAIN SHIFT]`**: Evaluated on out-of-distribution external microscopy datasets without fine-tuning or in-domain parameter adaptation.
4. **`[ENGINEERING MEASUREMENT]`**: Measured computational properties (latency, QPS, memory footprint, cryptographic bit-identity, test suite execution).

---

## 2. Exhaustive Audit of Claims $C_1$ through $C_{10}$

### Claim $C_1$: Visual Foundation Retrieval Without Fine-Tuning
- **Scientific Statement:** "Pretrained self-supervised Vision Transformers (`dinov2_vits14`) provide robust zero-shot microstructure retrieval without task-specific feature fine-tuning."
- **Target RQ:** RQ1 (Visual Foundation Feasibility)
- **Dataset / Sample:** HCCI Corpus ($N=774$, 67 acquisition conditions) & Held-out Zeiss Gemini test split ($N=212$).
- **Authoritative Metrics:**
  - Full Corpus ($N=774$ queries): Recall@1 = **0.9819**, MRR = **0.9894**, Recall@5 = **1.0000**, Precision@5 = **0.9693**.
  - Held-out Test Split ($N=212$ queries): Recall@1 = **0.9481** [95% CI: 0.926, 0.966], MRR = **0.9658**, Recall@5 = **1.0000**, Precision@5 = **0.8708**.
- **Authoritative Source Artifact:** `reports/phase2/tables/retrieval_hcci.csv` and `artifacts/phase5/metrics/phase5_results.json`.
- **Evidence Tag:** `[NATURAL DATA]`
- **Audit Findings & Bound:**
  - *Discrepancy:* None on metrics. Backbone model must strictly be named `dinov2_vits14` (384-d, 22.1M parameters), correcting erroneous narrative mentions of ViT-B/14.
  - *Scientific Bound:* High baseline retrieval reflects distinct alloy matrix morphology across the 3 heat treatments. Claim must not imply solved universal SEM retrieval across thousands of unknown phases.

---

### Claim $C_2$: Acquisition Invariance via Contrastive Projection
- **Scientific Statement:** "Acquisition-aware contrastive metric learning achieves a 68.15% measured reduction in within-vs-cross acquisition representation gap while preserving specimen material discriminability."
- **Target RQ:** RQ2 (Acquisition Invariance)
- **Dataset / Sample:** HCCI Specimen Pairs across 67 acquisition permutations.
- **Authoritative Metrics:**
  - Baseline `dinov2_vits14`: Within-acquisition cosine sim = **0.7973**, Cross-acquisition cosine sim = **0.5979**, Gap = **0.1994**, Ratio = **74.99%**.
  - Proposed Contrastive Projector (Seed 42): Within-acquisition sim = **0.9199**, Cross-acquisition sim = **0.8564**, Gap = **0.0635**, Ratio = **93.10%**.
  - Multi-seed Cross-Acquisition Mean: **0.8541 $\pm$ 0.0032** across seeds [42, 123, 2024].
  - Measured Gap Reduction: **68.15%** ($1 - 0.0635 / 0.1994$).
  - Material Discriminability Retention (Linear Probe): **98.71%** top-1 specimen accuracy.
- **Authoritative Source Artifact:** `data/processed/phase4/metrics/phase4_evaluation_results.json`, `reports/phase4/tables/table4_multiseed.csv`.
- **Evidence Tag:** `[NATURAL DATA]`
- **Audit Findings & Bound:**
  - *Discrepancy:* Phase 7 text erroneously misreported the raw baseline within/cross numbers as 0.8876 / 0.6882 / 77.53%. The authoritative JSON record confirms the baseline values are **0.7973 / 0.5979 / 74.99%**. The gap (0.1994) and relative gap reduction (68.15%) are mathematically exact and verified.
  - *Scientific Bound:* The reduction is an observational representation alignment; it does not reconstruct missing physical high-frequency information lost to poor focus or low beam current.

---

### Claim $C_3$: Generalization to Unseen Microscope Optics
- **Scientific Statement:** "Contrastive representation adaptation improves deep-ranked retrieval precision (Precision@5 = 0.9053 vs. 0.8708 baseline, $p=0.0028$) when generalized to a held-out microscope instrument (Zeiss GeminiSEM)."
- **Target RQ:** RQ2 (Cross-Instrument Generalization)
- **Dataset / Sample:** Held-out Zeiss Gemini split ($N=212$ queries, 18 acquisition conditions).
- **Authoritative Metrics:**
  - Baseline Precision@5: **0.8708** [95% CI: 0.848, 0.888].
  - Proposed Multi-Seed Precision@5: **0.9053 $\pm$ 0.0166** (paired t-test $t=3.04$, $p=0.0028$, Cohen's $d=0.65$).
  - Recall@1 remains statistically indistinguishable (0.9418 vs. 0.9481, $p>0.20$).
- **Authoritative Source Artifact:** `reports/phase7/PHASE7_REPORT.md` (Table 2 & Section 16), `reports/phase4/PHASE4_REPORT.md`.
- **Evidence Tag:** `[NATURAL DATA]`
- **Audit Findings & Bound:**
  - *Discrepancy:* None.
  - *Scientific Bound:* Evaluated on unseen optics for the *same 3 metallurgical alloy classes*. It demonstrates robustness to optical acquisition variance, not zero-shot transfer to novel alloys.

---

### Claim $C_4$: Neutrality of Late Metadata Fusion Under Saturated Vision
- **Scientific Statement:** "Under high-performing visual representations, late convex metadata fusion yields zero additive retrieval benefit ($\Delta \text{R@1} = 0.0, \Delta \text{MRR} = 0.0$), establishing an important negative finding where validation-calibrated optimal weight is strictly visual-dominant ($\alpha^* = 1.0$)."
- **Target RQ:** RQ3 (Multimodal Metadata Integration)
- **Dataset / Sample:** HCCI Validation split ($N=135$) and Test split ($N=212$) across 6 feature ablation groups A–F.
- **Authoritative Metrics:**
  - Isolated Metadata-Only Test Performance: Recall@1 = **0.3349**, MRR = **0.3443**, Recall@5 = **0.3349**, Precision@5 = **0.3349**.
  - Visual-Only Test Performance: Recall@1 = **0.9481**, MRR = **0.9658**.
  - Hybrid Test Performance ($\alpha^*=1.0$): Recall@1 = **0.9481**, MRR = **0.9658** ($\Delta = 0.0000$).
  - Validation grid search: $\alpha^* = 1.0$ across Groups A through F.
- **Authoritative Source Artifact:** `reports/phase5/tables/table_main_test_results.csv`, `reports/phase5/tables/table_alpha_ablation.csv`.
- **Evidence Tag:** `[NATURAL DATA]`
- **Audit Findings & Bound:**
  - *Discrepancy:* None.
  - *Scientific Bound:* Metadata does not assist when visual features are already saturated ($\approx 95\%$ R@1). Metadata remains vital for faceted structured search, provenance queries, and pre-filtering constraints.

---

### Claim $C_5$: Zero-Leakage 4-Stage Near-Duplicate Curation Cascade
- **Scientific Statement:** "A 4-stage sequential screening cascade (SHA-256 $\to$ perceptual hashes $\to$ DINOv2 cosine distance $\to$ structural SSIM/MAE verification) achieves 100% precision and 0.0% false positive rate on duplicate detection."
- **Target RQ:** RQ4 (Integrity & Deduplication)
- **Dataset / Sample:** Synthetic Duplicate Benchmark ($N=245$ pairs: 140 positive duplicate pairs under transformations, 105 hard negative pairs).
- **Authoritative Metrics:**
  - Precision: **1.0000** (74/74 flagged pairs were true duplicates).
  - False Positive Rate: **0.0000** (0 false positives).
  - Recall: **0.5286** (strict structural SSIM $\ge 0.95$ gate deliberately trades off recall to guarantee zero false deduplications).
- **Authoritative Source Artifact:** `artifacts/phase6/phase6_results.json`, `reports/phase6/PHASE6_REPORT.md` (Table 1).
- **Evidence Tag:** `[CONTROLLED SYNTHETIC BENCHMARK]`
- **Audit Findings & Bound:**
  - *Discrepancy:* None on cascade synthetic numbers.
  - *Scientific Bound:* The 100% precision claim applies strictly to the controlled synthetic benchmark transformations (rotation, cropping, compression, noise). Natural archive duplicate identification is evaluated via connected components graph clustering.

---

### Claim $C_6$: Natural Archive Redundancy Partitioning
- **Scientific Statement:** "In the uncurated natural HCCI archive ($N=774$), connected components clustering partitions the redundancy graph into 769 clusters (764 singletons and 5 pair clusters), categorizing the repository into 769 primary representations and 5 duplicate candidates for human review."
- **Target RQ:** RQ4 (Natural Archive Redundancy)
- **Dataset / Sample:** Natural HCCI Corpus ($N=774$ physical micrographs).
- **Authoritative Metrics:**
  - Total Clusters: **769**.
  - Singleton Clusters ($1 \text{ image}$): **764**.
  - Pair Clusters ($2 \text{ images}$): **5**.
  - Arithmetic Verification: $764 \times 1 + 5 \times 2 = 774$ images.
  - Action Accounting: **769 KEEP, 5 REVIEW** (representing 764 singletons + 5 cluster canonical representatives designated KEEP, and 5 secondary duplicates designated REVIEW).
- **Authoritative Source Artifact:** `artifacts/phase6/redundancy_summary.parquet`, `reports/phase6/PHASE6_REPORT.md`.
- **Evidence Tag:** `[NATURAL DATA]`
- **Audit Findings & Bound:**
  - *Discrepancy:* Semantic clarification required to prevent readers from assuming $769 + 5 = 774$ implies mutually exclusive partitions. Clarification: 769 distinct clusters exist; 764 singletons + 5 keepers = 769 KEEP, while 5 pair partners = 5 REVIEW.
  - *Scientific Bound:* Descriptive clustering output; no ground-truth physical re-imaging logs exist from the original microscope operators.

---

### Claim $C_7$: Image-Derived Quality Risk Assessment
- **Scientific Statement:** "Multi-attribute classical signal processing metrics (Laplacian blur, noise sigma, contrast dynamic range, clipping, and FFT high-frequency ratio) combined into a composite quality risk indicator achieve AUROC = 0.8803 and AUPRC = 0.9618 in detecting corrupted micrographs."
- **Target RQ:** RQ4 (Data Integrity & Quality Triage)
- **Dataset / Sample:** Controlled Synthetic Quality Benchmark ($N=120$: 100 degraded micrographs, 20 nominal controls).
- **Authoritative Metrics:**
  - Composite Quality Risk AUROC: **0.8803**.
  - Composite Quality Risk AUPRC: **0.9618**.
  - Individual Detector AUROC: Noise Anomaly = **0.9412**, Focus/Blur = **0.8925**, Dynamic Range/Contrast = **0.8540**, Sensor Clipping = **0.7265**, FFT High-Freq = **0.4240**.
- **Authoritative Source Artifact:** `reports/phase6/PHASE6_REPORT.md` (Section 5.3 & lines 439–441).
- **Evidence Tag:** `[CONTROLLED SYNTHETIC BENCHMARK]`
- **Audit Findings & Bound:**
  - *Discrepancy:* `reports/phase7/PHASE7_REPORT.md` Table 6 and Claim C7 narrative misreported AUPRC as 0.9742 (and in some summary text AUROC as 0.9124). The authoritative Phase 6 frozen artifact confirms **AUROC = 0.8803 and AUPRC = 0.9618**.
  - *Scientific Bound:* These are deterministic digital signal processing indicators, not certified physical beam calibration readings.

---

### Claim $C_8$: Representation Separation Under External Domain Shift
- **Scientific Statement:** "Visual foundation embeddings exhibit pronounced distributional shift when transferred zero-shot from metallographic SEM to semiconductor wafer defect archives (Carinthia SEM), yielding a mean cosine centroid separation of 0.5842."
- **Target RQ:** RQ5 (Cross-Domain Generalization & Shift)
- **Dataset / Sample:** Carinthia SEM ($N=4,591$ images across 6 defect classes) vs. HCCI ($N=774$).
- **Authoritative Metrics:**
  - In-domain HCCI intra-specimen cosine sim: **0.7973 – 0.9199**.
  - Out-of-distribution Carinthia to HCCI centroid cosine distance: **0.5842**.
  - Carinthia Zero-Shot Micro-Recall@1: **0.9952**, Macro-Recall@1: **0.9090** (demonstrating intra-domain defect clustering despite cross-domain shift).
- **Authoritative Source Artifact:** `reports/phase2/tables/retrieval_carinthia.csv`, `reports/phase7/PHASE7_REPORT.md` (Table 8).
- **Evidence Tag:** `[EXTERNAL DOMAIN SHIFT]`
- **Audit Findings & Bound:**
  - *Discrepancy:* None.
  - *Scientific Bound:* Carinthia lacks acquisition metadata; shift is quantified strictly through visual embedding geometry.

---

### Claim $C_9$: Diagnostic Review Queue Yield Under Constrained Human Budgets
- **Scientific Statement:** "Prioritizing candidate micrographs via composite anomaly scores concentrates degraded samples into the top tier of the curation review queue, achieving 100% precision at top-10 and top-25 inspection budgets."
- **Target RQ:** RQ6 (Human-in-the-Loop Curation Efficiency)
- **Dataset / Sample:** Controlled Synthetic Review Queue ($N=120$) & Exported Natural HCCI Review Queue ($N=50$ candidates).
- **Authoritative Metrics:**
  - Synthetic Review Queue: Precision@10 = **1.0000** (10/10 true degradations), Precision@25 = **1.0000** (25/25 true degradations), Precision@50 = **0.9600** (48/50 degradations).
  - Natural Review Queue Export: `top_n: 50` prioritized candidates exported in `artifacts/phase6/review_queue.parquet`.
- **Authoritative Source Artifact:** `reports/phase6/PHASE6_REPORT.md`, `configs/phase6.yaml`.
- **Evidence Tag:** `[ENGINEERING MEASUREMENT]` (for queue sorting and synthetic evaluation) & `[NATURAL DATA]` (for exported candidate rankings).
- **Audit Findings & Bound:**
  - *Discrepancy:* Phase 7 text in some places referred to 100 exported natural review items; configuration confirms `top_n: 50` is authoritative.
  - *Scientific Bound:* Natural queue candidates represent algorithmic outlier rankings; they have not undergone double-blind re-annotation by licensed metallurgists.

---

### Claim $C_{10}$: Deterministic Reproducibility & Zero-Leakage Architecture
- **Scientific Statement:** "The entire research pipeline reproduces deterministically with zero data leakage across 10 formal verification checks and 110/110 cryptographically verified frozen file checksums."
- **Target RQ:** RQ7 (Reproducibility & Research Integrity)
- **Dataset / Sample:** All experimental artifacts, checkpoints, manifests, and tables across Phases 1 through 7.
- **Authoritative Metrics:**
  - Frozen Artifact Checksums: **110 / 110** verified bit-for-bit identical via SHA-256 (`0 mismatches, 0 missing`).
  - Leakage Verification Checks: **10 / 10** passed (Zero bitwise, pixel, or near-duplicate overlap between train/val/test splits).
  - Platform Test Suite: **218 / 218** unit and integration tests passed.
  - Research-to-Platform Model Parity: Maximum absolute tensor difference $L_\infty < 1.0 \times 10^{-6}$.
- **Authoritative Source Artifact:** `artifacts/phase8/pre_phase8_frozen_checksums.json`, `reports/phase8/PHASE8_REPORT.md`.
- **Evidence Tag:** `[ENGINEERING MEASUREMENT]`
- **Audit Findings & Bound:**
  - *Discrepancy:* None.
  - *Scientific Bound:* Bit-exact parity is proven across PyTorch and TorchScript on CPU/CUDA; sub-millisecond execution times are subject to host CPU clock variance.

---

## 3. Summary of Narrative Corrections Required in Phase 9

1. **Backbone Naming:** Replace all instances of `DINOv2 ViT-B/14 (768-d)` with `dinov2_vits14 (384-d)`.
2. **FAISS Latency:** Replace erroneous 0.082 ms / 0.018 ms text with authoritative benchmark values: **0.7348 ms (IndexFlatIP)** and **0.3691 ms (IndexHNSWFlat)**.
3. **Phase 4 Baseline:** Replace erroneous 0.8876 / 0.6882 baseline sim text with authoritative: **0.7973 / 0.5979**.
4. **Quality Risk AUPRC:** Replace 0.9742 text with authoritative: **0.9618**.
5. **Review Queue Depth:** Clarify exported queue is `top_n = 50`.
6. **Redundancy Semantics:** State explicitly that 769 KEEP represents 764 singletons + 5 primary keepers, while 5 REVIEW represents the secondary duplicates.
