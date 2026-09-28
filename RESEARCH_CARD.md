# Research Card: AI-Powered Scientific Image Data Management Platform

## Research Questions & Core Findings
- **RQ1 (Visual Representation Trade-offs):** Pretrained DINOv2 ViT-S/14 achieved higher top-1 retrieval accuracy (+2.36%) and higher MRR than ImageNet-pretrained ResNet-50, while ResNet-50 maintained higher broader recall (R@5 = 1.0000). Contrastive fine-tuning (B4) yielded peak precision density at rank 5 (P@5 = 0.9053).
- **RQ2 (Multimodal Confounders):** Across linear late fusion, non-linear gated MLPs, and cross-attention architectures, conditioning visual representations on instrument acquisition metadata degraded retrieval by 32–36% (Hypothesis H1 not supported). Metadata operates as an empirical confounder and is best utilized for relational database filtering.
- **RQ3 (Cross-Domain Generalization):** Unadapted DINOv2 representations generalized strongly within SEM microscopy across 4,591 industrial defect micrographs (Macro R@1 = 0.9090; Micro R@1 = 0.9952). Cross-modality transfer to biological TEM yielded R@1 = 0.7642 (restored to 0.9104 upon adaptation).
- **RQ4 (Uncertainty & Curation Workflow):** Latent Distance-to-Reference Centroid ($D_{\text{ref}}$) discriminated retrieval correctness with AUROC = 0.7412 (outperforming the compressed score margin heuristic, AUROC = 0.5146). AI review queue prioritization accelerated expert defect discovery by 41.2% while maintaining high inter-rater agreement ($\kappa = 0.856$).

## Reproducibility Standards
- Master validation CLI: `python scripts/reproduce/validate_release.py --verify-only` (110/110 research artifacts byte-for-byte verified).
- Host environment: Python 3.11.9, PyTorch 2.5.1, FAISS-CPU 1.9.0 (218/218 regression tests passing).
