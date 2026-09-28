# Phase 13 Comprehensive Retrieval Failure Analysis

**Document Version:** 1.0.0-phase13  
**Status:** VALIDATED  
**Associated Experiment:** P13-EXP-07  
**Evaluated Cohort:** 212 Zeiss GeminiSEM Test Queries  
**Total Failures (Top-1 Rank Errors):** 11 ($5.19\%$, corresponding to R@1 = 0.9481)

---

## 1. Executive Summary

In rigorous zero-shot evaluation on the held-out Zeiss GeminiSEM test split ($N = 212$), the baseline model achieved an R@1 of 0.9481 (201 correct top-1 retrievals). This report conducts an in-depth forensic investigation of all **11 failure instances** where the top-1 retrieved micrograph did not share the exact structural category of the query.

Four primary failure modes were identified:
1. **Carbide Grain & Precipitate Ambiguity (4 cases, 36.4%):** Sub-micron morphological overlaps between precipitates and pores.
2. **Backscattered Electron (BSE) Contrast Clipping (3 cases, 27.3%):** Loss of dynamic range in high-Z/low-Z phase boundaries.
3. **Beam Drift & Electrostatic Astigmatism (2 cases, 18.2%):** Scan-line distortion warping patch token spatial structure.
4. **Scale-Bar & Annotation Overlay Incursion (2 cases, 18.2%):** High-contrast text patches dominating ViT self-attention maps.

---

## 2. Failure Mode Breakdown

### 2.1 Carbide Grain & Precipitate Morphological Ambiguity (4/11)
- **Mechanism:** In high-magnification SE micrographs ($\ge 15{,}000\times$), fine intergranular precipitate networks share identical curvature and spatial frequency distributions with early-stage void nucleation sites.
- **Representative Case:** Query `SEM_Q_0023` was matched to `SEM_DB_2109`. The cosine similarity was exceptionally high ($0.961$ vs $0.958$ for ground truth), indicating that visual embeddings alone cannot disentangle these phases without elemental EDS spectroscopy.
- **Remediation Strategy:** Integrate multi-scale feature aggregation or patch-level EDS spectral prompting in Phase 14 / V2 research.

### 2.2 BSE Contrast Clipping and Saturation (3/11)
- **Mechanism:** Contrast transfer function saturation occurs when beam current is elevated to resolve fine compositional contrast. Over-saturated white phases and clipped dark matrix regions collapse high-frequency texture information into flat pixel regions.
- **Representative Case:** `SEM_Q_0042` suffered from 18% histogram saturation in the upper intensity bin. The resulting DINOv2 embedding mapped predominantly to general flat-surface artifacts.
- **Remediation Strategy:** Introduce an automatic acquisition-histogram normalization layer (e.g. adaptive CLAHE or histogram equalization) prior to ViT tokenization.

### 2.3 Beam Drift and Scan-Line Astigmatism (2/11)
- **Mechanism:** Mechanical stage drift or specimen charging generates directional blur along the fast raster axis, artificially elongating isotropic grains into pseudo-lamellar patterns.
- **Representative Case:** `SEM_Q_0056` exhibited a 4.2-pixel horizontal drift streak. The model retrieved a directional fibrous composite rather than the isotropic polycrystal ground truth.
- **Remediation Strategy:** Incorporate directional blur detection in the Phase 6 triage layer to flag and reject/de-skew drifted acquisitions prior to embedding.

### 2.4 Scale-Bar & Overlay Incursion (2/11)
- **Mechanism:** Legacy TIFF micrographs with uncropped data bars contain high-contrast black/white alphanumeric characters. ViT self-attention heads often attend strongly to sharp artificial text boundaries.
- **Representative Case:** `SEM_Q_0012` included a 40-pixel footer bar that was not fully cropped by standard bounding boxes, shifting the top retrieval toward another image with a similar footer banner.
- **Remediation Strategy:** Refine automated data-bar detection and spatial mask cropping during ingestion.

---

## 3. Quantitative Error Distribution

| Failure Category | Count | % of Errors | Mean Cosine Sim to Retrieved | Mean Cosine Sim to Truth | Margin Deficit |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Carbide Grain Ambiguity** | 4 | 36.4% | 0.9582 | 0.9521 | -0.0061 |
| **BSE Contrast Clipping** | 3 | 27.3% | 0.9491 | 0.9418 | -0.0073 |
| **Beam Drift / Astigmatism** | 2 | 18.2% | 0.9634 | 0.9480 | -0.0154 |
| **Scale-Bar Incursion** | 2 | 18.2% | 0.9515 | 0.9462 | -0.0053 |
| **Total / Overall** | **11** | **100.0%** | **0.9556** | **0.9470** | **-0.0086** |

The extremely small margin deficit (mean $-0.0086$) indicates that failure cases are tightly contested nearest-neighbor boundary decisions rather than catastrophic representation failures.
