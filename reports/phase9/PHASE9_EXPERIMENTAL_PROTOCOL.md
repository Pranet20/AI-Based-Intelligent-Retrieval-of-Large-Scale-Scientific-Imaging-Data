# Section 4 & 6: Datasets, Partitioning & Experimental Protocol
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase9_experimental_protocol_001`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Section 4 & Section 6

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

---

### 4.2 External Domain Shift Benchmark: Carinthia SEM Defect Dataset (`carinthia`)
To evaluate foundation representation transferability across scientific domains without adaptation:
- **Archive Provenance:** Deposited on Zenodo under DOI `10.5281/zenodo.10715190` with CC-BY 4.0 license [CarinthiaDataset].
- **Physical Corpus Size:** $4,591$ grayscale PNG micrographs ($146,221,688$ bytes, ~146.2 MB).
- **Domain & Class Distribution:** Captures semiconductor wafer manufacturing defect morphologies partitioned across six defect classes: Class 0 (924), Class 1 (857), Class 2 (789), Class 3 (732), Class 4 (689), Class 5 (600).
- **Evaluation Role:** Evaluated zero-shot as an external domain shift benchmark (`[EXTERNAL DOMAIN SHIFT]`). Carinthia images lack embedded TIFF acquisition parameter tags, precluding cross-dataset metadata fusion.

---

### 4.3 External Reference Repositories
To establish the broader context of scientific microscopy data management, three large external repositories are cataloged as reference baselines:
- **Annotated SEM Dataset for Nanoscience (`sem_nanoscience`):** $18,577$ annotated micrographs across nanostructures, nanowires, and nanoparticles (CC-BY 4.0).
- **cigRockSEM Archive (`cigrocksem`):** $2,500$ geological SEM micrographs capturing rock porosity and mineral grains.
- **atomagined Archive (`atomagined`):** $1,200$ Scanning Transmission Electron Microscopy (STEM/HAADF) atomic-resolution micrographs.

---

### 4.4 Canonical Retrieval Protocol: Same-Specimen Cross-Acquisition Retrieval

A critical finding of our pre-Phase-9 audit is that each image in the HCCI dataset possesses a unique region-of-interest identifier (`roi_id` spanning `roi_1` to `roi_777`). Therefore, micrographs do *not* depict registered, identical physical pixel coordinates. 

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
2. **Validation Partition (Helios Instruments):** $N = 135$ micrographs spanning 13 distinct acquisition conditions on the FEI Helios NanoLab. Used exclusively for hyperparameter tuning (learning rate, temperature $\tau$, early stopping) and grid-search calibration of metadata fusion weight $\alpha^*$.
3. **Held-Out Test Partition (Zeiss GeminiSEM):** $N = 212$ micrographs spanning 18 distinct acquisition conditions collected exclusively on the **Zeiss GeminiSEM** instrument. This partition evaluates true zero-shot cross-instrument generalization on entirely unseen microscope optics.

---

### 6.2 Ten-Point Formal Leakage Audit

To guarantee scientific defensibility and eliminate subtle data leakage, the experimental pipeline was subjected to a 10-point audit (Table 2):
1. **Image Sample Disjointness (Check A):** 0 sample overlap between Train (427), Val (135), and Test (212).
2. **Cryptographic SHA-256 Bitwise Overlap (Check B):** 0 matching hashes across split boundaries.
3. **Decoded Pixel Array Overlap (Check C):** 0 identical uncompressed pixel buffers across splits.
4. **Near-Duplicate Cross-Split Leakage (Check D):** 0 near-duplicates cross split boundaries (all 5 near-duplicate pairs identified in HCCI are strictly intra-test).
5. **Specimen Partition Semantics (Check E):** All 3 alloy conditions (`AsCast`, `Q980_0h_WC`, `Q980_9h_AC`) are present across all splits, ensuring cross-instrument condition invariance is measured for all materials.
6. **Acquisition Disjointness (Check F):** 100% disjoint acquisition conditions (67 conditions partitioned disjointly across splits) and complete instrument isolation of the Zeiss GeminiSEM test split.
7. **Prohibited Feature Exclusion (Check G):** Verification that `specimen_id`, `roi_id`, `image_id`, `filename`, and `acquisition_id` are completely absent from metadata feature tensors.
8. **Threshold & Calibration Isolation (Check H):** Fusion weight $\alpha^*$ and quality thresholds tuned strictly on the validation partition without test split exposure.
9. **Hyperparameter Isolation (Check I):** Projector learning rates and temperature $\tau = 0.07$ finalized prior to test split inference.
10. **Zero Test-Set Tuning (Check J):** Zero backpropagation updates, parameter fitting, or iterative re-tuning on test data.
**Audit Outcome:** **PASSED (10/10 checks verified).**

---

### 6.3 Retrieval Evaluation Metrics

For each query image $q$ evaluated against candidate gallery $\mathcal{G}$:
- **Recall@K (R@K):** Fraction of queries where at least one valid positive hit appears within the top $K$ retrieved candidates:
  $$\text{Recall@K} = \frac{1}{|Q|} \sum_{q \in Q} \mathbb{I}\left( \left| \text{TopK}(q) \cap \mathcal{P}(q) \right| \ge 1 \right)$$
- **Mean Reciprocal Rank (MRR):** Harmonic mean of the rank of the first relevant candidate:
  $$\text{MRR} = \frac{1}{|Q|} \sum_{q \in Q} \frac{1}{\text{rank}_1(q)}$$
- **Precision@K (P@K):** Proportion of retrieved candidates in the top $K$ that are valid positives:
  $$\text{Precision@K} = \frac{1}{|Q|} \sum_{q \in Q} \frac{\left| \text{TopK}(q) \cap \mathcal{P}(q) \right|}{K}$$
- **Representation Geometry Metrics:** Within-acquisition cosine similarity ($\bar{S}_{\text{within}}$), cross-acquisition cosine similarity ($\bar{S}_{\text{cross}}$), representation gap ($\Delta = \bar{S}_{\text{within}} - \bar{S}_{\text{cross}}$), and cross/within ratio ($R = \bar{S}_{\text{cross}} / \bar{S}_{\text{within}}$).

---

### 6.4 Evaluated Baselines (B0 through B7)

- **B0 (Uniform Random Retrieval):** Theoretical expectation and empirical Monte Carlo sampling over gallery candidates.
- **B1 (pHash):** 64-bit 2D Discrete Cosine Transform perceptual hash with normalized Hamming distance [Zauner2010].
- **B2 (dHash):** 64-bit horizontal pixel gradient difference hash [Zauner2010].
- **B3 (DINOv2 Visual Baseline):** Frozen `dinov2_vits14` extractor yielding 384-dimensional $L_2$-normalized class token embeddings [Oquab2023].
- **B4 (Phase 4 Contrastive Adapted):** Proposed 2-layer MLP projection head ($384 \to 128 \to 128$) trained via Supervised Contrastive Loss with same-acquisition masking across random seeds [42, 123, 2024].
- **B5 (Metadata-Only Retrieval):** Standardized tabular metadata features projected to $\mathbb{R}^{384}$ using cosine distance.
- **B6 (DINOv2 + Metadata Late Fusion):** Late convex score fusion of B3 and B5 using validation-calibrated $\alpha^*$.
- **B7 (Phase 4 Adapted + Metadata Late Fusion):** Late convex score fusion of B4 and B5 using validation-calibrated $\alpha^*$.

---

### 6.5 Statistical Significance Testing Protocol

To ensure peer-review rigor:
1. **Confidence Intervals:** 95% non-parametric bootstrap confidence intervals are computed over $B = 1,000$ resamples.
2. **Hypothesis Testing:** Paired two-tailed Student's t-tests are conducted for normally distributed metric differences; two-sided Wilcoxon signed-rank tests are conducted for non-parametric rank distributions.
3. **Effect Sizes:** Standardized effect sizes are quantified via Cohen's $d$.
4. **Multi-Seed Stability:** All adapted neural models are evaluated across three distinct random seeds ([42, 123, 2024]), reporting mean and sample standard deviation ($\mu \pm \sigma$).

---

### 6.6 Cryptographic Reproducibility Protocol

All experimental artifacts, trained model checkpoints, FAISS index binaries, feature parquets, and tabular outputs are permanently registered with SHA-256 digests in `artifacts/pre_phase9/`. The complete end-to-end benchmark is executable via a single CLI entry point:
```bash
python -m src.cli.phase7_cmd reproduce
```
recomputing all figures, tables, and metric outputs deterministically from frozen assets.
