# Phase 5: Metadata Availability & Research-Integrity Audit

**Experiment ID:** `phase5_hybrid_metadata_retrieval_001`  
**Audit Status:** COMPLETE AND VERIFIED  
**Primary Dataset:** HCCI (774 micrographs)  
**Secondary Dataset:** Carinthia (4591 images) — EXCLUDED FROM METADATA FUSION  

---

## 1. Executive Summary & Zero-Leakage Policy

This audit establishes the empirical metadata schema for Phase 5 hybrid retrieval. Under strict research-integrity standards:
1. **Zero Ground-Truth Leakage:** No metadata feature may identify the retrieval target (`specimen_id`), the image file, or the acquisition group.
2. **Training-Only Parameters:** All scalers, imputers, and categorical vocabularies are strictly derived from the training partition.
3. **Physical/Scientific Interpretability:** Only physical microscope parameters and documented preparation variables are admitted.

---

## 2. Comprehensive Field Classification Table

| Field | Type | Unique Values | Missing | Missing % | Classification | Reason |
|---|---|---:|---:|---:|---|---|
| `manifest.specimen_id` | str | 3 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Ground-truth retrieval relevance label; strictly forbidden as a feature. |
| `manifest.roi_id` | str | 774 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Image identifier with unique instance correspondence; prohibited from feature representation. |
| `manifest.acquisition_id` | str | 67 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Compound condition identifier; used strictly for relationship definition and masking. |
| `manifest.image_id` | str | 774 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Image identifier with unique instance correspondence; prohibited from feature representation. |
| `manifest.filename` | str | 774 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Image identifier with unique instance correspondence; prohibited from feature representation. |
| `manifest.sample_id` | str | 3 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Semantic/target identifier; excluded to prevent target leakage. |
| `manifest.group_id` | str | 6 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Semantic/target identifier; excluded to prevent target leakage. |
| `manifest.label` | str | 2 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Semantic/target identifier; excluded to prevent target leakage. |
| `manifest.source_label` | str | 2 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Semantic/target identifier; excluded to prevent target leakage. |
| `manifest.duplicate_group_id` | object | 0 | 774 | 100.0% | **LEAKAGE_PRONE / EXCLUDED** | Deduplication tracking label; excluded from feature representation. |
| `manifest.near_duplicate_group_id` | object | 0 | 774 | 100.0% | **LEAKAGE_PRONE / EXCLUDED** | Deduplication tracking label; excluded from feature representation. |
| `normalized.microscope` | str | 4 | 0 | 0.0% | **CONDITIONALLY_SAFE** | Instrument identifier; disjoint across train/val/test splits (unknown at test time). |
| `normalized.instrument` | str | 4 | 0 | 0.0% | **CONDITIONALLY_SAFE** | Instrument identifier; disjoint across train/val/test splits (unknown at test time). |
| `normalized.detector` | str | 4 | 0 | 0.0% | **SAFE** | Physical electron detector collection mode (Group C). |
| `normalized.accelerating_voltage_kv` | float64 | 3 | 0 | 0.0% | **SAFE** | Primary electron beam parameter (Group B). |
| `normalized.magnification` | float64 | 8 | 0 | 0.0% | **SAFE** | Physical imaging geometry parameter (Group A). |
| `normalized.pixel_size_nm` | float64 | 24 | 0 | 0.0% | **SAFE** | Physical imaging geometry parameter (Group A). |
| `normalized.beam_current_na` | float64 | 28 | 0 | 0.0% | **SAFE** | Primary electron beam parameter (Group B). |
| `normalized.dwell_time_us` | float64 | 10 | 0 | 0.0% | **SAFE** | Primary electron beam parameter (Group B). |
| `normalized.working_distance_mm` | float64 | 139 | 0 | 0.0% | **SAFE** | Specimen chamber physical vacuum/geometry environment (Group D). |
| `normalized.chamber_pressure_pa` | float64 | 289 | 0 | 0.0% | **SAFE** | Specimen chamber physical vacuum/geometry environment (Group D). |
| `normalized.sample` | str | 3 | 0 | 0.0% | **LEAKAGE_PRONE / EXCLUDED** | Equivalent to specimen_id (AsCast, Q980_0h_WC, Q980_9h_AC); prohibited. |
| `normalized.sample_state` | str | 2 | 0 | 0.0% | **CONDITIONALLY_SAFE** | Field-of-view designation (Overview vs Detail); safe but secondary. |
| `normalized.etching_agent` | str | 2 | 0 | 0.0% | **SAFE** | Metallurgical chemical etching agent (Group E safe feature). |
| `normalized.imaging_mode` | str | 1 | 0 | 0.0% | **EXCLUDED** | Constant value ('SEM') across entire dataset; zero variance. |
| `normalized.scale` | str | 24 | 0 | 0.0% | **EXCLUDED** | Textual duplicate of pixel_size_nm. |
| `normalized.acquisition_date_if_available` | object | 0 | 774 | 100.0% | **EXCLUDED** | 100% missing values across all records. |

