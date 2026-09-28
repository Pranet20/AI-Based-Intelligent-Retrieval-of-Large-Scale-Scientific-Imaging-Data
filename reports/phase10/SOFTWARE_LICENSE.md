# Software License Governance & Rights Specification

**Project:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation  
**Phase:** Phase 10 — Reproducibility, Open-Source Release & Research Archive Build  
**Established License:** MIT License  
**Verification Date:** September 2026  

---

## 1. Provenance & Authorization

The platform source code, CLI utilities, neural projection adapters, and REST API services are released under the **MIT License**, consistent with the established project policy in `LICENSES.md` (Section 3).

### Copyright Holder
`Copyright (c) 2026 Research Team`

---

## 2. Scope of Software License Coverage

The MIT License strictly applies to:
- Core scientific algorithms and utilities in `src/`.
- Platform backend API, database schemas, and ML engines in `platform/backend/`.
- Web user interface components and state stores in `platform/frontend/`.
- Automated test suites in `tests/` and `platform/tests/`.
- Reproduction, acquisition, and validation scripts in `scripts/`.

---

## 3. Strict Exclusions from the Software License

The MIT License **does not apply** to:
1. **Third-Party Research Datasets:** Raw microscopy images (HCCI, Carinthia, SEM Nanoscience, atomagined, cigRockSEM, MicroAl) are governed exclusively by their respective author deposition terms and publisher agreements (see `reports/phase10/DATA_REDISTRIBUTION_POLICY.md`).
2. **Third-Party Pre-trained Model Weights:** The base DINOv2 vision transformer (`dinov2_vits14`) is licensed separately by Meta AI under the Apache 2.0 License.
3. **Academic Manuscript Text:** The text, figures, and narrative in `reports/phase9/` and academic publications remain under the copyright of the manuscript authors and prospective academic publishers.
