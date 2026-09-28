# Scientific Data Availability Statement

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Compliance Standard:** FAIR Data Principles & Peer-Reviewed Journal Open Science Guidelines  

---

## 1. General Data Availability Policy

This project strictly adheres to ethical research data governance. To protect third-party copyright, terms of deposition, and intellectual property rights, **raw microscopy image files are not uniformly bundled into public software repositories**. Instead, the platform implements a transparent, multi-tiered data availability framework that provides open access to code, derived features, and metadata manifests, while supplying deterministic acquisition pipelines for external raw data.

---

## 2. Multi-Tiered Data & Artifact Classification

### Tier 1: Openly Distributed in Release Package
The following scientific materials are directly included in the open-source release package:
1. **Source Code & Web Platform:** All core algorithms, CLI tools, REST API services, frontend user interface components, and automated test suites under the permissive MIT License.
2. **Normalized Metadata Manifests:** High-throughput columnar Parquet and CSV manifests (`data/manifests/hcci_manifest.parquet`, `data/manifests/carinthia_manifest.parquet`) containing normalized instrument parameters, image dimensions, file hashes, and benchmark split assignments.
3. **Derived Vector Representations:** Pre-computed 384-dimensional L2-normalized DINOv2 visual embeddings (`data/processed/embeddings/*.parquet`) enabling vector indexing and similarity retrieval reproduction without requiring re-execution of deep neural feature extraction.
4. **Trained Adapter Model Weights:** Pinned linear projection adapter checkpoints (`data/processed/phase4/checkpoints/best_checkpoint_seed42.pt`) trained with supervised contrastive loss.
5. **Experimental Configurations & Registries:** All YAML configuration snapshots, experiment manifests, random seed definitions, and evaluation metrics tables.

### Tier 2: Available from Original Deposition Repositories (Publicly Downloadable)
The following third-party datasets were utilized in benchmark evaluations and must be acquired directly from their authoritative institutional repositories:
1. **High-Chromium Cast Iron SEM Dataset (`hcci`):** 774 physical microscopy images deposited on Zenodo under DOI [10.5281/zenodo.21931379](https://doi.org/10.5281/zenodo.21931379). Automated download instructions and extraction scripts are provided in `scripts/data/download_hcci.py`.
2. **Carinthia SEM Defect Dataset (`carinthia`):** 4,591 industrial defect micrographs deposited on Zenodo under DOI [10.5281/zenodo.10715190](https://doi.org/10.5281/zenodo.10715190). Acquisition script provided in `scripts/data/download_carinthia.py`.
3. **SEM Images for Nanoscience (`sem_nanoscience`):** Open-access micrographs published under CC-BY-4.0 in Nature Scientific Data under DOI [10.1038/sdata.2018.172](https://doi.org/10.1038/sdata.2018.172). Variant acquisition script provided in `scripts/data/download_sem_nanoscience.py`.
4. **atomagined HAADF-STEM Benchmark (`atomagined`):** Synthetic atomic-resolution simulation micrographs deposited on the Materials Data Facility under DOI [10.18126/szeq-yde5](https://doi.org/10.18126/szeq-yde5). Acquisition guide provided in `scripts/data/download_atomagined.py`.
5. **cigRockSEM Microstructure Dataset (`cigrocksem`):** Geological porous rock SEM imagery deposited on Zenodo under DOI [10.5281/zenodo.14988631](https://doi.org/10.5281/zenodo.14988631). Acquisition helper provided in `scripts/data/download_cigrocksem.py`.

### Tier 3: Restricted Access Material (Contributor Authorization Required)
1. **MicroAl-Dataset (`microal`):** Contributed multi-modal aluminum micrographs ([https://github.com/neulmc/MicroAl-Dataset](https://github.com/neulmc/MicroAl-Dataset)). Restricted to authorized academic researchers. Direct public redistribution is strictly prohibited. Detailed researcher contact instructions are provided in `scripts/data/download_microal.py`.

---

## 3. Foundation Vision Model Weights
- **Model:** `dinov2_vits14` (Vision Transformer Small, patch size 14, 384-dimensional representation).
- **Source:** Pre-trained weights released by Meta AI under the Apache 2.0 License.
- **Acquisition:** Automatically downloaded via PyTorch Hub (`torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')`) during pipeline initialization, or manually cached in `~/.cache/torch/hub/`.

---

## 4. Integrity and Verification
Every released dataset manifest and derived vector embedding includes SHA-256 cryptographic hashes to verify physical file integrity against original raw archives without compromising legal redistribution boundaries.
