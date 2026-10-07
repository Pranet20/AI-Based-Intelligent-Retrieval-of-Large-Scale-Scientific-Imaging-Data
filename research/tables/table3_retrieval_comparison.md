### TABLE III: Protocol U Unconstrained Retrieval Comparison

| Representation Head / Baseline | Recall@1 | Recall@5 | Recall@10 | MRR | Precision@5 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| pHash (Perceptual Hash) | 0.0802 | 0.9717 | 0.9858 | 0.4782 | 0.5821 |
| dHash (Difference Hash) | 0.0660 | 0.9481 | 0.9717 | 0.4510 | 0.5519 |
| ResNet-50 (Pretrained) | 0.1179 | 0.9811 | 0.9953 | 0.5012 | 0.6019 |
| DINOv2 ViT-S/14 (Frozen Zero-Shot) | 0.1321 | 0.9858 | 1.0000 | 0.5200 | 0.6160 |
| Phase 4 Adapted (Seed 42) | 0.1321 | 0.9953 | 1.0000 | 0.5230 | 0.6283 |
| Phase 4 Adapted (Seed 123) | 0.1462 | 0.9906 | 1.0000 | 0.5214 | 0.6302 |
| Phase 4 Adapted (Seed 2024) | 0.1557 | 0.9906 | 1.0000 | 0.5338 | 0.6396 |
| Phase 4 Multi-Seed Ensemble | 0.1447 | 0.9921 | 1.0000 | 0.5261 | 0.6327 |

