# Phase 13 Retrieval Uncertainty & Margin Calibration Report

**Document Version:** 1.0.0-phase13  
**Status:** VALIDATED  
**Associated Experiment:** P13-EXP-09  
**Source Data:** `artifacts/phase13/uncertainty_calibration.json`  
**Evaluated Cohort:** 212 Zeiss GeminiSEM Test Queries

---

## 1. Executive Summary

This report evaluates confidence estimation and retrieval uncertainty quantification in dense ViT embedding spaces. Specifically, we investigate whether the nearest-neighbor score margin:
$$\Delta S = S_{(1)} - S_{(2)} = \cos(q, x_{(1)}) - \cos(q, x_{(2)})$$
serves as a reliable proxy for retrieval correctness and calibration in high-dimensional scientific microscopy search.

Key quantitative findings from the authoritative benchmark:
- **Mean Top-1 Cosine Similarity:** $0.9520 \pm 0.0182$
- **Mean Top-2 Cosine Similarity:** $0.9421 \pm 0.0195$
- **Mean Score Margin ($\Delta S$):** $0.0099 \pm 0.0084$
- **AUROC for Correctness Prediction:** $0.5146$ (raw margin alone has limited separation power due to representation space compression)
- **High-Confidence Tier (Margin > Median):** Accuracy = **95.28%** ($101/106$)
- **Low-Confidence Tier (Margin $\le$ Median):** Accuracy = **93.40%** ($99/106$)

---

## 2. Methodology & Uncertainty Formulation

1. **Retrieval Score Formulation:** For a normalized query embedding $q \in \mathbb{R}^{384}$ and database embeddings $\{x_i\}_{i=1}^N$, cosine similarities are computed and ranked: $S_{(1)} \ge S_{(2)} \ge \dots \ge S_{(k)}$.
2. **Confidence Proxy:** The primary metric is the score margin $\Delta S = S_{(1)} - S_{(2)}$. Queries with large score margins indicate distinct cluster separation, whereas queries with narrow margins indicate ambiguous decision boundaries.
3. **Partitioning:** Queries are partitioned into two equal-sized confidence cohorts around the median margin ($\Delta S_{\text{med}} = 0.0078$):
   - **High-Confidence Tier:** $\Delta S > \Delta S_{\text{med}}$
   - **Low-Confidence Tier:** $\Delta S \le \Delta S_{\text{med}}$

---

## 3. Detailed Results & Calibration Behavior

| Metric | High-Confidence Tier ($\Delta S > \text{med}$) | Low-Confidence Tier ($\Delta S \le \text{med}$) | Overall Cohort |
| :--- | :---: | :---: | :---: |
| **Sample Count ($n$)** | 106 | 106 | 212 |
| **Correct Top-1 Matches** | 101 | 99 | 200 |
| **Top-1 Accuracy / Precision** | **95.28%** | **93.40%** | **94.34%** |
| **Mean Cosine $S_{(1)}$** | 0.9584 | 0.9456 | 0.9520 |
| **Mean Margin $\Delta S$** | 0.0163 | 0.0036 | 0.0099 |

---

## 4. Scientific Discussion & Limitations

1. **Score Compression in Self-Supervised ViT Space:** DINOv2 representations yield tightly concentrated angular distributions for domain-specific microscopy images (cosine similarities clustered between $0.92$ and $0.98$). Consequently, the top-1 to top-2 margin is inherently small (mean $\Delta S \approx 0.010$).
2. **Discrimination Limitations (AUROC = 0.515):** While the high-confidence tier exhibits higher empirical accuracy (95.28% vs. 93.40%), the raw score margin alone achieves an AUROC of only 0.5146. This indicates that incorrect retrievals often occur with high apparent confidence when an acquisition artifact or contrast clipping mimics a cluster prototype.
3. **Recommendations for V2 Architecture:**
   - **Multi-Modal Ensemble Uncertainty:** Combine visual score margin with Mahalanobis distance in the feature space ($D_M(q)$) and temperature-scaled softmax entropy.
   - **Monte Carlo Dropout / Deep Ensembles:** Employ test-time augmentation or patch dropout during inference to quantify epistemic uncertainty directly.
