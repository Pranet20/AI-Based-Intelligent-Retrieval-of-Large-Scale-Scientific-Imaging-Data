"""Embedding distribution analysis and exploratory visualization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA


class EmbeddingDistributionAnalyzer:
    """Analyzes visual embedding geometry, cosine similarity distributions, and PCA projections."""

    def __init__(self, figures_dir: str | Path = "reports/phase2/figures") -> None:
        self.figures_dir = Path(figures_dir)
        self.figures_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_matrix(embeddings_path: str | Path) -> Tuple[np.ndarray, List[str], List[str]]:
        """Load embeddings as (N, D) float32 matrix, with image_ids and labels."""
        df = pd.read_parquet(embeddings_path)
        matrix = np.vstack(df["embedding"].to_numpy()).astype(np.float32)
        image_ids = df["image_id"].tolist()
        labels = df["label"].fillna("Unknown").tolist()
        return matrix, image_ids, labels

    def compute_distribution_statistics(
        self,
        hcci_matrix: np.ndarray,
        carinthia_matrix: np.ndarray,
        sample_pairs: int = 5000,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Compute per-dimension statistics and within/cross-dataset cosine similarity distributions."""
        rng = np.random.default_rng(seed)

        def get_sampled_similarities(mat_a: np.ndarray, mat_b: np.ndarray, n_pairs: int) -> np.ndarray:
            idx_a = rng.integers(0, len(mat_a), size=n_pairs)
            idx_b = rng.integers(0, len(mat_b), size=n_pairs)
            # Dot product of L2 normalized vectors is cosine similarity
            sims = np.sum(mat_a[idx_a] * mat_b[idx_b], axis=1)
            return sims

        # Within-dataset similarities
        hcci_sims = get_sampled_similarities(hcci_matrix, hcci_matrix, sample_pairs)
        carinthia_sims = get_sampled_similarities(carinthia_matrix, carinthia_matrix, sample_pairs)
        # Cross-dataset similarities
        cross_sims = get_sampled_similarities(hcci_matrix, carinthia_matrix, sample_pairs)

        stats = {
            "embedding_dimension": int(hcci_matrix.shape[1]),
            "hcci_samples": int(len(hcci_matrix)),
            "carinthia_samples": int(len(carinthia_matrix)),
            "hcci_within_cosine_similarity": {
                "mean": float(np.mean(hcci_sims)),
                "std": float(np.std(hcci_sims)),
                "min": float(np.min(hcci_sims)),
                "max": float(np.max(hcci_sims)),
                "median": float(np.median(hcci_sims)),
            },
            "carinthia_within_cosine_similarity": {
                "mean": float(np.mean(carinthia_sims)),
                "std": float(np.std(carinthia_sims)),
                "min": float(np.min(carinthia_sims)),
                "max": float(np.max(carinthia_sims)),
                "median": float(np.median(carinthia_sims)),
            },
            "cross_dataset_cosine_similarity": {
                "mean": float(np.mean(cross_sims)),
                "std": float(np.std(cross_sims)),
                "min": float(np.min(cross_sims)),
                "max": float(np.max(cross_sims)),
                "median": float(np.median(cross_sims)),
            },
        }

        # Save JSON
        json_path = Path("reports/phase2/embedding_statistics.json")
        json_path.parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

        # Save per-dimension CSV
        per_dim_df = pd.DataFrame({
            "dimension": list(range(hcci_matrix.shape[1])),
            "hcci_mean": np.mean(hcci_matrix, axis=0),
            "hcci_std": np.std(hcci_matrix, axis=0),
            "carinthia_mean": np.mean(carinthia_matrix, axis=0),
            "carinthia_std": np.std(carinthia_matrix, axis=0),
        })
        per_dim_df.to_csv("reports/phase2/embedding_statistics.csv", index=False)

        return stats

    def generate_research_plots(
        self,
        hcci_matrix: np.ndarray,
        carinthia_matrix: np.ndarray,
        sample_pairs: int = 5000,
        seed: int = 42,
    ) -> List[Path]:
        """Generate exploratory diagnostic figures without manual editing."""
        rng = np.random.default_rng(seed)
        generated_figures = []

        # 1. Embedding Norm Distribution
        hcci_norms = np.linalg.norm(hcci_matrix, axis=1)
        car_norms = np.linalg.norm(carinthia_matrix, axis=1)
        range_min = float(min(np.min(hcci_norms), np.min(car_norms))) - 0.05
        range_max = float(max(np.max(hcci_norms), np.max(car_norms))) + 0.05
        plt.figure(figsize=(7, 4), dpi=150)
        plt.hist(hcci_norms, bins=30, range=(range_min, range_max), alpha=0.6, label="HCCI Norms", color="#1f77b4")
        plt.hist(car_norms, bins=30, range=(range_min, range_max), alpha=0.6, label="Carinthia Norms", color="#ff7f0e")
        plt.title("Plot 1: Pretrained DINOv2 Embedding Norm Distribution (L2)")
        plt.xlabel(r"Vector Norm $\|v\|_2$")
        plt.ylabel("Frequency")
        plt.legend()
        plt.tight_layout()
        p1 = self.figures_dir / "embedding_norm_distribution.png"
        plt.savefig(p1)
        plt.close()
        generated_figures.append(p1)

        # 2. PCA HCCI
        pca_hcci = PCA(n_components=2, random_state=seed)
        hcci_pca = pca_hcci.fit_transform(hcci_matrix)

        plt.figure(figsize=(6, 5), dpi=150)
        plt.scatter(hcci_pca[:, 0], hcci_pca[:, 1], c="#1f77b4", alpha=0.6, s=15)
        plt.title(f"Plot 2: HCCI DINOv2 PCA (Var Expl: {pca_hcci.explained_variance_ratio_.sum():.1%})")
        plt.xlabel("Principal Component 1")
        plt.ylabel("Principal Component 2")
        plt.tight_layout()
        p2 = self.figures_dir / "pca_hcci.png"
        plt.savefig(p2)
        plt.close()
        generated_figures.append(p2)

        # 3. PCA Carinthia
        pca_car = PCA(n_components=2, random_state=seed)
        car_pca = pca_car.fit_transform(carinthia_matrix)

        plt.figure(figsize=(6, 5), dpi=150)
        plt.scatter(car_pca[:, 0], car_pca[:, 1], c="#ff7f0e", alpha=0.5, s=10)
        plt.title(f"Plot 3: Carinthia DINOv2 PCA (Var Expl: {pca_car.explained_variance_ratio_.sum():.1%})")
        plt.xlabel("Principal Component 1")
        plt.ylabel("Principal Component 2")
        plt.tight_layout()
        p3 = self.figures_dir / "pca_carinthia.png"
        plt.savefig(p3)
        plt.close()
        generated_figures.append(p3)

        # 4. Combined HCCI + Carinthia PCA
        combined_matrix = np.vstack([hcci_matrix, carinthia_matrix])
        pca_comb = PCA(n_components=2, random_state=seed)
        comb_pca = pca_comb.fit_transform(combined_matrix)

        plt.figure(figsize=(7, 5), dpi=150)
        plt.scatter(
            comb_pca[:len(hcci_matrix), 0],
            comb_pca[:len(hcci_matrix), 1],
            c="#1f77b4",
            alpha=0.6,
            s=15,
            label="HCCI (Metallurgy)",
        )
        plt.scatter(
            comb_pca[len(hcci_matrix):, 0],
            comb_pca[len(hcci_matrix):, 1],
            c="#ff7f0e",
            alpha=0.3,
            s=10,
            label="Carinthia (Semiconductor)",
        )
        plt.title("Plot 4: 2D PCA projection of combined HCCI and Carinthia embeddings.")
        plt.xlabel("Principal Component 1")
        plt.ylabel("Principal Component 2")
        plt.legend()
        plt.tight_layout()
        p4 = self.figures_dir / "pca_combined.png"
        plt.savefig(p4)
        plt.close()
        generated_figures.append(p4)

        # 5. Cosine Similarity Distribution
        idx_h_a = rng.integers(0, len(hcci_matrix), size=sample_pairs)
        idx_h_b = rng.integers(0, len(hcci_matrix), size=sample_pairs)
        h_sims = np.sum(hcci_matrix[idx_h_a] * hcci_matrix[idx_h_b], axis=1)

        idx_c_a = rng.integers(0, len(carinthia_matrix), size=sample_pairs)
        idx_c_b = rng.integers(0, len(carinthia_matrix), size=sample_pairs)
        c_sims = np.sum(carinthia_matrix[idx_c_a] * carinthia_matrix[idx_c_b], axis=1)

        cross_sims = np.sum(hcci_matrix[idx_h_a] * carinthia_matrix[idx_c_b], axis=1)

        plt.figure(figsize=(7, 4), dpi=150)
        plt.hist(h_sims, bins=40, density=True, alpha=0.5, label="Within HCCI", color="#1f77b4")
        plt.hist(c_sims, bins=40, density=True, alpha=0.5, label="Within Carinthia", color="#ff7f0e")
        plt.hist(cross_sims, bins=40, density=True, alpha=0.5, label="Cross-Dataset (HCCI ↔ Carinthia)", color="#2ca02c")
        plt.title("Plot 5: Sampled Cosine Similarity Density")
        plt.xlabel("Cosine Similarity")
        plt.ylabel("Probability Density")
        plt.legend()
        plt.tight_layout()
        p5 = self.figures_dir / "cosine_similarity_distribution.png"
        plt.savefig(p5)
        plt.close()
        generated_figures.append(p5)

        return generated_figures
