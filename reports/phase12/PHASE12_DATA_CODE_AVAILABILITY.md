# Phase 12 — Formal Data & Code Availability Statement

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Document ID:** `phase12_data_code_availability_001`  
**Date:** September 2026  
**Status:** Certified Submission Deliverable — Data & Code Availability  

---

## 1. Formal Journal-Ready Statement

> **Data & Code Availability Statement:**  
> The complete software framework developed in this investigation—including the visual representation pipelines, contrastive metric learning modules, FAISS indexing benchmarks, deduplication screening cascades, image quality risk estimators, and the full-stack FastAPI/React/PostgreSQL platform—is openly accessible under the permissive MIT Open Source License at the project repository ([REDACTED FOR PEER REVIEW / PUBLIC REPOSITORY URL]).
> 
> All experimental configuration files, training split manifests, precomputed feature embeddings, evaluation metric tables, and the trained contrastive adapter weights (SHA-256 digest: `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`) are openly released as part of the Phase 10 Research Archive under the Creative Commons Attribution 4.0 International license (CC-BY 4.0).
> 
> The primary in-domain scanning electron microscopy benchmark—the High-Chromium Cast Iron (HCCI) metallurgical dataset ($N=774$ physical micrographs across 67 acquisition conditions)—is openly hosted on Zenodo at https://doi.org/10.5281/zenodo.21931379 under CC-BY 4.0. The external semiconductor defect benchmark—the Carinthia SEM dataset ($N=4,591$ micrographs)—is openly hosted on Zenodo at https://doi.org/10.5281/zenodo.10715190 under CC-BY 4.0. Automated acquisition scripts to download and verify raw data payloads directly from Zenodo are bundled within the repository.
> 
> The project maintains a strict manifest-first data governance policy: third-party dataset terms exclusively govern external micrographs, and the project's software license does not claim or convey ownership over third-party imaging archives. Reference datasets utilized for cross-modality cataloging (cigRockSEM, atomagined, sem_nanoscience) are documented via open persistent identifiers, and restricted raw files are quarantined from unauthorized redistribution.

---

## 2. Granular Rights & Asset Classification Matrix

To prevent copyright confusion or overreach, the table below provides an explicit separation of rights across every asset layer:

| Asset Category | Specific Component | Authoritative License | Hosting / Distribution Location | Access & Redistribution Status |
| :--- | :--- | :---: | :--- | :--- |
| **1. Project Source Code** | Platform backend, frontend, CLI tools, ML pipelines | MIT License | Project Git Repository | Fully open, permissive redistribution |
| **2. Dataset Manifests** | Metadata parquet files, split JSONs, hash digests | CC-BY-4.0 | `data/manifests/`, `release/v1.0.0/` | Fully open for research citation |
| **3. Precomputed Embeddings**| 384-d DINOv2 class token arrays (.npy) | CC-BY-4.0 | `artifacts/phase2/`, `release/v1.0.0/` | Fully open research data |
| **4. Experiment Configurations**| YAML parameter files, grid specs, random seeds | MIT License | `configs/` | Fully open |
| **5. Model Checkpoints** | SupCon projection head weights (`phase4_adapter.pt`)| CC-BY-4.0 | `data/processed/phase4/checkpoints/` | Fully open, SHA-256 verified |
| **6. Primary Benchmark Data** | HCCI ($N=774$ physical micrographs) | CC-BY-4.0 | Zenodo (`10.5281/zenodo.21931379`) | Direct download from Zenodo |
| **7. External Benchmark Data** | Carinthia SEM ($N=4,591$ PNG micrographs) | CC-BY-4.0 | Zenodo (`10.5281/zenodo.10715190`) | Direct download from Zenodo |
| **8. Ingestion / Fetch Scripts**| Automated dataset retrieval and hash verifiers | MIT License | `scripts/download_datasets.py` | Bundled in repository |
| **9. Restricted Reference Sets** | `cigrocksem`, `atomagined`, `microal` | Proprietary / Academic | Manifest-only cataloging | **QUARANTINED** (No raw redistribution) |

---

## 3. Persistent Digital Identifiers (DOIs)

- **HCCI Metallurgy SEM Dataset:** `https://doi.org/10.5281/zenodo.21931379`
- **Carinthia Semiconductor SEM Dataset:** `https://doi.org/10.5281/zenodo.10715190`
- **Project Release Archive (Zenodo Reserved):** `https://doi.org/10.5281/zenodo.XXXXXXX` *(Author input required upon final deposit)*
- **Software Repository:** `https://github.com/[ANONYMIZED_ORGANIZATION]/scientific-image-platform` *(Author input required upon unblinding)*
