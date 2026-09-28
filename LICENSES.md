# Dataset Licenses & Access Rights Specification

This document details the licensing, terms of use, and redistribution restrictions applicable to each dataset enrolled in the platform.

> **Research Integrity Rule:** Never claim a verified license unless it has been explicitly confirmed from the source repository or publisher's metadata. Where licensing terms are unverified or ambiguous, the license is recorded as `UNKNOWN_VERIFY_SOURCE_TERMS`. No legal claims or rights are fabricated.

---

## 1. Master Licensing & Verification Matrix

| Dataset | Repository License | Dataset License | Commercial Use | Redistribution Allowed | Source | Verification Status | Notes |
|---|---|---|---|---|---|---|---|
| **HCCI** | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN` | `UNKNOWN` | [Zenodo 21931379](https://zenodo.org/records/21931379) | `UNKNOWN_VERIFY_SOURCE_TERMS` | Zenodo record 21931379 does not visibly display an explicit license badge; authoritative terms must be verified with depositors. |
| **Carinthia** | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN` | `UNKNOWN` | [Zenodo 10715190](https://zenodo.org/records/10715190) | `UNKNOWN_VERIFY_SOURCE_TERMS` | Zenodo record 10715190 does not visibly display an explicit license badge; terms must be confirmed before external redistribution. |
| **SEM Nanoscience** | `CC-BY-4.0` | `CC-BY-4.0` | `YES_WITH_ATTRIBUTION` | `YES_WITH_ATTRIBUTION` | [Nature Sci Data](https://doi.org/10.1038/sdata.2018.172) | `VERIFIED_OPEN_ACCESS` | Scientific Data article (Aversa et al., 2018) explicitly specifies Creative Commons Attribution 4.0 International (CC BY 4.0). |
| **atomagined** | `MIT` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `SOFTWARE_PERMITTED_DATA_UNKNOWN` | `UNKNOWN` | [GitHub / MDF](https://github.com/MaterialEyes/atomagined) | `REPOSITORY_MIT_DATASET_TERMS_REQUIRE_CONFIRMATION` | GitHub repository is licensed under MIT; however, dataset and synthetic HAADF-STEM benchmark rights on Materials Data Facility (DOI: 10.18126/szeq-yde5) require separate confirmation. |
| **cigRockSEM** | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN_VERIFY_SOURCE_TERMS` | `UNKNOWN` | `UNKNOWN` | [Zenodo 14988631](https://zenodo.org/records/14988631) | `UNKNOWN_VERIFY_SOURCE_TERMS` | Zenodo record 14988631 requires formal license verification prior to downstream distribution. |
| **MicroAl** | `Academic Use / Restricted` | `SUBSET_DEPENDENT` | `PROHIBITED_OR_RESTRICTED` | `RESTRICTED` | [GitHub neulmc](https://github.com/neulmc/MicroAl-Dataset) | `ACADEMIC_RESTRICTIONS_SUBSETS_PENDING_AUTHORIZATION` | Repository contains Optical, SEM, and TEM subsets. Specific subsets are restricted or require contributor authorization. Do not redistribute without per-subset audit. |

---

## 2. Policy on Data Redistribution

1. **Local Raw Data Retention:** Local research files (`data/raw/hcci`, `data/raw/carinthia`) remain in local workspace directories. No restricted or unverified third-party dataset is committed or redistributed in public git repositories.
2. **Derived Artifacts:** Only anonymized, aggregated manifests (`.parquet`, `.csv`), quality audit scores, and perceptual hash matrices are maintained within the project tree.
3. **Third-Party Subsets:** For datasets requiring manual authorization (e.g. MicroAl subsets), downstream users must download files directly from the original source repositories according to author instructions.

---

## 3. Platform Software License

The source code, adapters, and CLI tooling of the *AI-Powered Scientific Image Data Management Platform* are released for academic research under the **MIT License**.
