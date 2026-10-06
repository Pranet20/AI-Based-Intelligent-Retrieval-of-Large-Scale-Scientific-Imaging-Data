# IEEE Paper Section III: Methodology & Mathematical Formulation
**Target Section**: Section III. Problem Formulation & Methodology  

---

## III. METHODOLOGY & MATHEMATICAL FORMULATION

### A. Visual Representation & Metric Embedding Space
Let $\mathcal{I} = \{I_1, I_2, \dots, I_N\}$ denote a repository of scientific micrographs, where each image $I_i \in \mathbb{R}^{H \times W \times C}$. A foundation vision transformer backbone parameterized by weights $\theta$, denoted $f_\theta: \mathcal{I} \to \mathbb{R}^d$, maps each input micrograph to a dense continuous feature representation of dimensionality $d=384$. 

Before feature matching, raw embeddings are projected onto the unit hypersphere $\mathbb{S}^{d-1}$ via $L_2$ normalization:
$$\mathbf{e}_i = \frac{f_\theta(I_i)}{\|f_\theta(I_i)\|_2 + \epsilon}, \quad \text{where } \epsilon = 10^{-12}$$

This normalization establishes strict mathematical equivalence between the cosine similarity of two embeddings and their Euclidean dot product:
$$S_C(\mathbf{e}_i, \mathbf{e}_j) = \frac{\mathbf{e}_i \cdot \mathbf{e}_j}{\|\mathbf{e}_i\|_2 \|\mathbf{e}_j\|_2} = \langle \mathbf{e}_i, \mathbf{e}_j \rangle = 1 - \frac{1}{2}\|\mathbf{e}_i - \mathbf{e}_j\|_2^2$$

### B. Similarity Retrieval and Evaluation Metrics
Given a query micrograph $I_q$ with normalized embedding $\mathbf{e}_q$, the retrieval objective is to identify the ordered sequence of top-$k$ nearest neighbors from the database index $\mathcal{D}$:
$$\mathcal{R}_k(I_q) = \operatorname{arg\,top-}k_{j \in \mathcal{D}} \, S_C(\mathbf{e}_q, \mathbf{e}_j)$$

Retrieval efficacy is quantified using standard information retrieval metrics:
1. **Recall@$k$ ($\text{R@}k$)**: Indicator of whether a ground-truth relevant micrograph appears in the top-$k$ retrieved candidates:
   $$\text{Recall@}k = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \mathbb{I}\left( \text{rank}(I_q^*) \le k \right)$$
2. **Mean Reciprocal Rank ($\text{MRR}$)**: Evaluates the precision of the first relevant match:
   $$\text{MRR} = \frac{1}{|Q|} \sum_{q=1}^{|Q|} \frac{1}{\text{rank}(I_q^*)}$$

### C. Acquisition-Geometry Robustness Modeling
Let $I^{(a)}$ and $I^{(b)}$ denote micrographs of the same physical material specimen acquired under distinct experimental geometries (e.g., beam tilt angle $\theta_{\text{tilt}}$ or detector mode). The unadapted latent vectors exhibit a *measured cross-acquisition similarity gap*:
$$\Delta_{\text{geom}} = \mathbb{E}\left[ S_C(\mathbf{e}_i^{(a)}, \mathbf{e}_i^{(a)}) \right] - \mathbb{E}\left[ S_C(\mathbf{e}_i^{(a)}, \mathbf{e}_i^{(b)}) \right] > 0$$

To mitigate this gap, we formulate a parametric adaptation projection $W_{\text{proj}} \in \mathbb{R}^{d \times d}$:
$$\mathbf{e}_i^{\text{proj}} = \frac{W_{\text{proj}} \mathbf{e}_i}{\|W_{\text{proj}} \mathbf{e}_i\|_2}$$
optimized under a contrastive alignment loss to minimize $\Delta_{\text{geom}}$ while preserving inter-class discriminability.

### D. Image-Derived Quality-Risk Screening
Rather than attempting uncalibrated physical fault diagnosis, we formulate an objective image-derived quality-risk scoring function $S_{\text{risk}}(I) \in [0, 1]$ based on three complementary spatial and frequency metrics:
1. **Modified Laplacian Variance (Sharpness)**:
   $$V_{\text{Lap}}(I) = \operatorname{Var}\left( \nabla^2 I \right)$$
2. **Signal-to-Noise Ratio (SNR Estimation)**:
   $$\text{SNR}_{\text{est}}(I) = 10 \log_{10}\left( \frac{\mu_{\text{signal}}^2}{\sigma_{\text{noise}}^2} \right)$$
3. **Contrast Entropy**:
   $$H(I) = -\sum_{k=0}^{255} p_k \log_2(p_k)$$

The composite risk score is computed via calibrated sigmoid weighting:
$$S_{\text{risk}}(I) = \sigma\left( w_1 \cdot \tilde{V}_{\text{Lap}}^{-1} + w_2 \cdot \tilde{\text{SNR}}^{-1} + w_3 \cdot \tilde{H}^{-1} + b \right)$$
where $\tilde{(\cdot)}$ indicates min-max normalization. Images with $S_{\text{risk}} > \tau_{\text{risk}}$ are automatically queued for curator triage.

### E. Graph-Based Redundancy and Duplicate Clustering
To audit repository redundancy, we define an undirected redundancy graph $G = (V, E)$, where vertices $V$ correspond to the set of ingested micrographs, and an undirected edge exists between vertices $u$ and $v$ if and only if their embedding cosine similarity exceeds a conservative duplicate threshold $\tau_{\text{dup}} = 0.985$:
$$E = \left\{ (u, v) \in V \times V \;\middle|\; u \ne v \land S_C(\mathbf{e}_u, \mathbf{e}_v) \ge \tau_{\text{dup}} \right\}$$

Connected components of $G$ partition the repository into:
- **Singletons**: $|C_k| = 1$ (unique micrographs).
- **Candidate Redundancy Clusters**: $|C_k| \ge 2$ (candidate duplicate sets submitted to the curation workbench).

### F. Relative Embedding-Space Novelty Detection
To highlight atypical or rare microstructural features without manual labels, we compute the $k$-Nearest Neighbor ($k$-NN, $k=5$) latent Euclidean distance across the database:
$$\text{Nov}(I_q) = \frac{1}{k} \sum_{j=1}^k \|\mathbf{e}_q - \mathbf{e}_{(j)}\|_2$$
Micrographs exhibiting sparse local neighborhood density (high $\text{Nov}(I_q)$) are ranked at the top of the scientific discovery queue.
