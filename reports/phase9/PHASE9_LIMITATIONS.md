# Section 9: Limitations & Threats to Validity
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `phase9_limitations_001`  
**Date:** September 2026  
**Status:** Certified Manuscript Text — Section 9

---

# 9. Limitations & Threats to Validity

To uphold scientific integrity and provide a balanced foundation for future research, this section explicitly outlines the methodological boundaries, dataset constraints, and threats to validity inherent in this study.

---

### 9.1 Dataset Scope & Specimen Class Diversity
1. **Modest Corpus Size:** The primary in-domain benchmark (HCCI) consists of $774$ physical micrographs. While this dataset provides exceptional depth across acquisition parameter permutations (67 distinct instrument setups across three commercial microscopes), the total image volume is modest compared to large-scale computer vision benchmarks (e.g., ImageNet, COCO).
2. **Missing Upstream Zenodo Samples:** Prior documentation originally planned for 777 micrographs. Physical inspection of the author-deposited Zenodo archive (`10.5281/zenodo.21931379`) confirmed that sample indices 10, 20, and 30 were omitted by the originating authors prior to deposit. Our data ingestion manifest accurately registers the 774 physically available files.
3. **Limited Specimen Alloy Diversity:** The HCCI benchmark is partitioned across three heat-treatment conditions: `AsCast`, `Q980_0h_WC`, and `Q980_9h_AC`. Because these three alloy states exhibit distinct morphological carbide distributions, the baseline visual model achieved high retrieval recall ($\approx 95\%$). Performance on datasets featuring dozens of subtly differing multi-phase alloys or subtle compositional variations remains to be established.

---

### 9.2 Physical Field-of-View & ROI Registration
1. **Absence of Co-Registered Physical ROIs:** As revealed by our pre-Phase-9 audit, every micrograph in HCCI possesses a unique region-of-interest identifier (`roi_id` spanning `roi_1` to `roi_777`). Micrographs capture distinct spatial fields of view across the specimen surface rather than identical pixel-registered coordinates.
2. **Task Definition Boundary:** The retrieval task is strictly **same-specimen cross-acquisition retrieval**, not "same-ROI matching". While same-specimen retrieval accurately reflects real-world laboratory workflows (where an engineer searches for other acquisitions of the same material condition), it does not evaluate fine-grained pixel-to-pixel image alignment.

---

### 9.3 Metadata Heterogeneity & Generalization
1. **Metadata Standardization Deficits:** While HCCI contains rich, standardized TIFF tag metadata across 67 acquisition settings, external datasets (e.g., Carinthia SEM) lack embedded acquisition parameters. This heterogeneity precluded benchmarking cross-dataset multimodal fusion.
2. **Negative Result Generalizability:** Our negative finding regarding late metadata fusion ($\alpha^* = 1.0$) was established under the HCCI benchmark and a convex late-fusion architecture. While this demonstrates that scalar metadata does not boost saturated visual features, alternative architectures (e.g., cross-attention transformers or early multimodal token concatenation) might extract additive signal under different conditions.

---

### 9.4 Controlled Synthetic Benchmarks vs. Real-World Defect Diagnosis
1. **Synthetic Quality Evaluations:** The image quality risk benchmark was validated on $N = 120$ controlled synthetic samples (100 mathematically degraded micrographs across Gaussian blur, additive noise, clipping, and astigmatism, plus 20 nominal controls). While synthetic transformations provide rigorous, mathematically defined ground truth, they are approximations of real-world physical microscope hardware faults.
2. **Absence of Double-Blind Expert Annotations:** Natural archive review-queue rankings (`top_n = 50`) represent unsupervised algorithmic anomaly and novelty scores; they have not undergone formal double-blind re-annotation by certified metallurgists. Consequently, review queue outputs must be interpreted as prioritized operational triage lists rather than confirmed clinical/metallurgical diagnostic labels.

---

### 9.5 Deployment Environment & Runtime Validation
1. **Docker Runtime Verification Limitation:** While the full-stack platform passes 218 automated unit and integration tests and establishes bit-exact tensor parity ($L_\infty < 10^{-6}$) in the local Python environment, the containerized Docker environment was marked **`DOCKER_VALIDATION_NOT_EXECUTED`** due to host daemon unavailability during the closure audit. Production deployment in live enterprise clusters requires dedicated host daemon validation.
2. **Hardware-Dependent Timings:** While the algorithmic complexity of vector search is mathematically bounded ($\mathcal{O}(N)$ for Flat, $\mathcal{O}(\log N)$ for HNSW), measured sub-millisecond query execution times depend on host CPU clock frequency, memory bus bandwidth, and BLAS multi-threading configurations.

---

### 9.6 Threats to Validity

#### Construct Validity
- *Threat:* Retrieval success is defined by matching specimen alloy condition across acquisitions rather than identical spatial fields of view.
- *Mitigation:* We explicitly documented the same-specimen protocol, expunged all misleading "same-ROI" terminology, and verified that positive pairs require identical alloy condition and disjoint acquisition settings.

#### Internal Validity
- *Threat:* Data leakage across training, validation, and testing splits could artificially inflate retrieval and adaptation performance.
- *Mitigation:* A 10-point formal leakage audit confirmed zero sample, pixel, hash, or near-duplicate overlap across splits, with the test split collected on an entirely held-out commercial microscope (Zeiss GeminiSEM).

#### External Validity
- *Threat:* Findings derived from metallurgical and semiconductor SEM might not transfer to other scientific imaging modalities (e.g., Transmission Electron Microscopy [TEM], Atomic Force Microscopy [AFM], or optical metallography).
- *Mitigation:* We benchmarked external zero-shot transfer on Carinthia SEM ($N = 4,591$) and cataloged external reference repositories (SEM Nanoscience, atomagined, cigRockSEM), while explicitly noting that transfer to transmission or optical modalities requires separate domain calibration.
