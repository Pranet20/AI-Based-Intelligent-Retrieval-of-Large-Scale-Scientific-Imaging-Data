# Post-Phase-11 Audit Revised Manuscript — Section 4 & 6: Datasets & Protocol

**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase11_revised_experimental_protocol_v110`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Section 4 & Section 6 (Post-Phase-11 Audit Revision)  

---

# 4. Datasets & Retrieval Benchmark Formulation

### 4.1 Primary In-Domain Benchmark: High-Chromium Cast Iron (`hcci`)
The primary benchmark for evaluating acquisition-robust retrieval is the High-Chromium Cast Iron (HCCI) scanning electron microscopy archive [HCCIDataset]:
- **Archive Provenance & Open Access:** Deposited on Zenodo under DOI `10.5281/zenodo.21931379` with a Creative Commons Attribution 4.0 International license (CC-BY 4.0).
- **Physical Corpus Size:** Exactly $774$ physical 8-bit uncompressed grayscale TIFF micrographs (payload size: $4,211,221,382$ bytes, ~4.21 GB). While upstream documentation originally referenced 777 potential micrographs, physical inspection confirms that indices 10, 20, and 30 were omitted from the author-deposited archive prior to ingestion.
- **Specimen Material Conditions:** Micrographs span three macroscopic heat-treatment conditions of high-chromium cast iron alloy:
  1. **`AsCast`**: As-solidified hypoeutectic microstructure (305 images).
  2. **`Q980_0h_WC`**: Destabilization heat treatment at 980°C with 0-hour hold, water-cooled (236 images).
  3. **`Q980_9h_AC`**: Destabilization heat treatment at 980°C with 9-hour hold, air-cooled (233 images).
  *(Note: Unofficial literature references to 1000°C or 1100°C austenitization are incorrect; the canonical manifest strings are strictly `AsCast`, `Q980_0h_WC`, and `Q980_9h_AC`).*
- **Instrument & Acquisition Diversity:** Images were acquired across three commercial scanning electron microscopes: FEI Helios NanoLab 600i, TESCAN VEGA3, and Zeiss GeminiSEM. Across these instruments, 67 distinct combinations of accelerating voltage (5 kV to 30 kV), beam current (0.1 nA to 10 nA), working distance (4 mm to 15 mm), magnification (500x to 20,000x), and detector modalities (In-Lens SE, Chamber SE, In-Beam BSE) were systematically varied.

> **Experimental Unit Clarification:** Statistical comparisons evaluate consistency across $N=774$ micrograph acquisition instances under varying electron optics, rather than variance across independent metallurgical alloy melts or specimen populations. The experimental unit in our retrieval benchmarks is the individual acquired micrograph under a defined instrument configuration.

---

### 4.2 External Domain Shift Benchmark: Carinthia SEM Defect Dataset (`carinthia`)
To evaluate foundation representation transferability across scientific domains without adaptation:
- **Archive Provenance:** Deposited on Zenodo under DOI `10.5281/zenodo.10715190` with CC-BY 4.0 license [CarinthiaDataset].
- **Physical Corpus Size:** $4,591$ grayscale PNG micrographs ($146,221,688$ bytes, ~146.2 MB).
- **Domain & Class Distribution:** Captures semiconductor wafer manufacturing defect morphologies partitioned across six defect classes: Class 0 (924), Class 1 (857), Class 2 (789), Class 3 (732), Class 4 (689), Class 5 (600).
- **Evaluation Role:** Evaluated zero-shot as an external domain shift benchmark (`[EXTERNAL DOMAIN SHIFT]`). Carinthia images lack embedded TIFF acquisition parameter tags, precluding cross-dataset metadata fusion.

---

### 4.3 Canonical Retrieval Protocol: Same-Specimen Cross-Acquisition Retrieval

A critical finding of our pre-Phase-9 audit is that each image in the HCCI dataset possesses a unique region-of-interest identifier (`roi_id` spanning `roi_1` to `roi_777`). Therefore, micrographs do *not* depict registered, identical physical pixel coordinates. 

> **Micrograph Pairing Boundary:** Positive adaptation pairs represent identical specimen-condition material states under different imaging instruments, rather than micron-registered identical spatial fields of view. In multiphase cast iron alloys containing primary/eutectic carbides within an iron matrix, different fields of view exhibit local morphological and phase fraction variations; our benchmark evaluates representation stability across acquisition optics for the material state rather than pixel-to-pixel co-registration.

Consequently, the authoritative retrieval benchmark is formulated strictly as **Same-Specimen Cross-Acquisition Retrieval**:
- **Positive Pair Criterion:** For a given query micrograph $q$, candidate image $c$ is a valid positive hit iff:
  $$c.\text{specimen\_id} == q.\text{specimen\_id} \quad \text{AND} \quad c.\text{acquisition\_id} \neq q.\text{acquisition\_id}$$
- **Neutral / Exclusion Criteria:**
  - *Self-Match:* Query itself ($c == q$) is excluded.
  - *Identical Acquisition Neutrality:* Micrographs from the *same* specimen under the *identical* acquisition setting ($c.\text{specimen\_id} == q.\text{specimen\_id}$ and $c.\text{acquisition\_id} == q.\text{acquisition\_id}$) are treated as neutral and excluded from the ranking pool, ensuring the system is evaluated strictly on its ability to transcend instrument-induced shifts.
  - *Identified Near-Duplicates:* Cryptographically or structurally confirmed duplicates are excluded to prevent artificial metric inflation.

---

# 6. Experimental Design & Leakage Controls

### 6.1 Leakage-Safe Dataset Partitioning

The HCCI benchmark is partitioned into three strictly disjoint subsets structured by instrument and acquisition parameter clusters:
1. **Training Partition (Helios Instruments):** $N = 427$ micrographs spanning 36 distinct acquisition conditions on the FEI Helios NanoLab. Used strictly for training the contrastive adaptation projector head ($g$) and fitting metadata scalers.
2. **Validation Partition (Helios Instruments):** $N = 135$ micrographs spanning 13 distinct acquisition conditions on the FEI Helios NanoLab. Used strictly for hyperparameter selection and grid-search calibration of metadata fusion weight $\alpha$.
3. **Held-Out Test Partition (Zeiss GeminiSEM):** $N = 212$ micrographs spanning 18 distinct acquisition conditions collected exclusively on the Zeiss GeminiSEM instrument. Kept entirely unobserved until final frozen evaluation.

---

### 6.2 Ten-Point Formal Leakage Audit

A comprehensive 10-point audit confirmed zero data leakage across all splits:
1. **Sample Disjointness:** $\text{Train} \cap \text{Val} \cap \text{Test} = \emptyset$ (0 sample overlap).
2. **Cryptographic Checksum Disjointness:** Zero SHA-256 hash collisions across partitions.
3. **Decoded Pixel Array Disjointness:** Zero exact pixel matches between splits.
4. **Near-Duplicate Disjointness:** All 5 natural duplicate pairs identified in Phase 6 reside strictly within the Test partition; zero cross-split duplicate leakage exists.
5. **Specimen Label Representation:** All 3 material conditions (`AsCast`, `Q980_0h_WC`, `Q980_9h_AC`) are proportionally represented across all splits.
6. **Acquisition Parameter Disjointness:** Complete instrument and acquisition condition isolation between Helios (Train/Val) and Zeiss Gemini (Test).
7. **Prohibited Feature Purging:** Identifiers (`specimen_id`, `roi_id`, `image_id`, `acquisition_id`) quarantined.
8. **Threshold Parameter Isolation:** Deduplication and quality thresholds locked strictly on validation splits.
9. **Hyperparameter Locking:** Temperature $\tau=0.07$, learning rate, and batch size locked prior to test evaluation.
10. **Test Gradient Updates:** Zero gradient updates or fine-tuning performed on the test partition.  
*Audit Outcome:* **PASSED (10/10 checks verified).**

---

### 6.3 Evaluation Metrics

- **Retrieval Accuracy:** Recall@K ($K \in \{1, 5, 10\}$), Mean Reciprocal Rank (MRR), Precision@K ($K \in \{5, 10\}$).
- **Representation Geometry:** Within-acquisition similarity ($\bar{S}_{\text{within}}$), cross-acquisition similarity ($\bar{S}_{\text{cross}}$), representation gap ($\Delta = \bar{S}_{\text{within}} - \bar{S}_{\text{cross}}$), and ratio ($R = \bar{S}_{\text{cross}} / \bar{S}_{\text{within}}$).
- **Quality Risk Screening:** Area Under the Receiver Operating Characteristic (AUROC) and Area Under the Precision-Recall Curve (AUPRC).

---

### 6.4 Evaluated Baselines (B0 through B7)

- **B0 (Uniform Random Retrieval):** Theoretical expectation and empirical Monte Carlo sampling.
- **B1 (pHash):** 64-bit DCT perceptual hash with Hamming distance.
- **B2 (dHash):** 64-bit horizontal pixel gradient difference hash.
- **B3 (DINOv2 Visual Baseline):** Frozen `dinov2_vits14` extractor yielding 384-dimensional class token embeddings.
- **B4 (Phase 4 Contrastive Adapted):** Proposed 2-layer MLP projection head trained via SupCon with same-acquisition masking across seeds [42, 123, 2024].
- **B5 (Metadata-Only Retrieval):** Standardized tabular metadata features projected to $\mathbb{R}^{384}$.
- **B6 (DINOv2 + Metadata Late Fusion):** Late convex score fusion of B3 and B5 using validation-calibrated $\alpha^*$.
- **B7 (Phase 4 Adapted + Metadata Late Fusion):** Late convex score fusion of B4 and B5 using validation-calibrated $\alpha^*$.

---

### 6.5 Statistical Significance Testing Protocol

- **Bootstrap Confidence Intervals:** 95% non-parametric bootstrap confidence intervals over $B = 1,000$ resamples.
- **Hypothesis Testing:** Paired Student's t-tests for normally distributed differences; two-sided Wilcoxon signed-rank tests for non-parametric rank distributions.
- **Effect Sizes:** Quantified via Cohen's $d$. Multi-seed evaluation across seeds [42, 123, 2024] reporting mean and standard deviation ($\mu \pm \sigma$).

---

### 6.6 Cryptographic Reproducibility Protocol

All experimental artifacts are tracked by SHA-256 digests in `artifacts/pre_phase9/PRE_PHASE9_AUDIT.md`. The entire benchmark reproduces deterministically via:
```bash
python -m src.cli.phase7_cmd reproduce
```
