# P19 BASELINE MODEL CARD: RESNET-50 (IMAGENET PRETRAINED)

**Model Architecture**: Residual Network (ResNet-50, 50 layers)  
**Pretraining Regime**: Supervised 1,000-class classification on ImageNet-1K (ILSVRC-2012)  
**Checkpoint Source**: `torchvision.models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)`  
**Reported Metrics on Carinthia Defect SEM (P19-EXP-10)**:
- Micro R@1: `0.6420`
- Macro R@1: `0.5840`
- Mean Reciprocal Rank (MRR): `0.7110`

---

## 1. Specification & Protocol Audit

| Parameter | Specification / Declared State | Audit Finding |
|---|---|---|
| **Software Implementation** | PyTorch / `torchvision.models` | Standard library reference |
| **Input Resolution** | 224 x 224 pixels | Bilinear interpolation |
| **Normalization** | Mean `[0.485, 0.456, 0.406]`, Std `[0.229, 0.224, 0.225]` | Standard ImageNet transform |
| **Feature Layer** | Global Average Pooling (`avgpool`) output | Pre-classification 2048-d feature map |
| **Embedding Dimension** | 2048-dimensional vector | $L_2$-normalized to unit hypersphere |
| **Similarity Metric** | Cosine similarity ($\langle \hat{\mathbf{z}}_q, \hat{\mathbf{z}}_g \rangle$) | Unit inner product |
| **Query & Gallery Sets** | Carinthia Defect SEM ($N=4,591$, LOO protocol, 6 classes) | Matching DINOv2 evaluation protocol |
| **Independent Checkpoint Artifact** | Cached weights or precomputed `.parquet` embeddings in repo | **NOT LOCATED IN LOCAL REPO** |

---

## 2. Reproducibility Status

Because the exact cached per-image 2048-d ResNet-50 embeddings or standalone extraction script was not packaged in the frozen local repository artifacts, this comparative baseline is formally marked:

**STATUS: RESNET50_RESULT_REPRODUCTION_NOT_VERIFIED**

- **Historical Value Retention**: The reported descriptive metric (Micro R@1 = 0.6420) is preserved as a historical comparative reference point.
- **Scientific Claim Boundary**: Inferential superiority claims ($p < 10^{-15}$) are demoted to descriptive comparisons until full deterministic reproduction artifacts are packaged.
