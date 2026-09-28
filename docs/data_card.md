# DATASET GOVERNANCE & REDISTRIBUTION POLICY

**Project**: AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Status**: PERMANENTLY_FROZEN  
**Phase**: Phase 20 Deliverable  

---

## 1. Governance Principles
Scientific research reproducibility must be balanced against intellectual property, donor repository terms of use, and data privacy regulations. This platform adheres strictly to ethical data stewardship:
1. **Provenance First**: Every dataset ingestion requires SHA-256 cryptographic verification, immutable UUID assignment, and schema validation.
2. **Rights Compliance & Zero Unauthorized Redistribution**: Proprietary, sensitive, or license-restricted raw scientific imagery is NEVER bundled into open public code repositories.
3. **Manifest-Driven Reproducibility**: Where raw binary data cannot be redistributed, the platform provides exact SHA-256 cryptographic manifests, precomputed latent vector embeddings, and synthetic validation subsets.

---

## 2. Dataset Rights & Distribution Matrix

| Dataset Identifier | Full Name / Scope | Sample Count ($N$) | License / Rights Classification | Repository Inclusion Status | Access & Reproducibility Protocol |
|---|---|---|---|---|---|
| **HCCI** | High-Confidence Common Inclusions (SEM) | 774 | Academic Restricted / Core Facility IP | Manifests & Embeddings Only (`data/manifests/hcci_manifest.parquet`) | Precomputed 384-d embeddings provided; raw files referenced via SHA-256 hashes. |
| **Carinthia Defect SEM** | Carinthia Microelectronics Defect Corpus | 4,591 | Academic Research Only (Restricted) | Manifests & Embeddings Only (`data/manifests/carinthia_manifest.parquet`) | Precomputed LOO evaluation embeddings provided; raw image redistribution prohibited. |
| **SEM Nanoscience** | Nanomaterial Synthesis & Characterization | 21,169 | Public Domain / CC BY 4.0 | Fully Open Manifests | External open repository URL and checksum registry provided. |
| **Synthetic EDS** | Simulated X-ray Spectral Signatures | 1,000 | Open / Platform Synthetic (MIT) | Full In-Repo Distribution (`data/synthetic_eds/`) | Synthetic mock spectra for API schema and unit testing; no physical specimens. |
| **Perturbation Suite** | Controlled Corrupted Micrograph Split | 120 | Platform Derived (Academic Use) | Metadata & Metric Manifests | Deterministic synthetic corruptions (Gaussian noise, optical blur) reproducible via script. |

---

## 3. Compliance and Redistribution Safeguards
- **Repository Packaging**: Open-source distributions (`release_v4/`) exclude restricted raw micrographs.
- **Verification of Integrity**: Researchers with legitimate institutional access to the underlying raw corpora can verify bitwise parity against `data/manifests/SHA256SUMS_DATASETS.txt`.
- **Precomputed Artifacts**: Feature vectors, HNSW index files, metadata parquets, and evaluation matrices are distributed under open academic licenses to guarantee 100% downstream reproducibility without violating data rights.
