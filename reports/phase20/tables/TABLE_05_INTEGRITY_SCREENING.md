### Table 5: Data Integrity Assessment, Defocus Screening, and Duplicate Detection

| Screening Task | Method / Operator | Evaluation Set (N) | Key Metric 1 | Key Metric 2 | Operating Decision |
| --- | --- | --- | --- | --- | --- |
| Controlled Quality-Screening Benchmark (Defocus Indicators) | Tenengrad Gradient Energy | 120 Micrographs | AUROC = 0.8803 | AUPRC = 0.9618 | Threshold tau = 42.5 (Queue Route) |
| Near-Duplicate Screening | DCT pHash + Cosine Sim | 774 Micrographs | 0 Exact Duplicates | 5 Near-Duplicate Pairs | 769 Perceptual Clusters |
| Synthetic Corruptions | Perturbation Stress Test | 120 Corrupted | Noise sigma=0.05: 96.66% | Blur sigma=3.0: 69.83% | Flag Blurs for Triage |
