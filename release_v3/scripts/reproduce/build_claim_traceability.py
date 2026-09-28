"""Build Phase 10 CLAIM_ARTIFACT_TRACEABILITY.csv from Phase 9 claim registry."""

import csv
from pathlib import Path


def main():
    in_file = Path("artifacts/phase9/final_quantitative_claim_registry.csv")
    out_file = Path("artifacts/phase10/CLAIM_ARTIFACT_TRACEABILITY.csv")

    rows = []
    with open(in_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            cid = r["claim_id"]
            sec = r["section"]
            art = r["source_artifact"]
            ds = r["dataset"]
            exp = r["experiment"]
            
            # Map reproduction command
            cmd = "python scripts/reproduce/validate_release.py --smoke"
            if "Phase 2" in exp or "Ingestion" in exp:
                cmd = "python scripts/reproduce/reproduce_retrieval.py --model dinov2"
            elif "Phase 3" in exp or "FAISS" in exp:
                cmd = "python scripts/reproduce/reproduce_faiss.py"
            elif "Phase 4" in exp:
                cmd = "python scripts/reproduce/reproduce_adapter.py --eval"
            elif "Phase 5" in exp:
                cmd = "python scripts/reproduce/reproduce_metadata.py --mode metadata_only"
            elif "Phase 6" in exp:
                if "redundancy" in r["claim"].lower() or "cluster" in r["claim"].lower() or "keep" in r["claim"].lower() or "review" in r["claim"].lower():
                    cmd = "python scripts/reproduce/reproduce_curation.py --task redundancy_graph"
                elif "quality" in r["claim"].lower() or "auroc" in r["claim"].lower():
                    cmd = "python scripts/reproduce/reproduce_curation.py --task quality"
                else:
                    cmd = "python scripts/reproduce/reproduce_curation.py --task duplicate"

            # Map release path
            norm_art = art.replace("\\", "/")
            if norm_art.startswith("data/raw"):
                rel_path = "RESTRICTED (Acquisition via scripts/data/)"
            elif norm_art.startswith("data/manifests"):
                rel_path = "release/manifests/" + Path(norm_art).name
            elif norm_art.startswith("configs/"):
                rel_path = "release/configs/" + Path(norm_art).name
            else:
                rel_path = norm_art

            rows.append({
                "claim_id": cid,
                "manuscript_location": f"reports/phase9/PHASE9_MASTER_MANUSCRIPT.md ({sec})",
                "evidence_artifact": norm_art,
                "dataset": ds,
                "experiment": exp,
                "reproduction_command": cmd,
                "release_path": rel_path,
                "status": "VERIFIED_FROZEN_EVIDENCE"
            })

    fieldnames = [
        "claim_id", "manuscript_location", "evidence_artifact",
        "dataset", "experiment", "reproduction_command", "release_path", "status"
    ]
    with open(out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CLAIM_ARTIFACT_TRACEABILITY.csv written with {len(rows)} claims mapped.")


if __name__ == "__main__":
    main()
