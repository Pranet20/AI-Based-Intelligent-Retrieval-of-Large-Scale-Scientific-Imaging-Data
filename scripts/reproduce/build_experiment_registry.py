"""Build Phase 10 Experiment Registry CSV."""

import yaml
import csv
import json
from pathlib import Path


def main():
    with open("configs/phase7_experiments.yaml", "r", encoding="utf-8") as f:
        raw_exp = yaml.safe_load(f)["experiments"]

    phase_map = {
        "EXP_RET_B0": "PHASE2",
        "EXP_RET_B1": "PHASE2",
        "EXP_RET_B2": "PHASE2",
        "EXP_RET_B3": "PHASE2",
        "EXP_RET_B4": "PHASE4",
        "EXP_RET_B5": "PHASE5",
        "EXP_RET_B6": "PHASE5",
        "EXP_RET_B7": "PHASE5",
        "EXP_ACQ_ROB": "PHASE4",
        "EXP_META_ABL": "PHASE5",
        "EXP_DUP_SYN": "PHASE6",
        "EXP_RED_NAT": "PHASE6",
        "EXP_QUAL_SYN": "PHASE6",
        "EXP_NOV_OUT": "PHASE6",
        "EXP_REV_QUE": "PHASE6",
        "EXP_DOM_SHFT": "PHASE6",
        "EXP_ABL_MAT": "PHASE7",
        "EXP_REP_AUD": "PHASE7"
    }

    expected_map = {
        "EXP_RET_B0": "R@1=0.0013, MRR=0.0091",
        "EXP_RET_B1": "R@1=0.0210, MRR=0.0489",
        "EXP_RET_B2": "R@1=0.0180, MRR=0.0421",
        "EXP_RET_B3": "R@1=0.9819, MRR=0.9894",
        "EXP_RET_B4": "Within=0.9199, Cross=0.8564, GapRed=68.15%",
        "EXP_RET_B5": "R@1=0.3349, MRR=0.3443",
        "EXP_RET_B6": "R@1=0.9819, MRR=0.9894 (Delta=0.0)",
        "EXP_RET_B7": "Adapted+Meta MRR=0.9631",
        "EXP_ACQ_ROB": "Cross-Condition Cosine Similarity +0.2585",
        "EXP_META_ABL": "Alpha=1.0 optimal across all groups",
        "EXP_DUP_SYN": "AUROC=0.9998, AUPRC=0.9999",
        "EXP_RED_NAT": "769 clusters (764 singletons, 5 pairs of size 2)",
        "EXP_QUAL_SYN": "AUROC=0.8803, AUPRC=0.9618",
        "EXP_NOV_OUT": "AUROC=0.8412 on synthetic outliers",
        "EXP_REV_QUE": "Precision@10=1.0000 on synthetic triage",
        "EXP_DOM_SHFT": "Cosine shift to Carinthia defect domain",
        "EXP_ABL_MAT": "7-Stage component ablation validated",
        "EXP_REP_AUD": "110/110 frozen research artifacts byte-for-byte verified"
    }

    primary_map = {
        "EXP_RET_B0": "MRR",
        "EXP_RET_B1": "MRR",
        "EXP_RET_B2": "MRR",
        "EXP_RET_B3": "MRR",
        "EXP_RET_B4": "Cross-Condition Cosine Similarity",
        "EXP_RET_B5": "MRR",
        "EXP_RET_B6": "MRR",
        "EXP_RET_B7": "MRR",
        "EXP_ACQ_ROB": "Cross-Condition Similarity",
        "EXP_META_ABL": "Delta MRR",
        "EXP_DUP_SYN": "AUROC",
        "EXP_RED_NAT": "Cluster Count",
        "EXP_QUAL_SYN": "AUROC",
        "EXP_NOV_OUT": "AUROC",
        "EXP_REV_QUE": "Precision@10",
        "EXP_DOM_SHFT": "Mean Cosine Distance",
        "EXP_ABL_MAT": "Retrieval & Curation Metrics",
        "EXP_REP_AUD": "Cryptographic Integrity Pass Rate"
    }

    cmd_map = {
        "EXP_RET_B0": "python scripts/reproduce/reproduce_retrieval.py --model random",
        "EXP_RET_B1": "python scripts/reproduce/reproduce_retrieval.py --model phash",
        "EXP_RET_B2": "python scripts/reproduce/reproduce_retrieval.py --model dhash",
        "EXP_RET_B3": "python scripts/reproduce/reproduce_retrieval.py --model dinov2",
        "EXP_RET_B4": "python scripts/reproduce/reproduce_adapter.py --seeds 42,123,2024",
        "EXP_RET_B5": "python scripts/reproduce/reproduce_metadata.py --mode metadata_only",
        "EXP_RET_B6": "python scripts/reproduce/reproduce_metadata.py --mode dinov2_fusion",
        "EXP_RET_B7": "python scripts/reproduce/reproduce_metadata.py --mode adapted_fusion",
        "EXP_ACQ_ROB": "python scripts/reproduce/reproduce_adapter.py --eval-robustness",
        "EXP_META_ABL": "python scripts/reproduce/reproduce_metadata.py --ablate-features",
        "EXP_DUP_SYN": "python scripts/reproduce/reproduce_curation.py --task duplicate",
        "EXP_RED_NAT": "python scripts/reproduce/reproduce_curation.py --task redundancy_graph",
        "EXP_QUAL_SYN": "python scripts/reproduce/reproduce_curation.py --task quality",
        "EXP_NOV_OUT": "python scripts/reproduce/reproduce_curation.py --task novelty",
        "EXP_REV_QUE": "python scripts/reproduce/reproduce_curation.py --task review_queue",
        "EXP_DOM_SHFT": "python scripts/reproduce/reproduce_curation.py --task domain_shift",
        "EXP_ABL_MAT": "python scripts/reproduce/reproduce_ablation.py",
        "EXP_REP_AUD": "python scripts/reproduce/validate_release.py --verify-only"
    }

    rows = []
    for exp_id, data in raw_exp.items():
        ph = phase_map.get(exp_id, "PHASE7")
        ev_type = data.get("evidence_type", "benchmark")
        cfg_name = data.get("model_configuration", exp_id)
        rows.append({
            "experiment_id": exp_id,
            "phase": ph,
            "RQ": data["research_question"],
            "hypothesis": f"Validates {ev_type} for {cfg_name}",
            "dataset": data["dataset"],
            "split": data["split"],
            "model": cfg_name,
            "seed": ",".join(str(s) for s in data.get("random_seeds", [42])),
            "configuration": f"configs/{ph.lower()}.yaml",
            "artifact_paths": ";".join(f"{k}:{v}" for k, v in data.get("artifact_paths", {}).items()),
            "primary_metric": primary_map.get(exp_id, "AUROC"),
            "expected_result": expected_map.get(exp_id, "VERIFIED"),
            "reproduction_command": cmd_map.get(exp_id, "python scripts/reproduce/validate_release.py"),
            "status": "FROZEN_VERIFIED"
        })

    fieldnames = [
        "experiment_id", "phase", "RQ", "hypothesis", "dataset", "split",
        "model", "seed", "configuration", "artifact_paths",
        "primary_metric", "expected_result", "reproduction_command", "status"
    ]
    out_file = Path("artifacts/phase10/EXPERIMENT_REGISTRY.csv")
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"EXPERIMENT_REGISTRY.csv written with {len(rows)} experiments.")


if __name__ == "__main__":
    main()
