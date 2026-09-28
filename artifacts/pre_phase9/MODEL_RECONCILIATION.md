# Model Architecture Reconciliation & Formal Specification
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `pre_phase9_model_reconciliation_001`  
**Date:** September 2026  
**Status:** Authoritative Reconciliation — Pre-Phase-9 Audit

---

## 1. Executive Summary & Root Cause Analysis

During the Pre-Phase-9 Scientific Consistency Audit, a critical naming discrepancy was identified across project documentation:
- **Implemented Architecture:** The physical codebase, frozen tensor checkpoints, configuration files, manifest parquets, and FAISS indices exclusively use **`dinov2_vits14`** (Vision Transformer Small with 14x14 patch size, embedding dimension $D=384$, 22,056,576 parameters).
- **Erroneous Narrative Mentions:** Certain narrative sections in `reports/phase7/PHASE7_BENCHMARK_REPORT.md` and subsequent synthesis summaries erroneously referred to the foundation model as **"DINOv2 ViT-B/14"** with "768-dimensional embeddings".

**Audit Determination:**
This discrepancy is a pure **documentation/narrative typo** that occurred during manuscript drafting and synthesis reporting. At no point in the project lifecycle was a 768-dimensional model trained, embedded, or indexed. All numerical results, downstream evaluations (SupCon, FAISS, metadata fusion, curation cascades), and platform inference pipelines have always operated on 384-dimensional representations derived from `dinov2_vits14`.

---

## 2. Definitive Proof of Physical Implementation

### 2.1 Configuration Files
- `configs/phase2.yaml` specifies:
  ```yaml
  model:
    name: "dinov2_vits14"
    pretrained: true
    embedding_dim: 384
    patch_size: 14
    pooling: "cls"
  ```
- `configs/phase4.yaml` specifies:
  ```yaml
  backbone:
    name: "dinov2_vits14"
    input_dim: 384
    projector_dim: 128
  ```
- `configs/phase5.yaml` specifies:
  ```yaml
  fusion:
    visual_dim: 384
    metadata_dim: 384
    projection_dim: 384
  ```
- `configs/phase8.yaml` specifies:
  ```yaml
  model:
    name: "dinov2_vits14"
    embedding_dim: 384
  ```

### 2.2 Frozen Data Artifacts and Embeddings
- `data/processed/embeddings/hcci_dinov2_embeddings.parquet`:
  - Number of rows: $774$
  - Column `embedding`: Vector of length **384** (Float32).
- `data/processed/embeddings/carinthia_dinov2_embeddings.parquet`:
  - Number of rows: $4,591$
  - Column `embedding`: Vector of length **384** (Float32).
- Combined FAISS benchmark index:
  - Vector count: $5,365$
  - Vector dimension ($d$): **384**.

### 2.3 Checkpoint Weights and Parameter Counts
Inspecting the PyTorch checkpoint `data/processed/phase4/models/supcon_best_seed42.pt`:
- Checkpoint key: `projector.0.weight` has shape `[128, 384]`.
- Checkpoint key: `projector.2.weight` has shape `[128, 128]`.
- Backbone: `torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')`
  - Parameter count: $22,056,576$ (backbone) + $66,048$ (projector) = $22,122,624$ total parameters.
  - ViT-B/14 (86.6M parameters, 768-d) does not exist in any checkpoint or tensor dictionary.

---

## 3. Exhaustive Subsystem Architecture Matrix

| Phase | Subsystem / Component | Architecture / Method | Parameter Count | Embedding Dim ($D$) | Loss / Objective |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 2** | Visual Foundation Encoder | `dinov2_vits14` (Pre-trained self-supervised ViT-S/14) | 22,056,576 | 384 | Pretrained DINOv2 self-distillation (frozen) |
| **Phase 3** | Vector Retrieval Index | FAISS `IndexFlatIP` & `IndexHNSWFlat` ($M=32, efSearch=64, efConstruction=64$) | 0 (Index parameters) | 384 | Maximum Inner Product / Cosine Similarity |
| **Phase 4** | Acquisition-Robust Projector | Frozen `dinov2_vits14` + 2-layer MLP Projector ($384 \to 128 \to 128$ with BatchNorm & ReLU) | 66,048 (Trainable) | 128 (Projected) / 384 (Backbone) | Supervised Contrastive Loss ($\tau=0.07$) with same-acquisition masking |
| **Phase 5** | Metadata Encoder & Hybrid Fusion | Categorical Entity Embedding (32-d) + StandardScaler Numerical MLP $\to$ Linear $\to$ ReLU $\to$ Linear $\to$ L2-Norm | ~18,400 (Trainable) | 384 (Projected to match visual space) | Symmetric InfoNCE / Contrastive Alignment ($\tau=0.07$) + Convex visual-first fusion ($\alpha^*=1.0$) |
| **Phase 6** | Image Quality Assessment (IQA) | Multi-attribute classical signal processing (Laplacian blur, noise sigma, contrast, clipping, blockiness) | Deterministic (0 learnable params) | 5 scalar metrics | Quality Risk Score ($Q_{risk} \in [0, 1]$), Beta/Sigmoid calibrated |
| **Phase 6** | Near-Duplicate / Redundancy Graph | 4-Stage Cascade: 1. SHA-256; 2. pHash/dHash ($\le 6$); 3. DINOv2 cosine ($\ge 0.985$); 4. SSIM ($\ge 0.95$) + MAE ($\le 5.0$) | Deterministic / Cascade | 384 (Stage 3) | Union-Find Connected Components |
| **Phase 8** | Production Inference Engine | TorchScript / PyTorch `dinov2_vits14` + Phase 4 Projector ONNX/TorchScript | 22,122,624 | 384 / 128 | Bit-exact numerical parity ($L_\infty < 10^{-6}$) with frozen research |

