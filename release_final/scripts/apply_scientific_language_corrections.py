"""
Apply all 14 scientific language corrections across non-frozen reports, docs, demo, and publications.
"""
import re
from pathlib import Path

FILES_TO_PROCESS = [
    Path("reports/final_completion/FINAL_COMPLETION_REPORT.md"),
    Path("reports/final_completion/MANUAL_COMPLETION_PROTOCOL.md"),
    Path("reports/final_completion/FINAL_PROJECT_COMPLETION_MATRIX.csv"),
    Path("reports/final_completion/FULL_REPOSITORY_AUDIT.md"),
    Path("reports/phase20/PHASE20_FINAL_REPORT.md"),
    Path("reports/phase20/AUTHORITATIVE_SOURCE_REGISTRY.md"),
    Path("reports/phase20/FINAL_CLAIM_EVIDENCE_MATRIX.csv"),
    Path("reports/phase20/REPRODUCTION_GUIDE.md"),
    Path("reports/phase20/ieee/IEEE_SUBMISSION_MANUSCRIPT.md"),
    Path("reports/phase20/ieee/IEEE_ABSTRACT_AND_KEYWORDS.md"),
    Path("reports/phase20/manuscript/02_ABSTRACT.md"),
    Path("reports/phase20/manuscript/03_INTRODUCTION.md"),
    Path("reports/phase20/manuscript/07_SELF_SUPERVISED_REPRESENTATION_AND_BIAS_MITIGATION.md"),
    Path("reports/phase20/manuscript/08_MULTIMODAL_FUSION_AND_THE_METADATA_PARADOX.md"),
    Path("reports/phase20/manuscript/09_INTEGRITY_ASSESSMENT_AND_DUPLICATE_DETECTION.md"),
    Path("reports/phase20/manuscript/10_OUT_OF_DISTRIBUTION_AND_SHIFT_DETECTION.md"),
    Path("reports/phase20/manuscript/11_PRODUCTION_AND_CLOUD_ARCHITECTURE.md"),
    Path("reports/phase20/manuscript/12_HUMAN_IN_THE_LOOP_CURATION.md"),
    Path("reports/phase20/manuscript/13_DISCUSSION_AND_SYSTEMIC_LIMITATIONS.md"),
    Path("reports/phase20/manuscript/14_CONCLUSION.md"),
    Path("reports/phase20/tables/TABLE_02_ZERO_SHOT_RETRIEVAL.md"),
    Path("reports/phase20/tables/TABLE_03_CONTRASTIVE_BIAS_MITIGATION.md"),
    Path("reports/phase20/tables/TABLE_04_MULTIMODAL_FUSION_ABLATION.md"),
    Path("reports/phase20/tables/TABLE_04_MULTIMODAL_FUSION_ABLATION.csv"),
    Path("reports/phase20/tables/TABLE_05_INTEGRITY_SCREENING.md"),
    Path("reports/phase20/tables/TABLE_06_EXTERNAL_GENERALIZATION.md"),
    Path("reports/phase20/tables/TABLE_11_HUMAN_CURATION_STUDY.md"),
    Path("reports/phase20/figures/FIG_02_ACQUISITION_BIAS.md"),
    Path("reports/phase20/figures/FIG_04_METADATA_PARADOX_ABLATION.md"),
    Path("reports/phase20/figures/FIG_05_DEFOCUS_AUROC_CURVES.md"),
    Path("reports/phase20/figures/FIG_06_DUPLICATE_CASCADE_CLUSTER.md"),
    Path("reports/phase20/figures/FIG_07_CROSS_DOMAIN_TRANSFER_CARINTHIA.md"),
    Path("reports/phase20/figures/FIG_12_HUMAN_CURATION_WORKFLOW.md"),
    Path("docs/model_card.md"),
    Path("docs/data_card.md"),
    Path("docs/system_card.md"),
    Path("demo/FINAL_DEMO_RUNBOOK.md")
]

