### Table 3: Acquisition Bias Mitigation via Supervised Contrastive Learning (SupCon)

| Evaluation Metric | Baseline DINOv2 (Zero-Shot) | SupCon Adapted (Multi-Seed) | Absolute Delta | Relative Change | Statistical Significance |
| --- | --- | --- | --- | --- | --- |
| Acquisition Bias Gap (Delta) | 0.0543 | 0.0173 | -0.0370 | -68.15% | p = 1.42e-12 (Paired t-test) |
| Recall@1 (R@1) | 0.9481 | 0.9418 +/- 0.0059 | -0.0063 | -0.66% | Preserved Semantic Discrimination |
| Mean Reciprocal Rank (MRR) | 0.9658 | 0.9632 +/- 0.0042 | -0.0026 | -0.27% | Preserved Rank Quality |
| Precision@5 (P@5) | 0.8708 | 0.9053 +/- 0.0166 | +0.0345 | +3.96% | Statistically Significant Gain |
