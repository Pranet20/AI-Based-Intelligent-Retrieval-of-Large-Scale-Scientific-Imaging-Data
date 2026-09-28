# P19 BASELINE MODEL CARD: OPENAI CLIP (ViT-B/32)

**Model Architecture**: Vision Transformer (ViT-B/32)  
**Pretraining Regime**: Contrastive Language-Image Pretraining (CLIP) on 400M web image-text pairs  
**Checkpoint Source**: `openai/clip-vit-base-patch32` (HuggingFace / OpenAI release)  
**Reported Metrics on Carinthia Defect SEM (P19-EXP-10)**:
- Micro R@1: `0.7840`
- Macro R@1: `0.7120`
- Mean Reciprocal Rank (MRR): `0.8350`

---

## 1. Specification & Protocol Audit

| Parameter | Specification / Declared State | Audit Finding |
|---|---|---|
| **Software Implementation** | PyTorch / HuggingFace Transformers / `open_clip_torch` | Inferred standard package |
| **Input Resolution** | 224 x 224 pixels | Bicubic interpolation |
| **Normalization** | Mean `[0.48145466, 0.4578275, 0.40821073]`, Std `[0.26862954, 0.26130258, 0.27577711]` | Standard OpenAI CLIP image transform |
| **Feature Layer** | Visual Transformer Projection Head (`visual.proj`) | Penultimate pooled representation |
| **Embedding Dimension** | 512-dimensional vector | $L_2$-normalized to unit hypersphere |
| **Similarity Metric** | Cosine similarity ($\langle \hat{\mathbf{z}}_q, \hat{\mathbf{z}}_g \rangle$) | Unit inner product |
| **Query & Gallery Sets** | Carinthia Defect SEM ($N=4,591$, LOO protocol, 6 classes) | Matching DINOv2 evaluation protocol |
| **Independent Checkpoint Artifact** | Cached weights or precomputed `.parquet` embeddings in repo | **NOT LOCATED IN LOCAL REPO** |

---

## 2. Reproducibility Status

Because the exact cached per-image 512-d CLIP embeddings or standalone batch extraction script was not packaged in the frozen local repository artifacts, this comparative baseline is formally marked:

**STATUS: CLIP_RESULT_REPRODUCTION_NOT_VERIFIED**

- **Historical Value Retention**: The reported descriptive metric (Micro R@1 = 0.7840) is preserved as a historical comparative reference point.
- **Scientific Claim Boundary**: Inferential superiority claims ($p < 10^{-15}$) are demoted to descriptive comparisons until full deterministic reproduction artifacts are packaged.
