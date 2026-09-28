"""Generate Phase 11 PHASE11_CLAIM_STRESS_TEST.csv."""

import csv
from pathlib import Path


def main():
    claims = [
        {
            "Claim_ID": "CLM_01",
            "Claim": "DINOv2 foundation visual features outperform perceptual hashing by over 95% Recall@1 on scientific SEM micrographs.",
            "Location": "Abstract, Section 4.1",
            "Evidence": "Phase 2 baseline retrieval benchmark comparing DINOv2 vs pHash and dHash.",
            "Artifact": "artifacts/phase5/metrics/phase5_results.json; reports/phase2/tables/retrieval_hcci.csv",
            "Metric": "Recall@1: 0.9819 (DINOv2) vs 0.0210 (pHash)",
            "Dataset": "HCCI SEM (774 images)",
            "Direct_Evidence": "YES",
            "Threat": "Tested on single metallurgical dataset; does not cover biological or optical microscopy.",
            "Severity": "LOW",
            "Assessment": "SUPPORTED",
            "Required_Action": "Bound claim explicitly to SEM microscopy of metallic/crystalline materials."
        },
        {
            "Claim_ID": "CLM_02",
            "Claim": "Supervised contrastive acquisition adaptation reduces cross-instrument domain shift by 68.15%.",
            "Location": "Abstract, Section 4.2",
            "Evidence": "Phase 4 multi-seed linear adapter training on multi-instrument HCCI splits.",
            "Artifact": "data/processed/phase4/metrics/phase4_evaluation_results.json",
            "Metric": "Gap reduced from 0.1994 to 0.0635 (68.15% reduction, p = 1.42e-12)",
            "Dataset": "HCCI SEM (Helios Train, VEGA3 Val, Zeiss Test)",
            "Direct_Evidence": "YES",
            "Threat": "Pairing is defined by specimen-condition metadata rather than same-physical-ROI tracking.",
            "Severity": "MEDIUM",
            "Assessment": "SUPPORTED",
            "Required_Action": "Explicitly state that adaptation targets condition-level invariance across specimens."
        },
        {
            "Claim_ID": "CLM_03",
            "Claim": "Adapted representations generalize to unseen electron microscopes with statistically significant precision improvements.",
            "Location": "Abstract, Section 4.2",
            "Evidence": "Held-out Zeiss GeminiSEM test split evaluated with frozen adapter weights.",
            "Artifact": "reports/phase7/tables/table_held_out_zeiss_results.csv",
            "Metric": "Precision@5 improved from 0.8708 to 0.9053 (p = 0.0028, Cohen d = 0.65)",
            "Dataset": "HCCI SEM (Zeiss Gemini held-out test split, N=212)",
            "Direct_Evidence": "YES",
            "Threat": "Only a single unseen microscope model is evaluated in the held-out test split.",
            "Severity": "MEDIUM",
            "Assessment": "PARTIALLY_SUPPORTED",
            "Required_Action": "Clarify that generalization is demonstrated on one held-out field-emission instrument."
        },
        {
            "Claim_ID": "CLM_04",
            "Claim": "Late fusion of instrument metadata provides zero empirical benefit over strong visual representations alone.",
            "Location": "Abstract, Section 4.3",
            "Evidence": "Phase 5 grid ablation of fusion weight alpha from 0.0 to 1.0.",
            "Artifact": "reports/phase5/tables/table_main_test_results.csv; artifacts/phase5/metrics/phase5_results.json",
            "Metric": "Delta Recall@1 = 0.0000; optimal validation weight alpha* = 1.0",
            "Dataset": "HCCI SEM (Held-out Zeiss Test split, N=212)",
            "Direct_Evidence": "YES",
            "Threat": "Negative result could be specific to late linear fusion and Gower distance formulation.",
            "Severity": "HIGH",
            "Assessment": "SUPPORTED",
            "Required_Action": "Ensure wording clarifies that late linear fusion adds no value; do not claim all possible multimodal fusion fails."
        },
        {
            "Claim_ID": "CLM_05",
            "Claim": "The 4-stage duplicate detection cascade achieves 0.9998 AUROC with zero false positives on scientific micrographs.",
            "Location": "Section 4.4",
            "Evidence": "Controlled synthetic duplicate benchmark with 7 transformation families.",
            "Artifact": "reports/phase6/PHASE6_REPORT.md; artifacts/phase6/phase6_results.json",
            "Metric": "AUROC = 0.9998, AUPRC = 0.9999, FPR = 0.0000 on N=245 synthetic pairs",
            "Dataset": "Synthetic Duplicate Benchmark (derived from HCCI Train split)",
            "Direct_Evidence": "YES (on Synthetic Benchmark)",
            "Threat": "Synthetic transformations (affine, cropping, brightness) may not capture physical specimen duplication.",
            "Severity": "MEDIUM",
            "Assessment": "PARTIALLY_SUPPORTED",
            "Required_Action": "Explicitly distinguish synthetic benchmark verification from natural repository screening."
        },
        {
            "Claim_ID": "CLM_06",
            "Claim": "The repository contains zero natural duplicate micrographs under the declared cascade.",
            "Location": "Section 4.4, Section 5",
            "Evidence": "Full-corpus pairwise cascade execution on all 774 HCCI physical images.",
            "Artifact": "artifacts/phase6/redundancy_summary.parquet; artifacts/phase6/duplicate_pairs.parquet",
            "Metric": "769 clusters: 764 singletons + 5 pairs of near-duplicates (769 KEEP, 5 REVIEW)",
            "Dataset": "HCCI SEM (Full Corpus, N=774)",
            "Direct_Evidence": "YES",
            "Threat": "Does not prove global uniqueness across all microscopy worldwide.",
            "Severity": "LOW",
            "Assessment": "SUPPORTED",
            "Required_Action": "Maintain precise wording: 'no detected redundancy under the declared cascade within the HCCI corpus'."
        },
        {
            "Claim_ID": "CLM_07",
            "Claim": "Image-derived quality indicators reliably detect physical microscopy degradation with 0.8803 AUROC.",
            "Location": "Section 4.4",
            "Evidence": "Controlled synthetic degradation benchmark across 5 physical artifact families.",
            "Artifact": "reports/phase6/PHASE6_REPORT.md; artifacts/phase6/quality_anomaly_results.json",
            "Metric": "Overall AUROC = 0.8803, AUPRC = 0.9618 (N=120: 20 nominal, 100 degraded)",
            "Dataset": "Synthetic Quality Benchmark",
            "Direct_Evidence": "YES",
            "Threat": "Degradations are synthetically generated; beam damage detection failed (AUROC ~ 0.50).",
            "Severity": "MEDIUM",
            "Assessment": "PARTIALLY_SUPPORTED",
            "Required_Action": "Emphasize that indicators are image-derived screening heuristics, not calibrated physical sensor measurements."
        },
        {
            "Claim_ID": "CLM_08",
            "Claim": "The platform framework detects out-of-distribution scientific anomalies in microscopy repositories.",
            "Location": "Abstract, Section 1, Section 6",
            "Evidence": "Novelty score evaluation on Carinthia semiconductor dataset and synthetic outliers.",
            "Artifact": "artifacts/phase6/phase6_results.json",
            "Metric": "Synthetic outlier AUROC = 0.8412; Carinthia mean cosine distance shift > 0.65",
            "Dataset": "Carinthia SEM (N=4,591) vs HCCI SEM (N=774)",
            "Direct_Evidence": "NO (Measures Domain Shift & Embedding Outliers)",
            "Threat": "Conflating cross-corpus domain shift (metallurgy vs semiconductor) with scientific anomaly detection.",
            "Severity": "HIGH",
            "Assessment": "OVERSTATED",
            "Required_Action": "Replace 'scientific anomaly detection' with 'relative embedding-space novelty screening and domain shift characterization'."
        },
        {
            "Claim_ID": "CLM_09",
            "Claim": "FAISS HNSW vector indexing provides 1.99x speedup over exact brute-force search with 1.000 recall agreement.",
            "Location": "Section 4.5",
            "Evidence": "Vector indexing benchmark on combined HCCI + Carinthia corpus (5,365 embeddings).",
            "Artifact": "reports/phase3/PHASE3_REPORT.md; artifacts/phase10/reproduction_runs/faiss_benchmark.json",
            "Metric": "Latency reduced from 0.7348 ms to 0.3691 ms; 1-recall@10 = 1.0000",
            "Dataset": "Combined HCCI and Carinthia embeddings (N=5,365)",
            "Direct_Evidence": "YES",
            "Threat": "Corpus of 5,365 vectors is small for FAISS; HNSW advantage is modest at this scale.",
            "Severity": "LOW",
            "Assessment": "SUPPORTED",
            "Required_Action": "Acknowledge that exact IndexFlatIP is already highly efficient at N=5k; HNSW benefits will scale asymptotically."
        },
        {
            "Claim_ID": "CLM_10",
            "Claim": "The platform provides complete containerized reproducibility via Docker.",
            "Location": "Section 4.6, Release docs",
            "Evidence": "Dockerfile and docker-compose.yml configuration files present in repository.",
            "Artifact": "Dockerfile; docker-compose.yml; platform/docker/Dockerfile.backend",
            "Metric": "Status: DOCKER_VALIDATION_NOT_EXECUTED",
            "Dataset": "Platform codebase",
            "Direct_Evidence": "NO (Runtime not executed)",
            "Threat": "Docker engine was unavailable; live multi-container deployment was not verified during audit.",
            "Severity": "MEDIUM",
            "Assessment": "DOCUMENTATION_ONLY",
            "Required_Action": "Maintain honest classification: containerized configuration is provided but unverified at runtime."
        }
    ]

    out_file = Path("reports/phase11/PHASE11_CLAIM_STRESS_TEST.csv")
    fieldnames = [
        "Claim_ID", "Claim", "Location", "Evidence", "Artifact", "Metric",
        "Dataset", "Direct_Evidence", "Threat", "Severity", "Assessment", "Required_Action"
    ]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(claims)

    print(f"PHASE11_CLAIM_STRESS_TEST.csv written with {len(claims)} claims stress-tested.")


if __name__ == "__main__":
    main()
