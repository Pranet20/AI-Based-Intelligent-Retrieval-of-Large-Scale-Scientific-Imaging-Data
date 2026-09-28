# Phase 7 — Formal Research Questions and Hypotheses

**Experiment ID:** `phase7_publication_benchmark_001`  
**Framework:** AI-Powered Scientific Image Data Management Platform for Metadata-Aware Retrieval, Acquisition-Robust Representation, Data Integrity Assessment, and Anomaly-Aware Curation

---

## 1. Formal Research Questions

### RQ1: Pretrained Visual Representation Efficacy
> **"Can pretrained visual representations support robust scientific microscopy retrieval?"**
- **Hypothesis $H_1$:** Foundation visual models pretrained via self-supervised learning (DINOv2 ViT-B/14) capture structural, crystallographic, and morphological features in scientific micrographs without domain-specific pretraining, substantially outperforming classical hashing baselines (pHash, dHash) and random chance.
- **Evidence Tag:** `[NATURAL DATA]`
- **Target Metrics:** Recall@1, Recall@5, MRR, Precision@5 on the held-out test split and full HCCI benchmark.

---

### RQ2: Acquisition Robustness via Representation Adaptation
> **"Does acquisition-aware representation improve robustness under acquisition changes?"**
- **Hypothesis $H_2$:** Contrastive metric learning explicitly regularized across microscope acquisition parameters (accelerating voltage, working distance, beam current, detector type) will reduce the within-vs-cross-acquisition similarity gap and improve retrieval under unseen microscope instruments (Zeiss Gemini test split).
- **Terminology Rule:** Use *"measured reduction in similarity gap"*, NOT *"elimination of acquisition bias"*.
- **Evidence Tag:** `[NATURAL DATA]`
- **Target Metrics:** Cross/Within Cosine Similarity Ratio, Acquisition Gap $\Delta = \bar{s}_{\text{within}} - \bar{s}_{\text{cross}}$, held-out instrument zero-shot R@1/P@5 across seeds [42, 123, 2024].

---

### RQ3: Scientific Metadata Fusion Efficacy
> **"Does scientific metadata provide information beyond visual similarity, and under which benchmark conditions?"**
- **Hypothesis $H_3$:** Metadata fusion provides significant retrieval utility only when visual features are degenerate or when search queries are underspecified; conversely, when high-capacity visual representations are saturated ($R@1 \ge 0.94$), late fusion of standard numerical/categorical microscopy parameters yields marginal or zero delta ($\Delta R@1 = 0.0$), with optimal calibration selecting visual weight $\alpha \to 1.0$.
- **Integrity Rule:** Do NOT assume metadata must improve retrieval. Report zero/negative findings transparently.
- **Evidence Tag:** `[NATURAL DATA]`
- **Target Metrics:** $\Delta R@1$, $\Delta \text{MRR}$, $\Delta P@5$ between visual-only, metadata-only, and hybrid fusion across ablation groups A–F.

---

### RQ4: Redundancy Detection and Quality-Risk Identification
> **"Can the framework identify redundant images and potential data-quality issues?"**
- **Hypothesis $H_4$:** A hierarchical four-stage cascade (exact SHA-256 $\to$ perceptual hash $\to$ embedding similarity $\to$ structural verification) effectively isolates near-duplicate micrographs while preventing false matches, and image-derived quality indicators (Laplacian variance, edge density, dynamic range, clipping, FFT high-frequency ratio) reliably detect degraded acquisitions in a controlled synthetic benchmark.
- **Integrity Rule:** Never use synthetic degradation results as evidence of natural archive failure rates. Distinguish *"controlled synthetic benchmark"* from *"descriptive curation observations"*.
- **Evidence Tag:** `[CONTROLLED SYNTHETIC BENCHMARK]`
- **Target Metrics:** Cascade F1, FPR, AUROC, AUPRC on synthetic degradation benchmarks; review-queue precision@K.

---

### RQ5: Representation Behavior Across Scientific Microscopy Domains
> **"How does the representation behave across different scientific microscopy domains?"**
- **Hypothesis $H_5$:** The visual representation generalises across SEM material domains (e.g., cross-acquisition, cross-instrument) with high fidelity, but exhibits distinct distributional shifts when exposed to fundamentally different imaging modalities (e.g., optical microscopy in Carinthia) or divergent nano-scale geometries.
- **Integrity Rule:** Do not pool divergent domains into identical retrieval metrics without ground truth. Classify evidence into: `IN-DOMAIN`, `CROSS-ACQUISITION`, `CROSS-INSTRUMENT`, `CROSS-DATASET`, `CROSS-MODALITY`.
- **Evidence Tag:** `[EXTERNAL DOMAIN SHIFT]`
- **Target Metrics:** Embedding cosine separation, kNN outlier distances, distribution shift statistics.

---

### RQ6: Integrated Scientific Curation Capabilities
> **"Does the integrated framework provide useful curation capabilities beyond image retrieval alone?"**
- **Hypothesis $H_6$:** Integrating representation learning, duplicate clustering, quality screening, and provenance validation creates a scalable curation workflow that reduces human review overhead by pre-clustering redundant singletons and surfacing high-risk acquisition anomalies into an actionable review queue.
- **Integrity Rule:** No claims of human expert validation unless real domain experts conducted manual verification.
- **Evidence Tag:** `[ENGINEERING MEASUREMENT]`
- **Target Metrics:** Cluster pruning efficiency (769 canonical KEEP images from 774 candidates), anomaly yield across review queue budgets ($N=10, 25, 50, 100$).

---

### RQ7: Reproducibility and Auditability
> **"Can all reported experimental results be reproduced from frozen artifacts and an explicit experiment registry?"**
- **Hypothesis $H_7$:** Every reported metric, figure, and table can be deterministically reproduced from frozen Phase 1–6 artifacts using an immutable experiment registry, automated CLI command, and zero-leakage protocol without retraining models or modifying frozen assets.
- **Evidence Tag:** `[ENGINEERING MEASUREMENT]`
- **Target Metrics:** 100% checksum match across 84 frozen files, zero metric discrepancy, automated CLI reproduction success.
