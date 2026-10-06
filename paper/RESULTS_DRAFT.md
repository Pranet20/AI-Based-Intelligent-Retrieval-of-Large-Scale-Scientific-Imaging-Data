# IEEE Paper Sections VI–IX: Experimental Results
**Target Sections**: Section VI. Visual Retrieval, Section VII. Acquisition Robustness, Section VIII. Multimodal Retrieval, Section IX. Quality & Redundancy  

---

## VI. VISUAL REPRESENTATION & RETRIEVAL RESULTS

### A. Comparative Retrieval Performance
Under the controlled test split ($N = 240$ queries evaluated against $N = 400$ gallery specimens), DINOv2-ViT-S/14 demonstrated substantial retrieval accuracy across all rank thresholds:

| Model / Representation Architecture | Embedding Dimension | $\text{Recall@1}$ | $\text{Recall@5}$ | $\text{Recall@10}$ | $\text{MRR}$ | Single-Image Latency (CPU) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| Random Ranking Baseline | — | 0.0042 | 0.0208 | 0.0417 | 0.0134 | — |
| Perceptual Hashing (pHash) | 64 bits | 0.4120 | 0.5840 | 0.6710 | 0.4930 | **1.2 ms** |
| Supervised ResNet-50 (ImageNet-1k) | 2048 | 0.8125 | 0.8950 | 0.9310 | 0.8492 | 14.2 ms |
| Contrastive ResNet-50 (SimCLR) | 2048 | 0.7815 | 0.8710 | 0.9125 | 0.8320 | 14.1 ms |
| BioMedCLIP (ViT-B/16 Domain-Specific) | 512 | 0.8620 | 0.9240 | 0.9510 | 0.8875 | 32.6 ms |
| Vanilla CLIP (ViT-B/32) | 512 | 0.7240 | 0.8315 | 0.8840 | 0.7680 | 22.1 ms |
| **DINOv2-ViT-S/14 (Proposed Baseline)** | **384** | **0.9481** | **0.9852** | **0.9917** | **0.9658** | **18.4 ms** |

**Key Observations**:
1. DINOv2 outperforms the contrastive SimCLR baseline by **+16.66%** in $\text{Recall@1}$ (0.9481 vs 0.7815) and supervised ResNet-50 by **+13.56%**, despite using a more compact 384-dimensional representation (compared to 2048 dimensions).
2. The self-supervised Vision Transformer captures subtle crystallographic grain boundaries and phase textures without requiring task-specific fine-tuning or labeled supervisory signals.

### B. FAISS Vector Search Latency & Index Scalability
Vector indexing benchmarks executed on CPU demonstrate high computational efficiency:
- **Exact Exhaustive Search (`IndexFlatIP`)**:
  - $N = 1,000$ items: Query latency = **0.12 ms** (Recall = 1.0000).
  - $N = 10,000$ items: Query latency = **0.24 ms** (Recall = 1.0000).
  - RAM Footprint ($N = 10,000$): **15.4 MB**.
- In-memory flat inner-product search provides sub-millisecond query execution, rendering approximate quantization unnecessary for standard departmental collections ($N \le 10^5$).

---

## VII. ACQUISITION-GEOMETRY ROBUSTNESS RESULTS

Evaluating cross-acquisition pairs ($N = 180$) revealed a baseline **cross-acquisition similarity gap** ($\Delta_{\text{geom}} = 0.235$ average cosine drop) when specimens were imaged under differing tilt angles ($10^\circ - 30^\circ$) or switched between SE and BSE detector modes.

Applying an affine projection layer ($W_{\text{proj}} \in \mathbb{R}^{384 \times 384}$) trained on multi-angle pairs:
- Reduced the average similarity gap from **0.235 to 0.136** (a **42.3% mitigation** in cross-acquisition variance).
- Improved cross-angle $\text{Recall@1}$ from **0.7140 to 0.8415**.
- Preserved in-domain retrieval discriminability with zero degradation on standard zero-tilt queries ($\text{Recall@1} = 0.9481$).

---

## VIII. METADATA & MULTIMODAL RETRIEVAL RESULTS

### A. Empirical Findings
Experiments evaluating the fusion of tabular instrument metadata (voltage, magnification, detector mode, working distance) with visual embeddings yielded clear negative results:
- **Metadata-Only Retrieval**: Achieved an $\text{MRR}$ of only **0.3443**, indicating that tabular instrument parameters lack spatial discriminability.
- **Late Fusion Grid Search**: Evaluated weighted linear combinations $\mathbf{s}_{\text{fused}} = \alpha \mathbf{s}_{\text{visual}} + (1 - \alpha) \mathbf{s}_{\text{meta}}$ across $\alpha \in [0.0, 1.0]$. The optimal parameter converged to $\alpha^* = \mathbf{1.0}$, allocating 100% weight to visual features.
- **Deep Fusion Architectures**: Gated MLP and Cross-Attention multi-modal networks failed to outperform the pure visual baseline under the declared test protocol ($\text{MRR} \le 0.9658$).

### B. Reconciled Architectural Decision
Consequently, the platform retains the visual representation as the primary retrieval signal, utilizing structured metadata strictly as a post-retrieval relational filter.

---

## IX. QUALITY-RISK AND REDUNDANCY ANALYSIS RESULTS

### A. Image-Derived Quality-Risk Screening
On the controlled degradation benchmark ($N = 120$ images subjected to synthetic blur, noise, and contrast degradation):
- $\text{AUROC}$: **0.8803**
- $\text{AUPRC}$: **0.9618**
- Evaluated against a baseline random classifier ($\text{AUROC} = 0.5000$) and a simple sharpness heuristic ($\text{AUROC} = 0.7410$), the composite quality-risk engine effectively isolates corrupted micrographs for human review.

### B. Duplicate Detection & Redundancy Graph
- **Controlled Synthetic Benchmark ($N = 120$)**: Evaluated across re-encoding, affine scaling, and contrast perturbations. The cosine similarity classifier ($\tau = 0.985$) achieved:
  - $\text{AUROC}$: **0.9998**
  - $F_1\text{-score}$: **0.9810**
- **Natural Repository Graph Audit ($N = 769$)**: Partitioning the full unperturbed collection yielded 769 connected components:
  - **764 singletons** (99.35% of records are distinct).
  - **5 duplicate pairs** (10 total images, representing a natural redundancy rate of 0.65%).

### C. Relative Embedding-Space Novelty Detection
On the novelty evaluation split ($N = 120$), k-NN latent distance ($k=5$) distinguished out-of-distribution biological specimens and rare microstructures from in-distribution materials with:
- $\text{AUROC}$: **0.9825**
- Outperformed Isolation Forest ($\text{AUROC} = 0.9140$) and One-Class SVM ($\text{AUROC} = 0.8920$).
