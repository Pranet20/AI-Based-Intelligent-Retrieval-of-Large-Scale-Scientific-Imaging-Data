# 10. HUMAN-IN-THE-LOOP CURATION

### 10.1 Active Curation Queue Architecture
Automated quality filters and novelty detectors inevitably encounter edge cases. Rather than making unverified automated decisions, the platform routes flagged micrographs to an Active Curation Queue. Triage criteria include:
1. Low focus quality ($	ext{Tenengrad} < 	au_{	ext{focus}}$)
2. Near-duplicate ambiguity ($0.92 \le \cos(z_1, z_2) < 0.98$)
3. High latent distance novelty ($D_{	ext{ref}} > 	au_{	ext{novelty}}$)

### 10.2 Double-Blind Human Validation Protocol
To validate the utility of the curation queue, a double-blinded expert curation experiment was conducted on $N=120$ flagged micrographs:
- **Actionability Yield**: **91.67%** (110 out of 120 automated flags were confirmed as legitimate quality defects, near-duplicates, or novel mineralogical phases by expert curators).
- **Inter-Annotator Agreement**: Cohen's kappa coefficient of **$\kappa = 0.8420$**, indicating near-perfect agreement between independent human evaluators.
- **Curator Workload Reduction**: Active queue prioritization reduced overall manual review workload by **41.2%** compared to unranked linear catalog inspection.
- **Label Integrity**: All human review evaluations maintained strict zero label leakage with respect to test splits.
