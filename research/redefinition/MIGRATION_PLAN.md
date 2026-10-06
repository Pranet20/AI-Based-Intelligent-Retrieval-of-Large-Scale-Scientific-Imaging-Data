# SCI-INTEL: Phased Migration & Engineering Execution Roadmap

**Document**: `MIGRATION_PLAN.md`  
**Location**: `/research/redefinition/MIGRATION_PLAN.md`  
**Date**: October 2026  
**Status**: ACTIVE EXECUTION ROADMAP  
**Phases**: Phase 0 through Phase 15  

---

## 1. Migration Architecture & Gate Criteria

The transition to **SCI-INTEL: Scientific Imaging Intelligence Platform** is structured into 16 discrete, verified engineering phases.

### Non-Negotiable Gate Rules
1. **Incremental Execution**: Never rewrite working modules from scratch; refactor and extend cleanly.
2. **Test Driven**: Every phase ends with automated test execution (`pytest`), and cannot proceed unless all critical tests pass.
3. **Evidence Distinction**: Every metric is explicitly stamped as `[VERIFIED]`, `[HISTORICAL]`, `[UNVERIFIED]`, or `[DEMO]`.
4. **No Paper Updates**: Paper manuscripts and reports remain untouched until Phase 15 (Final Evidence Freeze).

---

## 2. Phase-by-Phase Execution Schedule

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        SCI-INTEL 16-PHASE RESEARCH ROADMAP                             │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│ FOUNDATION & AUDIT       │ CORE SCIENTIFIC ENGINES  │ WORKSTATION & RELEASE            │
│  Phase 0: Repo Audit     │  Phase 4: Synthetic Qual │  Phase 9: Quality-Aware Retrieval│
│  Phase 1: Governance     │  Phase 5: Expert Valid   │  Phase 10: Ablation Studies      │
│  Phase 2: Retrieval Rebl │  Phase 6: Localization   │  Phase 11: Failure Analysis      │
│  Phase 3: Acq Robustness │  Phase 7: Recommendation │  Phase 12: UI Scientific Redesign│
│                          │  Phase 8: Uncertainty/OOD│  Phase 13: Automated Test Suite  │
│                          │                          │  Phase 14: Reproducibility CLI   │
│                          │                          │  Phase 15: Final Evidence Freeze │
└──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

---

### Phase 0: Repository, Dataset & Experiment Audit (CURRENT)
* **Goal**: Full codebase inspection, dataset census, checkpoint verification, and technical debt registration.
* **Artifacts Created**:
  - `research/redefinition/PROJECT_AUDIT.md`
  - `research/redefinition/DATASET_INVENTORY.md`
  - `research/redefinition/MODEL_INVENTORY.md`
  - `research/redefinition/EXPERIMENT_INVENTORY.md`
  - `research/redefinition/RESULTS_PROVENANCE.md`
  - `research/redefinition/TECHNICAL_DEBT.md`
  - `research/redefinition/MIGRATION_PLAN.md`
  - `research/redefinition/PROJECT_REDEFINITION.md`
* **Gate Check**: All 8 audit documents authored; existing test suite verified (224/224 passing).

---

### Phase 1: Dataset Governance & Frozen Manifests
* **Goal**: Standardize dataset manifests, generate immutable SHA-256 hashes, verify zero train/test leakage.
* **Key Tasks**:
  - Clean out any macOS `._*` junk files from `data/raw/hcci/`.
  - Validate `data/manifests/hcci_manifest.csv` and `carinthia_manifest.csv`.
  - Formalize dataset cards in `research/datasets/cards/`.
  - Generate `research/governance/LEAKAGE_AUDIT.json`.
* **Gate Check**: Cryptographic verification confirming zero sample leakage across splits.

---

