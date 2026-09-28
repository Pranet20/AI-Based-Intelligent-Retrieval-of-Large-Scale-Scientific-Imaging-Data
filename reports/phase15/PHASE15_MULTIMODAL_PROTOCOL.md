# Phase 15 Multimodal Retrieval & Representation Protocol

**Document Version:** 1.0.0-phase15  
**Date:** 2026-09-27  
**Scope:** Rigorous Evaluation of Visual-Metadata Fusion Architectures  
**Hypothesis Evaluated:** H1 (Multimodal representation improvement vs degradation)

---

## 1. Scientific Objective

This protocol evaluates whether incorporating standardized microscope instrument metadata (accelerating voltage, beam current, magnification, detector mode, working distance) into self-supervised visual representations improves or preserves retrieval accuracy in scientific microscopy repositories.

---

## 2. Compared Architectures

Five distinct architectural configurations are benchmarked under identical splits and evaluation metrics:
1. **B0: Visual-Only Baseline:** Frozen DINOv2 ViT-S/14 mean patch-token embeddings ($d_v = 384$).
2. **B1: Metadata-Only Baseline:** 7 standardized acquisition scalar features projected to unit vector.
3. **B2: Linear Late Fusion:** Linear weighted score interpolation: $S(q, x) = \alpha S_{\text{vis}}(q, x) + (1-\alpha) S_{\text{meta}}(q, x)$ with $\alpha = 0.5$.
4. **B3: Gated MLP Fusion (Phase 13):** Learned non-linear projection with sigmoid gate: $z = \text{LayerNorm}(g \odot h_v + (1-g) \odot h_m)$.
5. **B4: Cross-Attention Multimodal Fusion (Phase 15):** Multi-head cross-attention mechanism where visual patch queries attend to projected metadata key/value tokens, followed by residual projection.

---

## 3. Evaluation Metrics & Falsification Criteria

- **Primary Metrics:** Recall@1 (R@1), Recall@5 (R@5), Recall@10 (R@10), Mean Reciprocal Rank (MRR), Precision@5 (P@5), Precision@10 (P@10).
- **Ablation Axes:** Missing-modality tolerance (metadata dropped at inference), feature weighting sensitivity ($\alpha \in [0.1, 0.9]$).
- **Falsification Threshold for H1:** If no multimodal configuration surpasses or matches Visual-Only B0 ($R@1 \ge 0.9481$), hypothesis H1 is formally falsified, confirming metadata as an empirical confounder.
