### Table 4: Multimodal Retrieval Performance and the Metadata Paradox

| Retrieval Modality / Configuration | R@1 | MRR | P@5 | Relative Delta to Visual | Scientific Outcome |
| --- | --- | --- | --- | --- | --- |
| Visual-Only (DINOv2 ViT-S/14) | 0.9481 | 0.9658 | 0.8708 | Baseline (0.0%) | Optimal Peak Precision |
| Metadata-Only (Unnormalized Logs) | 0.0519 | 0.3443 | 0.1820 | -64.3% MRR | Severe Noise / Disconnect |
| Gated MLP Neural Fusion | 0.5210 | 0.5896 | 0.4610 | -38.9% MRR | Degraded (Hypothesis H1 Refuted) |
| Cross-Attention Neural Fusion | 0.5480 | 0.6132 | 0.4890 | -36.5% MRR | Degraded (Hypothesis H1 Refuted) |
| Decoupled Visual + Metadata Filter | 0.9481 | 0.9658 | 0.8708 | 0.0% MRR | Adopted System Architecture |
