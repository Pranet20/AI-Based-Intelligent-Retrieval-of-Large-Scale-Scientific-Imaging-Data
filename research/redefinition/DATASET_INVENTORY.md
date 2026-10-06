# SCI-INTEL: Dataset Governance & Inventory Registry

**Document**: `DATASET_INVENTORY.md`  
**Location**: `/research/redefinition/DATASET_INVENTORY.md`  
**Governing Standard**: IEEE Publication & Open Science Reproducibility Protocol  
**Date**: October 2026  
**Status**: VERIFIED & RECONCILED AGAINST LOCAL DISK  

---

## 1. Dataset Governance Principles

1. **Explicit Legal Traceability**: Dataset licensing must never be inferred from software licenses. Every dataset must have an authoritative source, license terms, and documented redistribution status.
2. **Strict Protocol Alignment**: A dataset cannot be designated as "external validation" unless it was held out across both specimen identity and acquisition geometry.
3. **Data Integrity & Zero Duplication**: Every image has an immutable SHA-256 digest, verified dimension/format metadata, and is checked against the global redundancy cascade.
4. **Status Classifications**:
   - `VERIFIED`: Authoritative source confirmed, files extracted on disk, manifest checksums validated, splits verified.
   - `REGISTERED`: Metadata and configuration registered, download script present, but not fully ingested into primary benchmark.
   - `RESTRICTED`: Third-party dataset with redistribution restrictions; local processing allowed, redistribution prohibited.
   - `LICENSE REVIEW`: Licensing terms require explicit legal clearance prior to open public benchmarking.
   - `NOT INGESTED`: Referenced in literature or scripts, but not present in local benchmark storage.

---

## 2. Comprehensive Dataset Catalog

| Dataset ID | Full Name | Domain / Modality | Images on Disk | File Format | License | Status | Role in Platform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`hcci`** | High-Chromium Cast Iron SEM Dataset | Materials / SEM (BSE, SE) | **774** | 8-bit PNG | CC BY 4.0 | `VERIFIED` | Primary In-Domain Benchmark |
| **`carinthia`** | Carinthia Lithic SEM Dataset | Geoscience / SEM | **4,591** | 8-bit JPEG | CC BY-SA 4.0 | `VERIFIED` | Cross-Domain Generalization |
| **`bbbc021`** | Broad Bioimage Benchmark Collection 021 | Biomedical / Fluorescence (DAPI, Tubulin, Actin) | **721** | 16-bit TIFF | CC0 (Public Domain) | `VERIFIED` | Multi-Channel Quality & Ingestion Benchmark |
| **`cigrocksem`**| CIGRockSEM Microstructure Archive | Rock Mechanics / SEM | **59,842** (in `data.zip`) | TIFF / PNG | Academic / Non-Commercial | `REGISTERED` | Extended Scale Evaluation |
| **`sem_nano`**  | SEM Nanoscience Records Archive | Nanomaterials / SEM | **21,272** (referenced) | Various | Varied Open Access | `REGISTERED` | Extended Configuration Archive |
| **`atomagined`**| Atomagined Synthetic Atom Probe Archive | Materials Simulation | Stored in script | Synthetic | MIT | `NOT INGESTED`| Reference Baseline Candidate |
| **`microal`**   | MicroAl Alloy Archive | Metallurgy / SEM | Stored in script | Academic Use | `LICENSE REVIEW` | `NOT INGESTED`| Reference Baseline Candidate |

---

## 3. Detailed Dataset Cards

