### Table 2: Zero-Shot Retrieval Performance on HCCI Mineralogy Benchmark (N=774)

| Model Architecture | Pretraining Protocol | Embedding Dim | Recall@1 (R@1) | MRR | Precision@5 (P@5) | Notes / Status |
| --- | --- | --- | --- | --- | --- | --- |
| Uniform Random Baseline | None (Mathematical 1/6) | N/A | 0.1667 | 0.4083 | 0.1667 | Theoretical Null Baseline |
| ResNet-50 | Supervised (ImageNet-1k) | 2048 | 0.9245 | 0.9312 | 0.8120 | Descriptive (Literature Citation) |
| CLIP ViT-B/16 | Contrastive (WIT-400M) | 512 | 0.8920 | 0.9140 | 0.7850 | Descriptive (Literature Citation) |
| DINOv2 ViT-S/14 | Self-Supervised (LVD-142M) | 384 | 0.9481 | 0.9658 | 0.8708 | Authoritative Frozen Baseline |
