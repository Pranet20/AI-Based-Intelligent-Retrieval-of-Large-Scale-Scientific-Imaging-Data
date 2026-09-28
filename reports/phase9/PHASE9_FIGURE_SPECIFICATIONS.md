# Manuscript Figure Specifications & Technical Rendering Standards
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase9_figure_specifications_001`  
**Date:** September 2026  
**Status:** Certified Figure Specifications — 300 DPI Publication Standards

---

## 1. Overview & Rendering Guidelines
All manuscript figures are designed to meet IEEE/Elsevier 300 DPI vector-quality standards. Pre-rendered figures are archived in `reports/phase7/figures/`, with corresponding source plotting scripts in `src/visualization/`. Plotted data points trace strictly to cryptographically frozen artifacts.

---

## 2. Exhaustive Figure Catalog (Figures 1 through 12)

### Figure 1: End-to-End Scientific Image Data Management Architecture
- **Caption:** *"End-to-end architecture of the AI-powered scientific image data management platform, illustrating the sequential transition from raw electron micrograph ingestion and metadata parsing to self-supervised feature extraction, contrastive adaptation, vector retrieval, multi-stage integrity screening, and human-in-the-loop curation."*
- **Layout & Panels:** Horizontal flowchart (Left-to-Right).
  - *Panel A:* Ingestion & Provenance (SHA-256 digest, manifest registry, TIFF tag parser).
  - *Panel B:* Representation Core (Frozen `dinov2_vits14` 384-d encoder + SupCon 128-d adaptation head).
  - *Panel C:* High-Throughput Search (FAISS `IndexFlatIP` and `IndexHNSWFlat`).
  - *Panel D:* Data Integrity & Quality (4-stage duplicate cascade, 5 classical quality metrics).
  - *Panel E:* Operational Platform (FastAPI service, PostgreSQL audit trail, React curation dashboard).
- **Authoritative Data Source:** `src/platform/app.py`, `configs/phase8.yaml`.

---

### Figure 2: Leakage-Controlled Research Benchmark Methodology
- **Caption:** *"Methodological pipeline and 10-point leakage control topology, detailing the strict physical isolation between the Helios training partition (N=427), Helios validation partition (N=135), and the held-out Zeiss GeminiSEM test partition (N=212)."*
- **Layout:** Block diagram illustrating disjoint acquisition splits, sample flow, and the 10 leakage verification gates (Checks A through J).
- **Authoritative Data Source:** `reports/phase7/LEAKAGE_AUDIT.md`, `reports/phase9/PHASE9_EXPERIMENTAL_PROTOCOL.md`.

---

### Figure 3: Specimen Alloy Distribution & Multi-Instrument Microstructure Topography
- **Caption:** *"Distribution and representative SEM micrographs of the High-Chromium Cast Iron (HCCI) alloy across its three canonical heat-treatment conditions: (a) AsCast hypoeutectic matrix with primary chromium carbides, (b) Q980_0h_WC water-cooled destabilized matrix, and (c) Q980_9h_AC air-cooled destabilized matrix, illustrating high visual variance under varying accelerating voltages (5 kV to 30 kV) and detectors (SE vs. BSE)."*
- **Layout:** $3 \times 3$ image matrix showing 3 specimens across 3 distinct optical setups.
- **Authoritative Data Source:** `data/manifests/hcci_manifest.parquet`, `reports/phase2/figures/pca_hcci.png`.

---

### Figure 4: Self-Supervised Vision Transformer Representation Extraction
- **Caption:** *"Visual feature extraction pipeline utilizing frozen Meta DINOv2 ViT-S/14 (dinov2_vits14), illustrating deterministic bicubic resizing (224x224), 14x14 patch tokenization, multi-head self-attention distillation, and L2 unit-sphere normalization of the 384-dimensional class token."*
- **Layout:** Schematic diagram of ViT-S/14 patch projection and multi-layer transformer blocks.
- **Authoritative Data Source:** `src/models/dinov2_extractor.py`, `reports/phase2/PHASE2_BASELINE_REPORT.md`.

---

### Figure 5: Acquisition-Aware Contrastive Adaptation with Same-Acquisition Masking
- **Caption:** *"Architecture and pair sampling semantics of the Supervised Contrastive Learning (SupCon) adaptation head. (a) 2-layer MLP projector (384 -> 128 -> 128 with BatchNorm and ReLU). (b) Minibatch contrastive pair masking: positive pairs are constrained to identical specimen conditions imaged under disparate optical settings, while same-acquisition pairs are neutralized to eliminate instrument-memorized nuisance features."*
- **Layout:** Two subplots: Subplot (a) Network wiring; Subplot (b) Positive/negative contrastive similarity matrix.
- **Authoritative Data Source:** `src/models/supcon_projector.py`, `data/processed/phase4/metrics/phase4_evaluation_results.json`.

---

### Figure 6: Multi-Baseline Retrieval Performance Comparison (B0 through B7)
- **Caption:** *"Comparative retrieval performance across baselines B0 through B7 evaluated on the held-out Zeiss GeminiSEM test split (N=212). Bars denote empirical means; error bars represent 95% bootstrap confidence intervals over B=1,000 resamples. DINOv2 visual features (B3) and contrastive adapted features (B4) dominate perceptual hashing (B1, B2) and metadata-only retrieval (B5)."*
- **Layout:** Grouped bar chart comparing Recall@1, MRR, and Precision@5 across baselines B0–B7.
- **Authoritative Data Source:** `reports/phase7/figures/fig3_retrieval_comparison.png`, `reports/phase9/PHASE9_TABLES.md` (Table 10).

---

### Figure 7: Representation Geometry & Within-vs-Cross Acquisition Gap Compression
- **Caption:** *"Empirical kernel density estimates of cosine similarity distributions on HCCI cross-acquisition specimen pairs. (a) Baseline frozen DINOv2 exhibits a severe gap (Delta = 0.1994, ratio = 74.99%) between within-acquisition (mean = 0.7973) and cross-acquisition pairs (mean = 0.5979). (b) Proposed SupCon adaptation compresses the gap by 68.15% (Delta = 0.0635, ratio = 93.10%, p = 1.42e-12), pulling cross-acquisition representations toward the within-acquisition manifold."*
- **Layout:** Two overlapping density distribution plots (Baseline vs. Adapted).
- **Authoritative Data Source:** `reports/phase7/figures/fig4_acquisition_geometry.png`, `data/processed/phase4/metrics/phase4_evaluation_results.json`.

---

### Figure 8: Multimodal Metadata Feature Ablation & Alpha Calibration Curves
- **Caption:** *"Validation split grid-search calibration curves for late-fusion parameter alpha in [0.0, 1.0] across metadata feature groups A through F. In all configurations, retrieval accuracy monotonically increases with visual weight, peaking at alpha* = 1.0 (visual-dominant). Saturated visual features derive zero additive ranking benefit from late metadata score fusion."*
- **Layout:** Line plot showing Recall@1 and MRR as a function of $\alpha$ for Groups A–F.
- **Authoritative Data Source:** `reports/phase7/figures/fig5_metadata_calibration.png`, `reports/phase5/tables/table_alpha_ablation.csv`.

---

### Figure 9: Sequential 4-Stage Deduplication Cascade & Redundancy Graph Partitioning
- **Caption:** *"Integrity screening pipeline. (a) Sankey diagram illustrating candidate pair attrition across the 4-stage cascade (SHA-256 -> Dual Perceptual Hashes -> DINOv2 Cosine Gate -> Structural SSIM/MAE), highlighting 100% precision and zero false positives. (b) Graph connected components topology on the natural HCCI archive (N=774), partitioning images into 764 singletons and 5 pair clusters (769 KEEP representatives, 5 REVIEW candidates)."*
- **Layout:** Two panels: Panel (a) Sankey flow; Panel (b) Undirected cluster component network.
- **Authoritative Data Source:** `reports/phase7/figures/fig6_duplicate_pr_curve.png`, `reports/phase6/figures/fig1_duplicate_cascade_sankey.png`.

---

### Figure 10: Multi-Attribute Quality-Risk Receiver Operating Characteristic Curves
- **Caption:** *"Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves for image-derived quality risk indicators evaluated on controlled synthetic degradations (N=120: 100 corrupted, 20 nominal controls). The composite quality risk score achieves AUROC = 0.8803 and AUPRC = 0.9618, with individual detectors targeting noise (AUROC = 0.9412) and defocus blur (AUROC = 0.8925)."*
- **Layout:** ROC curves (left) and PR curves (right) displaying all 8 indicators.
- **Authoritative Data Source:** `reports/phase7/figures/fig7_quality_risk_roc.png`, `reports/phase6/PHASE6_REPORT.md`.

---

### Figure 11: Priority Triage Inspection Yield & Human-in-the-Loop Curation Workflow
- **Caption:** *"Human curator review efficiency under constrained inspection budgets. (a) Anomaly capture yield curve demonstrating 100% precision across Top-10 and Top-25 review tiers. (b) Interactive curator review dashboard in the React frontend, allowing domain experts to compare candidate duplicates and confirm quality triage dispositions with complete audit logging."*
- **Layout:** Subplot (a) Yield curve; Subplot (b) Platform UI workflow diagram.
- **Authoritative Data Source:** `reports/phase7/figures/fig11_curation_queue_yield.png`, `reports/phase6/figures/fig10_human_review_budget_yield.png`.

---

### Figure 12: High-Throughput Vector Search Latency vs. Corpus Scaling
- **Caption:** *"Computational scalability benchmark. Empirical query execution latency (ms) and throughput (QPS) comparing exact brute-force search (IndexFlatIP, 0.7348 ms) and approximate graph search (IndexHNSWFlat, 0.3691 ms, 1.99x speedup) on host CPU hardware across corpus scales up to N=100,000 vectors."*
- **Layout:** Log-log scaling plot of search latency vs. index vector count.
- **Authoritative Data Source:** `reports/phase7/figures/fig10_latency_vs_retention.png`, `reports/phase3/latency_benchmark.csv`.
