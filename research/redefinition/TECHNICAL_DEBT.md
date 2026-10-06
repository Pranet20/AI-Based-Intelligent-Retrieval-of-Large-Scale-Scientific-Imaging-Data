# SCI-INTEL: Technical Debt & Architectural Risk Register

**Document**: `TECHNICAL_DEBT.md`  
**Location**: `/research/redefinition/TECHNICAL_DEBT.md`  
**Date**: October 2026  
**Auditor**: Lead Scientific-Software Architect & MLOps Engineer  
**Status**: ACTIVE REMEDIATION REGISTER  

---

## 1. Technical Debt Classification Matrix

| Item ID | Category | Severity | Description | Impact | Remediation Plan |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`TD-01`** | **UI / Metrics** | HIGH | Hardcoded historical metrics in `Dashboard.tsx` | Misleads users with static numbers instead of dynamic results | Connect UI cards to dynamic research API endpoint `/api/v1/research/metrics` |
| **`TD-02`** | **Architecture** | HIGH | Redundant release code trees (`release/`, `release_v4/`, `release_final/`) | Code drift, file duplication, confusion over source of truth | Consolidate source of truth to `platform/` and `src/`; archive legacy trees to `research/archive/` |
| **`TD-03`** | **ML / Model** | MEDIUM | Lack of spatial anomaly localization | Quality engine outputs only global scalar risk; no spatial attention map | Implement patch-level ViT attention energy mapping in `src/quality/localization.py` |
| **`TD-04`** | **ML / Decision** | HIGH | Absence of evidence-backed recommendation engine | Users receive a risk score without physical cause or operator action | Implement deterministic scientific rule engine mapping quality risks $\to$ corrective actions |
| **`TD-05`** | **ML / Safety** | HIGH | Forced decisions without uncertainty / abstention | System predicts on low-confidence or OOD micrographs without flagging human review | Implement calibrated selective abstention (ECE + embedding distance thresholding) |
| **`TD-06`** | **Paths / Portability** | MEDIUM | Hardcoded Windows paths in select reproduction scripts | Fails on Linux/Mac or alternate drive paths | Replace all static strings with `pathlib.Path` relative to repo root or `configs/paths.yaml` |
| **`TD-07`** | **UI / Aesthetic** | MEDIUM | Remnants of SaaS dashboard aesthetic (purple gradients, rounded pill cards) | Diverges from clean, editorial, scientific instrument workstation aesthetic | Overhaul CSS design tokens with neutral palette, fine 1px borders, dense data hierarchy |
| **`TD-08`** | **Dependencies** | LOW | Deprecation warnings: `fs.F_OK` (Node.js) & `starlette.testclient` with httpx | Non-breaking build warnings during compilation and test runs | Pin updated testing client and ensure React scripts compatibility |
| **`TD-09`** | **Database** | MEDIUM | Dual SQLite/Postgres dialect configurations | Potential drift between local development and production Docker | Enforce declarative SQLAlchemy models and SQLite/Postgres parity validation tests |
| **`TD-10`** | **Security** | LOW | Default `SECRET_KEY` in development `.env` | Potential security risk if deployed to production without overriding | Enforce runtime validation failing server start if default key is used with `ENVIRONMENT=production` |

---

## 2. In-Depth Technical Debt Analysis

### 2.1 TD-01: UI Metric Hardcoding
* **Problem**: In `platform/frontend/src/pages/Dashboard.tsx`, metric values (such as `94.81%`, `68.15%`, `0.096 ms`) were statically coded in JSX. While historically derived, static presentation violates the principle of dynamically verifiable scientific evidence.
* **Remediation**:
  1. Add backend endpoint `GET /api/v1/research/metrics` reading from `data/processed/phase4/metrics/` and the research experiment registry.
  2. Frontend components fetch metrics via `ApiClient.getResearchMetrics()` with an explicit badge: `VERIFIED`, `HISTORICAL`, or `UNVERIFIED`.

---

### 2.2 TD-02: Code Tree Duplication
* **Problem**: The repository contains three separate frozen release copies:
  - `release/` (Phase 10 freeze)
  - `release_v4/` (Phase 14 freeze)
  - `release_final/` (Phase 20 freeze)
  Each directory contains duplicate copies of backend source files, reports, and configurations, consuming ~150 MB and introducing risk of editing the wrong file.
* **Remediation**:
  - The live operational platform resides exclusively in `platform/` and `src/`.
  - Move legacy release directories into `research/archive/legacy_releases/` with immutable checksum tracking.

---

### 2.3 TD-03 & TD-04: Anomaly Localization & Evidence Engine
* **Problem**: The current `QualityEngine` outputs scalar metrics ($\sigma^2_{\text{Lap}}$, entropy, dynamic range) and a composite risk label. When an image is flagged as `RISK_FLAGGED`, the user cannot see *where* on the specimen the problem occurs or *what* instrument corrective action is recommended.
* **Remediation**:
  1. Develop `src/quality/localization.py`: Extract $14 \times 14$ ViT patch tokens from DINOv2, compute spatial feature variance, and produce a normalized $224 \times 224$ heatmap overlay identifying suspicious regions.
  2. Develop `src/quality/recommendations.py`: A deterministic knowledge engine mapping `(degradation_type, severity, metadata)` to standardized microscopy corrective actions (e.g. adjust focus working distance, inspect charging ground, check detector gain).

---

### 2.4 TD-05: Uncertainty Calibration & OOD Abstention
* **Problem**: The platform previously had no mechanism to abstain when an image was out-of-distribution (e.g., non-microscopy image or severely corrupted specimen) or when the classifier had low confidence.
* **Remediation**:
  1. Add Mahalanobis / cosine distance outlier screening against the training distribution centroid.
  2. Implement confidence thresholding ($< 0.60 \implies \text{UNCERTAIN — HUMAN REVIEW REQUIRED}$).
  3. Calculate Expected Calibration Error (ECE) and selective accuracy curves.

---

### 2.5 TD-07: Scientific Workstation Design Language
* **Problem**: The frontend UI still carried traces of generic SaaS design (gradient hero headers, large rounded cards, soft shadows) rather than the requested **minimal, calm, editorial, scientific workstation** visual language.
* **Remediation**:
  - Update `platform/frontend/src/styles/tokens.css` with a high-contrast neutral slate palette, 2px/4px corner radii, 1px subtle borders, dense tabular layouts, and monospace data readouts.