---

## 4. Phase 4 Mechanism Clarification: Loss & Masking

A common ambiguity in literature review summaries is whether Phase 4 utilizes "adversarial domain regularization" or "metadata penalty regularization". The audit confirms the exact mathematical implementation:

1. **Architecture:**
   $$\mathbf{z} = g(\mathbf{v}) = W_2 \cdot \text{ReLU}(\text{BN}(W_1 \mathbf{v})), \quad \mathbf{v} \in \mathbb{R}^{384}, \; \mathbf{z} \in \mathbb{R}^{128}, \; \hat{\mathbf{z}} = \frac{\mathbf{z}}{\|\mathbf{z}\|_2}$$
2. **Supervised Contrastive Objective with Acquisition Masking:**
   The training objective is Supervised Contrastive Loss (SupCon) formulated over minibatches where positive pairs share the same material specimen/class label ($y_i = y_j$).
   Crucially, **same-acquisition pairs are masked out or down-weighted**: positive pairs $(i, j)$ are formed exclusively between images of the *same specimen acquired under different optical conditions / instruments* ($y_i = y_j$ and $a_i \neq a_j$).
3. **No Explicit Penalty Regularizer:**
   There is **no** Lagrangian penalty term (e.g. $+\lambda \|\text{corr}(z, a)\|^2$) added to the loss function. The domain-invariance is induced entirely through **positive/negative pair selection semantics** in SupCon. All mentions of "explicit metadata penalty regularization" must be corrected to "acquisition-contrastive pair masking".

---

## 5. Phase 5 Fusion Mechanism Clarification

1. **Metadata Feature Encoding:**
   - Categorical features (instrument, voltage, detector) pass through learnable embedding tables ($d_{cat}=32$).
   - Continuous numerical features (magnification, working distance) pass through standard scaling followed by a 2-layer MLP.
   - Combined representation is projected to $\mathbb{R}^{384}$ and $L_2$-normalized to form $\mathbf{m} \in \mathbb{R}^{384}$.
2. **Hybrid Retrieval Formulation:**
   Given query visual vector $\mathbf{v}_q$ and candidate visual vector $\mathbf{v}_c$, and metadata vectors $\mathbf{m}_q, \mathbf{m}_c$:
   $$S_{hybrid}(q, c) = \alpha \cdot \cos(\mathbf{v}_q, \mathbf{v}_c) + (1 - \alpha) \cdot \cos(\mathbf{m}_q, \mathbf{m}_c)$$
3. **Optimal Weight Selection:**
   On the validation split across all feature groups A through F, hyperparameter search evaluated $\alpha \in [0.0, 0.1, \dots, 1.0]$. The validation-optimal coefficient was found to be **$\alpha^* = 1.0$**.
   - Consequently, visual retrieval alone provides superior discriminative resolution over discrete metadata buckets.
   - Metadata filtering serves primarily as a pre-filtering constraint or secondary re-ranking criterion rather than a score attenuator for top-1 accuracy.

---

## 6. Inventory of Documentation Requiring Correction

The following files contain text referring to "ViT-B/14" or "768-d" that must be corrected to "ViT-S/14" and "384-d" prior to Phase 9 manuscript submission:

1. `reports/phase7/PHASE7_BENCHMARK_REPORT.md`:
   - Line 142: Change "DINOv2 ViT-B/14 (768-dimensional)" $\to$ "DINOv2 ViT-S/14 (`dinov2_vits14`, 384-dimensional, 22.1M parameters)".
   - Table 2 caption: Change "768-d feature space" $\to$ "384-d feature space".
2. `reports/phase8/PHASE8_REPORT.md`:
   - Section 3.2: Clarify that the platform model parity check was executed against `dinov2_vits14` (384-d) yielding maximum absolute difference $< 10^{-6}$.
3. Any master summary document mentioning 768 dimensions.

---

## 7. Audit Certification

This document formally certifies that:
1. `dinov2_vits14` (384-d) is the **exclusive, authoritative** vision backbone of the platform across Phases 1 through 8.
2. All empirical measurements, speed benchmarks, memory footprints, and retrieval scores correspond strictly to this 384-dimensional architecture.
3. No 768-dimensional model was ever trained or deployed in this project.
