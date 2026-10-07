### TABLE V: Quality-Risk Screening Classifier Performance (N=1,100 Test Samples)

| Feature Representation | AUROC | AUPRC | F1 Score | Balanced Accuracy | Macro F1 (11-Class) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Handcrafted Quality Indicators | 0.8281 | 0.9808 | 0.9518 | 0.5085 | -- |
| Phase 4 Adapted Representations | 0.8230 | 0.9792 | 0.9587 | 0.6645 | -- |
| Frozen DINOv2 ViT-S/14 (Branch A) | 0.8582 | 0.9841 | 0.9632 | 0.7036 | 0.6837 |
| Operating Threshold (tau = 0.900) | Specificity: 0.8200 | Balanced Acc: 0.7545 | MCC: 0.3054 | -- | -- |

