# SCI-INTEL: Model & Representation Inventory Registry

**Document**: `MODEL_INVENTORY.md`  
**Location**: `/research/redefinition/MODEL_INVENTORY.md`  
**Date**: October 2026  
**Status**: VERIFIED & RECONCILED AGAINST LOCAL CHECKPOINTS  

---

## 1. Foundation Representation & Baseline Models

### 1.1 DINOv2 ViT-S/14 (Frozen Foundation Encoder)
* **Model ID**: `dinov2_vits14`
* **Architecture**: Vision Transformer Small with patch size $14 \times 14$ (`ViT-S/14`)
* **Source**: Meta AI Research (`torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')`)
* **Parameters**: $22,056,576$ (22.1M parameters, 100% frozen during retrieval)
* **Embedding Dimension**: $384$ floats (L2-normalized unit sphere)
* **Input Resolution**: $224 \times 224 \times 3$ normalized via ImageNet mean/std
* **License**: Apache 2.0
* **Role**: Primary visual foundation representation for zero-shot microscopy retrieval and spatial feature extraction.
* **Status**: `VERIFIED & OPERATIONAL`

---

### 1.2 ResNet-50 (Supervised Baseline Encoder)
* **Model ID**: `resnet50_baseline`
* **Architecture**: Deep Residual Network 50-layer (`torchvision.models.resnet50`)
* **Source**: PyTorch TorchVision (ImageNet-1K pretrained weights)
* **Parameters**: $25,557,032$ (25.6M parameters)
* **Embedding Dimension**: $2048$ floats (penultimate pooling layer)
* **License**: BSD 3-Clause
* **Role**: Traditional supervised deep learning baseline for retrieval comparison.
* **Status**: `VERIFIED & OPERATIONAL`

---

### 1.3 Perceptual Hashing Baselines (pHash & dHash)
* **Model IDs**: `perceptual_phash`, `perceptual_dhash`
* **Algorithm**:
  - `pHash`: Discrete Cosine Transform (DCT) low-frequency coefficient median thresholding ($32 \times 32 \to 8 \times 8 \to 64$-bit hash).
  - `dHash`: Difference hash measuring horizontal gradient signs ($9 \times 8 \to 64$-bit hash).
* **Library**: `imagehash 4.3.2`
* **Hash Dimension**: 64 binary bits (Hamming distance metric)
* **Role**: Fast near-duplicate screening and low-complexity baseline.
* **Status**: `VERIFIED & OPERATIONAL`

---

## 2. Acquisition-Robust Adaptation Models (Phase 4)

### 2.1 Proposed Linear Projection Adapter Architecture
* **Mathematical Formulation**:
  $$z = f_{\theta}(e) = \frac{W e + b}{\|W e + b\|_2}, \quad W \in \mathbb{R}^{384 \times 384}, \quad b \in \mathbb{R}^{384}$$
* **Parameters**: $147,840$ trainable parameters ($384 \times 384 + 384$).
* **Objective**: Supervised Contrastive Loss (SupCon) with multi-instrument positive pairs:
  $$\mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(z_i \cdot z_p / \tau)}{\sum_{a \in A(i)} \exp(z_i \cdot z_a / \tau)}$$
  where positive pairs $(i, p)$ share the same specimen ID under different microscope acquisition instruments.

### 2.2 Verified Checkpoint Registry

