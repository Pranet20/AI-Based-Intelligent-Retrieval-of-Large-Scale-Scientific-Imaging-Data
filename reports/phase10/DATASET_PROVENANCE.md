# Comprehensive Dataset Provenance & Registry Package

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Audit Status:** FULLY VERIFIED & RESEARCH-INTEGRITY CONSTRAINED  

---

## 1. Master Dataset Summary Table

| Dataset ID | Full Dataset Name | Modality | Primary Research Role | Authoritative Image Count | Verified License | Acquisition & Ingestion Status | Included in Release? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`hcci`** | High-Chromium Cast Iron SEM Dataset | SEM | Robustness & Metadata Benchmarking | 774 physical images (777 planned records) | `UNKNOWN_VERIFY_SOURCE_TERMS` | `REGISTERED + ADAPTER + LOCALLY INGESTED` | **Manifest Only** (`.parquet`/`.csv`) |
| **`carinthia`** | Carinthia SEM Industrial Defect Dataset | SEM | Defect Categorization & Anomaly Detection | 4,591 physical images | `UNKNOWN_VERIFY_SOURCE_TERMS` | `REGISTERED + ADAPTER + LOCALLY INGESTED` | **Manifest Only** (`.parquet`) |
| **`sem_nanoscience`** | Annotated SEM Images for Nanoscience | SEM | Large-Scale SEM Representation | 18,577 (Orig) / 21,169 (100% Consensus) | `CC-BY-4.0` (Verified Open Access) | `REGISTERED + ADAPTER + NOT YET DOWNLOADED` | **Adapter & Script Only** |
| **`atomagined`** | atomagined HAADF-STEM Benchmark | HAADF-STEM (Synthetic) | Atomic Resolution Similarity Retrieval | ~16,000 synthetic micrographs | `REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION` | `REGISTERED + ADAPTER + NOT YET DOWNLOADED` | **Adapter & Script Only** |
| **`cigrocksem`** | cigRockSEM Microstructure Dataset | SEM | Cross-Domain Geological Validation | ~1,500 physical images | `UNKNOWN_VERIFY_SOURCE_TERMS` | `REGISTERED + ADAPTER + NOT YET DOWNLOADED` | **Adapter & Script Only** |
| **`microal`** | MicroAl Multi-Modal Aluminum Dataset | Optical, SEM, TEM | Cross-Modal Material Transfer | ~800 multi-modal micrographs | `ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION` | `REGISTERED + ADAPTER + NOT YET DOWNLOADED` | **Adapter & Guide Only** |

---

## 2. Detailed Dataset Provenance Profiles

