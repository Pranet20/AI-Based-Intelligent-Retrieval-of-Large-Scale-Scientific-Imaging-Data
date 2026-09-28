# Phase 1 Reproducibility Freeze Report

**Date of Freeze:** September 25, 2026  
**Platform Version:** 0.1.0  
**Phase State:** PHASE 1 FROZEN (Ready for Phase 2 Entry)  
**Research Topic:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Quality Assessment, Deduplication and Anomaly Detection

---

## 1. Exact Dataset Sources & Identifiers

| Dataset ID | Full Scientific Name | Authoritative Source URL | Official DOI | Role in Platform |
|---|---|---|---|---|
| `hcci` | High-Chromium Cast Iron SEM Dataset | https://zenodo.org/records/21931379 | `10.5281/zenodo.21931379` | `robustness_and_metadata` |
| `carinthia` | Carinthia SEM Dataset | https://zenodo.org/records/10715190 | `10.5281/zenodo.10715190` | `defect_anomaly_evaluation` |
| `sem_nanoscience` | Annotated SEM Images for Nanoscience | https://www.nature.com/articles/sdata2018172 | `10.1038/sdata.2018.172` | `general_sem_representation` |
| `atomagined` | atomagined HAADF-STEM Benchmark | https://github.com/MaterialEyes/atomagined | `10.18126/szeq-yde5` | `retrieval_benchmark` |
| `cigrocksem` | cigRockSEM Geological Microstructure | https://zenodo.org/records/14988631 | `10.5281/zenodo.14988631` | `cross_domain_validation` |
| `microal` | MicroAl-Dataset Multi-Modal Repository | https://github.com/neulmc/MicroAl-Dataset | `UNKNOWN` | `materials_microscopy_extension` |

---

## 2. Ingestion & File Count Reconciliation

| Dataset ID | Source Version | Local Raw Image Files Discovered | Parquet / CSV Manifest Records | Source Archive Checksum (SHA-256) | Manifest Checksum (SHA-256) |
|---|---|---|---|---|---|
| `hcci` | 1.0.0 | 774 valid PNG micrographs | 774 records (3 omitted in source: 10, 20, 30; status: FULLY INGESTED AVAILABLE FILES) | `31b0f81f8ec9060c93b0d71bf589a8d9ccd7bc6dab2e5dbcb9d702a7a764f72f` | `db01eb4dcf8a61adf9ecf7c00fba709af8693a14be31666c58047336575f21bb` |
| `carinthia` | 1.0.0 | 4,591 JPG micrographs | 4,591 records | `c23c4bb8e6360b386eabdae1d526718f358dd8b5e1446d95bc338ce9f7f3ffba` | `cd555945616ef386a03410e676dea5bfa0f7f3bd3f155359fcb963b968d6d4a7` |
| `sem_nanoscience` | 1.0.0 | 0 (Not yet downloaded; 18,577 Original / 1,038 Hierarchical / 21,272 Majority / 21,169 100% per 2019 Correction) | 0 (Manifest pending download) | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| `atomagined` | 1.0.0 | 0 (Not yet downloaded; ~16,000 synthetic pairs) | 0 (Manifest pending download) | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| `cigrocksem` | 1.0.0 | 0 (Not yet downloaded; ~1,500 micrographs) | 0 (Manifest pending download) | `NOT_AVAILABLE` | `NOT_AVAILABLE` |
| `microal` | 1.0.0 | 0 (Not yet downloaded; ~800 micrographs) | 0 (Manifest pending download) | `NOT_AVAILABLE` | `NOT_AVAILABLE` |

---

## 3. License Verification Status & Access Rights

