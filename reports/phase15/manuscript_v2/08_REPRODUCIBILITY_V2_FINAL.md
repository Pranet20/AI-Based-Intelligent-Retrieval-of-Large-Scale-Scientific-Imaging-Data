# 8. Reproducibility & Research Data Artifacts (Final V2 Manuscript Draft)

## 8.1 Cryptographic Immutability and Master Verification

The platform enforces absolute cryptographic traceability. All historical research artifacts from Phases 1 through 13 remain byte-for-byte immutable:
- **Phase 1–7 Research Artifacts:** 110 / 110 verified identical via SHA-256 against `artifacts/phase8/final_frozen_checksums.json`.
- **Phase 9 Manuscript Deliverables:** 17 / 17 verified identical via SHA-256 against `artifacts/phase9/PHASE9_FINAL_MANUSCRIPT_CHECKSUMS.json`.
- **Phase 12 Submission Package:** `reports/phase12/submission_package/` permanently frozen as the v1.1.0-submission-ready baseline.
- **Model Checkpoint:** `data/processed/phase4/checkpoints/best_checkpoint_seed42.pt` SHA-256 confirmed as `53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62`.
- **Master Reproduction CLI:** Validated via `python scripts/reproduce/validate_release.py --verify-only`.

---

## 8.2 Software Execution Environment & Pinned Dependencies

The platform runs on a dedicated virtual environment with strictly pinned dependencies:
- **Python Version:** 3.11.9
- **Core ML Framework:** PyTorch 2.5.1+cpu
- **Indexing Framework:** FAISS-CPU 1.9.0
- **Web API Engine:** FastAPI 0.115.0 / Uvicorn 0.30.6
- **Database Engine:** SQLAlchemy 2.0.35 with SQLite WAL mode and PostgreSQL compatibility
- **Host Testing Status:** 218 / 218 unit and integration tests passing natively in 44.82s.

---

## 8.3 Public Code, Data, and Manifest Repositories

- **Master Codebase:** Open-source release under MIT License hosted on GitHub.
- **Dataset Manifests:** Complete cryptographic manifests for all registered datasets are archived in `data/manifests/` and permanent Zenodo release packages under FAIR data guidelines.
- **Closure Manifests:** Phase 14 and Phase 15 cryptographic checksums are recorded in `reports/phase14/PHASE14_CHECKSUMS.json` and `reports/phase15/PHASE15_CHECKSUMS.json`.
