# Scientific Datasets Specification

This document details the six public research datasets registered in the platform for Phase 1 data management, auditing, and subsequent representation experiments.

> **Research Integrity Notice Regarding Legacy Local Data:** The project no longer has access to an earlier local exploratory dataset of approximately 725 images (e.g. BBBC021). No pipeline or code in this platform relies on or depends upon that lost dataset. All experiments and benchmarks are strictly built upon the public, peer-reviewed datasets specified below.

---

## 1. Master Dataset Registry & Acquisition Status

The platform strictly distinguishes between **adapter implementation**, **registration**, **local availability**, and **actual ingestion**:

| Dataset ID | Official Name | Research Role | Modality | Approximate Image Count | Verified License Status | Acquisition & Ingestion Status |
|---|---|---|---|---|---|---|
| `hcci` | High-Chromium Cast Iron SEM Dataset | `robustness_and_metadata` | SEM | 777 metadata records / 774 physical images | `UNKNOWN_VERIFY_SOURCE_TERMS` | **REGISTERED + ADAPTER + LOCALLY AVAILABLE + FULLY INGESTED AVAILABLE FILES** |
| `carinthia` | Carinthia SEM Dataset | `defect_anomaly_evaluation` | SEM | 4,591 | `UNKNOWN_VERIFY_SOURCE_TERMS` | **REGISTERED + ADAPTER + LOCALLY AVAILABLE + FULLY INGESTED** |
| `sem_nanoscience` | Annotated SEM Images for Nanoscience | `general_sem_representation` | SEM | 18,577 (Original) / 1,038 (Hierarchical) / 21,272 (Majority) / 21,169 (100%) | `VERIFIED_OPEN_ACCESS` (CC-BY-4.0) | **REGISTERED + ADAPTER + NOT YET DOWNLOADED** |
| `atomagined` | atomagined | `retrieval_benchmark` | HAADF-STEM (synthetic) | ~16,000 | `REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION` | **REGISTERED + ADAPTER + NOT YET DOWNLOADED** |
| `cigrocksem` | cigRockSEM | `cross_domain_validation` | SEM | ~1,500 | `UNKNOWN_VERIFY_SOURCE_TERMS` | **REGISTERED + ADAPTER + NOT YET DOWNLOADED** |
| `microal` | MicroAl-Dataset | `materials_microscopy_extension` | Optical, SEM, TEM | ~800 | `ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION` | **REGISTERED + ADAPTER + NOT YET DOWNLOADED** |

---

## 2. Detailed Dataset Profiles