| Dataset ID | License Status | Repository License | Dataset License | Commercial Use | Redistribution Allowed |
|---|---|---|---|---|---|
| `hcci` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN` | `UNKNOWN` |
| `carinthia` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN` | `UNKNOWN` |
| `sem_nanoscience` | `VERIFIED_OPEN_ACCESS` | `CC-BY-4.0` | `CC-BY-4.0` | `YES_WITH_ATTRIBUTION` | `YES_WITH_ATTRIBUTION` |
| `atomagined` | `REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION` | `MIT` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `SOFTWARE_PERMITTED_DATA_UNKNOWN` | `UNKNOWN` |
| `cigrocksem` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN` | `UNKNOWN` |
| `microal` | `ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION` | `Academic Use / Restricted` | `SUBSET_DEPENDENT` | `PROHIBITED_OR_RESTRICTED` | `RESTRICTED` |

---

## 4. Dataset Acquisition & Extraction Dates

- **`hcci`**: Extracted locally on `2026-09-25T18:43:49+05:30` from `HCCI Dataset .zip`.
- **`carinthia`**: Extracted locally on `2026-09-25T18:43:27+05:30` from `10715190.zip`.
- **`sem_nanoscience`, `atomagined`, `cigrocksem`, `microal`**: Adapters implemented; scheduled for acquisition on demand during benchmark execution.

---

## 5. Software & Runtime Provenance

- **Standardized Research Runtime (Verified):** `Python 3.11.9 (tags/v3.11.9:de54cf5, Apr 2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]`
- **Virtual Environment:** `.venv311` (`requires-python = ">=3.11, <3.12"`)
- **Git Commit:** `NOT_A_GIT_REPO` (standalone research workspace directory)
- **Key Scientific Dependency Versions (Python 3.11.9):**
  - `numpy`: 2.4.6
  - `pandas`: 3.0.6
  - `pillow`: 12.3.0
  - `tifffile`: 2026.3.3
  - `imagehash`: 4.3.2
  - `pyarrow`: 25.0.1
  - `scipy`: 1.17.1
  - `scikit-learn`: 1.9.1
  - `h5py`: 3.16.0
  - `matplotlib`: 3.11.2
  - `click`: 8.5.0
  - `pydantic`: 2.13.5
  - `pyyaml`: 6.0.3
  - `openpyxl`: 3.1.5
  - `requests`: 2.34.2
  - `tqdm`: 4.70.1
  - `pytest`: 9.1.1
  - `ruff`: 0.16.9

---

## 6. Verification & Test Suite Results

- **Automated Unit Tests:** 34 passing tests.
- **Execution Command:** `.\.venv311\Scripts\pytest.exe tests/ -v`
- **Runtime Environment:** Python 3.11.9 on Windows AMD64
- **Result:** `34 passed in 4.19s (100% PASSING)`
- **Key Invariants Verified:**
  1. Original SEM dataset count == 18,577
  2. Hierarchical dataset count == 1,038
  3. Majority dataset count == 21,272
  4. 100% dataset count == 21,169
  5. HCCI available physical image count == 774
  6. HCCI official metadata count == 777
  7. HCCI missing records == ["10", "20", "30"]
  8. Python runtime is 3.11.x (`sys.version_info.major == 3 and sys.version_info.minor == 11`)
  9. HCCI ingestion status does not imply 777 physical images (`FULLY_INGESTED_AVAILABLE_FILES`)

---

## 7. Known Scientific & Technical Limitations

1. **HCCI Missing Image Binaries:** 3 sample rows (IDs 10, 20, 30) documented in `Metadata_All_Samples.xlsx` were not packaged in `HCCI Dataset .zip` by the authors. The manifest faithfully represents 774 actual images without synthetic filler.
2. **Carinthia Instrument Tags:** Lacks accelerating voltage and magnification metadata; defect class labels are preserved without fabrication.
3. **SEM Nanoscience Image Compression:** Published in JPEG format rather than raw instrument TIFF; original EXIF/instrument tags were stripped.
4. **atomagined Modality:** Synthetic multislice HAADF-STEM simulation, not physical beam acquisition.

---

## 8. Unresolved Issues

- **Upstream License Confirmation:** Direct clarification from the depositors of Zenodo records 21931379 (HCCI) and 10715190 (Carinthia) regarding explicit CC-BY-4.0 badge confirmation is pending. Current operational status is set to `UNKNOWN_VERIFY_SOURCE_TERMS`.
- **Target Python Environment:** RESOLVED. Python 3.11.9 virtual environment (`.venv311`) is instantiated, validated, and all 34 Phase 1 unit tests pass under it. Ready for PyTorch/CUDA/DINOv2 Phase 2 installation.
