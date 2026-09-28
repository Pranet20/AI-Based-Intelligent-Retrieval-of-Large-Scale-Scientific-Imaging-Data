"""
Refine optical defocus and H1 wording in manuscript, IEEE, and tables.
"""
from pathlib import Path

# 1. reports/phase20/manuscript/08_MULTIMODAL_FUSION_AND_THE_METADATA_PARADOX.md
p = Path("reports/phase20/manuscript/08_MULTIMODAL_FUSION_AND_THE_METADATA_PARADOX.md")
content = p.read_text(encoding="utf-8")
content = content.replace("### 6.3 Scientific Refutation of Hypothesis H1 (The Metadata Paradox)\nThe empirical results conclusively **refute Hypothesis H1**.",
                          "### 6.3 Scientific Evaluation of Hypothesis H1 (The Metadata Paradox)\nThe empirical results demonstrate that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol.")
content = content.replace("conclusively **refute Hypothesis H1**", "demonstrate that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol.")
content = content.replace("conclusively refute Hypothesis H1", "demonstrate that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol.")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

# 2. reports/phase20/manuscript/02_ABSTRACT.md
p = Path("reports/phase20/manuscript/02_ABSTRACT.md")
content = p.read_text(encoding="utf-8")
content = content.replace("Automated data integrity assessment reliably flags optical defocusing via Tenengrad gradient energy (AUROC 0.8803), while perceptual duplicate screening detects redundant acquisitions with zero exact duplicates on in-domain data and $F_1 = 0.9810$ on external archives.",
                          "Automated data integrity assessment evaluates image-derived focus/quality indicators on the declared controlled quality-screening benchmark via Tenengrad gradient energy (AUROC 0.8803, AUPRC 0.9618); the HCCI corpus contained 0 bitwise-exact duplicate pairs (natural redundancy graph contained 769 clusters comprising 764 singleton clusters and 5 two-image near-duplicate/review clusters), with $F_1 = 0.9810$ on the controlled perturbation duplicate benchmark.")
content = content.replace("optical defocusing", "acquisition-induced defocus artifacts")
content = content.replace("optical defocus blur", "synthetic defocus blur")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

# 3. reports/phase20/manuscript/03_INTRODUCTION.md
p = Path("reports/phase20/manuscript/03_INTRODUCTION.md")
content = p.read_text(encoding="utf-8")
content = content.replace("afflicted by optical defocusing", "afflicted by acquisition-induced focus degradation")
content = content.replace("screening of optical defocusing via Tenengrad gradient energy", "screening of image-derived focus/quality indicators on the controlled quality-screening benchmark via Tenengrad gradient energy")
content = content.replace("detect optical defocus without ground-truth annotations", "evaluate focus/quality indicators without ground-truth annotations")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

# 4. reports/phase20/manuscript/09_INTEGRITY_ASSESSMENT_AND_DUPLICATE_DETECTION.md
p = Path("reports/phase20/manuscript/09_INTEGRITY_ASSESSMENT_AND_DUPLICATE_DETECTION.md")
content = p.read_text(encoding="utf-8")
content = content.replace("### 7.1 Real-Time Defocus Screening (Tenengrad Gradient Energy)\nOptical defocusing is among the most pervasive artifacts in high-throughput electron microscopy, occurring due to thermal drift, sample charging, or operator error. We evaluate unsupervised Tenengrad gradient energy for reference-free focus quality scoring.",
                          "### 7.1 Real-Time Defocus Screening (Tenengrad Gradient Energy)\nAcquisition-induced focus degradation is among the most pervasive artifacts in high-throughput electron microscopy. In this platform, image-derived focus/quality indicators were evaluated on the declared controlled quality-screening benchmark using unsupervised Tenengrad gradient energy.")
content = content.replace("curated evaluation split of in-focus and deliberately defocused SEM micrographs ($N=120$)",
                          "curated evaluation split of in-focus and controlled synthetic defocus SEM micrographs ($N=120$)")
content = content.replace("Severe Optical Defocus Blur ($\\sigma = 3.0$)",
                          "Severe Synthetic Defocus Blur ($\\sigma = 3.0$)")
content = content.replace("Severe optical defocus blur ($\\sigma = 3.0$)",
                          "Severe synthetic defocus blur ($\\sigma = 3.0$)")
content = content.replace("The cascade reveals:\n- **Exact Duplicate Pairs**: $0$\n- **Near-Duplicate Pairs ($\\ge 0.95$ cosine similarity)**: $5$ pairs (perceptual overlap across adjacent FOVs)\n- **Natural Perceptual Clusters**: $769$ unique specimen clusters\n\nOn controlled perturbation benchmarks with synthetic duplicates, the cascade achieves an overall duplicate detection **F1-score of 0.9810**.",
                          "The HCCI corpus contained 0 bitwise-exact duplicate pairs. The natural redundancy graph contained 769 clusters comprising 764 singleton clusters and 5 two-image near-duplicate/review clusters (perceptual overlap across adjacent FOVs at $\\tau \\ge 0.95$). On the separate controlled perturbation benchmark with synthetic duplicates, the cascade achieves an overall duplicate detection **F1-score of 0.9810**.")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

# 5. reports/phase20/ieee/IEEE_SUBMISSION_MANUSCRIPT.md
p = Path("reports/phase20/ieee/IEEE_SUBMISSION_MANUSCRIPT.md")
content = p.read_text(encoding="utf-8")
content = content.replace("uncurated optical defocusing", "uncurated focus degradation")
content = content.replace("achieving an AUROC of 0.8803 and AUPRC of 0.9618 in optical defocus screening via Tenengrad gradient energy",
                          "achieving an AUROC of 0.8803 and AUPRC of 0.9618 in evaluating image-derived focus/quality indicators on the declared controlled quality-screening benchmark via Tenengrad gradient energy")
content = content.replace("refuting standard multimodal superiority assumptions",
                          "confirming that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol")
content = content.replace("optical defocus screening", "controlled quality screening (defocus indicators)")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

# 6. reports/phase20/ieee/IEEE_ABSTRACT_AND_KEYWORDS.md
p = Path("reports/phase20/ieee/IEEE_ABSTRACT_AND_KEYWORDS.md")
content = p.read_text(encoding="utf-8")
content = content.replace("uncurated optical defocusing", "uncurated focus degradation")
content = content.replace("achieving an AUROC of 0.8803 and AUPRC of 0.9618 in image-derived focus/quality indicator screening on the controlled synthetic defocus benchmark gradient energy",
                          "achieving an AUROC of 0.8803 and AUPRC of 0.9618 in evaluating image-derived focus/quality indicators on the declared controlled quality-screening benchmark via Tenengrad gradient energy")
content = content.replace("refuting standard multimodal superiority assumptions",
                          "confirming that H1 was not supported under the tested settings, modalities, architectures, and evaluation protocol")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

# 7. reports/phase20/tables/TABLE_11_HUMAN_CURATION_STUDY.md
p = Path("reports/phase20/tables/TABLE_11_HUMAN_CURATION_STUDY.md")
content = p.read_text(encoding="utf-8")
content = content.replace("Optical Defocus / Blurry", "Focus/Quality Indicator Risk (Defocus)")
p.write_text(content, encoding="utf-8")
print(f"Updated: {p}")

print("All targeted refinements completed.")
