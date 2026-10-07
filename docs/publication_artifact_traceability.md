# SCI-INTEL Publication Artifact Traceability Matrix

**Platform:** SCI-INTEL — Scientific Imaging Intelligence Platform  
**Target Venue:** IEEE ISBI 2027 (International Symposium on Biomedical Imaging)  
**Classification:** Research Evidence Traceability & Provenance  

---

## 1. Figures Traceability Matrix

| Figure ID | Title | Source Artifact | Generation Script | Cohort / Dataset | Metrics Used | Frozen Evidence Source | Limitations | Manuscript Section |
|:---:|:---|:---|:---|:---|:---|:---|:---|:---:|
| **Fig 1** | SCI-INTEL System Architecture | System Implementation | `scripts/generate_publication_figures.py` | Full Platform Architecture | 17-stage workflow lifecycle | Architectural specification | Illustrative abstraction of local deployment | Section III (Proposed Framework) |
| **Fig 2** | Dual Representation Framework | `src/representation/`, `src/adaptation/` | `scripts/generate_publication_figures.py` | Architecture flow | Feature dimensions ($384 \to 384$) | Phase 2 & Phase 4 checkpoints | Independent composition; no learned fusion | Section IV (Methodology) |
| **Fig 3** | Acquisition Robustness Gap Reduction | `research/results/phase3/acquisition_pairs.csv` | `scripts/generate_publication_figures.py` | $N=55$ Matched Query Cohort | Cosine similarity, gap reduction (66.23%) | Phase 3 & Phase 6 reports | Evaluates observed acquisition geometry gap, not universal invariance | Section VII (Results - RQ2) |
| **Fig 4** | Retrieval Performance (Protocol M vs U) | `research/results/freeze1/retrieval_results.csv` | `scripts/generate_publication_figures.py` | HCCI Benchmark ($N=774$) | Recall@1, Recall@5, MRR, Precision@5 | Phase 2 & Phase 4 ensemble evaluations | Overlapping specimen classes across splits | Section VII (Results - RQ1) |
| **Fig 5** | Quality-Risk Screening & Uncertainty | `research/results/phase4/classification_results.csv` | `scripts/generate_publication_figures.py` | Controlled Synthetic Benchmark ($N=1,100$) | AUROC (0.8582), AUPRC (0.9841), Coverage vs Acc | Phase 4 evaluation report | Evaluated on synthetic artifacts, not physical defects | Section VII (Results - RQ3) |
| **Fig 6** | Suspicious Region Localization | `research/results/phase4/localization_results.csv` | `scripts/generate_publication_figures.py` | Controlled Synthetic Regions ($N=500$) | Macro IoU (0.4454), Dice (0.5103) | Phase 4 localization results | Model-derived suspicious region; not physical defect confirmation | Section VII (Results - RQ4) |
| **Fig 7** | Integrated Curation & Human Governance | Platform Curation Services | `scripts/generate_publication_figures.py` | Evaluated $N=55$ Evidence Cohort | Action codes, review triage, audit lineage | Phase 6 & Phase 10 verification | Suggestive evidence; human review is final decision authority | Section V & VIII (Discussion) |

---

## 2. Tables Traceability Matrix

| Table ID | Title | Source Artifact | Generation Script | Cohort / Dataset | Metrics Reported | Frozen Evidence Source | Limitations | Manuscript Section |
|:---:|:---|:---|:---|:---|:---|:---|:---|:---:|
| **Table I** | Evaluated Scientific Repositories | Phase 1 Manifests | `scripts/generate_publication_tables.py` | HCCI (774), Carinthia (4591), BBBC021 (720) | Active image counts, modalities, bit-depths | Phase 1 Data Freeze (`6c2627c6...`) | Publicly available benchmark archives | Section VI (Experimental Setup) |
| **Table II** | HCCI Partitions & Conditions | `research/final_manifests/hcci_splits.json` | `scripts/generate_publication_tables.py` | Train (427), Val (135), Held-out Test (212) | Micrograph counts, accelerating voltages (5-20 kV) | Phase 1 Split Manifest (`bb81b268...`) | Evaluates acquisition condition transfer, not unseen alloys | Section VI (Experimental Setup) |
| **Table III** | Protocol U Retrieval Comparison | `research/results/freeze1/retrieval_results.json` | `scripts/generate_publication_tables.py` | Protocol U Gallery ($N=774$) | R@1, R@5, R@10, MRR, P@5 for baselines & seeds | Phase 2 Retrieval Result (`83b276d8...`) | Unconstrained distractors from differing instruments | Section VII (Results - RQ1) |
| **Table IV** | Acquisition Robustness Analysis | `research/results/phase3/similarity_results.csv` | `scripts/generate_publication_tables.py` | $N=55$ Matched Query Cohort | Within (0.7811 $\to$ 0.9085), Cross (0.5794 $\to$ 0.8404), Gap (0.2016 $\to$ 0.0681) | Phase 3 Evidence Hash (`PHASE3_EVIDENCE_HASH.txt`) | Evaluated under declared acquisition protocols | Section VII (Results - RQ2) |
| **Table V** | Quality-Risk Classifier Performance | `research/results/phase4/classification_results.csv` | `scripts/generate_publication_tables.py` | Synthetic Benchmark Test Split ($N=1,100$) | AUROC (0.8582), AUPRC (0.9841), F1 (0.9632), BalAcc (0.7036) | Phase 4 Evidence Hash (`PHASE4_EVIDENCE_HASH.txt`) | Image-derived quality risk indicators | Section VII (Results - RQ3) |
| **Table VI** | Spatial Localization Performance | `research/results/phase4/localization_results.csv` | `scripts/generate_publication_tables.py` | Synthetic Localization Test Set ($N=500$) | Macro IoU (0.4454), Dice (0.5103), Precision (0.5259), Recall (0.4957) | Phase 4 Localization Benchmark | Saliency thresholding over $16\times 16$ patches | Section VII (Results - RQ4) |
| **Table VII** | Evidence Retrieval Cohort Verification | `research/results/phase6/evidence_results.csv` | `scripts/generate_publication_tables.py` | Grounded Evidence Cohort ($N=55$) | Availability (100%), Duplicate (0%), Provenance (0% missing) | Phase 6 Evidence Hash (`PHASE6_EVIDENCE_HASH.txt`) | Strictly applies to the evaluated $N=55$ cohort | Section VII (Results - RQ4) |
| **Table VIII** | Uncertainty Calibration & Prediction | `research/results/phase4/calibration_results.csv` | `scripts/generate_publication_tables.py` | Synthetic Test Split ($N=1,100$) & Carinthia ($N=100$) | ECE (0.3333), Brier (0.4821), Coverage/Acc at $\tau \in \{0.2, 0.4, 0.6\}$ | Phase 4 Calibration Report | 100% accuracy requires 90.27% abstention | Section VII (Results - RQ4) |
| **Table IX** | Integrated Pipeline Latency | `research/results/phase6/latency_results.csv` | `scripts/generate_publication_tables.py` | End-to-End Pipeline Inference | Preprocess (0.35 ms), Rep (3.12 ms), Quality (2.45 ms), Loc (8.84 ms), Total (23.40 ms) | Phase 6 Latency Benchmark | Declared local workstation benchmark environment | Section VII (Results - RQ5) |
