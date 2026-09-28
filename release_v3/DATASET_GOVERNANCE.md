# Master Final Dataset Rights & Governance Report

**Document Version:** 1.0.0-final-master  
**Audit Date:** 2026-09-27  
**Scope:** Legal & Intellectual Property Audit Across All Registered Project Datasets  
**Governance Matrix:** `reports/final_audit/FINAL_DATASET_GOVERNANCE_MATRIX.csv`  
**Overall Rights Verdict:** `ACADEMIC_LOCAL_RESEARCH_PERMITTED_REDISTRIBUTION_STRICTLY_RESTRICTED`

---

## 1. Executive Summary & Legal Principles

This report audits the intellectual property, copyright, and redistribution rights across all datasets utilized or registered in the platform.

**Core Legal Principle:**  
A software repository's open-source license (e.g. MIT, Apache 2.0) **never automatically extends** to the underlying datasets hosted or referenced by that software. Similarly, the ability to download a dataset from an open repository (such as Zenodo) does not imply unrestricted redistribution or commercial re-use rights unless an explicit Creative Commons or public domain license badge is attached.

---

## 2. Dataset Rights Summary Table

| Dataset ID | Modality & Domain | Verified License | Redistribution Status | Release Packaging Action |
| :--- | :--- | :--- | :--- | :--- |
| **HCCI** | SEM Metallurgy (774 img) | `RIGHTS_UNVERIFIED` | **DO NOT REDISTRIBUTE** | Omit raw images from release; provide download script and checksum manifest only |
| **Carinthia** | Industrial SEM Defects (4,591 img) | `RIGHTS_UNVERIFIED` | **DO NOT REDISTRIBUTE** | Omit raw images from release; provide download script and checksum manifest only |
| **SEM Nanoscience** | Public SEM Nanoscience (21,272 img)| `CC BY 4.0` | **ALLOWED WITH ATTRIBUTION**| Metadata manifests and open download links included |
| **atomagined** | Synthetic HAADF-STEM (16,000 img) | `RIGHTS_UNVERIFIED` | **DO NOT REDISTRIBUTE** | Excluded from physical redistribution |
| **cigRockSEM** | Geological Rock SEM (1,500 img) | `RIGHTS_UNVERIFIED` | **DO NOT REDISTRIBUTE** | Excluded from physical redistribution |
| **MicroAl** | Aluminium Micrographs (800 img) | `RIGHTS_UNVERIFIED` | **DO NOT REDISTRIBUTE** | Excluded from physical redistribution |

---

## 3. Strict Compliance Directives for Final Release

1. **Zero Raw Third-Party Data Redistribution:** The final release package (`release_final/`) contains **zero copyrighted raw image files** from HCCI, Carinthia, atomagined, cigRockSEM, or MicroAl.
2. **Manifests and Extraction Code Only:** In accordance with FAIR data principles and standard academic reproducibility guidelines, the release distributes deterministic Python scripts that download, verify checksums, and extract datasets directly from primary Zenodo DOIs into local directories.
3. **Attribution Commitment:** Proper academic citations for all dataset authors are permanently hosted in `DATASET_CITATIONS.md` and `release_final/DATASET_CITATIONS.md`.
