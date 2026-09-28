"""Generate Phase 11 PHASE11_BASELINE_AUDIT.csv."""

import csv
from pathlib import Path


def main():
    rows = [
        {
            "Baseline_Category": "Uniform Random Generator",
            "Specific_Method": "Uniform random rank permutation",
            "Included_in_Project": "YES (EXP_RET_B0)",
            "Observed_Performance": "Recall@1=0.0013, MRR=0.0091",
            "Reviewer_Relevance": "Establishes theoretical chance floor for 774-item retrieval pool.",
            "Expected_Reviewer_Demand": "LOW (Standard hygiene check)",
            "Absence_Threatens_Conclusion": "NO",
            "Reviewer_Critique": "Expected baseline; confirms benchmark is not degenerate.",
            "Recommended_Priority": "P3 (Already satisfied)"
        },
        {
            "Baseline_Category": "Perceptual Image Hashing",
            "Specific_Method": "pHash (64-bit DCT) & dHash (64-bit gradient)",
            "Included_in_Project": "YES (EXP_RET_B1, EXP_RET_B2)",
            "Observed_Performance": "pHash R@1=0.0210, MRR=0.0489; dHash R@1=0.0180, MRR=0.0421",
            "Reviewer_Relevance": "Standard industrial deduplication and visual hashing baselines.",
            "Expected_Reviewer_Demand": "MEDIUM",
            "Absence_Threatens_Conclusion": "NO",
            "Reviewer_Critique": "Demonstrates why classical perceptual hashes fail completely under scientific microscopy variations.",
            "Recommended_Priority": "P3 (Already satisfied)"
        },
        {
            "Baseline_Category": "Self-Supervised Vision Foundation Model",
            "Specific_Method": "DINOv2 ViT-S/14 (384-d, frozen, CLS token)",
            "Included_in_Project": "YES (EXP_RET_B3)",
            "Observed_Performance": "Recall@1=0.9819, MRR=0.9894",
            "Reviewer_Relevance": "Primary visual representation backbone; state-of-the-art SSL foundation model.",
            "Expected_Reviewer_Demand": "HIGH (Mandatory)",
            "Absence_Threatens_Conclusion": "NO",
            "Reviewer_Critique": "Strong baseline; demonstrates excellent in-domain retrieval, but exposes cross-instrument gap.",
            "Recommended_Priority": "P3 (Already satisfied)"
        },
        {
            "Baseline_Category": "Classical Local Feature Descriptors",
            "Specific_Method": "SIFT / ORB / RootSIFT + Bag-of-Visual-Words (BoVW) or VLAD",
            "Included_in_Project": "NO",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Historical benchmark for texture and microstructure retrieval prior to deep learning.",
            "Expected_Reviewer_Demand": "MEDIUM (Expected by classical computer vision reviewers)",
            "Absence_Threatens_Conclusion": "LOW",
            "Reviewer_Critique": "Reviewers might ask if DINOv2 is superior to classical SIFT. Prior literature (e.g. Oquab et al., 2023) thoroughly establishes DINOv2 superiority over SIFT/BoVW for semantic retrieval.",
            "Recommended_Priority": "P2 (Document as prior art; optional supplementary experiment)"
        },
        {
            "Baseline_Category": "Generic Pretrained Supervised CNN",
            "Specific_Method": "ResNet-50 (ImageNet-1k supervised pretraining)",
            "Included_in_Project": "NO",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Standard baseline to show advantage of self-supervised ViT over supervised CNNs.",
            "Expected_Reviewer_Demand": "HIGH (Reviewer A will likely request ResNet-50 comparison)",
            "Absence_Threatens_Conclusion": "MEDIUM",
            "Reviewer_Critique": "Common reviewer question: 'Does DINOv2 outperform a simple ImageNet-pretrained ResNet-50 on microscopy?' Adding ResNet-50 would strengthen claim of DINOv2 foundation suitability.",
            "Recommended_Priority": "P1 (Recommended additional validation for journal submission)"
        },
        {
            "Baseline_Category": "Alternative Self-Supervised Models",
            "Specific_Method": "MAE (Masked Autoencoder) / SimCLR v2 / DINO v1",
            "Included_in_Project": "NO",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Comparative evaluation across SSL paradigms (generative vs contrastive vs self-distillation).",
            "Expected_Reviewer_Demand": "MEDIUM",
            "Absence_Threatens_Conclusion": "LOW",
            "Reviewer_Critique": "DINOv2 is widely recognized as the strongest general-purpose self-supervised vision model; omitting MAE is acceptable if properly cited.",
            "Recommended_Priority": "P2 (Discuss in Related Work)"
        },
        {
            "Baseline_Category": "Vision-Language Multimodal Model",
            "Specific_Method": "CLIP ViT-B/16 or BioCLIP",
            "Included_in_Project": "NO",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Evaluates text-aligned embeddings against pure vision self-distillation.",
            "Expected_Reviewer_Demand": "MEDIUM (Trendy baseline in 2024-2026)",
            "Absence_Threatens_Conclusion": "LOW",
            "Reviewer_Critique": "CLIP models suffer on microscopy because training captions rarely describe electron optical parameters (kV, dwell time, detector).",
            "Recommended_Priority": "P2 (Discuss in Related Work why CLIP is unsuited for raw SEM physics)"
        },
        {
            "Baseline_Category": "Microscopy-Specific Foundation Models",
            "Specific_Method": "Microscopy foundation models (e.g., MicroVary, BioMedCLIP, or EMRIS)",
            "Included_in_Project": "NO",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Specialized domain models trained on cellular/biological or materials imaging.",
            "Expected_Reviewer_Demand": "HIGH (Materials informatics reviewers will ask about domain models)",
            "Absence_Threatens_Conclusion": "MEDIUM",
            "Reviewer_Critique": "Most existing microscopy models are biological (fluorescence/optical), not SEM metallurgy. The manuscript must explicitly justify why DINOv2 was chosen over biological models.",
            "Recommended_Priority": "P1 (Clarify domain discrepancy in Related Work)"
        },
        {
            "Baseline_Category": "End-to-End Metric Learning",
            "Specific_Method": "Full fine-tuning of ViT backbone with Triplet / SupCon loss",
            "Included_in_Project": "NO (Intentionally frozen backbone + linear adapter)",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Comparison between lightweight post-hoc adapter vs expensive full-network fine-tuning.",
            "Expected_Reviewer_Demand": "MEDIUM",
            "Absence_Threatens_Conclusion": "LOW",
            "Reviewer_Critique": "Freezing the 22M parameter backbone and training only a 384x384 linear projection head is an intentional efficiency decision to avoid catastrophic forgetting and overfitting on N=384 train images.",
            "Recommended_Priority": "P2 (Highlight efficiency and anti-overfitting rationale in Methodology)"
        },
        {
            "Baseline_Category": "Deep Multimodal Metadata Fusion",
            "Specific_Method": "Cross-Attention Transformer / Feature Concatenation MLP",
            "Included_in_Project": "NO (Only Gower distance late fusion evaluated)",
            "Observed_Performance": "NOT EVALUATED",
            "Reviewer_Relevance": "Tests whether non-linear or deep metadata fusion could succeed where late linear fusion failed.",
            "Expected_Reviewer_Demand": "HIGH (Reviewer B will question whether negative result is an artifact of simple late fusion)",
            "Absence_Threatens_Conclusion": "HIGH (Directly affects RQ3 interpretation)",
            "Reviewer_Critique": "Reviewer objection: 'You concluded metadata does not help, but you only tested late linear fusion of Gower distance. What if you used an early fusion MLP or cross-attention?'",
            "Recommended_Priority": "P1 (Critical: Explicitly bound RQ3 conclusion to late linear fusion)"
        }
    ]

    out_file = Path("reports/phase11/PHASE11_BASELINE_AUDIT.csv")
    fieldnames = [
        "Baseline_Category", "Specific_Method", "Included_in_Project",
        "Observed_Performance", "Reviewer_Relevance", "Expected_Reviewer_Demand",
        "Absence_Threatens_Conclusion", "Reviewer_Critique", "Recommended_Priority"
    ]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"PHASE11_BASELINE_AUDIT.csv written with {len(rows)} baseline categories audited.")


if __name__ == "__main__":
    main()
