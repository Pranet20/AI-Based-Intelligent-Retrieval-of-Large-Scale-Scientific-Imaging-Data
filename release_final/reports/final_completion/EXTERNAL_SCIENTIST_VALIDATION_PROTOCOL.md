# EXTERNAL SCIENTIST VALIDATION PROTOCOL

**Project**: AI-Powered Scientific Image Data Management Platform  
**Status**: `REQUIRES_HUMAN_PARTICIPANTS`  
**Prerequisites**: Independent domain-expert mineralogists, materials scientists, or certified electron microscopists.  

---

## 1. Blinding & Independence Principles
- **No Ground-Truth Leakage**: Evaluators must not have access to test labels or algorithmic internal confidence scores during review.
- **Independent Reviews**: Evaluators review cases independently without inter-rater communication.
- **Algorithmic Output Boundary**: AI recommendations must always be presented as *"algorithmic recommendations"*, never as ground truth.

## 2. Standardized Evaluation Protocol
1. **Sample Selection**: Stratified random sample of $N=120$ flagged micrographs across three risk categories: focus/quality risk, near-duplicate overlap, and relative embedding novelty ($D_{\text{ref}}$).
2. **Reviewer Tasks**:
   - Classify focus quality: Acceptable vs Defocused.
   - Classify redundancy: Unique specimen vs Redundant near-duplicate.
   - Classify novelty: Typical in-domain microstructure vs Novel morphology.
   - Usability rating of the Active Curation Workbench.
3. **Statistical Agreement**: Calculate Cohen's kappa coefficient ($\kappa$) and actionability yield (confirmed flags / total flagged).
