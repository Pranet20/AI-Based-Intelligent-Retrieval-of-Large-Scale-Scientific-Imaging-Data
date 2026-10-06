# SCI-INTEL: Scientific Imaging Intelligence Platform
## Complete Master Architecture, Research Redefinition, and Execution Blueprint

**System Name**: **SCI-INTEL**  
**Full Name**: Scientific Imaging Intelligence Platform  
**Research Title**: *AI-Based Intelligent Retrieval and Quality-Aware Curation of Scientific Microscopy Images*  
**Document**: `PROJECT_REDEFINITION.md`  
**Location**: `/research/redefinition/PROJECT_REDEFINITION.md`  
**Standard**: IEEE Publication & Open Science Reproducibility Protocol  
**Date**: October 2026  
**Status**: OFFICIALLY APPROVED RESEARCH BLUEPRINT (PHASE 0 AUDIT COMPLETE)  

---

## 1. Project Redefinition & Identity

### 1.1 The Shift from Simple Search to Imaging Intelligence
The project is fundamentally redefined from an "image search demo" into a **publication-grade Scientific Imaging Intelligence Platform**. 

Scientific imaging in electron microscopy (SEM, TEM) and multi-channel optical/fluorescence microscopy faces acute operational challenges:
1. **Acquisition Geometry & Instrument Shifts**: Imaging the same metallurgical or biological specimen across different microscope models (e.g. Zeiss Sigma vs FEI Helios vs Tescan), accelerating voltages ($10\text{ kV}$ vs $20\text{ kV}$), or detector modalities (BSE vs SE) alters visual appearance drastically, breaking naive visual retrieval systems.
2. **Undetected Quality Degradations**: Focus drift, detector clipping, mechanical vibration blur, charging artifacts, and noise corrupt downstream scientific measurements if not caught during acquisition.
3. **Black-Box Detection Without Action**: Conventional anomaly detection produces a scalar probability score without showing *where* the defect lies, *why* it was flagged, or *what* instrument corrective action the operator should take.
4. **Dangerous Overconfidence**: Classifiers forced to label every micrograph will output false certainties on corrupted, out-of-distribution, or borderline specimens.

**SCI-INTEL** solves this through an integrated, evidence-backed workflow:

```
                          [ SCIENTIFIC MICROGRAPH ]
                                     │
                                     ▼
                        DATA & METADATA VALIDATION
                                     │
                                     ▼
                      VISION FOUNDATION REPRESENTATION
                         (DINOv2 ViT-S/14, 384-D)
                                     │
        ┌────────────────────────────┴────────────────────────────┐
        │                                                         │
        ▼                                                         ▼
 RETRIEVAL SUBSYSTEM                                       QUALITY SUBSYSTEM
        │                                                         │
        ▼                                                         ▼
 ACQUISITION-ROBUST                                        PHYSICAL QUALITY &
 RETRIEVAL ENGINE                                          ANOMALY SCREENING
 (Phase 4 Contrastive Projection)                          (6 Physical Indicators)
        │                                                         │
        ▼                                                         ▼
 RETRIEVED COMPARABLE                                      ANOMALY TYPE &
 SPECIMEN REFERENCES                                       SEVERITY ASSESSMENT
        │                                                         │
        │                                                         ▼
        │                                                 PATCH LOCALIZATION
        │                                                 (ViT Attention Map)
        │                                                         │
        │                                                         ▼
        │                                                 EXPLANATION ENGINE
        │                                                 (Why Flagged?)
        │                                                         │
        └────────────────────────────┬────────────────────────────┘
                                     │
                                     ▼
                    EVIDENCE-BACKED RECOMMENDATION ENGINE
                (Links Anomaly + Reference + Rule → Action)
                                     │
                                     ▼
                     UNCERTAINTY & OUTLIER SCREENING
                  (Selective Abstention / Human Review)
                                     │
                                     ▼
                         SCIENTIST REVIEW WORKBENCH
```

---

## 2. Three Primary Research Contributions

### Contribution 1: Acquisition-Robust Scientific Image Retrieval
* **Problem**: Micrographs of the same physical specimen acquired under differing instruments, voltages, or detector modalities exhibit large cross-acquisition representation divergence in standard foundation models.
* **Method**: A contrastive projection adapter ($f_{\theta}: \mathbb{R}^{384} \to \mathbb{R}^{384}$ with L2 normalization) trained under Supervised Contrastive Loss with multi-instrument positive pairs.
* **Result**: Achieves state-of-the-art specimen identity retrieval across distinct acquisition conditions, significantly reducing the cross-acquisition geometry gap ($p < 10^{-11}$).

