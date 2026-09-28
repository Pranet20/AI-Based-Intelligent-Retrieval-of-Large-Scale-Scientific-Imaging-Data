# Authoritative ML Models & Checkpoint Specification

## 1. Visual Backbone: DINOv2 ViT-S/14
- **Model Architecture**: Vision Transformer Small with patch size 14 (`dinov2_vits14`).
- **Embedding Dimension**: 384 dimensions (L2 normalized: $\|\mathbf{z}\|_2 = 1.0$).
- **Source Repository**: `facebookresearch/dinov2` via official PyTorch Hub.
- **Parameters**: 22,056,576 parameters (strictly frozen).
- **Preprocessing Protocol**:
  - Image size: $224 \times 224$ pixels.
  - Interpolation: Bicubic with antialiasing.
  - Normalization: ImageNet mean `[0.485, 0.456, 0.406]`, std `[0.229, 0.224, 0.225]`.
  - Grayscale policy: Replicate 1 channel across 3 RGB channels (no CLAHE, no pseudo-coloring).

## 2. Acquisition-Aware Adapter (Phase 4)
- **Architecture**: Single linear projection layer ($384 \to 384$) followed by L2 normalization.
- **Objective**: Contrastive acquisition-invariance via Acquisition-Aware Supervised Contrastive Loss ($\tau = 0.07$).
- **Checkpoint Location**: `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt`.
- **Authoritative SHA-256 Hash**:
  `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`
- **Integrity Enforcement**: Verified via SHA-256 at backend application startup in `ModelRegistryService`. If the hash does not match, startup aborts immediately.

## 3. Vector Retrieval: FAISS IndexFlatIP
- **Index Type**: `faiss.IndexFlatIP` (Exact Inner Product on L2-normalized embeddings).
- **Retrieval Precision**: 100% recall relative to exhaustive brute-force search.
- **Persistence**: `platform/storage/indexes/faiss_exact_flatip.index` and `id_map.json`.
