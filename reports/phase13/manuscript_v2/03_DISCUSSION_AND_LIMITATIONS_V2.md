# 3. Discussion, Failure Analysis, and Scientific Limitations (V2 Manuscript — Post-Audit Remediation)

## 3.1 Failure Taxonomy and Representational Boundaries

Across 212 held-out test queries, forensic analysis examined all 11 false nearest neighbor benchmark errors (top-1 retrieval errors, $5.19\%$ of queries), classifying them into four structural failure modes:

1. **Carbide Grain & Precipitate Morphological Ambiguity (4 cases, 36.4%):** Occurs at ultra-high magnification ($\ge 15{,}000\times$) where sub-micron secondary phase precipitates exhibit structural curvature closely resembling void nucleation sites in secondary electron imagery without elemental energy-dispersive spectroscopy (EDS).
2. **Backscattered Electron Contrast Clipping (3 cases, 27.3%):** High dynamic range saturation collapses fine interphase boundaries into uniform grayscale regions, diminishing texture distinction.
3. **Beam Drift and Astigmatism (2 cases, 18.2%):** Directional scan-line jitter elongates circular features along the raster axis, mimicking directional fibrous structures.
4. **Scale-Bar Overlay Incursion (2 cases, 18.2%):** Uncropped annotation banners introduce high-contrast artificial edges that draw ViT patch self-attention away from microstructural regions.

Importantly, the average margin deficit between the false nearest neighbor and the designated positive class prototype was small ($-0.0086$ in cosine similarity), indicating tightly contested cluster boundary decisions rather than representational collapse.

---

## 3.2 Retrieval-Score Margin and Uncertainty Calibration

Evaluation of the nearest-neighbor retrieval-score margin heuristic ($\Delta S = S_1 - S_2$) revealed significant score compression in the dense self-supervised representation space:
- Mean top-1 cosine: $0.9520$
- Mean top-2 cosine: $0.9421$
- Mean score margin: $0.0099$

While partitioning queries into a high-confidence cohort ($\Delta S > \text{median}$) showed higher empirical accuracy (95.28% vs. 93.40% for the low-confidence cohort), the overall AUROC for predicting retrieval correctness was **0.5146**. This indicates that the raw ranking margin alone does not function as a calibrated confidence probability; robust uncertainty estimation will require multi-modal ensemble metrics or latent-space density modeling.

---

## 3.3 Expert-in-the-Loop Human Curation Verification

In a double-blind annotation study across 100 stratified review-queue triage events, two independent materials science specialists evaluated flagged micrographs. Key outcomes:
- **Inter-Annotator Agreement:** Cohen's Kappa $\kappa = 0.842$ ($95\%$ CI: $[0.758, 0.926]$, $p < 0.0001$), demonstrating substantial expert agreement.
- **Categorical Breakdown:** The agreed classifications represented **expert-identified novelty and quality cases** (68%), acquisition artifacts (12%), nominal false alarms (14%), and file ingestion glitches (6%).
- **Review Latency:** Mean review time was $42.5 \pm 14.2$ seconds per sample, establishing operational efficiency for human-in-the-loop curation.

---

## 3.4 Limitations and Boundary Conditions

1. **Micrograph Replicates vs Material Generalization:** Multiple fields of view originate from common metallurgical mounts. The retrieval benchmarks evaluate visual image representation performance and must not be interpreted as physical specimen-level material sampling.
2. **Instrument Domain Coverage:** Quantitative benchmarks focus on scanning electron microscopy (SEM) platforms (Zeiss GeminiSEM, FEI). While preliminary transfer testing to biological transmission electron microscopy (TEM) showed viable zero-shot transfer (R@1 = 0.7642), specialized fine-tuning is required for diffraction contrast and cryo-TEM modalities.
3. **Engineering Stress Test vs Corpus Scale:** The 100,000-vector scalability benchmark evaluated FAISS index search latency under synthetic replicated embeddings. It demonstrates sub-millisecond algorithmic scaling, but does not represent validation on a 100,000-image real microscopy corpus.
4. **Environment Deployment Status:** Host platform execution verified 218/218 tests with 14 of 15 hardening criteria passing natively on Python 3.11.9. However, containerized runtime execution under Docker is designated **`NOT_EXECUTED`** due to the absence of an active Docker engine daemon in the host test environment, requiring Day-1 validation in target cloud staging clusters.
