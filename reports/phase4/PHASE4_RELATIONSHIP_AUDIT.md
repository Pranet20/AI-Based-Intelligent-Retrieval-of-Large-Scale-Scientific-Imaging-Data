# Phase 4 — Data-Relationship & Metadata Semantic Audit

**Experiment ID:** `phase4_acquisition_aware_representation_001`  
**Phase State:** AUDIT COMPLETE & SCIENTIFIC FEASIBILITY VERIFIED  
**Audited Datasets:** HCCI SEM Micrograph Dataset (774 physical micrographs), Carinthia Defect Dataset (4,591 micrographs)

---

## 1. Executive Summary & Purpose

Before designing or training an acquisition-aware scientific image representation model, this audit investigates the underlying metadata relationships, acquisition parameters, grouping structures, and potential leakage pathways in the frozen Phase 1–3 data foundation.

The primary objective is to resolve:
1. Whether scientifically defensible material-level and acquisition-level relationships exist.
2. Whether positive pairs can be constructed **without fabricating same-physical-ROI relationships**.
3. Whether leakage-safe train/validation/test partitions can be established.
4. Whether the proposed acquisition-aware representation learning experiment is scientifically valid.

---

## 2. Empirical Answers to Core Relationship Questions

### A. What exactly does `specimen_id` represent?
- **Finding:** In HCCI, `specimen_id` (derived from `norm.sample` / raw `Sample`) represents the **macroscopic metallurgical material and heat-treatment condition** of high-chromium cast iron (hypereutectic alloy).
- **Unique Values (3 distinct categories):**
  1. `AsCast` (260 images, 33.6%): As-cast microstructure containing primary and eutectic $M_7C_3$ carbides in an austenitic/martensitic matrix.
  2. `Q980_0h_WC` (258 images, 33.3%): Destabilized at 980 °C with 0 hours holding time, followed by water cooling.
  3. `Q980_9h_AC` (256 images, 33.1%): Destabilized at 980 °C with 9 hours holding time, followed by air cooling.
- **Scientific Semantics:** `specimen_id` identifies a **material-condition category / specimen coupon**, NOT 774 distinct physical samples. Micrographs sharing `specimen_id` share identical alloy composition and thermal history.

### B. What exactly does `acquisition_id` represent?
- **Finding:** `acquisition_id` represents a specific, discrete configuration of SEM imaging parameters:
  $$\text{acquisition\_id} = f"{microscope}\_{detector}\_{voltage\_kv}\text{kV}\_{magnification}\text{x}"$$
- **Unique Values:** Exactly **67 discrete acquisition conditions** exist across the 774 images.
- **Microscope Distribution:**
  - `Helios NanoLab`: 215 images (FEG, 18 acquisition conditions)
  - `Helios G4 PFIB CXe`: 212 images (FEG, 19 acquisition conditions)
  - `Zeiss Gemini`: 212 images (FEG, 18 acquisition conditions)
  - `VEGA3 XMH`: 135 images (Tungsten thermionic gun, 12 acquisition conditions)
- **Detector Distribution:** `SE` (283), `BSE` (277), `InLens` (212), `ABS` (2).
- **Beam Voltage Distribution:** `10.0 kV` (261), `5.0 kV` (259), `20.0 kV` (254).
- **Magnification Levels:** `500x` (104), `600x` (107), `1000x` (107), `2800x` (108), `3250x` (108), `4000x` (72), `5000x` (105), `20000x` (63).

### C. What exactly does `roi_id` represent?
- **Finding:** In `src/datasets/hcci.py`, `roi_id = f"roi_{stem}"`, where `stem` is the numeric image filename (`1` to `774`).
- **Unique Values:** Exactly **774 unique values** across 774 images (100% 1-to-1 bijection with `image_id`).
- **Scientific Integrity Verdict:** `roi_id` **DOES NOT** represent a shared physical sub-micron region-of-interest tracked across imaging sessions. There are **zero co-registration coordinates, stage coordinates, or fiducial markers**. Any assumption of same physical ROI across acquisition conditions is completely unfounded and strictly prohibited.

### D. What acquisition-related metadata exists?
Every HCCI micrograph possesses 100% complete normalized and raw metadata from `Metadata_All_Samples.xlsx`:
- Instrument (`SEM`): 4 distinct instruments.
- Electron source (`Gun`): Field Emission Gun (`FEG`, 639) vs Tungsten filament (`W`, 135).
- Detector (`Detector`): `SE`, `BSE`, `InLens`, `ABS`.
- Accelerating voltage (`Voltage`): 5 kV, 10 kV, 20 kV.
- Magnification (`Magnification`): 500x to 20,000x.
- Chemical Etching (`Etching`): `Nital` (390) vs `Vilella` (384).
- Field of view regime (`Kind`): `Overview` (390) vs `Detail` (384).
- Pixel size in nm: 24 unique values (ranging from 6.74 nm to 269.8 nm).
- Beam current in nA: 28 unique values.
- Scan dwell time in $\mu\text{s}$: 10 values, classified into `high` (390) and `low` (384).
- Chamber pressure in Pa: 289 values.
- Working distance in mm: 139 values (ranging from 4.8 mm to 8.7 mm).

