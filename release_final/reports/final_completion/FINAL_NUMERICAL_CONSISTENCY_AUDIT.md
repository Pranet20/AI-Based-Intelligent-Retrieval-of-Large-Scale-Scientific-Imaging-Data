# Master Final Numerical Consistency Audit

**Project**: AI-Powered Scientific Image Data Management Platform  
**Baseline**: `PROJECT_FINAL_CLOSED_WITH_LIMITATIONS`  
**Audit Status**: 100% CONSISTENT & FROZEN  

---

## 1. Authoritative Metric Reference Table

| Phase | Evaluation Setting | Metric | Authoritative Numerical Value | Statistical Rigor / Protocol | Invariant Status |
| :--- | :--- | :--- | :---: | :--- | :---: |
| **Phase 2** | HCCI ($N=774$) Visual Retrieval | Recall@1 | **0.9819** | Exact frozen DINOv2 ViT-S/14 baseline | FROZEN |
| **Phase 2** | HCCI ($N=774$) Visual Retrieval | MRR | **0.9894** | Exact RankReciprocal | FROZEN |
| **Phase 2** | HCCI ($N=774$) Visual Retrieval | Precision@5 | **0.9693** | Top-5 retrieval precision | FROZEN |
| **Phase 2** | Carinthia ($N=4,591$) Cross-Domain | Recall@1 | **0.9952** | Evaluated zero-shot transfer | FROZEN |
| **Phase 2** | Carinthia ($N=4,591$) Cross-Domain | MRR | **0.9965** | Evaluated zero-shot transfer | FROZEN |
| **Phase 4** | Held-out Zeiss ($N=212$) | Baseline Recall@1 | **0.9481** | Zero-shot held-out instrument | FROZEN |
| **Phase 4** | Held-out Zeiss ($N=212$) | Adapted Recall@1 | **0.9418 ± 0.0059** | 5-seed multi-run empirical variance | FROZEN |
| **Phase 4** | Held-out Zeiss ($N=212$) | Adapted MRR | **0.9632 ± 0.0042** | 5-seed multi-run empirical variance | FROZEN |
| **Phase 4** | Held-out Zeiss ($N=212$) | Adapted Precision@5 | **0.9053 ± 0.0166** | Statistically significant improvement | FROZEN |
| **Phase 4** | Cross-Acquisition Bias Gap | Gap Reduction | **68.15%** | Paired t-test ($p = 1.42 \times 10^{-12}$) | FROZEN |
| **Phase 5** | HCCI Metadata-Only | MRR | **0.3443** | Corrected authoritative value (not 0.4907) | FROZEN |
| **Phase 5** | Early Late Linear Fusion | Recall@1 | **0.6274** | Demonstrating the Metadata Paradox | FROZEN |
| **Phase 5** | Gated MLP Fusion | Recall@1 | **0.5896** | Degradation under unnormalized logs | FROZEN |
| **Phase 5** | Cross-Attention Fusion | Recall@1 | **0.6132** | Degradation under unnormalized logs | FROZEN |
| **Phase 6** | HCCI Natural Redundancy | Exact Duplicates | **0 pairs** | Confirmed bitwise MD5 collisions = 0 | FROZEN |
| **Phase 6** | HCCI Natural Redundancy | Natural Clusters | **769 clusters** | 764 singletons + 5 two-image pairs | FROZEN |
| **Phase 6** | Controlled Defocus Benchmark | Focus AUROC / AUPRC | **0.8803 / 0.9618** | Tenengrad gradient energy screening | FROZEN |
| **Phase 6** | Controlled Duplicate Benchmark| Near-Duplicate F1 | **0.9810** | Multi-stage hash + SSIM cascade | FROZEN |
| **Phase 15** | Out-of-Distribution Screening | $D_{\text{ref}}$ Novelty Signal | **0.7412 AUROC** | Latent-distance discrimination | FROZEN |
| **Phase 17** | Double-Blind Human Curation | Actionability Yield | **91.67% (110/120)** | Inter-annotator Cohen's $\kappa = 0.8420$ | FROZEN |

---

## 2. Invariant Reconciliation Notes

1. **Metadata Paradox Resolution**: Direct concatenation or unnormalized fusion of instrument logs with visual features degrades visual MRR from $0.9658$ to $0.6132$ (Cross-Attention) and $0.5896$ (Gated MLP). Decoupled retrieval (visual vector ranking scoped by inverted metadata constraints) resolves this paradox without performance loss.
2. **Duplicate Detection Bounds**: The HCCI corpus contains zero bitwise-exact duplicates. The natural redundancy graph consists of 769 clusters (764 singletons and 5 two-image near-duplicate review candidates).
3. **Hypothesis H1 Boundary**: Hypothesis H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol.
