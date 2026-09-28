# Model Card: DINOv2 ViT-S/14 for Scientific Microscopy Data Management

## Model Details
- **Architecture:** Vision Transformer (DINOv2 ViT-S/14)
- **Model Checkpoint:** `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt`
- **Checkpoint SHA-256:** `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`
- **Embedding Dimension:** 384 float32 dimensions (L2 normalized)
- **Parameters:** 22,056,576 parameters (backbone frozen; 295,680 parameter SupCon projection head)
- **Pretraining Data:** LVD-142M (unsupervised natural image pretraining) + Domain Contrastive Adaptation on metallurgical SEM splits.

## Intended Use
- **Primary Use:** Microstructural similarity search, duplicate screening, relative embedding-space novelty detection, and curation triage for scanning electron microscopy archives.
- **Out-of-Scope Uses:** Direct diagnostic metallurgical failure certification without human metallurgist review; mineral/chemical phase quantification without energy dispersive spectroscopy (EDS).

## Known Failure Modes & Limitations
- **Carbide vs Void Ambiguity:** Sub-micron precipitate curvatures can mimic void nucleation sites in secondary electron images.
- **BSE Contrast Clipping:** Extreme detector gain saturation collapses fine interphase boundaries into uniform grayscale.
- **Directional Beam Drift:** Fast-scan raster drift elongates isotropic grains into directional pseudo-fibrous patterns.
- **Defocus Blur:** Severe focal plane drift reduces top-1 retrieval retention to 48%.