---

## 3. Approved Scientific Feature Groups

The following scientifically grounded feature groups are formulated from the **SAFE** fields:

- **Group A — Imaging Geometry:**
  - `magnification`: Optical magnification scale (500x to 20,000x, 8 discrete levels).
  - `pixel_size_nm`: Physical resolution per pixel (24 discrete values).

- **Group B — Electron Beam Parameters:**
  - `accelerating_voltage_kv`: High voltage accelerating potential (5.0, 10.0, 20.0 kV).
  - `beam_current_na`: Probe current (range: [0.1 nA, 13.0 nA], 28 unique values).
  - `dwell_time_us`: Electron dwell time per pixel (range: [1.0 µs, 100.0 µs], 10 unique values).

- **Group C — Detector Configuration:**
  - `detector`: Physical detector mechanism (`SE` [Secondary Electron], `BSE` [Backscattered Electron], `InLens`, `ABS`).

- **Group D — Chamber & Environment Parameters:**
  - `chamber_pressure_pa`: Chamber vacuum pressure (289 unique values).
  - `working_distance_mm`: Specimen working distance from pole piece (139 unique values).

- **Group E — Full Safe Scientific Metadata:**
  - Groups A + B + C + D combined with `etching_agent` (`Nital`, `Vilella`).

---

## 4. Carinthia Dataset Metadata Audit

Inspection of `data/manifests/carinthia_manifest.parquet` (4,591 images) confirmed:
- `specimen_id`: 100% null (4,591/4,591).
- `acquisition_id`: 100% null (4,591/4,591).
- `microscope`, `detector`, `voltage`, `magnification`, etc.: 100% null in `metadata_json`.

> [!IMPORTANT]
> **Carinthia Exclusion Statement:**
> Carinthia was excluded from metadata-fusion evaluation because the required scientifically meaningful acquisition metadata was unavailable in the authoritative project data.

## 5. Sample-Preparation Metadata Audit: etching_agent

Inspection of `etching_agent` (`Nital` vs `Vilella`) confirmed it represents physical metallurgical preparation.
A statistical independence test against `specimen_id` demonstrates:
- `AsCast`: 132 Nital, 128 Vilella (50.8% / 49.2%)
- `Q980_0h_WC`: 132 Nital, 126 Vilella (51.2% / 48.8%)
- `Q980_9h_AC`: 126 Nital, 130 Vilella (49.2% / 50.8%)
- Chi-square test: $\chi^2 = 0.2171, p = 0.8971$ (degrees of freedom = 2).
- **Conclusion:** With $p \gg 0.05$, `etching_agent` is statistically independent of specimen condition and cannot act as a direct or near-direct ground-truth proxy.

---

## 6. Instrument Domain Exclusion Rationale

`microscope`/`instrument` (`Helios NanoLab`, `Helios G4 PFIB CXe`, `VEGA3 XMH`, `Zeiss Gemini`) was excluded from the primary feature vector because instrument identity encodes split/domain identity under the instrument-disjoint evaluation protocol. Including it could produce domain-matching behavior rather than scientifically meaningful microstructure retrieval.

---

## 7. Numerical Fields Summary Statistics (HCCI Training Split)

To ensure zero leakage across splits, all numerical preprocessing parameters (mean, std, median) are fitted solely on the training partition (427 micrographs).
