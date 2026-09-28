"""Quickstart Example: Load DINOv2 Features and Search with FAISS."""
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
