# Dataset Redistribution Policy & Legal Compliance Specification

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Policy Status:** MANDATORY COMPLIANCE — NO UNAUTHORIZED REDISTRIBUTION  

---

## 1. Fundamental Legal & Research Principles

1. **Separation of Software and Data Rights:** The Open-Source Software license (MIT License) applied to the platform code, adapters, and search engines **never extends** to third-party research datasets.
2. **No Inferred Rights:** Public availability on platforms such as Zenodo, GitHub, Kaggle, or publisher websites does **not** grant third-party redistribution rights. Explicit license terms must be confirmed.
3. **Quarantine of Proprietary & Ambiguous Material:** Any dataset whose distribution terms are missing, ambiguous, or explicitly restrictive must remain strictly quarantined on local infrastructure and **never** packaged into public git repositories, archive releases, or Docker containers.
4. **Manifest-First Open Science:** When redistribution of raw imagery is prohibited, reproducibility is achieved by distributing cryptographically hashed metadata manifests, feature extraction embeddings, and deterministic automated acquisition scripts.

---

## 2. Dataset Legal Classification Matrix

| Dataset ID | Full Name | Primary Repository | Exact Legal Classification | Distribution Boundary in Release Package |
| :--- | :--- | :--- | :--- | :--- |
| **`hcci`** | High-Chromium Cast Iron SEM | Zenodo (`10.5281/zenodo.21931379`) | `MANIFEST_ONLY` / `DOWNLOAD_FROM_ORIGINAL_SOURCE` | Manifests (`.parquet`/`.csv`) only. Zero raw image bytes included. |
| **`carinthia`** | Carinthia SEM Industrial Defect | Zenodo (`10.5281/zenodo.10715190`) | `MANIFEST_ONLY` / `DOWNLOAD_FROM_ORIGINAL_SOURCE` | Manifest (`.parquet`) only. Zero raw image bytes included. |
| **`sem_nanoscience`** | SEM Images for Nanoscience | Nature Sci Data (`10.1038/sdata.2018.172`) | `REDISTRIBUTABLE` (CC-BY-4.0) | Automated download script provided; raw archive omitted to save bandwidth. |
| **`atomagined`** | atomagined HAADF-STEM | GitHub / MDF (`10.18126/szeq-yde5`) | `DOWNLOAD_FROM_ORIGINAL_SOURCE` / `LICENSE_REQUIRES_REVIEW` | Python acquisition script provided; data files excluded. |
| **`cigrocksem`** | cigRockSEM Microstructure | Zenodo (`10.5281/zenodo.14988631`) | `MANIFEST_ONLY` / `DOWNLOAD_FROM_ORIGINAL_SOURCE` | Acquisition script and manifest schemas provided; raw data excluded. |
| **`microal`** | MicroAl-Dataset | GitHub (`neulmc/MicroAl-Dataset`) | `RESTRICTED` / `LICENSE_REQUIRES_REVIEW` | Manual contributor authorization required; third-party distribution prohibited. |

---

## 3. Detailed Per-Dataset Enforcement Policies

