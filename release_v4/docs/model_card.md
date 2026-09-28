# MODEL CARD: DINOv2 ViT-S/14 SCIENTIFIC RETRIEVAL BACKBONE

## Model Details
- **Architecture**: Vision Transformer Small with 14x14 patch size (ViT-S/14)
- **Model Parameters**: 22,056,576 parameters
- **Input Resolution**: $224 \times 224$ pixels (3 channels; grayscale micrographs replicated across RGB)
- **Output Representation**: 384-dimensional penultimate class token (`[CLS]`), $L_2$-normalized
- **Pretraining**: Self-supervised learning on LVD-142M dataset via DINOv2 (Oquab et al., 2023)
- **Adaptation Layer**: Optional Supervised Contrastive (SupCon) projection head ($384 \to 128$ dimensions)

## Intended Use
- **Primary Use Case**: Unsupervised and few-shot semantic retrieval of scanning electron microscopy (SEM) micrographs across variable accelerating voltages, beam currents, and detectors.
- **Out-of-Scope Use Cases**:
  - Direct diagnostic or clinical medical pathology decision-making without expert oversight.
  - Optical microscopy or natural color photograph retrieval without domain adaptation.
  - Calibrated posterior probability estimation of anomaly (latent distance $D_{\text{ref}}$ is an uncalibrated relative metric).

## Performance Summary
- **Zero-Shot In-Domain Retrieval (HCCI Benchmark, $N=774$)**:
  - Recall@1: **0.9481**
  - Mean Reciprocal Rank (MRR): **0.9658**
  - Precision@5: **0.8708**
- **SupCon Contrastive Adaptation (Mitigating Instrument Bias)**:
  - Bias Gap Reduction: **68.15%** ($0.0543 \to 0.0173$, paired $t$-test $p = 1.42 \times 10^{-12}$)
  - Multi-seed R@1: **0.9418 ± 0.0059**, MRR: **0.9632 ± 0.0042**, P@5: **0.9053 ± 0.0166**
- **External Zero-Shot Transfer (Carinthia Defect SEM, $N=4,591$)**:
  - Micro R@1: **0.9952**, Macro R@1: **0.9090**, MRR: **0.9961**
- **Inference Latency**:
  - GPU (NVIDIA RTX / T4): $\approx 8.4\text{ ms}$ per image
  - CPU (Intel/AMD x86_64): $\approx 42.1\text{ ms}$ per image
  - FAISS HNSW Retrieval Latency: $0.096\text{ ms}$ (5k vectors) to $0.317\text{ ms}$ (100k vectors)

## Factors & Limitations
1. **Acquisition Sensitivity**: While SupCon reduces accelerating voltage bias by $68.15\%$, severe optical blur ($\sigma = 3.0$) degrades feature retention to $69.83\%$.
2. **Comparative Baselines**: Baselines against CLIP and ResNet-50 are descriptive citations from published literature; local re-execution across identical splits was not verified.
3. **Class Imbalance**: External zero-shot transfer exhibits lower macro sensitivity ($0.9090$) on rare defect classes compared to overall micro accuracy ($0.9952$).
