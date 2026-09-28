# 5. SELF-SUPERVISED REPRESENTATION & ACQUISITION BIAS MITIGATION

### 5.1 Foundation Model Representation (DINOv2 ViT-S/14)
We evaluate the frozen DINOv2 Vision Transformer (ViT-S/14, 22.06M parameters) operating without task-specific fine-tuning. DINOv2 constructs discriminative, patch-level semantic representations via self-distillation with multi-crop objectives. In zero-shot retrieval across the $N=774$ HCCI benchmark, DINOv2 (384-dimensional penultimate class token) achieves:
- **Recall@1 (R@1)**: $0.9481$
- **Mean Reciprocal Rank (MRR)**: $0.9658$
- **Precision@5 (P@5)**: $0.8708$

For comparative context, classical supervised ResNet-50 baselines reported in prior literature achieved $\text{R@1} = 0.9245$. We emphasize that this ResNet-50 metric is cited as a descriptive baseline from historical literature and was not locally re-executed.

### 5.2 Supervised Contrastive Adaptation (SupCon)
While zero-shot DINOv2 features exhibit strong semantic clustering, empirical inspection revealed that micrographs of the same physical mineral specimen acquired under different accelerating voltages (e.g., $5\text{ kV}$ vs. $20\text{ kV}$) exhibited an acquisition bias gap: the average cosine similarity between same-specimen/different-voltage pairs was lower than same-specimen/same-voltage pairs by an initial gap of $\Delta_{\text{bias}} = 0.0543$.

To explicitly suppress acquisition variance without destroying semantic discrimination, we train a lightweight projection head ($384 \to 128$ dimensions) using Supervised Contrastive Loss (SupCon):
$$\mathcal{L}_{\text{SupCon}} = \sum_{i \in I} \frac{-1}{|P(i)|} \sum_{p \in P(i)} \log \frac{\exp(z_i \cdot z_p / \tau)}{\sum_{a \in A(i)} \exp(z_i \cdot z_a / \tau)}$$
where positive pairs $P(i)$ consist of micrographs of the identical specimen acquired under differing instrument settings.

### 5.3 Quantitative Bias Reduction Results
Following contrastive adaptation, the acquisition bias gap is reduced from $0.0543$ to $0.0173$. This represents an absolute bias gap reduction of **68.15%**, verified as statistically significant via a paired two-tailed $t$-test ($p = 1.42 \times 10^{-12}$). Across multi-seed evaluation, the adapted representation yields:
- $\text{R@1} = 0.9418 \pm 0.0059$
- $\text{MRR} = 0.9632 \pm 0.0042$
- $\text{P@5} = 0.9053 \pm 0.0166$

While global R@1 shows a minor trade-off ($0.9481 \to 0.9418$), top-5 precision increases significantly ($0.8708 \to 0.9053$), demonstrating superior retrieval stability across diverse acquisition parameters.
