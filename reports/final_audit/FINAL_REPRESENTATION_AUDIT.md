# Master Final Representation Audit (Phase 2)

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Visual Backbone Verification, Determinism, Parameter Count, and Preprocessing  
**Status:** `EMPIRICALLY_VERIFIED`

---

## 1. Model Architecture & Mathematical Specification

- **Architecture:** Vision Transformer (DINOv2 ViT-S/14)
- **Patch Resolution:** $14 \times 14$ pixels
- **Input Dimension:** $224 \times 224 \times 3$
- **Patch Token Count:** $(224 / 14)^2 = 16 \times 16 = 256$ spatial patches (pre-pooling)
- **Latent Embedding Dimension ($d$):** **384** float32 scalars
- **Total Parameter Count:** Exactly **22,056,576 parameters**
- **Trainable Parameters in Backbone:** Exactly **0** (Backbone is strictly frozen in inference and adaptation).
- **Projection Head (B4 SupCon):** 2-layer MLP ($384 \to 384 \to 384$ with ReLU and L2 normalization; 295,680 parameters).
- **Authoritative Checkpoint:** `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` (SHA-256: `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`).

---

## 2. Preprocessing Determinism & Boundary Conditions

- **Input Conversion:** Single-channel grayscale SEM TIFF images are replicated across 3 RGB channels without color jitter.
- **Normalization:** Evaluated using ImageNet channel mean ($\mu = [0.485, 0.456, 0.406]$) and standard deviation ($\sigma = [0.229, 0.224, 0.225]$).
- **Resizing Behavior & Scoped Language:**  
  Micrographs are resized directly to $224 \times 224$ pixels using bicubic interpolation (`Image.Resampling.BICUBIC`).  
  > [!IMPORTANT]
  > **Language Correction:** The manuscript must **never claim resolution preservation**. Standard resizing alters high-frequency pixel scales. Instead, the correct scoped phrasing is: *"Micrographs are standardized to $224 \times 224$ pixels via bicubic interpolation, with self-supervised patch tokens capturing local spatial frequency patterns."*
- **L2 Hypersphere Normalization:** Embeddings are explicitly unit-normalized: $\|z\|_2 = 1.0000 \pm 10^{-6}$.
