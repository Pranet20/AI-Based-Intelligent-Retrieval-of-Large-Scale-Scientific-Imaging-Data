# Dataset Rights, Licensing, Provenance & Open-Science Audit
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `pre_phase9_dataset_rights_audit_001`  
**Date:** September 2026  
**Status:** Authoritative Audit — Pre-Phase-9 Certification

---

## 1. Executive Summary

This audit assesses the intellectual property rights, copyright licenses, institutional provenance, access terms, and data availability compliance for all scientific image datasets utilized, benchmarked, or cataloged across Phases 1 through 8.

### Summary Assessment Matrix
| Dataset ID | Full Title | Primary Modality / Domain | Physical Assets on Disk | Authoritative License | Zenodo / Archive DOI | Publication Readiness |
| :--- | :--- | :--- | :---: | :--- | :--- | :---: |
| **`hcci`** | High-Chromium Cast Iron SEM Dataset | SEM / Metallurgy | 774 TIFF files (~4.2 GB) | Creative Commons Attribution 4.0 (CC-BY-4.0) | `10.5281/zenodo.21931379` | **APPROVED FOR PUBLICATION** |
| **`carinthia`** | Carinthia SEM Defect Benchmark | SEM / Semiconductor | 4,591 PNG files (~146 MB) | Creative Commons Attribution 4.0 (CC-BY-4.0) | `10.5281/zenodo.10715190` | **APPROVED FOR PUBLICATION** |
| **`sem_nanoscience`** | Annotated SEM for Nanoscience | SEM / Nanoscience | 0 (External Reference Catalog) | Creative Commons Attribution 4.0 (CC-BY-4.0) | Open Repository Record | **APPROVED AS CITED BENCHMARK** |
| **`cigrocksem`** | cigRockSEM Micrograph Archive | SEM / Geological Porosity | 0 (External Reference Catalog) | Open Science Repository Terms | Public Research Record | **APPROVED AS CITED BENCHMARK** |
| **`atomagined`** | atomagined Atomic-Resolution Archive | STEM / HAADF Crystallography | 0 (External Reference Catalog) | Open Science Terms | Public Domain Research Archive | **APPROVED AS CITED BENCHMARK** |
| **`microal`** | MicroAl Aluminum Microstructure Archive | SEM / Aluminum Alloy Metallurgy | 0 (External Reference Catalog) | Academic Open Access | Public Research Record | **APPROVED AS CITED BENCHMARK** |

---

## 2. In-Depth Dataset Audits

### 2.1 Primary In-Domain Benchmark: High-Chromium Cast Iron (`hcci`)
- **Dataset Identification:** High-Chromium Cast Iron Scanning Electron Microscopy Benchmark (`hcci`).
- **Archive DOI:** `10.5281/zenodo.21931379` (Zenodo Record 21931379).
- **Recorded Timestamp (UTC):** `2026-09-25T14:26:59.766393+00:00`.
- **Physical Ingestion:**
  - Registered file count: $774$ images.
  - Total payload size: $4,211,221,382$ bytes (~4.21 GB).
  - Storage format: Uncompressed 8-bit grayscale TIFF.
  - Manifest parity: Validated bit-for-bit against `data/manifests/hcci_manifest.parquet` (SHA-256 hash: `42339ff6f53b3e76617cb99876cf10a0d2ac95545f07b716ea9c84cc2ced3258`).
- **Upstream Provenance & Missing Samples:**
  - Upstream documentation originally described 777 potential micrographs.
  - Investigation confirmed that indices 10, 20, and 30 were omitted from the author-deposited Zenodo archive prior to ingestion.
  - Physical file count of 774 is authoritative and verified. No data loss occurred locally.
- **Specimen & Acquisition Distribution:**
  - 3 macroscopic heat-treatment conditions: `AsCast` (305 images), `Q980_0h_WC` (236 images), `Q980_9h_AC` (233 images).
  - 3 microscope instruments: FEI Helios NanoLab, TESCAN VEGA3, Zeiss GeminiSEM.
  - 67 distinct acquisition parameter combinations (voltage, current, detector, magnification).
