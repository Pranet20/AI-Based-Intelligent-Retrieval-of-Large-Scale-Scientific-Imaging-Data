# Scientific Experiment & Anti-Leakage Protocol

This document establishes the experimental protocols, anti-leakage grouping standards, and data integrity safeguards governing all evaluations on the scientific image data management platform.

---

## 1. Data Leakage Prevention Protocol

In scientific imaging, data leakage is a pervasive flaw. When multiple images are captured from the same metallurgical specimen, ROI (region of interest), or continuous acquisition sequence, naive random train/test splitting leaks microstructural patterns across partitions, resulting in inflated and non-generalizable performance metrics.

### 1.1 Hierarchical Grouping Identifiers
Every manifest record enforces a strict hierarchy of grouping attributes:

- `group_id`: Primary group boundary for partition splitting. Any split algorithm (e.g., `GroupKFold`, `GroupShuffleSplit`) MUST ensure that all images sharing a `group_id` reside strictly within either train, validation, or test, never across multiple splits.
- `specimen_id`: Identifies the distinct physical metallurgical or material sample (e.g., sample heat treatment batch).
- `roi_id`: Identifies a specific physical field-of-view or region of interest on the specimen surface.
- `acquisition_id`: Identifies an acquisition series captured under specific microscope conditions (e.g., specific voltage, detector, magnification combination).

### 1.2 Dataset-Specific Grouping Rules

| Dataset | Specimen Source | Leakage Prevention Strategy |
|---|---|---|
| **HCCI** | `Sample` & `Kind` columns in `Metadata_All_Samples.xlsx` | Group by `sample_<id>_<state>`. All 777 acquisition variations of a sample must stay in the same split. |
| **Carinthia** | Defect class in `carinthia.csv` | Group by class label for stratified defect evaluation. |
| **atomagined** | Crystal structure ID | Query target and gallery choices sharing a structure identifier must stay paired according to official benchmark definitions. |
| **cigRockSEM** | Geological rock core | Quarantined entirely for out-of-distribution cross-domain validation (`split="external_validation"`). |
| **MicroAl** | Alloy grade and modality | Group by alloy subset to avoid intra-alloy contamination. |

---

## 2. Experimental Integrity & Non-Fabrication Standards

To ensure the research meets the highest standards of academic peer review:

1. **Non-Destructive Operations:** Data cleansing, deduplication, and quality filtering must NEVER delete raw scientific image files. Instead, records are tagged in the manifest (`quality_status="REVIEW"`, `duplicate_group_id="..."`).
2. **Metric Integrity:** Precision, Recall, mAP, Recall@K, NDCG, and anomaly detection AUROC scores must be computed strictly via reproducible scripts against frozen test manifests. No score will ever be hand-written, estimated, or fabricated.
3. **Missing Value Policy:** When a value has not yet been experimentally determined or metadata is absent from the original source, it MUST be recorded as:
   - `NOT YET MEASURED`
   - `NOT AVAILABLE`
   - `NULL` / `None`
4. **Distinction of Prior Work:** The manuscript and documentation will explicitly delineate:
   - Existing open-source models and benchmark datasets.
   - Our software platform and pipeline implementation.
   - Our original empirical contributions and experimental findings.

---

## 3. Computational Quality Assessment Protocol

Image quality indicators implemented in Phase 1 serve as computational proxies, not absolute arbiters of scientific validity.

- Metrics computed:
  1. Intensity mean & variance
  2. Standard deviation
  3. Dynamic range
  4. RMS contrast
  5. Laplacian variance (focus sharpness proxy)
  6. Saturation ratio (upper clipping)
  7. Dark-pixel ratio (under-exposure)
  8. Bright-pixel ratio
  9. Shannon entropy (information content in bits)
- Classification policy:
  - `PASS`: All indicators satisfy high-clarity thresholds.
  - `REVIEW`: One or more indicators indicate potential blur, mild saturation, or low contrast. Flagged with specific rationale strings for researcher inspection.
  - `FAIL`: Severe collapse of dynamic range, total sensor clipping, or fatal blur.

---

## 4. Reproducibility & Provenance Standard

Every evaluation run must automatically record:
1. Unique `experiment_id` and UTC timestamp.
2. Complete environment dump via `src.utils.reproducibility.create_reproducibility_snapshot()`:
   - Git commit hash
   - OS and CPU architecture
   - Exact Python version and binary path
   - Explicit versions of all scientific packages (`numpy`, `pandas`, `tifffile`, `pyarrow`, etc.)
   - Global deterministic random seed (default: 42)
   - SHA-256 hashes of all configuration YAML files
   - Dataset manifest hash recorded in `data/manifests/dataset_versions.json`
