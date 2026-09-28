# 7. DATA INTEGRITY ASSESSMENT & DUPLICATE DETECTION

### 7.1 Real-Time Defocus Screening (Tenengrad Gradient Energy)
Acquisition-induced focus degradation is among the most pervasive artifacts in high-throughput electron microscopy. In this platform, image-derived focus/quality indicators were evaluated on the declared controlled quality-screening benchmark using unsupervised Tenengrad gradient energy.

On a curated evaluation split of in-focus and controlled synthetic defocus SEM micrographs ($N=120$), the Tenengrad operator achieves:
- **Focus AUROC**: $0.8803$
- **Focus AUPRC**: $0.9618$

The high AUPRC confirms that gradient energy provides an effective zero-shot screening filter for uncurated ingestion pipelines, reliably identifying blurred acquisitions without requiring annotated training data.

### 7.2 Perceptual Duplicate & Redundancy Screening
High-throughput automated scanning frequently generates near-duplicate micrographs of identical microstructures. We implement a two-stage duplicate detection cascade:
1. **Perceptual Hash Filtering (pHash)**: Hamming distance comparison over 64-bit DCT perceptual hashes.
2. **Latent Cosine Matching**: Pairwise cosine similarity thresholding ($	au = 0.95$) over normalized DINOv2 embeddings.

Across the $N=774$ HCCI benchmark, the cascade reveals:
- **Exact Duplicate Pairs**: $0$
- **Near-Duplicate Pairs ($\ge 0.95$ cosine similarity)**: $5$ pairs (perceptual overlap across adjacent FOVs)
- **Natural Perceptual Clusters**: $769$ unique specimen clusters

On controlled perturbation benchmarks with synthetic duplicates, the cascade achieves an overall duplicate detection **F1-score of 0.9810**.

### 7.3 Perturbation Robustness Analysis
We stress-tested the visual representation under simulated physical acquisition corruptions:
- **Additive Gaussian Noise ($\sigma = 0.05$)**: Feature retention of **96.66%** relative to unperturbed embeddings.
- **Severe Synthetic Defocus Blur ($\sigma = 3.0$)**: Feature retention drops to **69.83%**, demonstrating that severe blur induces a meaningful shift in the latent space that aligns with quality-risk flagging.