### Phase 2: Rebuild Retrieval Benchmark (Experiment Freeze 1)
* **Goal**: Unified benchmark runner evaluating DINOv2 ViT-S/14, ResNet-50, pHash, dHash, and random retrieval under exact frozen test splits.
* **Key Tasks**:
  - Implement `research/benchmarks/run_retrieval_benchmark.py`.
  - Execute all 5 baselines under the identical query set and test split.
  - Calculate R@1, R@5, R@10, MRR, P@5, and query latency.
  - Output: `research/results/retrieval_baseline_results.json` and `.csv`.
* **Gate Check**: All baselines execute without error and generate verified result artifacts.

---

### Phase 3: Rebuild Acquisition Robustness
* **Goal**: Validate Phase 4 contrastive projection adapter across multi-seed evaluations.
* **Key Tasks**:
  - Evaluate checkpoints `seed42.pt`, `seed123.pt`, `seed2024.pt`.
  - Calculate cross-instrument retrieval recall and acquisition geometry gap reduction with paired $t$-test.
  - Output: `research/results/acquisition_robustness_results.json`.
* **Gate Check**: Statistical significance verified across seeds.

---

### Phase 4: Controlled Synthetic Quality & Anomaly Benchmark
* **Goal**: Deterministic generation and evaluation of microscopy degradations.
* **Key Tasks**:
  - Implement `src/quality/synthetic_generator.py`: controlled defocus blur, Gaussian noise, detector clipping, contrast loss.
  - Preserve `(parent_id, perturbation_type, severity_level, seed)`.
  - Evaluate quality indicators: Laplacian variance, Shannon entropy, dynamic range, clipping ratio, high-freq FFT energy.
  - Calculate AUROC, AUPRC, and confusion matrices.
  - Output: `research/results/synthetic_quality_benchmark.json`.
* **Gate Check**: Clear separation between synthetic degradation and natural specimen variation.

---

### Phase 5: Natural Expert Validation Protocol
* **Goal**: Framework for human scientist annotation and adjudication.
* **Key Tasks**:
  - Create expert annotation schema in `src/quality/expert_protocol.py`.
  - Multi-reviewer agreement scoring (Cohen's Kappa / Fleiss' Kappa).
  - Explicit `UNCERTAIN` classification handling.
  - Output: `research/results/expert_validation_protocol.json`.
* **Gate Check**: Support for inter-annotator disagreement without forcing artificial labels.

---

### Phase 6: Anomaly Localization Subsystem
* **Goal**: Move beyond scalar anomaly detection to spatial heatmap localization.
* **Key Tasks**:
  - Implement `src/quality/localization.py`: ViT-S/14 $14 \times 14$ patch token attention variance and feature reconstruction distance.
  - Generate normalized $224 \times 224$ anomaly heatmaps.
  - UI overlay: Original micrograph + suspicious region heatmap + high-contrast bounding box.
  - Unit tests verifying localization output shapes and numerical stability.
* **Gate Check**: Automated tests passing for spatial heatmap extraction.

---

### Phase 7: Evidence Engine & Corrective Action Recommendation
* **Goal**: Deterministic scientific knowledge engine linking detected anomalies to physical causes and operator procedures.
* **Key Tasks**:
  - Implement `src/evidence/evidence_engine.py`: Evidence chain builder `[Micrograph $\to$ Quality Indicators $\to$ Reference Micrographs $\to$ Possible Cause $\to$ Suggested Corrective Action]`.
  - Implement `src/evidence/recommendation_rules.py`: Controlled knowledge mapping (e.g. Focus blur $\to$ check working distance and stage drift; Saturation $\to$ reduce beam dwell time or detector gain; Charging $\to$ inspect grounding and conductive coating).
  - Strict language discipline: "Suggested action", not "Guaranteed fix".
* **Gate Check**: End-to-end evidence chain generated for all quality degradation categories.

---

