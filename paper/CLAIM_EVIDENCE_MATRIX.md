# IEEE Manuscript Claim-Evidence Matrix
**Target Manuscript**: Claim-Evidence Verification Table  
**Rule**: Strict alignment between empirical artifacts and manuscript claims.

---

## 1. Master Claim-Evidence Table

### Claim 1: Visual Representation & Retrieval Superiority
- **Manuscript Claim**: Pretrained DINOv2-ViT-S/14 achieves strong visual retrieval performance on scientific electron micrographs without fine-tuning, outperforming contrastive and supervised convolutional baselines.
- **Evidence Artifact**: `reports/phase2/` evaluation logs and `reports/phase3/` comparison logs.
- **Dataset / Split**: In-domain structural materials test split ($N = 240$ queries, $N = 400$ gallery).
- **Metric**: $\text{Recall@1} = \mathbf{0.9481}$, $\text{Recall@5} = \mathbf{0.9852}$, $\text{MRR} = \mathbf{0.9658}$ (vs. SimCLR $\text{Recall@1} = 0.7815$, Supervised ResNet-50 $\text{Recall@1} = 0.8125$).
- **Reproducibility Command**:
  ```bash
  pytest tests/test_retrieval.py -q
  ```
- **Confidence / Status**: **VERIFIED (Frozen Baseline)**
- **Allowed Wording**: *"DINOv2-ViT-S/14 achieved a Recall@1 of 0.9481 and an MRR of 0.9658 under the declared evaluation protocol, outperforming the contrastive baseline by +16.66%."*
- **Disallowed Wording**: "Universally superior retrieval model", "state-of-the-art across all vision tasks".

---

### Claim 2: Acquisition-Geometry Robustness Adaptation
- **Manuscript Claim**: Latent representations exhibit a cross-acquisition similarity gap across varied beam tilt and detector modes, which can be partially mitigated through parametric affine projection layers.
- **Evidence Artifact**: `reports/phase4/PHASE4_REPORT.md` and `reports/phase4/figures/pca_phase2_vs_phase4.png`.
- **Dataset / Split**: Multi-angle specimen split ($N = 180$ pairs under $10^\circ - 30^\circ$ tilt).
- **Metric**: Baseline similarity gap $\Delta_{\text{geom}} = 0.235$ reduced to $0.136$ (**42.3% mitigation**); cross-angle $\text{Recall@1}$ improved from $0.7140$ to $0.8415$.
- **Reproducibility Command**:
  ```bash
  pytest tests/test_acquisition_adaptation.py -q
  ```
- **Confidence / Status**: **VERIFIED (Empirical Mitigation)**
- **Allowed Wording**: *"Latent representations exhibit a measured cross-acquisition similarity gap under varying tilt and detector conditions, which affine adaptation partially mitigated under the evaluated protocol."*
- **Disallowed Wording**: "Geometric invariance", "invariant to microscope view angle".

---

### Claim 3: Tabular Metadata Retrieval & Multimodal Fusion
- **Manuscript Claim**: Metadata-only retrieval substantially underperforms visual representations, and evaluated multimodal fusion approaches do not improve retrieval over the pure visual baseline under the declared protocol.
- **Evidence Artifact**: `reports/phase5/tables/table_main_test_results.csv` and `reports/phase5/PHASE5_REPORT.md`.
- **Dataset / Split**: Test split ($N = 240$ queries with complete instrument metadata).
- **Metric**: Metadata-only $\text{MRR} = \mathbf{0.3443}$; late fusion optimal weight $\alpha^* = \mathbf{1.0}$; Gated MLP and Cross-Attention $\text{MRR} \le 0.9658$.
- **Reproducibility Command**:
  ```bash
  pytest tests/test_multimodal_fusion.py -q
  ```
- **Confidence / Status**: **VERIFIED (Defensible Negative Finding)**
- **Allowed Wording**: *"Metadata-only retrieval substantially underperformed the frozen visual baseline (MRR = 0.3443 vs 0.9658), while evaluated metadata-fusion approaches did not improve retrieval performance over the frozen visual baseline under the declared evaluation protocol. The final retrieval configuration retained the visual representation as the primary retrieval signal."*
- **Disallowed Wording**: "Multimodal fusion enhances visual search", "metadata provides rich semantic guidance".

---

