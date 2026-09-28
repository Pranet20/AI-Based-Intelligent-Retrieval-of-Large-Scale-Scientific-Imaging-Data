# Standardized Scientific Terminology & Style Guide
**Project:** AI-Powered Scientific Image Data Management Platform  
**Document ID:** `pre_phase9_terminology_standard_001`  
**Date:** September 2026  
**Status:** Mandatory Standard for Phase 9 Manuscript and Documentation

---

## 1. Overview & Objective

To ensure peer-review defensibility, eliminate ambiguity, and prevent inadvertent mischaracterization of physical experiments, all manuscripts, technical reports, platform documentation, and code docstrings must adhere strictly to this Terminology Standard.

---

## 2. Canonical Terminology Dictionary

| Domain / Concept | Forbidden / Inaccurate Phrasing | Mandatory Approved Terminology | Rationale & Empirical Grounding |
| :--- | :--- | :--- | :--- |
| **Vision Backbone Architecture** | "DINOv2 ViT-B/14", "768-dimensional model", "86M parameter backbone" | **"DINOv2 ViT-S/14 (`dinov2_vits14`)"**, **"384-dimensional embeddings"**, **"22.1M parameter backbone"** | Physical codebase, checkpoints, parquet files, and FAISS indices exclusively use ViT-S/14 (384-d). ViT-B/14 was never implemented. |
| **Retrieval Evaluation Protocol** | "Same-ROI retrieval", "ROI matching across acquisitions", "ROI-registered retrieval" | **"Same-specimen cross-acquisition retrieval"**, **"Cross-instrument alloy condition matching"** | Each physical image possesses a unique `roi_id` (`roi_1` to `roi_777`); micrographs capture distinct spatial fields of view on the specimen surface rather than identical registered pixel coordinates. |
| **Material Specimen Classes** | "1000°C / 1100°C heat treatments", "Austenitized at 1000C" | **"`AsCast`"**, **"`Q980_0h_WC`"** (Quenched from 980°C, 0h hold, water-cooled), **"`Q980_9h_AC`"** (Quenched from 980°C, 9h hold, air-cooled) | These are the exact canonical strings in `hcci_manifest.parquet`. Temperature 1000°C/1100°C does not exist in the HCCI dataset. |
| **Acquisition Representation Learning** | "Adversarial domain regularization", "Metadata penalty loss", "Lagrangian domain loss" | **"Acquisition-aware contrastive learning"**, **"Supervised contrastive learning with same-acquisition masking"** | The loss function is strictly Supervised Contrastive Loss ($\tau=0.07$); acquisition invariance is induced via negative/positive pair sampling masks, not an explicit Lagrangian penalty term. |
| **Multimodal Metadata Fusion** | "Metadata enhances visual retrieval", "Multimodal synergy boost", "Combined feature superiority" | **"Neutral late metadata fusion ($\alpha^* = 1.0$)"**, **"Visual-dominant representation"**, **"Documented negative finding for late score fusion"** | Validation grid search selected $\alpha^* = 1.0$ across all feature groups A–F, yielding $\Delta \text{R@1} = 0.0$. Saturated visual representations derive no additive signal from scalar metadata. |
| **Redundancy Partitioning** | "769 images kept and 5 images reviewed mutually exclusively" | **"769 clusters identified (764 singletons, 5 pairs)"**, **"769 KEEP (representatives) and 5 REVIEW (duplicates)"** | Arithmetic: $764 \times 1 + 5 \times 2 = 774$ images. The 769 KEEP count comprises 764 singletons plus 5 canonical cluster exemplars. |
| **Quality Assessment Method** | "Deep neural quality prediction", "End-to-end learned quality network" | **"Deterministic classical signal processing indicators"**, **"Composite multi-attribute quality-risk score"** | Indicators are deterministic mathematical transforms (Laplacian variance, noise sigma, clipping ratio, dynamic range, FFT ratio) calibrated into a bounded risk score. |
| **Curation Queue Output** | "Ground-truth human-annotated defects in natural corpus", "Validated expert curation" | **"Descriptive algorithmic anomaly ranking"**, **"Unsupervised outlier triage queue"** | Top-50 natural candidates are ranked algorithmically by composite anomaly score; no formal double-blind metallurgist annotations exist for natural images. |
| **Synthetic vs Natural Evidence** | Presenting synthetic degradation scores as field performance | Explicitly tagging: **`[CONTROLLED SYNTHETIC BENCHMARK]`** vs **`[NATURAL DATA]`** | Prevents confusing controlled mathematical approximations (Gaussian blur, salt-and-pepper noise) with true physical microscope operational faults. |
| **Vector Search Latency** | "0.082 ms / 12,200 QPS Flat search", "0.018 ms / 55,500 QPS HNSW search" | **"0.7348 ms / 1,361 QPS (`IndexFlatIP`)"**, **"0.3691 ms / 2,709 QPS (`IndexHNSWFlat`)"** | Authoritative empirical benchmark on 5,365 samples ($d=384, K=10$) in `reports/phase3/latency_benchmark.csv`. Erroneous microsecond values in Phase 7 narrative were ungrounded typos. |

---

## 3. Mandatory Manuscript Phrasing Guidelines

### 3.1 Describing Negative Results
When presenting Phase 5 metadata findings, authors must avoid apologetic phrasing or claiming metadata is useless:
- **Approved:** *"Systematic ablation across six microscopy parameter groups demonstrated that late score-level metadata fusion does not provide additive retrieval accuracy over saturated self-supervised visual features ($\alpha^* = 1.0, \Delta \text{R@1} = 0.0000$). However, metadata remains essential as a hard relational pre-filter and for provenance auditing."*

### 3.2 Describing Representation Invariance
When presenting Phase 4 SupCon findings:
- **Approved:** *"Acquisition-aware contrastive projection reduces the empirical representation gap between identical specimens imaged under disparate optical configurations by 68.15% (similarity gap reduced from 0.1994 to 0.0635), while maintaining specimen classification accuracy at 98.71%."*

### 3.3 Describing Human Review Queue
When presenting Phase 6 curation:
- **Approved:** *"The curation engine constructs a priority review queue ranking images by composite quality and novelty risk. In controlled synthetic validation, prioritizing the top 25 budget slots achieved 100% anomaly capture. In natural archive screening, 50 prioritized candidates were surfaced for manual disposition."*

---

## 4. Enforcement

Reviewers of Phase 9 drafts must cross-check text against this document. Any draft using forbidden terms will be returned for revision prior to submission.
