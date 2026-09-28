"""Generate Phase 11 PHASE11_RQ_COVERAGE.csv."""

import csv
from pathlib import Path


def main():
    rows = [
        {
            "RQ": "RQ1",
            "Hypothesis": "H1: Frozen DINOv2 visual features significantly outperform classical perceptual hashes for SEM image retrieval.",
            "Experiment": "EXP_RET_B0 to EXP_RET_B3",
            "Dataset": "HCCI SEM (774 physical images)",
            "Protocol": "Full-corpus query retrieval (774 leave-one-out queries against gallery of 773 images).",
            "Metric": "Recall@1, Recall@5, MRR, Precision@5",
            "Observed_Evidence": "DINOv2 achieves R@1=0.9819, MRR=0.9894 vs pHash R@1=0.0210, MRR=0.0489, dHash R@1=0.0180, random R@1=0.0013.",
            "Statistical_Evidence": "Recall@1 difference +0.9609 over pHash; paired differences non-overlapping bootstrap CI [0.9716, 0.9910].",
            "Directly_Answered": "YES",
            "Partially_Answered": "NO",
            "Evidence_Gap": "Evaluated on single metallurgical material system (HCCI); does not evaluate broader non-SEM scientific domains.",
            "Recommended_Action": "Bound claim to electron microscopy of crystalline/metallurgical materials rather than all scientific microscopy."
        },
        {
            "RQ": "RQ2",
            "Hypothesis": "H2: Supervised contrastive acquisition adaptation compresses the cross-instrument embedding gap without degrading visual discrimination.",
            "Experiment": "EXP_RET_B4, EXP_ACQ_ROB",
            "Dataset": "HCCI SEM (Train: Helios/PFIB, Val: VEGA3, Test: Zeiss Gemini)",
            "Protocol": "Cross-instrument held-out partition; SupCon loss with neutral exclusion of identical condition pairs.",
            "Metric": "Within-condition cosine, cross-condition cosine, gap reduction (%), held-out Zeiss Precision@5",
            "Observed_Evidence": "Gap compressed from 0.1994 to 0.0635 (68.15% reduction). Held-out Zeiss P@5 improved from 0.8708 to 0.9053.",
            "Statistical_Evidence": "Paired t-test t=9.48, p=1.42e-12 (gap reduction); Zeiss test paired t=3.04, p=0.0028, Cohen d=0.65.",
            "Directly_Answered": "YES",
            "Partially_Answered": "NO",
            "Evidence_Gap": "Adaptation relies on same-specimen/different-instrument pairs defined by material class; lack of same-physical-ROI ground truth.",
            "Recommended_Action": "Explicitly document in limitations that adaptation operates at specimen-condition level, not micron-scale identical ROI tracking."
        },
        {
            "RQ": "RQ3",
            "Hypothesis": "H3: Combining normalized scientific metadata with visual features via late fusion improves retrieval over visual features alone.",
            "Experiment": "EXP_RET_B5, EXP_RET_B6, EXP_META_ABL",
            "Dataset": "HCCI SEM (Held-out Zeiss Test split, N=212 queries)",
            "Protocol": "Continuous/categorical Gower distance normalization; calibrated spline late fusion over alpha in [0.0, 1.0].",
            "Metric": "Recall@1, Recall@5, MRR, Delta R@1 over visual baseline",
            "Observed_Evidence": "Metadata-only MRR=0.3443 (R@1=0.3349). Late fusion yields Delta R@1=0.0000; optimal validation alpha*=1.0.",
            "Statistical_Evidence": "Empirical delta is exactly 0.0 across all cross-validation folds. Hypothesis H3 is formally NOT SUPPORTED.",
            "Directly_Answered": "YES (Negative Result)",
            "Partially_Answered": "NO",
            "Evidence_Gap": "Only evaluates coarse late linear score fusion; does not evaluate cross-attention or deep multimodal projection architectures.",
            "Recommended_Action": "Frame explicitly as a rigorous negative result: late fusion of instrument metadata is dominated by strong visual features."
        },
        {
            "RQ": "RQ4",
            "Hypothesis": "H4: Multi-stage perceptual cascades and image-derived quality indicators reliably detect duplicate, redundant, and degraded micrographs.",
            "Experiment": "EXP_DUP_SYN, EXP_RED_NAT, EXP_QUAL_SYN",
            "Dataset": "HCCI SEM (774 natural images) + Controlled Synthetic Benchmark (N=245 duplicates, N=120 quality degradations)",
            "Protocol": "4-stage duplicate cascade (pHash -> DINO -> adapted -> SSIM); composite quality risk over 6 indicators.",
            "Metric": "Duplicate AUROC/AUPRC, False Positive Rate, Natural cluster partition, Quality AUROC/AUPRC",
            "Observed_Evidence": "Synthetic duplicate AUROC=0.9998 (FPR=0.0). Natural HCCI: 769 clusters (764 singletons, 5 pairs). Quality AUROC=0.8803, AUPRC=0.9618.",
            "Statistical_Evidence": "Quality risk bootstrap 95% CI [0.8124, 0.9351]; duplicate benchmark achieves 0 false positives on N=245.",
            "Directly_Answered": "PARTIALLY",
            "Partially_Answered": "YES",
            "Evidence_Gap": "Evaluated primarily on synthetic corruptions and transformations; lacks expert human-annotated natural defect ground truth.",
            "Recommended_Action": "Clarify that duplicate detection is verified on synthetic transforms and natural screening is descriptive candidate triage."
        },
        {
            "RQ": "RQ5",
            "Hypothesis": "H5: Deep representations and novelty estimators detect out-of-distribution defects and cross-corpus distribution shifts.",
            "Experiment": "EXP_NOV_OUT, EXP_DOM_SHFT",
            "Dataset": "HCCI SEM (Metallurgy) vs Carinthia SEM (Semiconductor Defect, N=4,591)",
            "Protocol": "Train isolation forest / k-NN estimators on nominal HCCI; evaluate novelty scores on Carinthia cross-corpus images.",
            "Metric": "Novelty score distribution, separation distance, AUROC on synthetic outliers (N=120)",
            "Observed_Evidence": "Synthetic outlier AUROC=0.8412. Carinthia exhibits extreme domain shift (mean cosine distance > 0.65 from HCCI centroid).",
            "Statistical_Evidence": "Carinthia novelty score distribution statistically distinct from HCCI test distribution (Kolmogorov-Smirnov p < 1e-15).",
            "Directly_Answered": "PARTIALLY",
            "Partially_Answered": "YES",
            "Evidence_Gap": "Cross-corpus shift between metallurgy and semiconductor is massive; does not test subtle intra-domain physical defect anomalies.",
            "Recommended_Action": "Distinguish between coarse cross-corpus domain shift and fine-grained scientific anomaly detection. Avoid 'confirmed anomaly' claims."
        },
        {
            "RQ": "RQ6",
            "Hypothesis": "H6: Combining redundancy graphs with risk-prioritized review queues reduces manual curation effort without missing degraded images.",
            "Experiment": "EXP_REV_QUE",
            "Dataset": "Synthetic triage simulation (N=120 mixed quality) + Natural HCCI review queue simulation",
            "Protocol": "Rank images by composite risk; simulate curation budget thresholds (top-10%, top-20%, top-50%).",
            "Metric": "Precision@k, Recall@k, Triage efficiency, Representative retention rate",
            "Observed_Evidence": "Top-10 triage captures 100% of severe synthetic corruptions (Precision@10=1.0000). Natural queue partitions 769 KEEP vs 5 REVIEW.",
            "Statistical_Evidence": "Simulation demonstrates 80% reduction in manual inspection burden on synthetic benchmark with zero missed critical failures.",
            "Directly_Answered": "YES",
            "Partially_Answered": "NO",
            "Evidence_Gap": "Tested via computational simulation; lacks a formal user study with practicing microscopists measuring real-time workflow latency.",
            "Recommended_Action": "State that curation acceleration is demonstrated via computational budget simulation rather than human-in-the-loop user study."
        },
        {
            "RQ": "RQ7",
            "Hypothesis": "H7: An explicit experiment registry and cryptographic artifact ledger enable complete, deterministic reproducibility of all benchmark claims.",
            "Experiment": "EXP_REP_AUD",
            "Dataset": "All 110 frozen research artifacts + 17 manuscript chapters + 18 registered experiments",
            "Protocol": "Deterministic re-execution of checksums, manifests, FAISS indices, and metrics evaluation via validate_release.py CLI.",
            "Metric": "Cryptographic bit-for-bit parity pass rate, test suite pass rate (218 tests)",
            "Observed_Evidence": "110/110 research artifacts verified byte-for-byte identical; 17/17 manuscript chapters verified; 218/218 automated tests passed.",
            "Statistical_Evidence": "100% cryptographic parity across all evaluation metrics and tables. Overall release validation CLI returned PASSED.",
            "Directly_Answered": "YES",
            "Partially_Answered": "NO",
            "Evidence_Gap": "Docker daemon validation was not executed due to host service availability; containerized reproducibility remains unverified.",
            "Recommended_Action": "Acknowledge host-level Python 3.11 reproducibility is fully verified while containerized Docker execution is documented but unexecuted."
        }
    ]

    out_file = Path("reports/phase11/PHASE11_RQ_COVERAGE.csv")
    fieldnames = [
        "RQ", "Hypothesis", "Experiment", "Dataset", "Protocol", "Metric",
        "Observed_Evidence", "Statistical_Evidence", "Directly_Answered",
        "Partially_Answered", "Evidence_Gap", "Recommended_Action"
    ]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"PHASE11_RQ_COVERAGE.csv written with {len(rows)} research questions analyzed.")


if __name__ == "__main__":
    main()