### Contribution 2: Multi-Indicator Quality Assessment with Spatial Localization & Uncertainty
* **Problem**: Scalar anomaly scores fail to provide spatial interpretability or safe rejection.
* **Method**: A dual-tier screening engine combining 6 physically grounded optical/detector indicators (Laplacian focus variance, Shannon entropy, dynamic range, clipping ratio, edge density, high-frequency 2D FFT energy) with patch-level Vision Transformer feature variance for spatial defect localization.
* **Safety Mechanism**: Calibrated uncertainty estimation (ECE) and embedding-distance OOD screening enable selective prediction: the model explicitly outputs `"UNCERTAIN — HUMAN REVIEW REQUIRED"` rather than making ungrounded predictions.

### Contribution 3: Evidence-Backed Corrective-Action Recommendation
* **Problem**: Operators are left without actionable steps when a quality risk is identified.
* **Method**: A deterministic scientific rule engine synthesizing detected degradation patterns, instrument metadata, and visually comparable reference micrographs to recommend concrete laboratory adjustments (e.g. refocusing working distance, grounding adjustment for charging, beam current reduction for saturation).
* **Language Discipline**: Formulated strictly as *"Suggested corrective action"* backed by transparent evidence chains.

---

## 3. Comprehensive Repository Architecture Map

```
Mini Project/
├── configs/                          # Authoritative YAML Configurations
│   ├── datasets.yaml                 # Dataset paths, splits, and metadata schema
│   ├── paths.yaml                    # System-wide path definitions
│   └── phase4.yaml                   # Model, optimizer, and loss configurations
├── data/                             # Data Layer
│   ├── raw/                          # Authentic primary datasets (HCCI, Carinthia)
│   ├── manifests/                    # Checksum-verified Parquet/CSV manifests
│   └── processed/                    # Frozen embeddings, indexes, checkpoints
├── platform/                         # Full-Stack Application
│   ├── backend/                      # Production FastAPI Application
│   │   ├── app/
│   │   │   ├── api/                  # REST Endpoints (Images, Search, Quality, System)
│   │   │   ├── core/                 # Configs, Security, Rate Limiter
│   │   │   ├── db/                   # SQLAlchemy ORM Models & Migrations
│   │   │   ├── ml/                   # ML Serving Engines (DINOv2, FAISS, Quality)
│   │   │   └── services/             # Ingestion, Audit, Provenance, Storage
│   └── frontend/                     # Scientific Workstation UI (React 18 / TypeScript)
│       └── src/
│           ├── components/           # Navigation, Telemetry, Footer, Viewer
│           ├── pages/                # Analysis Workspace, Quality, Models, Registry
│           └── styles/               # Scientific Design System Tokens
├── research/                         # Research & Reproducibility Core
│   ├── redefinition/                 # Master Audit & Redefinition Documents (This Directory)
│   ├── benchmarks/                   # Standardized Benchmark Runners (Freeze 1)
│   ├── results/                      # Dynamic JSON Results & Traceable Artifacts
│   ├── governance/                   # Manifest Hashes & Leakage Audits
│   └── archive/                      # Preserved Legacy Reports & Obsolete Release Trees
├── src/                              # Scientific Core Libraries
│   ├── adaptation/                   # Phase 4 Contrastive Projection Architecture
│   ├── evidence/                     # Evidence Chain & Recommendation Engine
│   ├── ingestion/                    # 16-Bit Scientific Image Reader & Percentile Stretch
│   ├── integrity/                    # Physical Quality Indicators & Redundancy Cascade
│   ├── quality/                      # Spatial Localization, Uncertainty & OOD
│   ├── representation/               # DINOv2 Foundation Feature Extractor
│   └── retrieval/                    # Exact FAISS IndexFlatIP & Evaluation
├── tests/                            # Automated Pytest Suite (224 Tests Passing)
├── docker-compose.yml                # Multi-Container Orchestration (API, UI, PostgreSQL)
└── pyproject.toml                    # Python Package Configuration
```

---

## 4. File-by-File Disposition Table