In contrast, **Carinthia contains zero acquisition metadata** (`acquisition_id` is null, `raw_metadata` is empty; it contains only semiconductor defect-class labels).

### E. Which fields can legitimately define an acquisition domain?
1. **Instrument-Level Domain (`SEM`):** 4 major domains (`Helios NanoLab`, `Helios G4 PFIB CXe`, `Zeiss Gemini`, `VEGA3 XMH`). Note that VEGA3 XMH differs fundamentally in electron gun physics (thermionic tungsten emitter vs FEG).
2. **Discrete Acquisition Condition (`acquisition_id`):** 67 discrete combinations of microscope, detector, accelerating voltage, and magnification. Each acquisition condition belongs to exactly one SEM instrument.
3. **Chemical Preparation Domain (`Etching`):** `Nital` vs `Vilella` etching creates distinct surface relief and carbide contrast.

### F. Which fields can legitimately define material/specimen identity?
`specimen_id` (or `sample`): Identifies the 3 metallurgical material states (`AsCast`, `Q980_0h_WC`, `Q980_9h_AC`).
Optionally combined with `Kind` (`Overview` vs `Detail`) yielding 6 distinct material-magnification categories (`group_id = f"sample_{sample_str}_{state_str}"`).

### G. Are there multiple acquisition domains per material/specimen category?
**Yes, comprehensively.**
- `AsCast`: 260 micrographs acquired across 67 acquisition conditions, 4 microscopes.
- `Q980_0h_WC`: 258 micrographs acquired across 66 acquisition conditions, 4 microscopes.
- `Q980_9h_AC`: 256 micrographs acquired across 66 acquisition conditions, 4 microscopes.
66 out of the 67 acquisition conditions contain micrographs of all three material states.

### H. Are there duplicate or near-duplicate relationships across domains?
- **Exact Duplicates:** 0 (all 774 SHA-256 hashes are strictly unique).
- **Near Duplicates:** 0 near-duplicate clusters identified under Phase 2 perceptual hashing and feature deduplication.

### I. Are there enough samples per group to construct statistically meaningful training/validation/test splits?
**Yes.** An instrument-based held-out partition provides:
- **Train (Helios NanoLab + Helios G4 PFIB CXe):** 427 micrographs (~55.2%), 37 acquisition conditions, all 3 materials balanced (141 / 143 / 143).
- **Validation (VEGA3 XMH):** 135 micrographs (~17.4%), 12 acquisition conditions, all 3 materials balanced (48 / 43 / 44), unique thermionic gun.
- **Test (Zeiss Gemini):** 212 micrographs (~27.4%), 18 acquisition conditions, all 3 materials balanced (71 / 72 / 69), unseen microscope optics.

---

## 3. Detailed Cross-Tabulations & Distributions

### Table 1 — Instrument (`SEM`) $\times$ Material (`specimen_id`)
| Instrument | AsCast | Q980_0h_WC | Q980_9h_AC | Total Images | Total Acquisition Conditions | Electron Gun |
|---|---|---|---|---|---|---|
| **Helios G4 PFIB CXe** | 69 | 71 | 72 | 212 | 19 | FEG |
| **Helios NanoLab** | 72 | 72 | 71 | 215 | 18 | FEG |
| **VEGA3 XMH** | 48 | 43 | 44 | 135 | 12 | Tungsten (W) |
| **Zeiss Gemini** | 71 | 72 | 69 | 212 | 18 | FEG |
| **Total** | **260** | **258** | **256** | **774** | **67** | - |

### Table 2 — Detector $\times$ Material (`specimen_id`)
| Detector | AsCast | Q980_0h_WC | Q980_9h_AC | Total Images |
|---|---|---|---|---|
| **SE** (Secondary Electron) | 94 | 93 | 96 | 283 |
| **BSE** (Backscattered Electron) | 93 | 93 | 91 | 277 |
| **InLens** | 71 | 72 | 69 | 212 |
| **ABS** (Angular BSE) | 2 | 0 | 0 | 2 |

### Table 3 — Accelerating Voltage $\times$ Material (`specimen_id`)
| Accelerating Voltage | AsCast | Q980_0h_WC | Q980_9h_AC | Total Images |
|---|---|---|---|---|
| **5.0 kV** | 87 | 87 | 85 | 259 |
| **10.0 kV** | 86 | 88 | 87 | 261 |
| **20.0 kV** | 87 | 83 | 84 | 254 |

### Table 4 — Etching Agent $\times$ Field-of-View Kind
| Etching Agent | Detail | Overview | Total Images |
|---|---|---|---|
| **Nital** | 196 | 194 | 390 |
| **Vilella** | 188 | 196 | 384 |

