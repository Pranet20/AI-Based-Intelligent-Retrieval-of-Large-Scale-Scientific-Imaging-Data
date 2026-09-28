# PHASE 16 + 17: DECLARED REMAINING SYSTEM LIMITATIONS

**Date:** 2026-09-27  
**Scope:** Transparent System and Infrastructure Boundaries  
**Declaration Status:** `LIMITATIONS_FORMALLY_DECLARED`  

---

### 1. Declared Limitations Register

| Limitation ID | Category | Subsystem | Description & Root Cause | Operational Impact | Mitigation & Fallback |
|---|---|---|---|---|---|
| `LIM-16-01` | Infrastructure | Container Orchestration | Docker Desktop Linux engine daemon inactive on host system (`npipe:////./pipe/dockerDesktopLinuxEngine` unavailable). | Container orchestration via `docker compose up` could not be executed live. | All platform services, API endpoints, and model inference run natively and cleanly under Python 3.11 (`.venv311`). |
| `LIM-16-02` | Governance | Dataset Redistribution | Upstream Zenodo repositories for HCCI and Carinthia lack explicit permissive open redistribution badges (`RIGHTS_UNVERIFIED`). | Raw micrographs cannot be distributed in public bundles without potential copyright infringement. | Strict non-redistribution policy: raw images omitted from release bundle; automated downloaders and manifests provided. |
| `LIM-17-01` | Modality | Physical EDS Integration | Direct hardware coupling with physical electron beamline EDS spectrometers has not been performed on live microscope. | Cross-modal spectral retrieval is `IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA` rather than experimentally validated on live physical specimens. | Implemented EMSA/MAS parser and calibrated physics-based synthetic spectral generator (`is_synthetic=True`). |
| `LIM-17-02` | Database | Multi-Node Scalability | SQLite used as local testing fallback database. | SQLite is limited to single-writer concurrency. | Production configuration defines PostgreSQL with connection pooling (`pool_size=20`); automated backup/restore scripts tested. |
| `LIM-17-03` | Representation | Zoom Scale Invariance | Standard ViT input resizing (224x224) collapses continuous field-of-view differences between 500x and 20,000x magnifications. | Visual-only similarity can conflate wide-field overviews with localized microstructural features. | Scientific Query Language enforces scale-banded metadata constraints (`magnification >= X AND magnification <= Y`) prior to vector search. |
| `LIM-17-04` | Active Learning | Supervised Retraining Gate | Automatic self-training on human review decisions is deliberately prohibited. | Model weights do not update in real-time as curators submit reviews. | Human-in-the-loop review actions are logged to persistent audit trail; explicit batch retraining requires offline administrative sign-off. |
