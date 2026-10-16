# SCI-INTEL IEEE ISBI 2027 Final QA Report
**Title:** SCI-INTEL: Acquisition-Aware Retrieval and Quality-Risk Curation of Scientific Microscopy Images  
**Target Venue:** IEEE International Symposium on Biomedical Imaging (ISBI 2027)  
**Primary Author:** Pranet Pallati  
**Date:** 2026-10-16  

---

## 1. Executive Verdict
**STATUS: READY FOR AUTHOR REVIEW AND SUBMISSION PREPARATION**  
All central scientific claims, dataset partitions, retrieval benchmarks, quality screening indicators, localization metrics, and latency numbers have been reconciled against canonical repository evidence. Stale historical metrics (`91.18%`, `118.80 ms`) and uncalibrated values are 100% excluded.

---

## 2. Summary of Key Corrections
1. **Authorship Sequence & Primary Author Confirmation:**
   - **Pranet Pallati** is confirmed as **Primary Author**, Submitting Author, and Corresponding Author (`24881A05B7@student.vardhaman.org`).
   - **Gollakota Charan Deep** and **Pooja Vunnam** are designated as Authors (Co-Authors).
   - **Ms. C. Bhavana** is designated as Faculty Guide & Research Supervisor, Author.
   - All metadata references designating Pooja Vunnam as Primary Author in `research/paper/author_metadata.md`, `reports/final_release_validation.json`, and `research/phase9/isbi2027/ISBI2027_AUTHOR_INFORMATION.md` were corrected.
   - Corrected guide email typo from `vardhman.org` to `vardhaman.org`.
2. **Numerical Alignment with Attached Manuscript:**
   - All values in the user's attached manuscript (Gap $\Delta: 0.2016 \to 0.0681$, $R@5: 0.9858 \to 0.9921$, Macro-F1: $0.6837 \to 0.6323$, IoU: $0.4454$, Selective Acc: $99.08\%$, Evidence Cohort: $N=55$ queries with $275$ items, Latency: $46.00\text{ ms}$ sealed log and $23.40\text{ ms}$ profile) match the repository ground truth 100%.
3. **ISBI 2027 Page Bounds Calibration:**
   - Technical content (Sections I–VII, Figures 1–3, Tables I–IV) is strictly confined to **Pages 1–4**.
   - Optional **Page 5** is strictly restricted to non-technical material: Ethical Compliance, Disclosures & Conflicts, and References [1]–[29].
   - Zero overflow onto Page 6.

---

## 3. Outstanding Human Actions Prior to Submission
- [ ] Confirm author sequence on official ISBI 2027 paper submission portal (Pranet Pallati first/corresponding).
- [ ] Register ORCID identifiers for all four authors (optional at initial submission, required for camera-ready).
- [ ] Confirm faculty guide institutional details and final PDF proof sign-off before official submission deadline.
