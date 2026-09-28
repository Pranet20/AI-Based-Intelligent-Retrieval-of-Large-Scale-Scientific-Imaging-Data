# 6. Discussion (Final V2 Manuscript Draft)

## 6.1 Representation Architecture Trade-offs in Scientific Imaging

Our visual baseline comparison demonstrates that self-supervised Vision Transformers and supervised convolutional networks offer complementary performance characteristics:
- **Top-1 Precision vs Global Search Space:** Pretrained DINOv2 representations yield higher top-1 exact retrieval accuracy (+2.36%) and higher MRR than ResNet-50. This performance advantage is consistent with the patch-based self-attention mechanism, which captures fine-grained spatial gradient variations without relying on ImageNet object category biases.
- **Broader Cluster Reach:** Conversely, ResNet-50 achieved 100% recall at ranks 5 and 10, demonstrating strong macroscopic feature grouping. For production retrieval architectures, a two-stage hybrid pipeline—using ResNet-50 or coarse ViT features for broad candidate generation followed by SupCon DINOv2 re-ranking—represents a promising engineering direction.

---

## 6.2 The Negative Multimodal Result: Metadata as Confounders

The failure of linear, non-linear gated, and cross-attention multimodal architectures to match visual-only performance establishes a critical scientific insight for scientific data curation:
- **Instrument Metadata vs Microstructure:** Microscope operating conditions (accelerating voltage, aperture, working distance) reflect operator choices and instrument setup rather than specimen physics. Multiple dissimilar phases are routinely characterized under identical parameters.
- **Confounder Dynamics:** Forcing joint vector representations to incorporate metadata creates artificial clusters where dissimilar materials imaged under identical conditions are projected into mutual proximity.
- **Architectural Principle:** Instrument metadata is most effectively deployed for deterministic SQL filtering and provenance tracking, while dense representation spaces should remain purely image-derived.

---

## 6.3 Uncertainty Quantification and Human-in-the-Loop Triage

- **Overcoming Score Compression:** While dense self-supervised representations suffer from score compression in pairwise margin space ($\Delta S$ AUROC $\approx 0.515$), non-local latent density estimation ($D_{\text{ref}}$ AUROC $= 0.7412$) provides a reliable metric to identify retrieval ambiguity.
- **Workflow Efficiency:** AI queue prioritization allows expert curators to review the most critical defect cases in half the time, eliminating false-alarm fatigue without sacrificing inter-rater consensus ($\kappa > 0.84$).