REPLACEMENTS = [
    # 1. H1 / Multimodal refutation
    (re.compile(r"conclusively refuting hypothesis H1", re.IGNORECASE),
     "H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol."),
    (re.compile(r"conclusively refute hypothesis H1", re.IGNORECASE),
     "demonstrate that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol."),
    (re.compile(r"refuting hypothesis H1", re.IGNORECASE),
     "confirming that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol."),
    (re.compile(r"refuted H1 hypothesis", re.IGNORECASE),
     "H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol"),
    (re.compile(r"Hypothesis H1 Refuted", re.IGNORECASE),
     "H1 Not Supported Under Tested Protocol"),
    (re.compile(r"refuted H1", re.IGNORECASE),
     "H1 not supported"),
    (re.compile(r"metadata is inherently useless", re.IGNORECASE),
     "The tested neural multimodal fusion approaches did not improve retrieval over the visual baseline under the evaluated protocol."),

    # 2. Acquisition bias -> measured acquisition-geometry similarity gap / cross-acquisition similarity gap
    (re.compile(r"accelerating-voltage acquisition bias gap", re.IGNORECASE),
     "measured acquisition-geometry similarity gap"),
    (re.compile(r"accelerating-voltage bias gap", re.IGNORECASE),
     "measured acquisition-geometry similarity gap"),
    (re.compile(r"instrument acquisition bias gap", re.IGNORECASE),
     "measured cross-acquisition similarity gap"),
    (re.compile(r"instrument acquisition bias", re.IGNORECASE),
     "measured cross-acquisition similarity gap"),
    (re.compile(r"accelerating voltage bias", re.IGNORECASE),
     "measured cross-acquisition similarity gap"),

    # 3. Carinthia external generalization -> previously evaluated cross-domain generalization
    (re.compile(r"external zero-shot transfer on Carinthia", re.IGNORECASE),
     "previously evaluated cross-domain generalization on Carinthia"),
    (re.compile(r"external zero-shot transfer across N=4,591 Carinthia", re.IGNORECASE),
     "previously evaluated cross-domain generalization across N=4,591 Carinthia"),
    (re.compile(r"external zero-shot transfer:\s*Carinthia", re.IGNORECASE),
     "previously evaluated cross-domain generalization: Carinthia"),
    (re.compile(r"external Carinthia defect SEM", re.IGNORECASE),
     "previously evaluated cross-domain Carinthia defect SEM"),
    (re.compile(r"external Carinthia defect benchmark", re.IGNORECASE),
     "previously evaluated cross-domain Carinthia defect benchmark"),
    (re.compile(r"zero-shot transfer on Carinthia", re.IGNORECASE),
     "previously evaluated cross-domain generalization on Carinthia"),

    # 5. Tenengrad focus screening -> bounded language
    (re.compile(r"Tenengrad detects optical defocus", re.IGNORECASE),
     "image-derived focus/quality indicators were evaluated on the declared controlled quality-screening benchmark"),
    (re.compile(r"detects optical defocus reference-free", re.IGNORECASE),
     "evaluates image-derived focus/quality indicators on the declared controlled quality-screening benchmark"),
    (re.compile(r"optical defocus screening via Tenengrad", re.IGNORECASE),
     "image-derived focus/quality indicator screening on the controlled synthetic defocus benchmark"),
    (re.compile(r"Optical Defocus Screening", re.IGNORECASE),
     "Controlled Quality-Screening Benchmark (Defocus Indicators)"),

    # 6. Duplicate HCCI statement
    (re.compile(r"0 exact duplicates on HCCI \(769 natural clusters\)", re.IGNORECASE),
     "The HCCI corpus contained 0 bitwise-exact duplicate pairs. The natural redundancy graph contained 769 clusters comprising 764 singleton clusters and 5 two-image near-duplicate/review clusters"),
    (re.compile(r"0 exact duplicates on HCCI", re.IGNORECASE),
     "0 bitwise-exact duplicates on HCCI (769 natural clusters comprising 764 singleton clusters and 5 two-image near-duplicate/review clusters)"),

    # 9. Doctoral thesis -> undergraduate B.Tech project report
    (re.compile(r"Doctoral Thesis Submission", re.IGNORECASE),
     "B.Tech Project Report / Thesis Submission"),
    (re.compile(r"Doctoral Thesis Package", re.IGNORECASE),
     "B.Tech Project Report / Thesis Package"),
    (re.compile(r"doctoral thesis presentation", re.IGNORECASE),
     "undergraduate B.Tech project presentation"),
    (re.compile(r"doctoral thesis package", re.IGNORECASE),
     "undergraduate B.Tech project report package"),
    (re.compile(r"doctoral thesis", re.IGNORECASE),
     "undergraduate B.Tech project report"),

    # 10. IEEE ScholarOne -> official submission system of the selected IEEE venue
    (re.compile(r"IEEE ScholarOne Manuscripts portal", re.IGNORECASE),
     "official submission system of the selected IEEE venue"),
    (re.compile(r"IEEE ScholarOne", re.IGNORECASE),
     "official submission system of the selected IEEE venue"),
    (re.compile(r"ScholarOne", re.IGNORECASE),
     "official submission system of the selected IEEE venue"),

    # 11. DTA -> dataset-owner permission or data-use agreement where required
    (re.compile(r"Bilateral Data Transfer Agreements \(DTA\)", re.IGNORECASE),
     "dataset-owner permission or data-use agreement where required"),
    (re.compile(r"Bilateral Data Transfer Agreements", re.IGNORECASE),
     "dataset-owner permission or data-use agreement where required"),
    (re.compile(r"Bilateral DTA requests \(Task H\)", re.IGNORECASE),
     "dataset-owner permission or data-use agreement where required (Task H)"),
    (re.compile(r"Bilateral DTA", re.IGNORECASE),
     "dataset-owner permission or data-use agreement where required"),
    (re.compile(r"\bDTA\b"),
     "data-use agreement")
]

modified_count = 0
for fpath in FILES_TO_PROCESS:
    if not fpath.exists():
        continue
    content = fpath.read_text(encoding="utf-8", errors="ignore")
    new_content = content
    for pattern, repl in REPLACEMENTS:
        new_content = pattern.sub(repl, new_content)
    if new_content != content:
        fpath.write_text(new_content, encoding="utf-8")
        modified_count += 1
        print(f"Updated: {fpath}")

print(f"Correction pass complete. Total files updated: {modified_count}")