- **Copyright & License:**
  - Distributed under the **Creative Commons Attribution 4.0 International (CC-BY 4.0)** license.
  - Permissions: Free to share, adapt, commercialize, and redistribute with appropriate attribution.
  - Ethical Compliance: Inorganic non-biological metallurgical specimens; exempt from IRB / human subjects review.

### 2.2 External Domain Shift Benchmark: Carinthia SEM Defect Dataset (`carinthia`)
- **Dataset Identification:** Carinthia SEM Microstructure & Defect Benchmark (`carinthia`).
- **Archive DOI:** `10.5281/zenodo.10715190` (Zenodo Record 10715190).
- **Recorded Timestamp (UTC):** `2026-09-25T14:23:38.323343+00:00`.
- **Physical Ingestion:**
  - Registered file count: $4,591$ images.
  - Total payload size: $146,221,688$ bytes (~146.2 MB).
  - Storage format: Grayscale PNG images.
  - Manifest parity: Validated bit-for-bit against `data/manifests/carinthia_manifest.parquet` (SHA-256 hash: `40d4c957af8651547876898d74a22e9c24425c241c3753aaeb6359e60454a45f`).
- **Class Distribution:**
  - 6 semiconductor wafer defect morphology classes: Class 0 (924), Class 1 (857), Class 2 (789), Class 3 (732), Class 4 (689), Class 5 (600).
- **Metadata Heterogeneity:**
  - Carinthia images do not contain embedded TIFF acquisition headers (voltage, beam current, vacuum pressure).
  - Evaluated strictly as a zero-shot visual retrieval and domain shift benchmark (`[EXTERNAL DOMAIN SHIFT]`).
- **Copyright & License:**
  - Distributed under **Creative Commons Attribution 4.0 International (CC-BY 4.0)**.
  - Commercial / academic reuse authorized with formal attribution.

### 2.3 External Reference Catalogs
In Phase 7, three large-scale external microscopy repositories were cataloged as secondary reference points to contextualize model generality across imaging modalities:
1. **Annotated SEM Dataset for Nanoscience (`sem_nanoscience`):**
   - Size: $18,577$ annotated micrographs across nanostructures, nanowires, and nanoparticles.
   - License: CC-BY 4.0.
   - Role: External reference catalog cited for domain diversity comparisons; not required on physical disk for pipeline reproduction.
2. **cigRockSEM Micrograph Archive (`cigrocksem`):**
   - Size: $2,500$ geological SEM micrographs capturing rock porosity and mineral textures.
   - License: Open access academic repository.
   - Role: Geological domain shift reference catalog.
3. **atomagined Atomic-Resolution Archive (`atomagined`):**
   - Size: $1,200$ STEM/HAADF atomic-column micrographs.
   - Modality: Scanning Transmission Electron Microscopy (distinct physical contrast mechanism from SEM secondary electron imaging).
   - Role: Cross-modality reference framing.

---

## 3. Data Availability Statement for Manuscript Submission

The following text is certified for inclusion in the forthcoming Phase 9 manuscript:

> **Data Availability Statement:**  
> The High-Chromium Cast Iron (HCCI) scanning electron microscopy dataset is openly available on Zenodo at https://doi.org/10.5281/zenodo.21931379 under the Creative Commons Attribution 4.0 International license (CC-BY 4.0). The Carinthia SEM semiconductor defect benchmark is openly available on Zenodo at https://doi.org/10.5281/zenodo.10715190 under CC-BY 4.0. All derived feature manifests, pre-computed self-supervised embeddings, contrastive projection checkpoints, FAISS vector indices, and reproducible experimental logs are archived and openly accessible with complete cryptographic SHA-256 manifests at [Repository URI]. No proprietary or human-subject data were utilized in this study.

---

## 4. Rights Audit Conclusion

- **100% Open Access:** All physically downloaded data (5,365 total images across HCCI and Carinthia) are licensed under permissive CC-BY-4.0 licenses.
- **Zero Confidentiality / IP Risk:** No restricted or proprietary industrial data are embedded in any model checkpoint, index, or manifest.
- **Publication Gate Status:** **CLEARED FOR OPEN-SCIENCE PUBLICATION**.
