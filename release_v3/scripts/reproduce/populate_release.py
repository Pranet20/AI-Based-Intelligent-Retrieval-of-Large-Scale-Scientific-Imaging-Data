"""Script to populate the release/ distribution directory."""

import shutil
import os
from pathlib import Path


def main():
    release_root = Path("release")
    release_root.mkdir(parents=True, exist_ok=True)

    # 1. Root documentation to release/
    root_files = [
        "README.md", "LICENSE", "CITATION.cff", "CITATION.md",
        "DATASET_CITATIONS.md", "REPRODUCE.md"
    ]
    for rf in root_files:
        src = Path(rf)
        if src.exists():
            shutil.copy2(src, release_root / rf)

    # 2. Environment files
    env_dir = release_root / "environment"
    env_dir.mkdir(parents=True, exist_ok=True)
    env_files = [
        "requirements.txt", "requirements-lock.txt", "environment.yml",
        "pyproject.toml", "Dockerfile", "docker-compose.yml"
    ]
    for ef in env_files:
        src = Path(ef)
        if src.exists():
            shutil.copy2(src, env_dir / ef)

    # 3. Scripts
    for sub in ["data", "validation", "reproduce"]:
        s_src = Path("scripts") / sub
        s_dst = release_root / "scripts" / sub
        s_dst.mkdir(parents=True, exist_ok=True)
        if s_src.exists():
            for pyf in s_src.glob("*.py"):
                shutil.copy2(pyf, s_dst / pyf.name)

    # 4. Manifests
    man_dst = release_root / "manifests"
    man_dst.mkdir(parents=True, exist_ok=True)
    man_files = [
        "data/manifests/hcci_manifest.parquet",
        "data/manifests/hcci_manifest.csv",
        "data/manifests/carinthia_manifest.parquet"
    ]
    for mf in man_files:
        src = Path(mf)
        if src.exists():
            shutil.copy2(src, man_dst / src.name)

    # 5. Documentation
    doc_dst = release_root / "documentation"
    doc_dst.mkdir(parents=True, exist_ok=True)
    doc_files = [
        "DATASET_PROVENANCE.md", "DATA_REDISTRIBUTION_POLICY.md",
        "ENVIRONMENT_SPECIFICATION.md", "PLATFORM_REPRODUCTION.md",
        "DATA_AVAILABILITY_STATEMENT.md", "SOFTWARE_LICENSE.md"
    ]
    for df in doc_files:
        src = Path("reports/phase10") / df
        if src.exists():
            shutil.copy2(src, doc_dst / df)

    # 6. Examples
    ex_dst = release_root / "examples"
    ex_dst.mkdir(parents=True, exist_ok=True)
    ex_script = """\"\"\"Quickstart Example: Load DINOv2 Features and Search with FAISS.\"\"\"
import pandas as pd
import numpy as np
import faiss

def main():
    print("Loading pre-extracted embeddings...")
    emb_path = "data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet"
    df = pd.read_parquet(emb_path)
    vectors = np.stack(df["embedding"].values).astype(np.float32)
    print(f"Loaded {vectors.shape[0]} embeddings of dimension {vectors.shape[1]}.")

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    # Query with the first vector
    query = vectors[:1]
    distances, indices = index.search(query, k=5)
    print("Top 5 Image Indices:", indices[0])
    print("Top 5 Cosine Similarities:", distances[0])

if __name__ == "__main__":
    main()
"""
    with open(ex_dst / "quickstart_search.py", "w", encoding="utf-8") as f:
        f.write(ex_script)

    print("Release directory populated successfully.")


if __name__ == "__main__":
    main()
