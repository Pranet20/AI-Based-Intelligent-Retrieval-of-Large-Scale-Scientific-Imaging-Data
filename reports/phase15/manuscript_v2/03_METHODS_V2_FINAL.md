# 3. Methodology & System Architecture (Final V2 Manuscript Draft)

## 3.1 Self-Supervised Vision Transformer Pipeline

Micrographs are standardized to dimensions $224 \times 224$ pixels via bicubic interpolation and normalized using ImageNet channel statistics. The primary visual encoder is a self-supervised Vision Transformer (DINOv2 ViT-S/14, 12 layers, 384 hidden dimension, 6 heads, $14 \times 14$ pixel patch tokenization):
$$X \in \mathbb{R}^{H \times W \times C} \xrightarrow{\text{Patch Tokenizer}} [x_{\text{CLS}}; x_1, \dots, x_{196}] \in \mathbb{R}^{197 \times 384}$$
The output representation is obtained by mean-pooling the spatial patch tokens followed by L2 normalization on the unit hypersphere:
$$z_v = \frac{\bar{x}_{\text{patch}}}{\|\bar{x}_{\text{patch}}\|_2} \in \mathbb{S}^{383}$$
In the supervised contrastive adapted configuration (B4), a lightweight multi-layer projection head is fine-tuned using the Supervised Contrastive (SupCon) loss over domain-labeled metallurgical classes while preserving the frozen ViT backbone.

---

## 3.2 Nearest-Neighbor Indexing & Scalable Retrieval

Normalized embeddings are indexed using the Hierarchical Navigable Small World (HNSW) graph algorithm implemented via FAISS ($M = 32$, `efSearch` = 64, `efConstruction` = 40). Nearest neighbors are ranked by cosine similarity:
$$S(q, x_i) = q \cdot x_i$$
Evaluation metrics are computed across held-out query splits:
- **Recall at Rank $k$ (R@$k$):** Proportion of queries for which at least one valid class positive appears in the top $k$ candidates.
- **Mean Reciprocal Rank (MRR):** Reciprocal rank of the first relevant candidate: $\text{MRR} = \frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$.
- **Precision at Rank $k$ (P@$k$):** Proportion of the top $k$ retrieved candidates that belong to the query class.

---

## 3.3 Latent Density Uncertainty Estimation

To overcome the near-random discriminative power of the raw score margin heuristic ($\Delta S = S_1 - S_2$, AUROC $\approx 0.515$), retrieval uncertainty is quantified via the Euclidean distance in normalized latent space to the nearest reference class centroid:
$$D_{\text{ref}}(q) = \min_{k} \|q - \mu_k\|_2$$
where $\mu_k = \frac{1}{|C_k|} \sum_{x \in C_k} x$ is the empirical centroid of reference class $k$. Queries with large $D_{\text{ref}}$ indicate out-of-distribution acquisition conditions or specimen anomalies and are prioritized for expert review.

---

## 3.4 Composite Curation Priority Workflow

Ingested micrographs are screened through automated quality-risk filters (Laplacian focus variance $\sigma_{\text{Lap}}^2 < 100$, histogram dynamic range clipping, and OCR scale-bar masking) and assigned a composite Curation Priority Index (CPI):
$$\text{CPI}(x) = 0.40 \cdot \text{Risk}_{\text{quality}}(x) + 0.35 \cdot D_{\text{ref}}(x) + 0.25 \cdot (1 - \text{Conf}(x))$$
Micrographs are queued in descending CPI order for double-blind expert review in the curation dashboard.
