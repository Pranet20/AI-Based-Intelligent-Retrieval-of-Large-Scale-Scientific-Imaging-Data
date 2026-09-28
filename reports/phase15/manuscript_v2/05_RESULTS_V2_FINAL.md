# 5. Experimental Results (Final V2 Manuscript Draft)

## 5.1 Visual Representation Baseline Comparison (RQ1)

On the held-out Zeiss GeminiSEM test split ($N = 212$ queries, $N = 5{,}365$ gallery), self-supervised Vision Transformers and supervised convolutional networks demonstrate distinct performance profiles:

### Table 1: Visual Architecture Retrieval Performance

| Model Architecture | Pretraining Objective | R@1 | R@5 | R@10 | MRR | P@5 | P@10 |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ResNet-50** | Supervised (ImageNet-1k) | 0.9245 | **1.0000** | **1.0000** | 0.9542 | 0.8670 | 0.7929 |
| **DINOv2 ViT-S/14 (B3)** | Self-Supervised (LVD-142M) | **0.9481** | 0.9906 | 0.9953 | **0.9658** | 0.8708 | 0.7958 |
| **DINOv2 SupCon (B4)** | Contrastive Fine-Tuned | 0.9387 | 0.9906 | 0.9953 | 0.9612 | **0.9053** | **0.8038** |

**Empirical Findings:**
1. DINOv2 ViT-S/14 (B3) achieved higher top-1 exact retrieval accuracy (+0.0236 in R@1) and higher overall Mean Reciprocal Rank (+0.0116 in MRR) compared to the ImageNet-pretrained ResNet-50 baseline.
2. ResNet-50 achieved higher broader candidate recall at ranks 5 and 10 ($R@5 = 1.0000$ vs $0.9906$).
3. Supervised contrastive adaptation (B4) yielded the highest top-5 precision density ($P@5 = 0.9053$ vs $0.8670$, a +0.0383 improvement over ResNet-50), demonstrating optimal cluster purity in the top-5 retrieval window.

---

## 5.2 Multimodal Representation & Confounder Evaluation (RQ2)

Conditioning visual representations on instrument acquisition metadata degraded retrieval performance across all evaluated architectures:

### Table 2: Multimodal Architecture Retrieval Benchmarks

| Configuration ID | Architecture Description | R@1 | MRR | P@5 | $\Delta$ R@1 vs Visual |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **B0** | **Visual-Only (DINOv2 ViT-S/14)** | **0.9481** | **0.9658** | **0.8708** | **Baseline** |
| **B1** | Metadata-Only (7 Scalar Features) | 0.0519 | 0.3443 | 0.0632 | -0.8962 |
| **B2** | Linear Late Fusion ($\alpha = 0.5$) | 0.6274 | 0.7289 | 0.5981 | -0.3207 |
| **B3** | Non-Linear Gated MLP (Phase 13) | 0.5896 | 0.7034 | 0.5745 | -0.3585 |
| **B4** | Learned Cross-Attention (Phase 15) | 0.6132 | 0.7180 | 0.5858 | -0.3349 |

Conditioning on acquisition parameters reduced R@1 by 32.1% to 35.8%. As an empirical failure mechanism, instrument parameters vary independently of metallurgical phase, acting as confounding coordinates in joint representation space.

---

## 5.3 Cross-Domain Generalization Benchmarks (RQ3)

In leave-one-out evaluation across 4,591 Carinthia industrial SEM defect micrographs, unadapted DINOv2 representations demonstrated robust generalization within the SEM modality:
- **Micro-Averaged R@1:** **0.9952** ($4{,}569 / 4{,}591$).
- **Macro-Averaged R@1:** **0.9090** across the six defect categories (Class 1: 0.8545; Class 2: 0.8750; Class 3: 0.9988; Class 4: 0.9758; Class 5: 0.7500; Class 6: 1.0000).
- **Domain Centroid Distance:** Cosine similarity of 0.4018 (Euclidean distance: 1.0938) between HCCI and Carinthia centroids, quantifying structural domain shift.
- **Cross-Modality Transfer (SEM $\to$ TEM):** Zero-shot transfer achieved R@1 = 0.7642, which improved to 0.9104 upon supervised adaptation.

---

## 5.4 Uncertainty Discrimination & Curation Workflow (RQ4)

- **Uncertainty Calibration:** Latent Distance-to-Reference Centroid ($D_{\text{ref}}$) achieved an AUROC of **0.7412** for predicting retrieval correctness, substantially outperforming the raw score margin heuristic ($\text{AUROC} = 0.5146$).
- **Human Curation Acceleration:** Under AI-prioritized queue sorting (Condition B), experts discovered **85.3% ($58/68$) of actionable novelty/quality cases within the first 50% of the review queue** (35.4 minutes), reducing expert review workload by 41.2% compared to unprioritized review while maintaining high inter-annotator agreement ($\kappa = 0.856$).
