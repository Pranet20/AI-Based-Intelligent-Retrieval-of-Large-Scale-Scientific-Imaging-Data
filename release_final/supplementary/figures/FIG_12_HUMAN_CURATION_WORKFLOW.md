# Figure 12: Active Curation Queue Triage and Expert Validation Workflow

**Caption**: Double-blinded review workflow demonstrating 91.67% actionability yield, Cohen's kappa=0.8420, and 41.2% curator workload reduction.

**Figure Type**: Workflow Flowchart

```mermaid
graph TD
    FLAGGED[Flagged Micrographs: Defocus / Near-Duplicate / Novelty] --> QUEUE[Active Curation Triage Queue]
    QUEUE --> BLIND[Double-Blind Review: Expert A & Expert B]
    BLIND --> AGREE{Inter-Annotator Agreement: kappa = 0.8420}
    AGREE --> CONFIRM[110 Confirmed Valid: 91.67% Actionability Yield]
    AGREE --> FALSE[10 False Flags Rejected]
    CONFIRM --> REPO[Curated Repository Master State]
    CONFIRM --> WORKLOAD[41.2% Reduction in Manual Audit Workload]
```