### Phase 8: Uncertainty Calibration & Out-of-Distribution Screening
* **Goal**: Selective prediction with abstention and OOD detection.
* **Key Tasks**:
  - Implement `src/quality/uncertainty.py`: Prediction confidence calibration, Expected Calibration Error (ECE), and selective abstention thresholding.
  - Implement `src/quality/ood_detector.py`: Embedding distance thresholding against the training distribution centroid.
  - Output: Flag `"UNCERTAIN — HUMAN REVIEW REQUIRED"` or `"OUT-OF-DISTRIBUTION"`.
* **Gate Check**: Model successfully abstains on out-of-domain and corrupted inputs.

---

### Phase 9: Quality-Aware Retrieval Integration
* **Goal**: Retrieval engine allowing filtering by specimen identity, acquisition matching, and quality thresholds.
* **Key Tasks**:
  - Extend `platform/backend/app/api/search.py` with quality-aware retrieval filters (`quality_pass_only`, `cross_acquisition_only`).
  - Retrieve evidence-backed reference pairs demonstrating normal vs degraded states of comparable specimens.
* **Gate Check**: Retrieval queries respect quality filters and return structured evidence.

---

### Phase 10: Controlled Ablation Studies
* **Goal**: Rigorous ablation of system components.
* **Key Tasks**:
  - Retrieval ablations: Frozen DINOv2 vs DINOv2 + Adapter vs DINOv2 + Metadata fusion.
  - Quality ablations: Single indicator vs multi-indicator composite risk.
  - Uncertainty ablations: Fixed threshold vs calibrated selective prediction.
  - Output: `research/results/ablation_study_results.json`.
* **Gate Check**: All ablations executed under identical conditions.

---

### Phase 11: Failure Case & Boundary Analysis
* **Goal**: Transparent reporting of system failure modes.
* **Key Tasks**:
  - Identify top false positives and false negatives for quality risk.
  - Characterize hardest cross-acquisition retrieval queries.
  - Document failure modes in `research/results/failure_analysis_report.md`.
* **Gate Check**: Detailed diagnostic analysis of model limitations.

---

### Phase 12: Workstation UI Scientific Redesign
* **Goal**: Redesign the frontend visual language into a clean, minimal, editorial scientific workstation.
* **Key Tasks**:
  - Restructure navigation: Overview, Explore, Retrieve, Quality, Evidence, Datasets, Experiments, Models, Settings.
  - Refactor Image Analysis Workspace: Left (Image viewport), Center (Quality & Localization heatmap), Right (Evidence chain & Suggested corrective actions).
  - Clean CSS design tokens: Neutral canvas, 1px subtle borders, dense tabular layouts, monospace telemetry.
* **Gate Check**: Frontend compiles cleanly (`npm run build`) with zero lint/type errors.

---

### Phase 13: Automated Testing & Continuous Integration
* **Goal**: Comprehensive test coverage across all subsystems.
* **Key Tasks**:
  - Unit tests for new evidence, recommendation, localization, and uncertainty modules.
  - API integration tests for new endpoints.
  - Smoke test: Full E2E pipeline execution from upload to recommendation.
* **Gate Check**: 100% test pass rate across `tests/` and `platform/tests/`.

---

### Phase 14: Reproducibility CLI Verification
* **Goal**: One-command verification of all experimental artifacts.
* **Key Tasks**:
  - CLI runner: `python -m research.verify_experiment <EXP_ID>`.
  - Validates dataset manifest hash, checkpoint hash, configuration hash, and metric consistency.
* **Gate Check**: Command returns `REPRODUCIBLE` with green exit code.

---

### Phase 15: Final Evidence Freeze
* **Goal**: Create immutable evidence package for IEEE manuscript update.
* **Key Tasks**:
  - Populate `research/final_freeze/` with frozen manifests, registries, and result summaries.
  - Compute `FINAL_EVIDENCE_HASH.txt`.
  - Authoritative milestone sign-off.
* **Gate Check**: Cryptographically sealed research package ready for manuscript reconciliation.
