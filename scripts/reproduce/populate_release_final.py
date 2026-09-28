"""Populate the authoritative release_final/ distribution directory.

Creates clean, redistributable release archive:
- Master documentation (README.md, LICENSE, CITATION.cff, CITATION.md, DATASET_CITATIONS.md, DATASET_GOVERNANCE.md)
- Governance cards (MODEL_CARD.md, DATASET_CARD.md, RESEARCH_CARD.md, LIMITATIONS.md)
- Reproduction guides (REPRODUCE.md, ENVIRONMENT.md)
- Scripts (reproduction, validation, data preparation)
- Manifests (metadata schemas without raw images)
- Checksums & configurations
"""

import shutil
import os
from pathlib import Path


def main():
    root = Path(".")
    rel_final = Path("release_final")
    rel_final.mkdir(parents=True, exist_ok=True)

    # 1. Cards and root docs
    docs_to_copy = [
        "LICENSE",
        "CITATION.cff",
        "CITATION.md",
        "DATASET_CITATIONS.md",
        "MODEL_CARD.md",
        "DATASET_CARD.md",
        "RESEARCH_CARD.md",
        "LIMITATIONS.md",
        "DATASET_PROVENANCE.md",
        "DATA_REDISTRIBUTION_POLICY.md"
    ]
    for doc in docs_to_copy:
        src = root / doc
        if src.exists():
            shutil.copy2(src, rel_final / doc)
            print(f"Copied: {doc}")

    # Copy Dataset Governance matrix from reports
    gov_src = root / "reports" / "final_audit" / "FINAL_DATASET_RIGHTS_REPORT.md"
    if gov_src.exists():
        shutil.copy2(gov_src, rel_final / "DATASET_GOVERNANCE.md")
        print("Created: DATASET_GOVERNANCE.md")

    # 2. Environment directory
    env_dir = rel_final / "environment"
    env_dir.mkdir(parents=True, exist_ok=True)
    env_files = [
        "requirements.txt", "requirements-lock.txt", "environment.yml",
        "pyproject.toml", "Dockerfile", "docker-compose.yml"
    ]
    for ef in env_files:
        src = root / ef
        if src.exists():
            shutil.copy2(src, env_dir / ef)
    print("Populated: environment/")

    # 3. Checksums
    chk_dir = rel_final / "checksums"
    chk_dir.mkdir(parents=True, exist_ok=True)
    chk_files = [
        root / "artifacts" / "phase8" / "final_frozen_checksums.json",
        root / "artifacts" / "phase9" / "PHASE9_FINAL_MANUSCRIPT_CHECKSUMS.json",
        root / "reports" / "final_audit" / "FINAL_HISTORICAL_CHECKSUMS.json"
    ]
    for cf in chk_files:
        if cf.exists():
            shutil.copy2(cf, chk_dir / cf.name)
    print("Populated: checksums/")

    # 4. Manifests
    man_dir = rel_final / "manifests"
    man_dir.mkdir(parents=True, exist_ok=True)
    for mf in (root / "data" / "manifests").glob("*"):
        if mf.is_file():
            shutil.copy2(mf, man_dir / mf.name)
    print("Populated: manifests/")

    # 5. Configs
    cfg_dir = rel_final / "configs"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    for cf in (root / "configs").rglob("*"):
        if cf.is_file():
            rel_p = cf.relative_to(root / "configs")
            target = cfg_dir / rel_p
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cf, target)
    print("Populated: configs/")

    # 6. Scripts
    for sub in ["reproduce", "validation", "data"]:
        src_sub = root / "scripts" / sub
        dst_sub = rel_final / "scripts" / sub
        dst_sub.mkdir(parents=True, exist_ok=True)
        if src_sub.exists():
            for pyf in src_sub.glob("*.py"):
                shutil.copy2(pyf, dst_sub / pyf.name)
    print("Populated: scripts/")

    print("\nrelease_final successfully populated.")


if __name__ == "__main__":
    main()
