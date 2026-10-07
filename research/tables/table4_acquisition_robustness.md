### TABLE IV: Acquisition-Geometry Similarity Gap Analysis (N=55 Matched Cohort)

| Metric / Condition | Frozen DINOv2 Baseline | Phase 4 Adapted (Proposed) | Observed Change | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- |
| Within-Acquisition Cosine Sim | 0.7811 | 0.9085 | +0.1274 (+16.31%) | Paired t-test p < 1e-15 |
| Cross-Acquisition Cosine Sim | 0.5794 | 0.8404 | +0.2610 (+45.05%) | Paired t-test p < 1e-20 |
| Observed Acquisition Gap (Delta) | 0.2016 | 0.0681 | -0.1335 (-66.23%) | Wilcoxon W=21743, p=5.03e-36 |
| Query-Level Mean Reduction | -- | 66.40% | -- | Paired Cohen's dz = 2.19 |
| Multi-Seed Gap Variance | -- | Seed 42: 0.0791 | 123: 0.0598 | 2024: 0.0654 | Mean: 0.0681 | Stable across initializations |