| Repository Path | Category | Action | Rationale / Detail |
| :--- | :--- | :--- | :--- |
| `src/representation/dinov2_encoder.py` | ML Core | **PRESERVE** | Fully tested, active DINOv2 ViT-S/14 extraction. |
| `src/adaptation/phase4_model.py` | ML Core | **PRESERVE** | Verified contrastive projection adapter. |
| `src/integrity/quality_indicators.py` | ML Core | **PRESERVE** | Updated 16-bit percentile-stretched physics metrics. |
| `src/integrity/duplicate_cascade.py` | ML Core | **PRESERVE** | 6-stage redundancy cascade; 100% precision. |
| `src/retrieval/faiss_index.py` | ML Core | **PRESERVE** | Sub-millisecond exact IndexFlatIP retrieval. |
| `platform/backend/app/api/images.py` | API | **PRESERVE** | Deep pixel analysis, 16-bit display PNG generator. |
| `platform/backend/app/api/search.py` | API | **REFACTOR** | Extend with quality-aware retrieval filters. |
| `platform/backend/app/api/system.py` | API | **PRESERVE** | Active subsystem diagnostic runner. |
| `platform/frontend/src/pages/` | Frontend | **REFACTOR** | Redesign visual language into minimal scientific workstation. |
| `platform/frontend/src/styles/tokens.css`| Frontend | **REFACTOR** | Replace SaaS gradients with neutral scientific tokens. |
| `src/quality/localization.py` | ML Core | **CREATE (NEW)**| ViT patch attention variance heatmap generator. |
| `src/evidence/evidence_engine.py` | ML Core | **CREATE (NEW)**| Deterministic evidence chain & recommendation engine. |
| `src/quality/uncertainty.py` | ML Core | **CREATE (NEW)**| Calibrated selective abstention and OOD detection. |
| `research/benchmarks/run_retrieval.py` | Research | **CREATE (NEW)**| Unified benchmark runner for Experiment Freeze 1. |
| `release/`, `release_v4/`, `release_final/` | Legacy | **ARCHIVE** | Move redundant trees to `research/archive/legacy_releases/`. |
| `scripts/phase16/` through `phase20/` | Legacy | **ARCHIVE** | Move one-off legacy scripts to `research/archive/scripts/`. |

---

## 5. Scientific & Engineering Risk Analysis

### 5.1 Scientific Risks & Mitigation
1. **Risk: Artificial Inflation of Quality Performance via Synthetic Data**
   * *Mitigation*: Strictly tag all synthetically perturbed images as `CONTROLLED_SYNTHETIC` and segregate from `NATURAL_EXPERT_VALIDATED` micrographs.
2. **Risk: Semantic Shift Across Extreme Magnifications**
   * *Mitigation*: Feature extraction preserves metadata-aware filtering to prevent comparing a $500\times$ overview with a $50,000\times$ atomic defect.
3. **Risk: Over-Claiming Anomaly Causality**
   * *Mitigation*: The recommendation engine never asserts absolute truth; it frames findings as *"Model-derived suspicious region"* and *"Suggested corrective action"*.

### 5.2 Engineering Risks & Mitigation
1. **Risk: Large 16-Bit TIFF Memory Exhaustion**
   * *Mitigation*: Ingestion uses streaming memory mapping via `tifffile` and converts directly to normalized float32 arrays without full uncompressed memory cloning.
2. **Risk: Local vs Container Environment Discrepancies**
   * *Mitigation*: Dual-dialect SQLAlchemy ORM tested against both local SQLite and containerized PostgreSQL 15.
3. **Risk: FAISS Index Drift on Dynamic Upload**
   * *Mitigation*: Immediate dynamic indexing via `FAISSEngine.add_vector()` synchronized with database commit.

---

## 6. Implementation Sequence & Execution Roadmap

The implementation proceeds in strict phased increments:

* **PHASE 0 (CURRENT)**: Repository & dataset audit complete. Required documentation created in `research/redefinition/`.
* **PHASE 1**: Archive legacy trees, clean junk files, freeze dataset manifests and leakage audits.
* **PHASE 2**: Rebuild retrieval benchmark (Experiment Freeze 1: DINOv2 vs ResNet-50 vs pHash vs dHash).
* **PHASE 3**: Rebuild acquisition robustness evaluation across multi-seed checkpoints.
* **PHASE 4**: Controlled synthetic quality/anomaly benchmark generation and scoring.
* **PHASE 5**: Natural expert validation protocol & inter-annotator agreement framework.
* **PHASE 6**: ViT patch-level anomaly localization engine with spatial heatmaps.
* **PHASE 7**: Deterministic evidence engine & corrective-action recommendation layer.
* **PHASE 8**: Uncertainty calibration (ECE), selective abstention, and OOD screening.
* **PHASE 9**: Quality-aware retrieval API integration.
* **PHASE 10**: Controlled ablation studies across retrieval, quality, and uncertainty.
* **PHASE 11**: Diagnostic failure case and boundary analysis.
* **PHASE 12**: Workstation UI scientific redesign (minimal, editorial, data-centric).
* **PHASE 13**: Automated test suite validation (unit, integration, API, E2E).
* **PHASE 14**: Reproducibility CLI verification (`python -m research.verify_experiment`).
* **PHASE 15**: Final evidence freeze and cryptographic sealing.