### Claim 4: Image-Derived Quality-Risk Screening
- **Manuscript Claim**: Automated image-derived quality indicators effectively identify degraded micrographs (blur, noise, poor contrast) on controlled benchmarks to prioritize curator review.
- **Evidence Artifact**: `reports/phase6/PHASE6_REPORT.md` and `reports/phase6/figures/fig5_synthetic_quality_anomaly_auroc.png`.
- **Dataset / Split**: Controlled degradation benchmark ($N = 120$ images).
- **Metric**: $\text{AUROC} = \mathbf{0.8803}$, $\text{AUPRC} = \mathbf{0.9618}$ (vs Random $\text{AUROC} = 0.5000$).
- **Reproducibility Command**:
  ```bash
  pytest tests/test_quality_risk.py -q
  ```
- **Confidence / Status**: **VERIFIED (Controlled Benchmark)**
- **Allowed Wording**: *"The platform computes image-derived quality-risk indicators, achieving an AUROC of 0.8803 on a controlled synthetic degradation benchmark of N=120."*
- **Disallowed Wording**: "Physical microscope defect detection", "automated lens fault diagnosis".

---

### Claim 5: Archival Redundancy & Duplicate Candidate Identification
- **Manuscript Claim**: Cosine similarity thresholding on DINOv2 embeddings detects near-exact duplicate perturbations on synthetic benchmarks and effectively audits natural repository redundancy.
- **Evidence Artifact**: `reports/phase6/PHASE6_DATA_AUDIT.md` and `reports/phase6/figures/fig2_synthetic_duplicate_roc.png`.
- **Dataset / Split**: Synthetic perturbation split ($N = 120$) and Natural repository collection ($N = 769$).
- **Metric**: Synthetic benchmark $\text{AUROC} = \mathbf{0.9998}$, $F_1 = \mathbf{0.9810}$; Natural graph: $764$ singletons ($99.35\%$), $5$ pairs ($0.65\%$).
- **Reproducibility Command**:
  ```bash
  pytest tests/test_deduplication.py -q
  ```
- **Confidence / Status**: **VERIFIED (Separated Benchmark & Natural Audit)**
- **Allowed Wording**: *"Achieved F1=0.9810 on synthetic duplicate perturbations; an exhaustive graph audit of the 769 natural repository micrographs identified 764 singletons and 5 duplicate pairs (0.65% natural redundancy)."*
- **Disallowed Wording**: "Cryptographic proof of database uniqueness", "zero duplicate guarantee".

---

### Claim 6: Relative Embedding-Space Novelty Scoring
- **Manuscript Claim**: Latent-space k-NN distance effectively flags outlier specimens and rare microstructures to prioritize discovery in curator review queues.
- **Evidence Artifact**: `reports/phase6/PHASE6_REPORT.md` and `reports/phase6/figures/fig6_novelty_score_distributions.png`.
- **Dataset / Split**: Out-of-distribution evaluation split ($N = 120$).
- **Metric**: $\text{AUROC} = \mathbf{0.9825}$ (vs Isolation Forest $\text{AUROC} = 0.9140$).
- **Reproducibility Command**:
  ```bash
  pytest tests/test_novelty.py -q
  ```
- **Confidence / Status**: **VERIFIED (Latent-Space Metric)**
- **Allowed Wording**: *"Relative embedding-space novelty detection via k-NN latent distance achieved an AUROC of 0.9825 against held-out out-of-distribution specimens."*
- **Disallowed Wording**: "Physical anomaly discovery engine", "automated physical law discovery".

---

### Claim 7: Sub-Millisecond Vector Search Latency
- **Manuscript Claim**: FAISS flat inner-product indexing delivers exact exhaustive search with sub-millisecond query execution on standard CPU hardware.
- **Evidence Artifact**: `reports/phase7/PHASE7_REPORT.md`.
- **Dataset / Split**: Benchmark vector index ($N = 10,000$ 384-dimensional vectors).
- **Metric**: Search latency = **0.24 ms** per query; Exact Recall = **1.0000**; RAM footprint = **15.4 MB**.
- **Reproducibility Command**:
  ```bash
  pytest platform/tests/test_search.py -q
  ```
- **Confidence / Status**: **VERIFIED (Benchmarked CPU Execution)**
- **Allowed Wording**: *"FAISS IndexFlatIP executes exact nearest-neighbor search in 0.24 ms across 10,000 384-dimensional vectors on commodity CPU hardware with exact 1.0000 recall."*
- **Disallowed Wording**: "Billion-scale real-time search on a laptop".
