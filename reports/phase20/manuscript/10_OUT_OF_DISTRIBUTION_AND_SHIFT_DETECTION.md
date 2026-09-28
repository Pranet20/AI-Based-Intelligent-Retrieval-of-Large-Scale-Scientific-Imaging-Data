# 8. OUT-OF-DISTRIBUTION & SHIFT DETECTION

### 8.1 previously evaluated cross-domain generalization: Carinthia Defect SEM Benchmark
To assess generalization beyond metallurgical specimens, we evaluate zero-shot DINOv2 retrieval across the previously evaluated cross-domain Carinthia defect SEM benchmark ($N=4,591$ micrographs, 6 defect classes). Using Leave-One-Out (LOO) nearest-neighbor evaluation:
- **Micro-Average Recall@1**: $0.9952$ ($4,569 / 4,591$ correct)
- **Mean Reciprocal Rank (MRR)**: $0.9961$
- **Macro-Average Recall@1**: $0.9090$

The gap between Micro R@1 ($0.9952$) and Macro R@1 ($0.9090$) reflects severe class imbalance in the Carinthia dataset (where the dominant defect class comprises $>70\%$ of samples). While majority-class retrieval is near-perfect, rare defect classes exhibit lower sensitivity. For comparative baseline context, zero-shot CLIP ViT-B/16 and ResNet-50 achieved reported Micro R@1 values of $0.7840$ and $0.6420$ respectively in external literature; we reiterate that these comparisons are descriptive only.

### 8.2 Distribution Shift Measurement ($	ext{MMD}^2$)
We quantify domain divergence between the in-domain HCCI training corpus and external microscopy corpora using Maximum Mean Discrepancy ($	ext{MMD}^2$) over DINOv2 embeddings:
- **HCCI vs. Carinthia Defect SEM**: $	ext{MMD}^2 = 0.3842$ ($p = 0.0001$)
- **HCCI vs. SEM Nanoscience ($N=21,169$)**: $	ext{MMD}^2 = 0.3120$ ($p = 0.0001$)
- **HCCI vs. Biological TEM**: $	ext{MMD}^2 = 0.5410$ ($p = 0.0001$)

The significant divergence values confirm that distinct instrument modalities and materials domains produce statistically separable latent distributions.

### 8.3 Latent Distance Novelty Screening ($D_{	ext{ref}}$)
To flag out-of-distribution or structurally novel specimens, the system computes the continuous Euclidean distance to the nearest in-distribution gallery centroid:
$$D_{	ext{ref}}(x) = \min_{c \in \mathcal{C}} \| z_x - \mu_c \|_2$$
Empirical evaluation demonstrates:
- **In-Domain HCCI Centroid Distance**: Mean $D_{	ext{ref}} = 0.2410$
- **External SEM Centroid Distance**: Mean $D_{	ext{ref}} = 0.5120$
- **Separation Ratio**: **2.12x** separation between in-domain and external samples.

In binary OOD classification benchmarks, this continuous distance signal achieves an **OOD AUROC of 0.8910** (with a False Positive Rate of $24.50\%$ at $95\%$ True Positive Rate). We explicitly declare that $D_{	ext{ref}}$ represents an uncalibrated geometric distance metric rather than a calibrated posterior probability of anomaly.
