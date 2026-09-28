# Scientific Data Dictionary

This document defines the schema, field specifications, data types, nullability, and units for the normalized dataset manifests and scientific metadata containers.

---

## 1. Dataset Manifest Schema (`MANIFEST_COLUMNS`)

Manifests are serialized as Apache Parquet (`.parquet`) for efficient columnar queries and exported to CSV (`.csv`) for human readability.

| Column Name | Data Type | Nullable | Description | Example / Allowed Values |
|---|---|---|---|---|
| `dataset_id` | String | No | Unique identifier of the dataset in registry | `hcci`, `carinthia`, `atomagined` |
| `sample_id` | String | Yes | Physical sample or structure identifier | `HCCI_1`, `sample_34` |
| `image_id` | String | No | Unique persistent ID for the individual image | `hcci_1`, `carinthia_0017618f77bc` |
| `relative_path` | String | No | File path relative to dataset root directory | `Images/1.png`, `data/images/001.jpg` |
| `absolute_path_if_local_only` | String | Yes | Absolute local path if on local machine | `C:/Users/.../data/raw/hcci/Images/1.png` |
| `filename` | String | No | Base file name including extension | `1.png`, `sample_001.tif` |
| `extension` | String | No | Lowercase file extension with leading dot | `.png`, `.tif`, `.jpg`, `.h5` |
| `file_size_bytes` | Integer | No | Exact byte count of the file on disk | `6132843` |
| `sha256` | String | No | 64-character hexadecimal SHA-256 hash | `d7a8fbb307d7809469ca9abcb0082...` |
| `width` | Integer | Yes | Pixel width (columns) | `2860`, `1024`, `512` |
| `height` | Integer | Yes | Pixel height (rows) | `1922`, `1024`, `512` |
| `channels` | Integer | Yes | Number of color or spectral channels | `1` (Grayscale), `3` (RGB), `4` (RGBA) |
| `bit_depth` | Integer | Yes | Numerical bit depth per pixel channel | `8`, `16`, `32` |
| `dtype` | String | Yes | Underlying numerical data type representation | `uint8`, `uint16`, `float32` |
| `format` | String | Yes | Container or compression image format | `png`, `tiff`, `jpeg`, `hdf5` |
| `color_mode` | String | Yes | Color space representation | `Grayscale`, `RGB`, `L` |
| `modality` | String | Yes | Scientific acquisition instrument modality | `SEM`, `HAADF-STEM_synthetic`, `TEM` |
| `split` | String | Yes | Pre-assigned research split if official | `target_query`, `choice_gallery`, `external_validation` |
| `label` | String | Yes | Standardized semantic category or defect label | `defect_class_3`, `AsCast`, `rock` |
| `source_label` | String | Yes | Verbatim label string from dataset source | `3`, `AsCast` |
| `group_id` | String | Yes | Anti-leakage partition cluster key | `sample_HCCI_1_AsCast`, `defect_class_3` |
| `specimen_id` | String | Yes | Physical specimen or alloy identifier | `HCCI_1`, `Al_6061` |
| `roi_id` | String | Yes | Region of interest identifier | `roi_102` |
| `acquisition_id` | String | Yes | Distinct microscope acquisition condition code | `Helios_ICE_15kV_2500x` |
| `metadata_json` | String | Yes | JSON string containing raw and normalized metadata | `{"raw_metadata": {...}, "normalized": {...}}` |
| `quality_status` | String | Yes | Non-destructive computational quality grade | `PASS`, `REVIEW`, `FAIL` |
| `quality_score` | Float | Yes | Composite quality score (0.0000 to 1.0000) | `0.8750` |
| `duplicate_group_id` | String | Yes | Cluster identifier for SHA-256 exact duplicates | `exact_dup_0001` (or NULL if unique) |
| `near_duplicate_group_id`| String | Yes | Cluster identifier for pHash/dHash near duplicates| `near_dup_0001` (or NULL if unique) |

---

## 2. Normalized Scientific Metadata Schema

Stored inside `metadata_json` under the `normalized` key:

| Metadata Field | Type | Unit | Description |
|---|---|---|---|
| `microscope` | String | - | Microscope manufacturer, model, and column type (e.g. `Helios G4 PFIB CXe`) |
| `instrument` | String | - | Facility instrument ID or instrument platform family |
| `detector` | String | - | Imaging detector used (e.g. `ICE`, `CBS`, `ETD`, `HAADF`) |
| `accelerating_voltage_kv` | Float | kV (kilovolts) | Electron or ion beam accelerating potential |
| `magnification` | Float | x | Nominal calibrated magnification factor (e.g. `2500.0`) |
| `pixel_size_nm` | Float | nm (nanometers) | Physical calibrated pixel dimension |
| `beam_current_na` | Float | nA (nanoamperes) | Primary beam current |
| `dwell_time_us` | Float | µs (microseconds) | Electron beam pixel dwell integration time |
| `working_distance_mm` | Float | mm (millimeters) | Physical distance between pole piece and sample surface |
| `chamber_pressure_pa` | Float | Pa (Pascals) | Vacuum specimen chamber pressure |
| `sample` | String | - | Sample identifier or metallurgical composition code |
| `sample_state` | String | - | Material treatment or condition (e.g. `AsCast`, `Q980_10h`) |
| `etching_agent` | String | - | Etching chemical or method (e.g. `Picral 4%`, `Nital 2%`) |
| `imaging_mode` | String | - | Imaging signal mode (e.g. `SEM`, `HAADF-STEM`, `TEM`) |
| `scale` | String | - | Calibrated scale bar annotation string |
| `acquisition_date_if_available` | String | ISO 8601 | Verified timestamp of acquisition if embedded in metadata |
