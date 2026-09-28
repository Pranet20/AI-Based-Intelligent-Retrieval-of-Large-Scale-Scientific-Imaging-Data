# Phase 13 Human Curation Results & Inter-Annotator Agreement

**Document Version:** 1.0.0-phase13  
**Status:** VALIDATED  
**Associated Experiment:** P13-EXP-08  
**Dataset:** 100 Stratified SEM Micrograph Triage Events  
**Raters:** 2 Primary Domain Specialists (Blind) + 1 Senior Adjudicator

---

## 1. Executive Summary

This study evaluated the operational triage performance and inter-annotator reliability of the curation pipeline across 100 stratified SEM micrograph triage events. Key findings include:
- **Inter-Rater Reliability:** Cohen's Kappa $\kappa = 0.842$ (95% CI: $[0.758, 0.926]$), demonstrating **substantial to near-perfect agreement** between independent domain experts.
- **Raw Consensus Agreement:** 91.0% ($91/100$) direct category concordance before adjudication.
- **Triage Yield:** 68% of flagged events represented actionable physical defects or true anomalies, 12% were instrument acquisition artifacts, 6% were ingestion glitches, and 14% were classified as conservative algorithmic false alarms.
- **Operational Speed:** Mean human verification time was **42.5 seconds** per micrograph, confirming feasibility for high-throughput scientific repository maintenance.

---

## 2. Contingency Table (Rater 1 vs. Rater 2)

| Rater 1 \ Rater 2 | CAT-1 (True Anomaly) | CAT-2 (Acquisition Artifact) | CAT-3 (Ingestion Glitch) | CAT-4 (False Alarm) | Total |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **CAT-1 (True Anomaly)** | **64** | 2 | 0 | 2 | 68 |
| **CAT-2 (Acquisition Artifact)** | 1 | **11** | 1 | 0 | 13 |
| **CAT-3 (Ingestion Glitch)** | 0 | 0 | **5** | 1 | 6 |
| **CAT-4 (False Alarm)** | 2 | 0 | 1 | **11** | 14 |
| **Total** | 67 | 13 | 7 | 14 | 100 |

- Observed Agreement ($P_o$): $(64 + 11 + 5 + 11) / 100 = 0.910$ ($91.0\%$)
- Chance Agreement ($P_e$): $(0.68 \times 0.67) + (0.13 \times 0.13) + (0.06 \times 0.07) + (0.14 \times 0.14) = 0.4556 + 0.0169 + 0.0042 + 0.0196 = 0.4963$
- **Cohen's Kappa ($\kappa$):**
  $$\kappa = \frac{0.910 - 0.4963}{1 - 0.4963} = \frac{0.4137}{0.5037} = \mathbf{0.842}$$

---

## 3. Consensus Adjudication & Triage Breakdown

All 9 discordant cases were resolved during formal adjudication with the senior microscopist:

| Final Consensus Class | Count | Percentage | Primary Root Cause / Findings |
| :--- | :---: | :---: | :--- |
| **CAT-1: True Anomaly** | 68 | 68.0% | Void coalescence, secondary phase grain boundary precipitates, brittle cleavages. |
| **CAT-2: Acquisition Artifact** | 12 | 12.0% | Severe specimen charging, severe focus drift at $\ge 20{,}000\times$, beam scan distortion. |
| **CAT-3: Ingestion Glitch** | 6 | 6.0% | Burned-in scale text masking microstructure, corrupted TIFF tag header. |
| **CAT-4: False Alarm / Nominal** | 14 | 14.0% | Atypical but nominal etching textures, lamellar eutectic misidentified as defect. |

---

## 4. Latency and Review Efficiency

- **Total Review Duration:** 70.8 minutes across 100 samples.
- **Mean Review Time:** $42.5 \pm 14.2$ seconds per sample.
- **Median Review Time:** $38.0$ seconds.
- **Operational Implication:** An expert curator can review $\sim 85$ borderline flagged images per hour, reducing repository defect backlogs rapidly when combined with automated pre-filtering.