### 2.1 HCCI (High-Chromium Cast Iron SEM Dataset)
- **Dataset ID:** `hcci`
- **Source:** [https://zenodo.org/records/21931379](https://zenodo.org/records/21931379)
- **DOI:** `10.5281/zenodo.21931379`
- **License Status:** `UNKNOWN_VERIFY_SOURCE_TERMS` (Zenodo record lacks visible explicit license badge)
- **Modality:** Scanning Electron Microscopy (SEM)
- **Role:** `robustness_and_metadata`
- **Image Count:** 777 planned records in `Metadata_All_Samples.xlsx` / 774 valid physical images in source archive
- **Count Reconciliation:** Samples 10, 20, and 30 are listed in the Excel metadata table but omitted from the author-distributed `Images/` directory in `HCCI Dataset .zip`. See [hcci_count_reconciliation.json](file:///c:/Users/Pranet/Downloads/Mini%20Project/reports/dataset_audit/hcci_count_reconciliation.json) for forensic reconciliation.
- **Intended Scientific Use:** Acquisition robustness evaluation, scientific instrument metadata normalization, metallurgy microscopy representation.
- **Key Characteristics:**
  - Controlled acquisition variations (voltage: 5kV to 30kV, magnification: 250x to 10,000x, detectors: ICE, CBS, ETD, working distance, beam current, dwell time).
  - Accompanied by `Metadata_All_Samples.xlsx` and `Classes.txt` phase mappings.
- **Anti-Leakage Strategy:** Grouping preserved via `group_id` (`sample_<id>_<state>`), `specimen_id`, and `acquisition_id`. Images from identical specimen states must never be randomly split across training and test partitions.

---

### 2.2 Carinthia SEM Dataset
- **Dataset ID:** `carinthia`
- **Source:** [https://zenodo.org/records/10715190](https://zenodo.org/records/10715190)
- **DOI:** `10.5281/zenodo.10715190`
- **License Status:** `UNKNOWN_VERIFY_SOURCE_TERMS` (Zenodo record lacks visible explicit license badge)
- **Modality:** Scanning Electron Microscopy (SEM)
- **Role:** `defect_anomaly_evaluation`
- **Image Count:** 4,591 images
- **Intended Scientific Use:** Defect categorization, anomaly detection benchmarking, and out-of-distribution defect retrieval.
- **Key Characteristics:**
  - Contains six real-world industrial SEM defect classes documented in `data/carinthia.csv`.
  - Class distribution (verified directly from dataset):
    - Class 3: 4,008 images
    - Class 4: 289 images
    - Class 6: 227 images
    - Class 1: 55 images
    - Class 2: 8 images
    - Class 5: 4 images
  - Labels are read dynamically from `carinthia.csv` (semicolon delimited). No labels are fabricated.
- **Limitations:** Lacks instrument acquisition metadata tags (voltage, magnification).

---

### 2.3 SEM Images for Nanoscience & Released Variants
- **Dataset ID:** `sem_nanoscience`
- **Source:** [https://www.nature.com/articles/sdata2018172](https://www.nature.com/articles/sdata2018172)
- **DOI:** `10.1038/sdata.2018.172`
- **Citation:** Aversa, R., Modarres, M.H., Cozzini, S. et al. The first annotated set of scanning electron microscopy images for nanoscience. Sci Data 5, 180172 (2018); Author Correction: Sci Data 6, 190018 (2019). DOI: 10.1038/sdata.2018.172
- **License Status:** `VERIFIED_OPEN_ACCESS` (CC-BY-4.0 explicitly stated in Nature Scientific Data)
- **Modality:** Scanning Electron Microscopy (SEM)
- **Role:** `general_sem_representation`
- **Dataset Family:** `SEM_Nanoscience`
- **Available Variants (Authoritative Counts from 2018 Paper & 2019 Author Correction):**
  1. **Original_SEM_Dataset:** Full set of SEM micrographs with initial crowdsourced annotations (18,577 images).
  2. **Hierarchical_Dataset:** Micrographs structured into multi-level hierarchical taxonomies (1,038 images).
  3. **Majority_Dataset:** Curated subset filtered by majority crowd-annotator consensus agreement (21,272 images, corrected in 2019 Author Correction removing duplicate-image replicates).
  4. **100_Percent_Dataset:** Highly curated gold-standard subset where all independent annotators were in 100% agreement (21,169 images, corrected in 2019 Author Correction removing duplicate-image replicates).
- **Variant Policy:** Do not download all variants unnecessarily. Future experiments in Phase 2+ must explicitly declare and select one variant.
- **Critical Technical Limitation:**
  - Published in JPEG format rather than native instrument TIFF files.
  - Original instrument header metadata tags were stripped during publication.

---

### 2.4 atomagined
- **Dataset ID:** `atomagined`
- **Source:** [https://github.com/MaterialEyes/atomagined](https://github.com/MaterialEyes/atomagined)
- **DOI:** `10.18126/szeq-yde5`
- **License Status:** `REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION` (GitHub repo is MIT; dataset rights on Materials Data Facility require separate confirmation)
- **Modality:** High-Angle Annular Dark-Field Scanning Transmission Electron Microscopy (HAADF-STEM) - Synthetic
- **Role:** `retrieval_benchmark`
- **Image Count:** ~16,000 images
- **Intended Scientific Use:** Fine-grained atomic-resolution similarity retrieval benchmark under simulated beam aberrations, tilt, and noise.
- **Key Structural Requirement:**
  - Preserves native target/choice retrieval pair structure (query images matched against gallery choices with ground-truth crystal structure identifiers).
  - Must not be flattened into generic random train/test splits.
  - Accompanied by multislice simulation attributes in HDF5 format.

---

### 2.5 cigRockSEM
- **Dataset ID:** `cigrocksem`
- **Source:** [https://zenodo.org/records/14988631](https://zenodo.org/records/14988631)
- **DOI:** `10.5281/zenodo.14988631`
- **License Status:** `UNKNOWN_VERIFY_SOURCE_TERMS`
- **Modality:** Scanning Electron Microscopy (SEM)
- **Role:** `cross_domain_validation`
- **Image Count:** ~1,500 images
- **Intended Scientific Use:** Cross-domain generalizability evaluation.
- **Isolation Rule:**
  - Represents geological porous rock microstructure.
  - Kept strictly quarantined from model pretraining or representation adaptation.
  - Tagged explicitly as `split="external_validation"`.

---

### 2.6 MicroAl-Dataset
- **Dataset ID:** `microal`
- **Source:** [https://github.com/neulmc/MicroAl-Dataset](https://github.com/neulmc/MicroAl-Dataset)
- **DOI:** `UNKNOWN`
- **License Status:** `ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION`
- **Modality:** Multi-Modal Microscopy (Optical Microscopy, SEM, TEM)
- **Role:** `materials_microscopy_extension`
- **Image Count:** ~800 images
- **Intended Scientific Use:** Cross-modality representation transfer across aluminum alloy microstructures.
- **Access Notice:**
  - Repository contains diverse subsets with potentially distinct access and copyright restrictions.
  - The adapter audits and records access conditions per subset without redistributing restricted materials.
