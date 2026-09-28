"""Generate Phase 11 PHASE11_EVIDENCE_GAP_REGISTER.csv."""

import csv
from pathlib import Path


def main():
    gaps = [
        {
            "Gap_ID": "GAP_01",
            "Research_Area": "Physical Specimen Linkage",
            "Missing_Evidence": "Lack of same-physical-micron ROI spatial coordinate ground truth in HCCI dataset.",
            "Affected_RQ": "RQ2",
            "Affected_Claim": "CLM_02, CLM_03",
            "Severity": "HIGH",
            "Why_It_Matters": "Reviewer B will argue that two micrographs from the same specimen at different fields of view may differ in phase composition (carbide density), confounding acquisition invariance with local spatial heterogeneity.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Can be clarified in text; dataset does not have stage coordinates)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Collect multi-instrument SEM dataset with fiducial laser markers to guarantee identical physical field of view.",
            "Priority": "P1"
        },
        {
            "Gap_ID": "GAP_02",
            "Research_Area": "Baseline Representation Comparison",
            "Missing_Evidence": "No comparative benchmark against standard supervised CNN (e.g. ResNet-50) or microscopy-specific models.",
            "Affected_RQ": "RQ1",
            "Affected_Claim": "CLM_01",
            "Severity": "MEDIUM",
            "Why_It_Matters": "Reviewer A will ask whether self-supervised ViT is genuinely required or if standard ImageNet ResNet-50 achieves comparable retrieval.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Literature establishes DINOv2 baseline superiority)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Extract ImageNet-pretrained ResNet-50 features on HCCI and evaluate Recall@1.",
            "Priority": "P1"
        },
        {
            "Gap_ID": "GAP_03",
            "Research_Area": "Multimodal Fusion Scope",
            "Missing_Evidence": "Only evaluated late linear score fusion on Gower distance; no evaluation of early concatenation or cross-attention.",
            "Affected_RQ": "RQ3",
            "Affected_Claim": "CLM_04",
            "Severity": "HIGH",
            "Why_It_Matters": "Reviewers may claim the negative result is an artifact of simplistic late fusion rather than intrinsic metadata unhelpfulness.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Bound claim precisely to late linear fusion protocol)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Train an early-fusion cross-attention MLP concatenating visual features and normalized metadata.",
            "Priority": "P1"
        },
        {
            "Gap_ID": "GAP_04",
            "Research_Area": "Natural Anomaly Ground Truth",
            "Missing_Evidence": "Lack of human-expert annotated ground-truth anomalies in real-world microscopy repositories.",
            "Affected_RQ": "RQ5",
            "Affected_Claim": "CLM_08",
            "Severity": "HIGH",
            "Why_It_Matters": "Evaluating anomaly detection using synthetic corruptions or cross-corpus semiconductor shift does not prove detection of subtle physical metallurgical defects.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Terminology correction suffices)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Partner with materials characterization facility to label genuine metallurgical anomalies (inclusions, cracks).",
            "Priority": "P1"
        },
        {
            "Gap_ID": "GAP_05",
            "Research_Area": "User Study for Curation Efficiency",
            "Missing_Evidence": "No human-in-the-loop user study measuring empirical time savings of the prioritized review queue.",
            "Affected_RQ": "RQ6",
            "Affected_Claim": "CLM_06",
            "Severity": "MEDIUM",
            "Why_It_Matters": "Claim that framework accelerates expert triage is supported by computational budget simulation, not human ergonomics data.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Clarify simulation nature of evidence)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Conduct user study with 5 materials scientists measuring time to triage 500 micrographs with vs without review queue.",
            "Priority": "P2"
        },
        {
            "Gap_ID": "GAP_06",
            "Research_Area": "Containerized Deployment Runtime",
            "Missing_Evidence": "Docker daemon validation was not executed at runtime (DOCKER_VALIDATION_NOT_EXECUTED).",
            "Affected_RQ": "RQ7",
            "Affected_Claim": "CLM_10",
            "Severity": "LOW",
            "Why_It_Matters": "Reviewer C may attempt to run docker-compose up and encounter host-specific configuration issues.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Host-level Python 3.11 reproduction is 100% verified)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Execute end-to-end Docker Compose build and automated test suite on a dedicated Linux CI runner.",
            "Priority": "P2"
        },
        {
            "Gap_ID": "GAP_07",
            "Research_Area": "Material Diversity",
            "Missing_Evidence": "Acquisition adaptation was trained and tested exclusively on High-Chromium Cast Iron.",
            "Affected_RQ": "RQ2",
            "Affected_Claim": "CLM_02",
            "Severity": "MEDIUM",
            "Why_It_Matters": "Reviewers will question whether the 68.15% gap reduction transfers to aluminum alloys, ceramics, or biological tissue.",
            "Can_Writing_Fix": "YES",
            "Additional_Experiment_Needed": "NO (Bound claims to evaluated alloy class)",
            "Recommended_Experiment": "RECOMMENDED ADDITIONAL VALIDATION: Train and evaluate adapter across multiple alloy systems in MicroAl and SEM Nanoscience.",
            "Priority": "P1"
        }
    ]

    out_file = Path("reports/phase11/PHASE11_EVIDENCE_GAP_REGISTER.csv")
    fieldnames = [
        "Gap_ID", "Research_Area", "Missing_Evidence", "Affected_RQ",
        "Affected_Claim", "Severity", "Why_It_Matters", "Can_Writing_Fix",
        "Additional_Experiment_Needed", "Recommended_Experiment", "Priority"
    ]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(gaps)

    print(f"PHASE11_EVIDENCE_GAP_REGISTER.csv written with {len(gaps)} evidence gaps cataloged.")


if __name__ == "__main__":
    main()
