# Manuscript Table Specifications & Captions

All tables are compiled in LaTeX (`.tex`) and Markdown (`.md`) format under `research/tables/`.

---

### Table I: Evaluated Scientific Microscopy Repositories
- **Source Artifact:** `research/tables/table1_dataset_composition.tex` (Markdown: `table1_dataset_composition.md`)
- **Caption:** *TABLE I: Multi-modality scientific microscopy corpus summary, detailing active population, image formats, resolutions, bit-depths, and study roles across HCCI, Carinthia SEM, and BBBC021.*
- **Placement:** Section VI (Experimental Setup), Page 2, Column 1.

### Table II: Benchmark Partitions & Acquisition Conditions
- **Source Artifact:** `research/tables/table2_dataset_splits.tex` (Markdown: `table2_dataset_splits.md`)
- **Caption:** *TABLE II: HCCI partition breakdown (Training, Validation, Held-out Test) across accelerating voltage capture grids (5.0–20.0 kV) and multi-detector capture configurations.*
- **Placement:** Section VI (Experimental Setup), Page 2, Column 2.

### Table III: Protocol U Unconstrained Retrieval Comparison
- **Source Artifact:** `research/tables/table3_retrieval_comparison.tex` (Markdown: `table3_retrieval_comparison.md`)
- **Caption:** *TABLE III: Retrieval performance comparison under unconstrained cross-acquisition distractors (Protocol U), comparing classical hashing, ResNet-50, DINOv2 baseline, and Phase 4 adapted multi-seed ensemble.*
- **Placement:** Section VII (Results - RQ1), Page 3, Column 1.

### Table IV: Acquisition-Geometry Similarity Gap Analysis
- **Source Artifact:** `research/tables/table4_acquisition_robustness.tex` (Markdown: `table4_acquisition_robustness.md`)
- **Caption:** *TABLE IV: Acquisition-geometry cosine similarity gap analysis across N=55 matched query cohort, demonstrating a 66.23% observed similarity gap reduction ($p = 5.03 \times 10^{-36}$, $d_z = 2.19$).*
- **Placement:** Section VII (Results - RQ2), Page 3, Column 2.

### Table V: Quality-Risk Screening Classifier Performance
- **Source Artifact:** `research/tables/table5_quality_risk_performance.tex` (Markdown: `table5_quality_risk_performance.md`)
- **Caption:** *TABLE V: Quality screening classification metrics on N=1,100 test samples across handcrafted features, adapted representations, and frozen DINOv2 visual representations (Branch A).*
- **Placement:** Section VII (Results - RQ3), Page 4, Column 1.

### Table VI: Model-Derived Suspicious Region Localization
- **Source Artifact:** `research/tables/table6_localization_performance.tex` (Markdown: `table6_localization_performance.md`)
- **Caption:** *TABLE VI: Spatial localization metrics (Macro IoU, Dice, Precision, Recall) evaluated across N=500 controlled synthetic artifact masks.*
- **Placement:** Section VII (Results - RQ4), Page 4, Column 2.

### Table VII: Grounded Evidence Cohort Verification
- **Source Artifact:** `research/tables/table7_evidence_cohort.tex` (Markdown: `table7_evidence_cohort.md`)
- **Caption:** *TABLE VII: Verification audit of the grounded evidence retrieval cohort (N=55), demonstrating 100% evidence availability and 0% duplicate contamination.*
- **Placement:** Optional Appendix / Supplementary.

### Table VIII: Uncertainty Calibration & Selective Prediction
- **Source Artifact:** `research/tables/table8_uncertainty_calibration.tex` (Markdown: `table8_uncertainty_calibration.md`)
- **Caption:** *TABLE VIII: Selective prediction accuracy and coverage under varying confidence thresholds, illustrating error-calibration dynamics and necessary human abstention rates.*
- **Placement:** Optional Appendix / Supplementary.

### Table IX: End-to-End Processing & Retrieval Latency Breakdown
- **Source Artifact:** `research/tables/table9_latency_breakdown.tex` (Markdown: `table9_latency_breakdown.md`)
- **Caption:** *TABLE IX: Stage-wise inference latency breakdown of the integrated SCI-INTEL pipeline on the declared research workstation benchmark environment (23.40 ms mean, 28.30 ms P95).*
- **Placement:** Optional Appendix / Supplementary.