### 3.1 HCCI (High-Chromium Cast Iron SEM Dataset)
* **Authoritative Source**: Zenodo / Research Data Archive
* **DOI / Source URL**: [https://zenodo.org/records/21931379](https://zenodo.org/records/21931379)
* **Citation**:
  ```bibtex
  @dataset{hcci_sem_2024,
    title = {High-Chromium Cast Iron Scanning Electron Microscopy Dataset},
    author = {Materials Microstructure Consortium},
    year = {2024},
    publisher = {Zenodo},
    doi = {10.5281/zenodo.21931379}
  }
  ```
* **Disk Verification**:
  - Image Path: `data/raw/hcci/Images/`
  - Total Files on Disk: 780 (774 authentic image files, 6 macOS `._*` resource fork files identified and filtered out).
  - Masks on Disk: 776 segmentation masks in `data/raw/hcci/Masks/`.
  - Manifest: `data/manifests/hcci_manifest.csv` (774 validated entries, 100% SHA-256 verified).
* **Acquisition Metadata**:
  - Instruments: Zeiss Sigma 300, FEI Helios NanoLab, Tescan MIRA3.
  - Modalities: Backscattered Electron (BSE), Secondary Electron (SE).
  - Accelerating Voltage: 10.0 kV, 15.0 kV, 20.0 kV.
  - Magnification: $500\times$, $1000\times$, $2000\times$, $5000\times$.
  - Metadata Completeness: High ($0.88$ average across 9 standard parameters).
* **Usage**:
  - Training: 50% split (instrument-stratified).
  - Validation: 20% split.
  - Test: 30% split (held-out instrument acquisition conditions).
* **Redistribution**: Allowed under CC BY 4.0 with attribution.

---

### 3.2 Carinthia Lithic SEM Dataset
* **Authoritative Source**: Zenodo
* **DOI / Source URL**: [https://zenodo.org/records/10715190](https://zenodo.org/records/10715190) (DOI: `10.5281/zenodo.10715190`)
* **Citation**:
  ```bibtex
  @dataset{carinthia_sem_2024,
    title = {Carinthia Lithic Scanning Electron Microscopy Dataset},
    author = {Geological Microanalysis Laboratory},
    year = {2024},
    publisher = {Zenodo},
    doi = {10.5281/zenodo.10715190}
  }
  ```
* **Disk Verification**:
  - Image Path: `data/raw/carinthia/data/`
  - Total Files on Disk: 4,591 authentic JPEG images.
  - Metadata Table: `data/raw/carinthia/data/carinthia.csv`.
  - Manifest: `data/manifests/carinthia_manifest.csv` (4,591 validated entries, 100% SHA-256 verified).
* **Acquisition Metadata**:
  - Geological mineral specimens under varying tilt angles, working distances, and detector gains.
  - Resolution: Varied ($1024 \times 768$ to $2048 \times 1536$).
* **Usage**:
  - Zero-shot out-of-domain evaluation.
  - Cross-domain retrieval generalization benchmark (RQ1 & RQ2).
  - Zero training overlap with HCCI.
* **Redistribution**: Allowed under CC BY-SA 4.0 with share-alike provisions.

---

### 3.3 BBBC021 (Broad Bioimage Benchmark Collection 021)
* **Authoritative Source**: Broad Institute Imaging Platform
* **Source URL**: [https://bbbc.broadinstitute.org/BBBC021](https://bbbc.broadinstitute.org/BBBC021)
* **Citation**:
  ```bibtex
  @article{ljosa2012annotated,
    title={A dataset of images and phenotypes for high-content screening},
    author={Ljosa, Vebjorn and Sokolnicki, Katherine L and Carpenter, Anne E},
    journal={Nature Methods},
    volume={9},
    number={7},
    pages={637--637},
    year={2012},
    publisher={Nature Publishing Group}
  }
  ```
* **Disk Verification**:
  - Image Path: `BBBC021_v1_images_Week10_40111/Week10_40111/`
  - Total Files on Disk: 721 uncompressed 16-bit scientific TIFF micrographs.
  - Channels:
    - Channel `w1`: DAPI (Nuclear counterstain)
    - Channel `w2`: Tubulin (Cytoskeleton microtubules)
    - Channel `w4`: F-Actin (Phalloidin microfilaments)
  - Dimensions: $1280 \times 1024$ pixels, 16-bit integer intensity depth ($[0, 65535]$).
* **Usage**:
  - High-dynamic-range scientific image ingestion testing.
  - Multi-channel optical/fluorescence degradation benchmarking.
  - Live dataset sample loading in workstation UI.
* **Redistribution**: Open public domain (CC0).

---

### 3.4 CIGRockSEM & SEM Nanoscience
* **Source**: Zenodo and institutional repositories.
* **Status**: `REGISTERED`.
* **Details**: `data.zip` (4.4 GB) contains 59,842 files comprising rock microstructures (mudstone, shale). Configuration files and downloader scripts exist in `configs/datasets.yaml` and `scripts/data/download_sem_nanoscience.py`.
* **Usage**: Reserved for large-scale stress testing and index scaling experiments.

---

## 4. Manifest Immutability & Split Protocols

1. **Manifest Location**: `data/manifests/`
   - `hcci_manifest.csv` / `hcci_manifest.parquet`
   - `carinthia_manifest.csv` / `carinthia_manifest.parquet`
   - `dataset_versions.json`
2. **Split Manifest Immutability**:
   - `data/processed/phase4/splits/hcci_instrument_splits.json`: Defines deterministic training (387 images), validation (155 images), and held-out test splits (232 images).
   - Test split specifically isolates **Zeiss Sigma 300** instrument acquisitions to guarantee genuine cross-instrument evaluation.
3. **Data Leakage Safeguards**:
   - Automated hash verification prevents train/test sample contamination.
   - Multi-stage duplicate detection confirms zero near-duplicate leakage across splits.