---

## 4. Empirical Evidence of Acquisition Bias in Phase 2 DINOv2

A preliminary probe and cosine similarity audit of frozen Phase 2 DINOv2 embeddings on HCCI reveals stark acquisition-induced bias:

1. **Within vs Cross Acquisition Cosine Similarity:**
   - Same material, **within same acquisition condition**: mean similarity = **0.7973** ($N = 1,136$ pairs).
   - Same material, **cross acquisition conditions**: mean similarity = **0.5979** ($N = 98,327$ pairs).
   - Cross-acquisition drop: **$\Delta = -0.1994$** (a ~25% relative reduction in representation similarity solely due to detector, voltage, or microscope variation).
   - Different materials, cross acquisition: mean similarity = **0.5078** ($N = 199,688$ pairs).
   - **Cross/Within Similarity Ratio:** **0.7499**.
2. **Instrument Predictability (Linear Probe):**
   - A logistic regression probe trained on frozen Phase 2 DINOv2 embeddings predicts the 4 SEM instruments with **65.64% accuracy** (chance is 25.0%), indicating substantial instrument-specific domain signatures in the raw representation.
3. **Material Predictability:**
   - Linear probe for material category: **99.48% accuracy**.
   - kNN ($k=5$) for material category: **98.84% accuracy**.
4. **Baseline Retrieval Performance on Split Partitions:**
   - **Full HCCI Corpus ($N=774$):** R@1 = 0.9819, R@5 = 1.0000, R@10 = 1.0000, MRR = 0.9894, P@5 = 0.9693.
   - **Train (Helios, $N=427$):** R@1 = 0.9906, R@5 = 1.0000, R@10 = 1.0000, MRR = 0.9943, P@5 = 0.9677.
   - **Validation (VEGA3, $N=135$):** R@1 = 0.9778, R@5 = 1.0000, R@10 = 1.0000, MRR = 0.9889, P@5 = 0.9007.
   - **Test (Zeiss Gemini, $N=212$):** R@1 = **0.9481**, R@5 = 1.0000, R@10 = 1.0000, MRR = **0.9658**, P@5 = **0.8708**.

On the held-out Zeiss Gemini test partition, Recall@1 drops to 0.9481 and Precision@5 drops to 0.8708, providing clear experimental headroom for cross-acquisition adaptation.

---

## 5. Candidate vs Rejected Positive-Pair Formulations

### Candidate Formulation 1 (APPROVED & RECOMMENDED): Material-Level Cross-Acquisition Pairs
- **Positive Pair:** Micrographs $(i, j)$ where:
  $$i.\text{specimen\_id} == j.\text{specimen\_id} \quad \text{AND} \quad i.\text{acquisition\_id} \neq j.\text{acquisition\_id}$$
- **Negative Pair:** Micrographs $(i, k)$ where:
  $$i.\text{specimen\_id} \neq k.\text{specimen\_id}$$
- **Exclusion:** $i.\text{acquisition\_id} == j.\text{acquisition\_id}$ (same acquisition condition of the same material) are masked from the contrastive positive numerator to prevent reinforcing within-acquisition clustering.
- **Scientific Justification:** Directly optimizes material-condition invariance across differing microscope optics, beam voltages, detectors, and magnifications, while preserving microstructural discrimination across alloy states.

### Candidate Formulation 2 (REJECTED): "Same-ROI" Cross-Acquisition Pairs
- **Definition:** Asserting that $(i, j)$ represent the identical microscopic patch of physical material under differing acquisition conditions based on `roi_id` or filename stem.
- **Reason for Rejection:** Scientifically false. `roi_id` is an artificial identifier assigned 1-to-1 to image filenames. Stage coordinates and co-registration records do not exist. Claiming same-ROI correspondence is scientifically invalid.

### Candidate Formulation 3 (REJECTED): Pure Unsupervised Acquisition Invariance
- **Definition:** Pushing all images from different acquisitions together regardless of material condition.
- **Reason for Rejection:** Destroys metallurgical discrimination by collapsing distinct material conditions into a trivial representation.

---

## 6. Audit Conclusion & Feasibility Verdict

**FEASIBILITY VERDICT: SCIENTIFICALLY VALID AND FEASIBLE.**

1. The data foundation strictly supports material-condition identity (`specimen_id`) and discrete acquisition conditions (`acquisition_id`).
2. There is no need or justification for fabricating same-ROI pairs.
3. A clean, leakage-safe train/val/test split by SEM instrument (Helios $\rightarrow$ VEGA3 $\rightarrow$ Zeiss Gemini) completely isolates acquisition conditions, optical systems, and images while maintaining all 3 material classes in every partition.
4. Phase 4 adaptation can proceed using supervised contrastive adaptation over frozen DINOv2 representations with an explicit contrastive objective encouraging cross-acquisition invariance while penalizing cross-material confusion.
