# Phase 15 Human-in-the-Loop Curation Workflow Protocol

**Document Version:** 1.0.0-phase15  
**Date:** 2026-09-27  
**Scope:** A/B Evaluation of AI-Prioritized Triage Queues vs. Unprioritized FIFO Review  
**Hypothesis Evaluated:** H4 (Workload reduction and triage efficiency through algorithmic prioritization)

---

## 1. Scientific Objective

In Phase 13, inter-rater reliability between materials specialists was confirmed ($\kappa = 0.842$). This protocol evaluates whether algorithmic review queue prioritization—combining image-derived quality screening, latent novelty, and retrieval uncertainty—increases expert review efficiency and reduces false-alarm burden compared to unprioritized review.

---

## 2. Experimental Design (Condition A vs. Condition B)

A cohort of 100 audited triage micrographs (containing 68 expert-identified novelty/quality cases, 12 acquisition artifacts, 6 ingestion glitches, and 14 nominal false alarms) is evaluated under two workflow queue presentations:

- **Condition A (Control — Unprioritized FIFO Queue):** Micrographs are presented to curators in random arrival order.
- **Condition B (Experimental — AI-Prioritized Queue):** Micrographs are sorted descending by the composite Curation Priority Index (CPI):
  $$\text{CPI}(x) = 0.40 \cdot \text{Risk}_{\text{quality}}(x) + 0.35 \cdot D_{\text{ref}}(x) + 0.25 \cdot (1 - \text{Conf}_{\text{retrieval}}(x))$$
  where $\text{Risk}_{\text{quality}}$ includes Laplacian blur and histogram saturation flags, $D_{\text{ref}}$ is latent novelty distance, and $\text{Conf}$ is retrieval certainty.

---

## 3. Measured Operational Metrics

1. **Cumulative Defect Yield:** Proportion of total actionable novelty/quality cases discovered after reviewing $K \in \{25, 50, 75, 100\}$ samples.
2. **False-Alarm Burden:** Number of nominal/clean micrographs reviewed before finding actionable cases.
3. **Review Throughput:** Time required to review and curate critical anomalies.
4. **Inter-Rater Agreement:** Cohen's Kappa maintained across prioritized review cohorts.
