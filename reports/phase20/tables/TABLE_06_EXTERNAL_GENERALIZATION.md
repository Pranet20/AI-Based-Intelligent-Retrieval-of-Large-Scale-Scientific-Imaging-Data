### Table 6: External Transfer and Zero-Shot Classification on Carinthia Defect SEM (N=4,591)

| Evaluation Metric / Model | Micro-Average | Macro-Average | Dominant Class | Minority Class | Comparative Context |
| --- | --- | --- | --- | --- | --- |
| Balanced Uniform Random Prior | 0.1667 | 0.1667 | 0.1667 | 0.1667 | Null Baseline |
| Gallery-Weighted Random Prior | 0.7687 | 0.1665 | 0.8710 | 0.0120 | Class Skew Null Baseline |
| DINOv2 ViT-S/14 (Zero-Shot LOO) | 0.9952 | 0.9090 | 0.9991 | 0.7420 | Authoritative Frozen Result |
| CLIP ViT-B/16 (Literature) | 0.7840 | 0.6810 | 0.8240 | 0.4120 | Descriptive External Citation |
| ResNet-50 (Literature) | 0.6420 | 0.5230 | 0.7110 | 0.3250 | Descriptive External Citation |
