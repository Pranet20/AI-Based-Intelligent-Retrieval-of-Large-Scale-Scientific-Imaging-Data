# Phase 7 — Formal Leakage Audit Report

**Experiment ID:** `phase7_publication_benchmark_001`  
**Protocol:** Publication-Grade Leakage Control and Cross-Split Contamination Audit

## Summary of Leakage Verification Checks

| Check ID | Verification Item | Status | Key Audit Finding |
| :--- | :--- | :---: | :--- |
| **Check A** | Image Overlap Across Splits | `PASSED` | 0 overlap across train (427), val (135), and test (212). |
| **Check B** | Exact SHA-256 Bitwise Overlap | `PASSED` | 0 cross-split exact SHA-256 hash matches. |
| **Check C** | Decoded Pixel Duplicate Overlap | `PASSED` | 0 decoded uncompressed pixel duplicates. |
| **Check D** | Near-Duplicate Split Leakage | `PASSED` | 0 cross-split near duplicates; all 5 pairs strictly intra-test. |
| **Check E** | Specimen Partition Documentation & Audit | `PASSED` | Cross-instrument domain generalization verified across macroscopic alloys. |
| **Check F** | Acquisition Condition Disjointness | `PASSED` | 100% disjoint acquisitions (67 conditions) and 0 instrument overlap. |
| **Check G** | Prohibition of Direct Metadata Identifiers | `PASSED` | 0 forbidden identifier violations (specimen_id, roi_id, etc. excluded). |
| **Check H** | Threshold and Calibration Isolation | `PASSED` | Alpha calibrated strictly on validation set (validation). |
| **Check I** | Hyperparameter Protocol Isolation | `PASSED` | Hyperparameters finalized prior to test evaluation. |
| **Check J** | Prohibition of Post-Hoc Test Set Tuning | `PASSED` | Zero test-set tuning or backpropagation. |

---

## Detailed Audit Findings by Check

### Check A: Image Overlap Across Splits
- **Status:** `PASSED`
- **Requirement:** Images must be strictly partitioned across train, validation, and test sets with zero set intersection.
- **Audit Details:**
  - `train_count`: 427
  - `val_count`: 135
  - `test_count`: 212
  - `total_partitioned`: 774
  - `total_manifest`: 774
  - `train_val_overlap`: 0
  - `train_test_overlap`: 0
  - `val_test_overlap`: 0

### Check B: Exact SHA-256 Bitwise Overlap
- **Status:** `PASSED`
- **Requirement:** Exact bitwise SHA-256 duplicate content must not cross train/val/test split boundaries.
- **Audit Details:**
  - `train_hashes_unique`: 427
  - `val_hashes_unique`: 135
  - `test_hashes_unique`: 212
  - `cross_split_hash_matches`: 0

### Check C: Decoded Pixel Duplicate Overlap
- **Status:** `PASSED`
- **Requirement:** Decoded uncompressed pixel matrices must not contain identical duplicates crossing split boundaries.
- **Audit Details:**
  - `pixel_identical_cross_split_pairs`: 0

### Check D: Near-Duplicate Split Leakage
- **Status:** `PASSED`
- **Requirement:** Near-duplicate micrograph pairs detected by the 4-stage cascade must not bridge train and test splits.
- **Audit Details:**
  - `total_near_duplicate_pairs`: 5
  - `cross_split_near_duplicates`: 0
  - `distribution`: {'train_train': 0, 'val_val': 0, 'test_test': 5, 'cross_split': 0}
  - `audit_note`: All 5 near-duplicate pairs are strictly intra-test (between Zeiss micrographs); 0 cross-split leakage.

### Check E: Specimen Partition Documentation & Audit
- **Status:** `PASSED`
- **Requirement:** Clarifies material/specimen distribution across splits: instrument-held-out benchmark evaluates cross-acquisition invariance on identical alloy compositions.
- **Audit Details:**
  - `train_specimens`: ['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']
  - `val_specimens`: ['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']
  - `test_specimens`: ['AsCast', 'Q980_0h_WC', 'Q980_9h_AC']
  - `benchmark_semantics`: Cross-instrument domain generalization. All 3 alloy material states (AsCast, 1000C, 1100C) appear in each split, enabling evaluation of material-preserving retrieval under unseen instrument optics (Zeiss Gemini).

### Check F: Acquisition Condition Disjointness
- **Status:** `PASSED`
- **Requirement:** Acquisition conditions and instrument hardware configurations must be 100% disjoint across splits.
- **Audit Details:**
  - `train_acquisitions`: 37
  - `val_acquisitions`: 12
  - `test_acquisitions`: 18
  - `total_unique_acquisitions`: 67
  - `cross_split_acquisition_overlap`: 0
  - `instruments_train`: ['Helios NanoLab', 'Helios G4 PFIB CXe']
  - `instruments_val`: ['VEGA3 XMH']
  - `instruments_test`: ['Zeiss Gemini']
  - `instrument_overlap`: 0

### Check G: Prohibition of Direct Metadata Identifiers
- **Status:** `PASSED`
- **Requirement:** Direct identifiers (specimen_id, roi_id, image_id, filenames, duplicate labels, acquisition_id) must be strictly forbidden in representation or retrieval features.
- **Audit Details:**
  - `forbidden_identifiers_checked`: ['specimen_id', 'roi_id', 'image_id', 'filename', 'duplicate_group', 'retrieval_label', 'acquisition_id', 'filepath']
  - `violations_found`: []
  - `active_metadata_feature_count`: 9
  - `active_features_sample`: ['accelerating_voltage_kv', 'beam_current_na', 'chamber_pressure_pa', 'detector', 'dwell_time_us', 'etching_agent', 'magnification', 'pixel_size_nm']

### Check H: Threshold and Calibration Isolation
- **Status:** `PASSED`
- **Requirement:** Fusion weights (alpha), scaling parameters, and anomaly thresholds must be fitted strictly on train/val without test exposure.
- **Audit Details:**
  - `phase5_alpha_calibration_split`: validation
  - `selected_alpha`: 1.0
  - `selection_criterion`: MRR on validation
  - `test_set_exposure`: None (evaluated strictly post-calibration)

### Check I: Hyperparameter Protocol Isolation
- **Status:** `PASSED`
- **Requirement:** Hyperparameters must be finalized before held-out test split evaluation.
- **Audit Details:**
  - `phase4_learning_rate`: 0.0001
  - `phase4_margin`: 0.3
  - `phase4_weight_decay`: 0.0001
  - `phase4_selection_metric`: Validation loss / MRR on VEGA3 XMH split
  - `test_evaluations_run_during_tuning`: 0

### Check J: Prohibition of Post-Hoc Test Set Tuning
- **Status:** `PASSED`
- **Requirement:** No iterative optimization, threshold adjustment, or retraining performed using test set metrics.
- **Audit Details:**
  - `reproducibility_protocol`: Frozen checkpoint inference only
  - `test_split_backpropagation`: False
  - `zero_shot_guarantee`: Zeiss Gemini test split evaluated without gradient updates or threshold re-fitting.