### 3.1 High-Chromium Cast Iron SEM Dataset (`hcci`)
- **Classification:** `MANIFEST_ONLY` / `DOWNLOAD_FROM_ORIGINAL_SOURCE`
- **Source Record:** Zenodo DOI [10.5281/zenodo.21931379](https://doi.org/10.5281/zenodo.21931379)
- **Legal Justification:** The Zenodo deposition record does not display an explicit open-access license badge (such as CC-BY). While freely downloadable from Zenodo for personal research, downstream third-party redistribution is legally unverified.
- **Enforcement:**
  - Raw archive `HCCI Dataset .zip` and unpacked TIFF files in `data/raw/hcci` are **excluded** from `release/`.
  - Authorized researchers must download `HCCI Dataset .zip` directly from Zenodo and place it into `data/raw/hcci`.
  - The project distributes `data/manifests/hcci_manifest.parquet`, which includes normalized instrument metadata, image dimensions, and SHA-256 hashes of the original files.

---

### 3.2 Carinthia SEM Defect Dataset (`carinthia`)
- **Classification:** `MANIFEST_ONLY` / `DOWNLOAD_FROM_ORIGINAL_SOURCE`
- **Source Record:** Zenodo DOI [10.5281/zenodo.10715190](https://doi.org/10.5281/zenodo.10715190)
- **Legal Justification:** Similar to HCCI, Zenodo record 10715190 does not grant explicit downstream re-licensing or redistribution permissions.
- **Enforcement:**
  - Raw archive `10715190.zip` and unpacked PNG files in `data/raw/carinthia` are **strictly excluded** from `release/`.
  - Researchers must download the archive from Zenodo and execute `scripts/data/download_carinthia.py`.
  - `data/manifests/carinthia_manifest.parquet` is released to permit manifest validation and embedding indexing.

---

### 3.3 SEM Images for Nanoscience (`sem_nanoscience`)
- **Classification:** `REDISTRIBUTABLE` (CC-BY-4.0) / `DOWNLOAD_FROM_ORIGINAL_SOURCE`
- **Source Record:** Nature Scientific Data DOI [10.1038/sdata.2018.172](https://doi.org/10.1038/sdata.2018.172)
- **Legal Justification:** The dataset is formally licensed under **Creative Commons Attribution 4.0 International (CC-BY-4.0)**, which legally allows redistribution with appropriate attribution.
- **Operational Decision:** Because the full dataset exceeds 15–20 GB across its variants, the release package distributes a deterministic acquisition script (`scripts/data/download_sem_nanoscience.py`) rather than bundling the raw binaries, ensuring lean archive downloads.

---

### 3.4 atomagined HAADF-STEM Benchmark (`atomagined`)
- **Classification:** `DOWNLOAD_FROM_ORIGINAL_SOURCE` / `LICENSE_REQUIRES_REVIEW`
- **Source Record:** Materials Data Facility DOI [10.18126/szeq-yde5](https://doi.org/10.18126/szeq-yde5)
- **Legal Justification:** The software code on GitHub is under the MIT License, but the simulated multislice HDF5 dataset stored on the Materials Data Facility is governed by separate data repository access policies.
- **Enforcement:** Do not mirror data. Provide `scripts/data/download_atomagined.py` to fetch benchmarks via MDF Globus / HTTP endpoints.

---

### 3.5 cigRockSEM Microstructure Dataset (`cigrocksem`)
- **Classification:** `MANIFEST_ONLY` / `DOWNLOAD_FROM_ORIGINAL_SOURCE`
- **Source Record:** Zenodo DOI [10.5281/zenodo.14988631](https://doi.org/10.5281/zenodo.14988631)
- **Legal Justification:** Unverified third-party distribution rights on Zenodo.
- **Enforcement:** Acquire directly from Zenodo; execute `scripts/data/download_cigrocksem.py`.

---

### 3.6 MicroAl-Dataset (`microal`)
- **Classification:** `RESTRICTED` / `LICENSE_REQUIRES_REVIEW`
- **Source Record:** GitHub repository [https://github.com/neulmc/MicroAl-Dataset](https://github.com/neulmc/MicroAl-Dataset)
- **Legal Justification:** Multi-institutional alloy dataset with explicit contributor-specific academic use constraints. Specific sub-folders require author permission.
- **Enforcement:** Strictly prohibited from automated mass redistribution. Downstream researchers must submit an access request to the repository authors following the manual instructions in `scripts/data/download_microal.py`.

---

## 4. Release Directory Audit Rule

Before generating release archives or publishing repository tags:
1. Verify that `release/` contains **0 raw microscopy image bytes** (`.tif`, `.tiff`, `.png`, `.jpg`).
2. Verify that only metadata manifests, derived embeddings, mathematical indices, and configuration files are included.
3. Confirm that all dataset citations and DOIs are referenced in `DATASET_CITATIONS.md`.
