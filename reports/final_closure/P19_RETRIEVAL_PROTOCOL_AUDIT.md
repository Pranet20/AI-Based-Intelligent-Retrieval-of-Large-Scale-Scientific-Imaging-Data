# P19 RETRIEVAL & EVALUATION PROTOCOL AUDIT

**Project**: AI-Powered Scientific Image Data Management Platform  
**Document**: P19 Protocol Specification & Classification Audit  
**Date**: 2026-09-27  
**Status**: AUDITED_AND_CLARIFIED  

---

## 1. Executive Summary & Terminology Standardization

The evaluation conducted on the Carinthia Defect SEM dataset (4,591 micrographs, 6 defect classes) was previously termed:
> *"Leave-one-out image retrieval (Micro R@1 = 0.9952, Macro R@1 = 0.9090)"*

### Authoritative Protocol Classification:
Because the ground truth available for Carinthia consists of **categorical defect class labels** rather than same-physical-specimen multi-view identity pairs, this protocol is formally classified as:
> **"Nearest-Neighbor Class Retrieval / Class-Consistency Evaluation (Leave-One-Out Protocol)"**

Under this protocol, a retrieval of rank 1 is counted as successful if and only if the top-1 nearest neighbor in the gallery shares the identical ground-truth defect class label with the query image.

---

## 2. Complete Mathematical & Operational Protocol Specification

1. **Query Set ($Q$)**:
   - All 4,591 images in the Carinthia defect corpus.
   - Total queries: $|Q| = 4,591$.
2. **Gallery Set ($G_q$) for Query $q$**:
   - The entire Carinthia corpus excluding the query image itself ($G_q = \text{Carinthia} \setminus \{q\}$).
   - Gallery size per query: $|G_q| = 4,590$.
3. **Self-Match Exclusion**:
   - Query image $q$ is strictly excluded from its own candidate search gallery ($d(q, q)$ is masked).
4. **Positive Definition**:
   - Any gallery image $g \in G_q$ whose annotated defect class label matches the query class label: $\text{Class}(g) == \text{Class}(q)$.
5. **Negative Definition**:
   - Any gallery image $g \in G_q$ whose defect class label differs from the query: $\text{Class}(g) \ne \text{Class}(q)$.
6. **Distance / Similarity Metric**:
   - Inner product (cosine similarity) on $L_2$-normalized 384-dimensional feature embeddings extracted from the frozen DINOv2 ViT-S/14 backbone:
     $$S(q, g) = \langle \hat{\mathbf{z}}_q, \hat{\mathbf{z}}_g \rangle, \quad \hat{\mathbf{z}} = \frac{\mathbf{z}}{\|\mathbf{z}\|_2}$$
7. **Embedding Normalization**:
   - Strict unit Euclidean norm ($\|\hat{\mathbf{z}}\|_2 = 1.0$) applied to all query and gallery vectors prior to distance computation.
8. **Top-$K$ Procedure**:
   - Exact nearest neighbor ranking computed via dense matrix multiplication:
     $$\text{Rank}(q) = \operatorname{arg\,sort}_{g \in G_q} (-S(q, g))$$
9. **Class Label Usage**:
   - Class labels are strictly evaluation-time ground truth. The model operates zero-shot with no class-conditional adaptation or classification head during inference.
10. **Specimen Grouping**:
    - Individual physical defect specimens were not segregated into disjoint wafer groups because wafer/die metadata was stripped in the upstream industrial benchmark; grouping is strictly by defect class label.
11. **Duplicate Handling**:
    - All 4,591 physical images are distinct acquisitions; perceptual hashing confirmed zero exact duplicates in the gallery.
12. **Ties**:
    - Floating-point cosine ties are resolved by arbitrary index order; empirically, zero identical cosine scores were observed between distinct image pairs.
13. **Missing Labels**:
    - None (100% of Carinthia samples possess verified integer class annotations 1 through 6).
14. **Metric Calculation**:
    - **Micro-Averaged R@1**:
      $$\text{Micro R@1} = \frac{1}{|Q|} \sum_{q \in Q} \mathbb{I}\left[\text{Class}(g_q^{(1)}) == \text{Class}(q)\right] = \frac{4569}{4591} = 0.9952$$
    - **Macro-Averaged R@1**:
      $$\text{Macro R@1} = \frac{1}{C} \sum_{c=1}^C \frac{1}{|Q_c|} \sum_{q \in Q_c} \mathbb{I}\left[\text{Class}(g_q^{(1)}) == c\right] = 0.9090$$
    - **Mean Reciprocal Rank (MRR)**:
      $$\text{MRR} = \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\min \{r : \text{Class}(g_q^{(r)}) == \text{Class}(q)\}} = 0.9961$$