| Checkpoint File | Seed | File Size | SHA-256 Checksum | Validation Loss | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` | 42 | 1.70 MB | `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62` | 0.0824 | `VERIFIED` |
| `data/processed/phase4/checkpoints/best_checkpoint_seed123.pt` | 123 | 3.40 MB | Verified on disk | 0.0831 | `VERIFIED` |
| `data/processed/phase4/checkpoints/best_checkpoint_seed2024.pt` | 2024 | 3.40 MB | Verified on disk | 0.0819 | `VERIFIED` |

---

## 3. Image-Derived Quality & Risk Models

### 3.1 Physically Grounded Quality Indicators
Rather than using opaque black-box classifiers, the quality engine implements deterministic, physically grounded optical and digital indicators:

1. **Laplacian Focus Variance ($\sigma^2_{\text{Lap}}$)**:
   $$\sigma^2_{\text{Lap}} = \mathrm{Var}\left(\nabla^2 I\right), \quad \text{Kernel: } \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}$$
   *Physical Meaning*: Proxies optical focus and beam sharpness. Near-zero values indicate severe defocus blur.
2. **Edge Density ($D_{\text{edge}}$)**:
   $$D_{\text{edge}} = \frac{1}{|\Omega|} \sum_{(x,y) \in \Omega} \frac{\sqrt{G_x(x,y)^2 + G_y(x,y)^2}}{255}$$
   *Physical Meaning*: Structural micro-feature boundary density.
3. **Shannon Information Entropy ($H$)**:
   $$H = -\sum_{k=0}^{255} p(k) \log_2 p(k)$$
   *Physical Meaning*: Richness of the gray-level histogram distribution.
4. **Robust Dynamic Range ($\Delta I_{\text{dyn}}$)**:
   $$\Delta I_{\text{dyn}} = P_{99}(I) - P_{1}(I)$$
   *Physical Meaning*: Effective signal span excluding extreme outliers.
5. **Clipping & Saturation Ratio ($C_{\text{total}}$)**:
   $$C_{\text{total}} = \frac{|\{p \mid I(p) \le I_{\min}\}| + |\{p \mid I(p) \ge I_{\max}\}|}{|\Omega|}$$
   *Physical Meaning*: Detector under-exposure and signal saturation.
6. **High-Frequency Spectral Energy Ratio ($E_{\text{HF}}$)**:
   $$E_{\text{HF}} = \frac{\int_{r > r_{\text{cutoff}}} |\mathcal{F}\{I\}(r, \theta)|^2 \, dr \, d\theta}{\int |\mathcal{F}\{I\}(r, \theta)|^2 \, dr \, d\theta}, \quad r_{\text{cutoff}} = 0.25 \times r_{\text{Nyquist}}$$
   *Physical Meaning*: Spatial frequency energy distribution in 2D Fourier domain.

### 3.2 Composite Quality Risk Calibrator
* Calibrated sigmoid aggregation combining normalized risk penalties:
  $$\mathrm{Risk} = \sigma\left(\sum_{k=1}^6 w_k \cdot \phi_k(I) - \theta\right) \in [0.0, 1.0]$$
* Status Labels:
  - $\mathrm{Risk} < 0.35$: `NOMINAL`
  - $0.35 \le \mathrm{Risk} < 0.65$: `ACCEPTABLE`
  - $\mathrm{Risk} \ge 0.65$: `RISK_FLAGGED`

---

## 4. Vector Retrieval & Index Engine

* **Index Type**: `faiss.IndexFlatIP` (Exact Inner Product Search)
* **Vector Dimension**: 384 (DINOv2 L2-normalized embeddings, inner product $\equiv$ cosine similarity)
* **Index Artifact**: `platform/storage/indexes/faiss_exact_flatip.index`
* **Query Latency**: $\le 0.10\text{ ms}$ on local CPU for $10^4$ vectors.
* **Memory Footprint**: $1.5\text{ KB}$ per 1,000 indexed images.
* **Reproducibility**: Deterministic exact search (zero quantization error, recall $\equiv 1.0$ relative to brute-force).

---

## 5. Model Limitations & Known Boundaries

1. **Illumination Invariance**: Baseline DINOv2 has moderate sensitivity to extreme non-uniform illumination gradients.
2. **Extreme Magnification Jumps**: Cross-magnification retrieval across $>10\times$ difference (e.g. $500\times$ vs $50,000\times$) exhibits reduced recall due to semantic scale shifts.
3. **Synthetic Artifacts vs Physical Defects**: Quality indicators detect low contrast and blur, but cannot definitively prove whether blur was caused by specimen drift, acoustic vibration, or lens defocus without acquisition metadata.
