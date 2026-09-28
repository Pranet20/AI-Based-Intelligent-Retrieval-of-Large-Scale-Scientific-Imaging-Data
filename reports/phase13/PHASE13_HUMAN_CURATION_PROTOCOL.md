# Phase 13 Human Curation Protocol

**Document Version:** 1.0.0-phase13  
**Status:** VALIDATED  
**Associated Experiment:** P13-EXP-08  
**Scope:** Expert-in-the-Loop Triage and Verification for Scientific Image Anomaly & Curation Systems

---

## 1. Objective & Scope

The human curation protocol provides a standardized, double-blind evaluation procedure to audit algorithmic triage decisions made by the platform's anomaly detection and data integrity subsystem (Phases 6 and 8). The primary goal is to measure inter-annotator reliability, establish ground-truth labels for ambiguous edge cases, and evaluate the operational efficiency of expert human review.

---

## 2. Sampling Methodology

1. **Target Pool:** Review queue generated during bulk ingestion of SEM micrographs from the Carinthian Tech Research and HCCI repositories ($N = 5,365$).
2. **Stratification Scheme:** Stratified random sampling ($n = 100$) across algorithmic triage flags:
   - **Stratum A (Blur / Focus Triage):** Laplacian variance $\sigma_{\text{Lap}}^2 < \tau_{\text{blur}}$ ($n = 25$)
   - **Stratum B (Visual Outlier / Mahalanobis):** $D_M(x) > \tau_{\text{anom}}$ ($n = 25$)
   - **Stratum C (Scale-bar / Overlay Incursion):** High OCR text density / edge bounding box trigger ($n = 25$)
   - **Stratum D (Algorithmic In-Distribution Control):** Micrographs flagged as nominal / clean ($n = 25$)

---

## 3. Annotator Qualifications & Training

- **Panel Composition:** Two primary independent domain evaluators (Materials Science / Electron Microscopy specialists, $\ge 3$ years SEM operational experience) and one senior adjudicator.
- **Blinding:** Micrographs are presented with randomized identifiers; evaluators are blind to algorithmic triage scores, detector thresholds, and peer annotations.
- **Standardization Phase:** A pre-study calibration calibration set of 20 non-study micrographs was annotated jointly to harmonize edge-case definitions prior to formal scoring.

---

## 4. Annotation Taxonomy & Scoring Schema

Each sampled micrograph is classified into one mutually exclusive primary category:

| Category ID | Label Name | Operational Definition |
| :--- | :--- | :--- |
| **CAT-1** | **True Anomaly** | Genuine metallurgical or microstructural defect (e.g., micro-cracks, foreign inclusions, pore clusters, anomalous grain boundary precipitation). |
| **CAT-2** | **Acquisition Artifact** | Instrument- or preparation-induced flaw rendering visual analysis non-standard (e.g., severe defocus, astigmatism, electrostatic charging flare, beam drift striping). |
| **CAT-3** | **Ingestion / Metadata Glitch** | File format corruption, missing TIFF tags, header-image dimension mismatch, or burned-in data bar obstruction of specimen structure. |
| **CAT-4** | **False Alarm / Nominal** | Standard microstructural morphology misflagged by conservative thresholding; image is fully usable for scientific analysis. |

---

## 5. Adjudication & Consensus Workflow

1. **Independent Scoring:** Rater 1 and Rater 2 independently evaluate all 100 samples via the Curation UI.
2. **Discordance Flagging:** Samples where $\text{Category}(\text{Rater 1}) \neq \text{Category}(\text{Rater 2})$ are automatically flagged for arbitration.
3. **Adjudication Session:** The senior adjudicator convenes a consensus review with both raters to review discordant cases and assign the final consensus ground truth.

---

## 6. Statistical Metrics

- **Raw Agreement Percentage:**
  $$P_o = \frac{\sum_{i=1}^k n_{ii}}{N}$$
- **Cohen's Kappa ($\kappa$):**
  $$\kappa = \frac{P_o - P_e}{1 - P_e}$$
  where $P_e = \sum_{i=1}^k p_{i \cdot} p_{\cdot i}$ is the expected hypothetical chance agreement.
- **Operational Metrics:** Mean triage time per sample (seconds), false alarm rate reduction post-curation.
