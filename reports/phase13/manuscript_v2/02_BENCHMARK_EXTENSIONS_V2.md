# 2. Extended Experimental Benchmarks (V2 Manuscript — Post-Audit Remediation)

## 2.1 Convolutional vs. Transformer Representation Learning

To address reviewer interest regarding standard supervised convolutional baselines, additional validation evaluated an ImageNet-1k pretrained ResNet-50 against our self-supervised DINOv2 ViT-S/14 configurations on the identical held-out Zeiss GeminiSEM test split ($N = 212$ queries, $N = 5{,}365$ gallery).

### Table: Visual Architecture Performance Comparison

| Model Architecture | Pretraining Objective | Target Split | R@1 | R@5 | R@10 | MRR | P@5 | P@10 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **ResNet-50** | Supervised (ImageNet-1k) | Zeiss SEM Held-Out | 0.9245 | **1.0000** | **1.0000** | 0.9542 | 0.8670 | 0.7929 |
| **DINOv2 ViT-S/14 (B3)** | Self-Supervised (LVD-142M) | Zeiss SEM Held-Out | **0.9481** | 0.9906 | 0.9953 | **0.9658** | 0.8708 | 0.7958 |
| **DINOv2 SupCon (B4)** | Contrastive Fine-Tuned | Zeiss SEM Held-Out | 0.9387 | 0.9906 | 0.9953 | 0.9612 | **0.9053** | **0.8038** |

**Empirical Analysis & Scoped Findings:**
1. On the evaluated held-out Zeiss Gemini retrieval benchmark, DINOv2 ViT-S/14 achieved higher top-1 retrieval performance (R@1 = 0.9481 vs 0.9245, a +0.0236 delta) and higher MRR (0.9658 vs 0.9542, +0.0116) than the ImageNet-pretrained ResNet-50 baseline.
2. Conversely, ResNet-50 achieved higher broader recall at ranks 5 and 10 ($R@5 = 1.0000$ vs $0.9906$).
3. Supervised contrastive adaptation (B4) yielded the highest precision density at rank 5 ($P@5 = 0.9053$ vs $0.8670$, a +0.0383 gain), demonstrating the effectiveness of domain-specific contrastive fine-tuning for cluster purity.

---

## 2.2 Deep Non-Linear Multimodal Fusion Evaluation

To determine whether the degradation observed with linear multimodal fusion in Phase 5 was an artifact of linear score combination, additional validation evaluated a non-linear gated Multi-Layer Perceptron (MLP). The network maps normalized metadata vectors ($d_m = 7$) and visual features ($d_v = 384$) through learned non-linear projections with sigmoid gating:

$$h_v = \text{GELU}(W_v v + b_v), \quad h_m = \text{GELU}(W_m m + b_m)$$
$$g = \sigma(W_g [h_v; h_m] + b_g)$$
$$z_{\text{fused}} = \text{LayerNorm}(g \odot h_v + (1 - g) \odot h_m)$$

### Table: Multimodal Fusion Ablation Results

| Pipeline Configuration | Fusion Mechanism | R@1 | MRR | P@5 | $\Delta$ R@1 vs Visual Baseline |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Visual-Only (DINOv2 B3)** | None | **0.9481** | **0.9658** | **0.8708** | Baseline |
| **Metadata-Only (Linear)** | None | 0.0519 | 0.3443 | 0.0632 | -0.8962 |
| **Multimodal Linear Late Fusion** | Linear Combination ($\alpha = 0.5$) | 0.6274 | 0.7289 | 0.5981 | -0.3207 |
| **Multimodal Gated MLP (Phase 13)** | Non-Linear Gated Fusion | 0.5896 | 0.7034 | 0.5745 | **-0.3522** |

**Discussion & Hypothesized Failure Mechanism:**  
On this benchmark, conditioning the visual representation on the evaluated metadata configuration reduced retrieval performance across both linear and non-linear fusion. As a hypothesized failure mechanism, instrument acquisition settings (accelerating voltage, aperture size, working distance) vary independently of metallurgical phase identity; dissimilar microstructures are frequently acquired under identical machine settings, causing metadata features to act as confounding signals when fused with dense visual representations.

---

## 2.3 Acquisition Robustness Under Controlled Image Perturbations

We subjected the retrieval pipeline to five controlled synthetic perturbations approximating operational variations ($N = 212$ queries, using the B4 seed 42 checkpoint with clean baseline R@1 = 0.9434):

| Perturbation Condition | Evaluated Variation | Empirical R@1 | Relative Retention |
| :--- | :--- | :---: | :---: |
| **Clean Baseline** | Nominal calibrated micrograph | **0.9434** | **100.0%** |
| **JPEG-50 Compression** | Lossy transmission compression | 0.9057 | 96.0% |
| **Scale-Bar Overlay** | Uncropped measurement banner | 0.8491 | 90.0% |
| **Low Contrast (50%)** | Reduced detector dynamic range | 0.7264 | 77.0% |
| **Gaussian Noise ($\sigma=15$)** | Fast raster scan noise | 0.6038 | 64.0% |
| **Severe Defocus Blur** | Objective lens focal plane drift | 0.4528 | 48.0% |

The model showed graceful degradation under localized artifacts (scale-bars, mild compression), but severe degradation under defocus blur, which reduced top-1 retention to 48%. This highlights the operational importance of automated blur pre-filtering during repository ingestion.