### 2.1 High-Chromium Cast Iron SEM Dataset (`hcci`)
- **Official Title:** High-Chromium Cast Iron Scanning Electron Microscopy Dataset
- **Repository / Source:** Zenodo
- **Permanent DOI:** `10.5281/zenodo.21931379`
- **Direct Record URL:** [https://zenodo.org/records/21931379](https://zenodo.org/records/21931379)
- **Archive File Name:** `HCCI Dataset .zip` (MD5 / SHA-256 verified)
- **Local Identifier:** `hcci`
- **Physical Image Count:** 774 valid TIFF images on disk.
- **Metadata Count:** 777 entries in `Metadata_All_Samples.xlsx`.
- **Forensic Count Reconciliation:** Samples 10, 20, and 30 are defined in the author metadata spreadsheet but omitted from the distributed `Images/` subdirectory. Verified and logged in `reports/dataset_audit/hcci_count_reconciliation.json`.
- **Instrument Acquisition Parameters:** Accelerating voltage (5kV–30kV), magnification (250x–10,000x), detectors (CBS, ICE, ETD), working distance, beam current.
- **License Terms:** `UNKNOWN_VERIFY_SOURCE_TERMS` (Zenodo deposition record lacks an explicit machine-readable license badge).
- **Commercial Restrictions:** Unknown; presumed non-commercial research use only pending depositor clarification.
- **Redistribution Policy:** `MANIFEST_ONLY`. Raw microscopy files are not bundled in open-source releases. Researchers must acquire the raw archive directly from Zenodo.
- **Citation Requirement:** Deposition record at Zenodo (DOI: 10.5281/zenodo.21931379).

---

### 2.2 Carinthia SEM Industrial Defect Dataset (`carinthia`)
- **Official Title:** Carinthia Scanning Electron Microscopy Defect Dataset
- **Repository / Source:** Zenodo
- **Permanent DOI:** `10.5281/zenodo.10715190`
- **Direct Record URL:** [https://zenodo.org/records/10715190](https://zenodo.org/records/10715190)
- **Archive File Name:** `10715190.zip` (MD5 / SHA-256 verified)
- **Local Identifier:** `carinthia`
- **Physical Image Count:** 4,591 valid PNG images.
- **Defect Taxonomy & Distribution:** Semicolon-delimited `carinthia.csv`:
  - Class 3 (Surface Imperfections): 4,008 images
  - Class 4 (Particle Contamination): 289 images
  - Class 6 (Boundary Discontinuities): 227 images
  - Class 1 (Micro-Cracks): 55 images
  - Class 2 (Void Defects): 8 images
  - Class 5 (Severe Delamination): 4 images
- **License Terms:** `UNKNOWN_VERIFY_SOURCE_TERMS` (Zenodo deposition record lacks visible explicit license badge).
- **Commercial Restrictions:** Unknown.
- **Redistribution Policy:** `MANIFEST_ONLY`. Raw image files must be obtained directly from Zenodo record 10715190.
- **Citation Requirement:** Deposition record at Zenodo (DOI: 10.5281/zenodo.10715190).

---

### 2.3 Annotated SEM Images for Nanoscience (`sem_nanoscience`)
- **Official Title:** The first annotated set of scanning electron microscopy images for nanoscience
- **Publisher / Journal:** Nature Scientific Data (Springer Nature)
- **Permanent DOI:** `10.1038/sdata.2018.172` (Author Correction: `10.1038/sdata.2019.18`)
- **Direct Article URL:** [https://www.nature.com/articles/sdata2018172](https://www.nature.com/articles/sdata2018172)
- **Local Identifier:** `sem_nanoscience`
- **Available Variants:**
  1. `Original_SEM_Dataset`: 18,577 micrographs
  2. `Hierarchical_Dataset`: 1,038 micrographs
  3. `Majority_Dataset`: 21,272 micrographs (consensus filtered)
  4. `100_Percent_Dataset`: 21,169 micrographs (gold-standard 100% agreement)
- **License Terms:** `CC-BY-4.0` (Creative Commons Attribution 4.0 International, explicitly granted by Nature Scientific Data).
- **Commercial Restrictions:** Permitted with proper academic attribution.
- **Redistribution Policy:** `REDISTRIBUTABLE`, but distributed as `DOWNLOAD_FROM_ORIGINAL_SOURCE` via script `scripts/data/download_sem_nanoscience.py` to conserve release bandwidth.
- **Citation Requirement:** Aversa, R., Modarres, M.H., Cozzini, S. et al. Sci Data 5, 180172 (2018).

---

### 2.4 atomagined HAADF-STEM Benchmark (`atomagined`)
- **Official Title:** atomagined: High-Throughput Synthetic HAADF-STEM Image Simulation Benchmark
- **Repository / Source:** GitHub / Materials Data Facility (MDF)
- **Permanent DOI:** `10.18126/szeq-yde5`
- **Code Repository:** [https://github.com/MaterialEyes/atomagined](https://github.com/MaterialEyes/atomagined)
- **Local Identifier:** `atomagined`
- **Micrograph Count:** ~16,000 synthetic micrographs with paired query-choice structure.
- **License Terms:** `REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION` (GitHub repo licensed under MIT; MDF dataset access rights require separate confirmation).
- **Commercial Restrictions:** Code is MIT; data commercial terms unverified.
- **Redistribution Policy:** `DOWNLOAD_FROM_ORIGINAL_SOURCE`. Automated acquisition script provided in `scripts/data/download_atomagined.py`.

---

### 2.5 cigRockSEM Microstructure Dataset (`cigrocksem`)
- **Official Title:** cigRockSEM: Micro-CT and SEM Imaging of Porous Geological Rock Formations
- **Repository / Source:** Zenodo
- **Permanent DOI:** `10.5281/zenodo.14988631`
- **Direct Record URL:** [https://zenodo.org/records/14988631](https://zenodo.org/records/14988631)
- **Local Identifier:** `cigrocksem`
- **Image Count:** ~1,500 SEM micrographs.
- **Research Role:** Quarantined out-of-domain geological evaluation (`split="external_validation"`).
- **License Terms:** `UNKNOWN_VERIFY_SOURCE_TERMS`.
- **Redistribution Policy:** `DOWNLOAD_FROM_ORIGINAL_SOURCE` via `scripts/data/download_cigrocksem.py`.

---

### 2.6 MicroAl Multi-Modal Aluminum Dataset (`microal`)
- **Official Title:** MicroAl: Multi-Modal Microscopy Dataset for Aluminum Alloys
- **Repository / Source:** GitHub
- **Repository URL:** [https://github.com/neulmc/MicroAl-Dataset](https://github.com/neulmc/MicroAl-Dataset)
- **Local Identifier:** `microal`
- **Image Count:** ~800 images (Optical Microscopy, SEM, TEM).
- **License Terms:** `ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION`.
- **Redistribution Policy:** `RESTRICTED`. Third-party distribution is strictly prohibited. Users must follow contributor access instructions in `scripts/data/download_microal.py`.
