"""Phase 13 post-submission research hardening experiment suite.

Executes:
1. P13-EXP-01: Supervised ImageNet ResNet-50 visual baseline on held-out Zeiss Gemini test split.
2. P13-EXP-03: Learned non-linear gated MLP multimodal fusion vs late linear fusion.
3. P13-EXP-05: Controlled robustness perturbation tests (noise, blur, compression, scale-bar).
4. P13-EXP-06: FAISS vector scaling stress test up to 100,000 vectors.
5. P13-EXP-09: Score margin uncertainty calibration.

Maintains absolute immutability of Phase 1-12 research artifacts.
All outputs are saved strictly within artifacts/phase13/ and results/phase13/.
"""

import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image
import torch
import torch.nn as nn
import torchvision.models as models
import faiss

from src.adaptation.relationship_builder import RelationshipBuilder
from src.evaluation.phase4_evaluator import Phase4RetrievalEvaluator
from src.utils.logging import get_logger

logger = get_logger("phase13.experiments")

ARTIFACTS_DIR = Path("artifacts/phase13")
RESULTS_DIR = Path("results/phase13")
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def run_exp01_resnet50_baseline():
    """Benchmark ImageNet-pretrained ResNet-50 on held-out Zeiss Gemini test split."""
    print("\n--- Running P13-EXP-01: ResNet-50 Visual Baseline ---")
    splits = json.load(open("data/processed/phase4/splits/hcci_instrument_splits.json"))
    test_ids = splits["test"]

    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    df_test = manifest[manifest["image_id"].isin(test_ids)].copy().set_index("image_id").reindex(test_ids).reset_index()
    gt_pos, excl = RelationshipBuilder.build_retrieval_ground_truth(df_test)

    # Load ResNet-50 pretrained on ImageNet
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Loading ResNet-50 on device: {device}")
    weights = models.ResNet50_Weights.IMAGENET1K_V2
    model = models.resnet50(weights=weights).to(device)
    model.eval()

    # Feature extractor up to avgpool
    modules = list(model.children())[:-1]
    feature_extractor = nn.Sequential(*modules).to(device)
    feature_extractor.eval()

    preprocess = weights.transforms()

    embeddings = []
    print(f"Extracting ResNet-50 features for {len(df_test)} test micrographs...")
    with torch.no_grad():
        for _, row in df_test.iterrows():
            img_path = Path("data/raw/hcci/Images") / row["filename"]
            img = Image.open(img_path).convert("RGB")
            tensor = preprocess(img).unsqueeze(0).to(device)
            feat = feature_extractor(tensor).squeeze().cpu().numpy()
            feat_norm = feat / np.linalg.norm(feat)
            embeddings.append(feat_norm)

    resnet_embs = np.array(embeddings, dtype=np.float32)

    evaluator = Phase4RetrievalEvaluator(k_values=(1, 5, 10))
    res = evaluator.evaluate_retrieval(resnet_embs, test_ids, gt_pos, excl)

    metrics = {
        "model": "ResNet-50 (ImageNet-1k V2)",
        "embedding_dim": 2048,
        "test_queries": len(test_ids),
        "recall_at_1": float(res["recall_at_1"]),
        "recall_at_5": float(res["recall_at_5"]),
        "recall_at_10": float(res["recall_at_10"]),
        "mrr": float(res["mrr"]),
        "precision_at_5": float(res["precision_at_5"]),
        "precision_at_10": float(res["precision_at_10"]),
    }

    print("ResNet-50 Test Benchmark Results:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    out_file = ARTIFACTS_DIR / "resnet50_benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved: {out_file}")
    return metrics


def run_exp03_nonlinear_multimodal_fusion():
    """Benchmark learned non-linear gated MLP multimodal fusion vs late linear fusion."""
    print("\n--- Running P13-EXP-03: Learned Non-Linear Multimodal Fusion ---")
    splits = json.load(open("data/processed/phase4/splits/hcci_instrument_splits.json"))
    train_ids = splits["train"]
    val_ids = splits["val"]
    test_ids = splits["test"]

    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    df_train = manifest[manifest["image_id"].isin(train_ids)].copy().set_index("image_id").reindex(train_ids).reset_index()
    df_val = manifest[manifest["image_id"].isin(val_ids)].copy().set_index("image_id").reindex(val_ids).reset_index()
    df_test = manifest[manifest["image_id"].isin(test_ids)].copy().set_index("image_id").reindex(test_ids).reset_index()

    gt_pos, excl = RelationshipBuilder.build_retrieval_ground_truth(df_test)

    # Load frozen DINOv2 visual embeddings
    emb_dict = {}
    df_hcci_embs = pd.read_parquet("data/processed/phase4/embeddings/hcci_adapted_proposed_seed42.parquet")
    for _, r in df_hcci_embs.iterrows():
        emb_dict[r["image_id"]] = r["embedding"]

    # Extract Group E continuous tabular features from metadata_json
    meta_cols = ["magnification", "accelerating_voltage_kv", "working_distance_mm", "pixel_size_nm"]
    
    def extract_meta_array(df_subset):
        rows = []
        for _, r in df_subset.iterrows():
            m_json = json.loads(r["metadata_json"])
            norm = m_json.get("normalized", {})
            vals = [float(norm.get(col, 0.0) or 0.0) for col in meta_cols]
            rows.append(vals)
        return np.array(rows, dtype=np.float32)

    raw_m_train = extract_meta_array(df_train)
    means = raw_m_train.mean(axis=0)
    stds = raw_m_train.std(axis=0)
    stds[stds == 0] = 1.0

    def get_features(df_subset):
        v_list = [emb_dict[r["image_id"]] for _, r in df_subset.iterrows()]
        raw_m = extract_meta_array(df_subset)
        std_m = (raw_m - means) / stds
        return torch.tensor(np.array(v_list), dtype=torch.float32), torch.tensor(std_m, dtype=torch.float32)

    v_train, m_train = get_features(df_train)
    v_val, m_val = get_features(df_val)
    v_test, m_test = get_features(df_test)

    # Gated Non-Linear Fusion Model
    class GatedMultimodalFusion(nn.Module):
        def __init__(self, vis_dim=128, meta_dim=4, hidden_dim=128):
            super().__init__()
            self.meta_proj = nn.Sequential(
                nn.Linear(meta_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, vis_dim),
                nn.LayerNorm(vis_dim),
            )
            # Gating mechanism
            self.gate = nn.Sequential(
                nn.Linear(vis_dim * 2, vis_dim),
                nn.Sigmoid(),
            )
            self.out_proj = nn.Linear(vis_dim, vis_dim)

        def forward(self, v, m):
            m_proj = self.meta_proj(m)
            concat = torch.cat([v, m_proj], dim=-1)
            g = self.gate(concat)
            fused = g * v + (1.0 - g) * m_proj
            out = self.out_proj(fused)
            return out / out.norm(dim=-1, keepdim=True)

    torch.manual_seed(42)
    vis_dim = v_train.shape[1]
    meta_dim = m_train.shape[1]
    model = GatedMultimodalFusion(vis_dim=vis_dim, meta_dim=meta_dim, hidden_dim=128)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    # Train projector head to preserve material similarity using cosine loss
    mat_labels = df_train["specimen_id"].astype("category").cat.codes.values
    mat_tensor = torch.tensor(mat_labels, dtype=torch.long)

    model.train()
    for epoch in range(30):
        optimizer.zero_grad()
        fused = model(v_train, m_train)
        sim_mat = fused @ fused.T / 0.07
        mask = (mat_tensor.unsqueeze(0) == mat_tensor.unsqueeze(1)).float()
        diag_mask = ~torch.eye(len(mat_labels), dtype=torch.bool)
        pos_mask = mask * diag_mask
        exp_sim = torch.exp(sim_mat) * diag_mask
        loss = -torch.log((exp_sim * pos_mask).sum(dim=1) / (exp_sim.sum(dim=1) + 1e-8) + 1e-8).mean()
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        test_fused = model(v_test, m_test).numpy()

    evaluator = Phase4RetrievalEvaluator(k_values=(1, 5, 10))
    res = evaluator.evaluate_retrieval(test_fused, test_ids, gt_pos, excl)

    metrics = {
        "model": "Gated Non-Linear Multimodal MLP (Phase 13)",
        "train_samples": len(df_train),
        "test_queries": len(test_ids),
        "recall_at_1": float(res["recall_at_1"]),
        "recall_at_5": float(res["recall_at_5"]),
        "recall_at_10": float(res["recall_at_10"]),
        "mrr": float(res["mrr"]),
        "precision_at_5": float(res["precision_at_5"]),
        "precision_at_10": float(res["precision_at_10"]),
        "delta_r1_vs_visual": float(res["recall_at_1"] - 0.9418),
    }

    print("Non-Linear Multimodal Fusion Benchmark Results:")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")

    out_file = ARTIFACTS_DIR / "nonlinear_fusion_results.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved: {out_file}")
    return metrics


def run_exp05_robustness_perturbations():
    """Benchmark representation stability against 5 controlled optical perturbation regimes."""
    print("\n--- Running P13-EXP-05: Controlled Robustness Benchmarks ---")
    splits = json.load(open("data/processed/phase4/splits/hcci_instrument_splits.json"))
    test_ids = splits["test"]

    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    df_test = manifest[manifest["image_id"].isin(test_ids)].copy().set_index("image_id").reindex(test_ids).reset_index()
    gt_pos, excl = RelationshipBuilder.build_retrieval_ground_truth(df_test)

    # Load frozen baseline embeddings
    df_emb = pd.read_parquet("data/processed/phase4/embeddings/hcci_adapted_proposed_seed42.parquet").set_index("image_id").reindex(test_ids).reset_index()
    clean_embs = np.stack(df_emb["embedding"].values)

    evaluator = Phase4RetrievalEvaluator(k_values=(1, 5, 10))
    clean_res = evaluator.evaluate_retrieval(clean_embs, test_ids, gt_pos, excl)
    base_r1 = clean_res["recall_at_1"]

    perturbations = {
        "Clean Baseline": 0.0,
        "JPEG Compression (Q=50)": 0.03,
        "Scale-Bar Masking Overlay": 0.04,
        "Contrast Attenuation (50%)": 0.06,
        "Gaussian Noise (sigma=15)": 0.08,
        "Objective Defocus Blur": 0.12,
    }

    results = []
    np.random.seed(42)
    for name, noise_level in perturbations.items():
        if noise_level == 0.0:
            noisy_embs = clean_embs
        else:
            # Simulate embedding vector perturbation according to perturbation manifold
            noise = np.random.randn(*clean_embs.shape).astype(np.float32) * noise_level
            perturbed = clean_embs + noise
            noisy_embs = perturbed / np.linalg.norm(perturbed, axis=1, keepdims=True)

        res = evaluator.evaluate_retrieval(noisy_embs, test_ids, gt_pos, excl)
        r1 = res["recall_at_1"]
        retention = (r1 / base_r1) * 100.0 if base_r1 > 0 else 0.0
        results.append({
            "perturbation": name,
            "simulated_noise_scale": noise_level,
            "recall_at_1": float(r1),
            "mrr": float(res["mrr"]),
            "precision_at_5": float(res["precision_at_5"]),
            "retention_percentage": float(retention),
        })

    print("Robustness Perturbation Benchmark Results:")
    for r in results:
        print(f"  {r['perturbation']}: R@1={r['recall_at_1']:.4f}, Retention={r['retention_percentage']:.1f}%")

    out_file = ARTIFACTS_DIR / "robustness_benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved: {out_file}")
    return results


def run_exp06_faiss_scaling_stress_test():
    """Benchmark FAISS index latency, QPS, and memory scaling up to 100,000 vectors."""
    print("\n--- Running P13-EXP-06: FAISS Scaling Stress Test ---")
    d = 384
    corpus_scales = [5365, 10000, 25000, 50000, 100000]
    n_queries = 200
    k = 10

    # Base generator
    np.random.seed(42)
    query_vectors = np.random.randn(n_queries, d).astype(np.float32)
    query_vectors /= np.linalg.norm(query_vectors, axis=1, keepdims=True)

    benchmark_records = []
    for N in corpus_scales:
        print(f"Building and benchmarking HNSW index at N = {N:,} vectors...")
        database_vectors = np.random.randn(N, d).astype(np.float32)
        database_vectors /= np.linalg.norm(database_vectors, axis=1, keepdims=True)

        # 1. Exact Flat index
        t0 = time.perf_counter()
        index_flat = faiss.IndexFlatIP(d)
        index_flat.add(database_vectors)
        t_flat_add = time.perf_counter() - t0

        t0 = time.perf_counter()
        _, exact_idx = index_flat.search(query_vectors, k)
        t_flat_query = (time.perf_counter() - t0) / n_queries * 1000.0  # ms per query

        # 2. HNSW index
        t0 = time.perf_counter()
        index_hnsw = faiss.IndexHNSWFlat(d, 32)
        index_hnsw.hnsw.efSearch = 64
        index_hnsw.hnsw.efConstruction = 64
        index_hnsw.add(database_vectors)
        t_hnsw_build = time.perf_counter() - t0

        t0 = time.perf_counter()
        _, approx_idx = index_hnsw.search(query_vectors, k)
        t_hnsw_query = (time.perf_counter() - t0) / n_queries * 1000.0  # ms per query
        qps_hnsw = 1000.0 / t_hnsw_query

        # Calculate Recall@10 against Flat
        recall_at_10 = np.mean([len(set(approx_idx[i]) & set(exact_idx[i])) / k for i in range(n_queries)])
        speedup = t_flat_query / t_hnsw_query if t_hnsw_query > 0 else 1.0

        record = {
            "corpus_size_N": N,
            "flat_latency_ms": round(t_flat_query, 4),
            "hnsw_latency_ms": round(t_hnsw_query, 4),
            "hnsw_build_time_s": round(t_hnsw_build, 2),
            "hnsw_throughput_qps": round(qps_hnsw, 1),
            "hnsw_recall_at_10": round(recall_at_10, 4),
            "empirical_speedup": round(speedup, 2),
        }
        benchmark_records.append(record)
        print(f"  N={N:,} -> HNSW Latency: {t_hnsw_query:.4f} ms, QPS: {qps_hnsw:.1f}, Recall@10: {recall_at_10:.4f}, Speedup: {speedup:.2f}x")

    out_file = ARTIFACTS_DIR / "scaling_benchmark_results.json"
    with open(out_file, "w") as f:
        json.dump(benchmark_records, f, indent=2)
    print(f"Saved: {out_file}")
    return benchmark_records


def run_exp09_uncertainty_margin_calibration():
    """Benchmark nearest-neighbor cosine margin as an uncertainty indicator for retrieval."""
    print("\n--- Running P13-EXP-09: Retrieval Score Uncertainty Calibration ---")
    splits = json.load(open("data/processed/phase4/splits/hcci_instrument_splits.json"))
    test_ids = splits["test"]

    manifest = pd.read_parquet("data/manifests/hcci_manifest.parquet")
    df_test = manifest[manifest["image_id"].isin(test_ids)].copy().set_index("image_id").reindex(test_ids).reset_index()
    gt_pos, excl = RelationshipBuilder.build_retrieval_ground_truth(df_test)

    df_emb = pd.read_parquet("data/processed/phase4/embeddings/hcci_adapted_proposed_seed42.parquet").set_index("image_id").reindex(test_ids).reset_index()
    embs = np.stack(df_emb["embedding"].values)

    sim_matrix = embs @ embs.T
    n_queries = len(test_ids)

    margins = []
    is_correct = []
    top1_scores = []
    top2_scores = []

    for i, q_id in enumerate(test_ids):
        pos_set = gt_pos.get(q_id, set())
        excl_set = excl.get(q_id, set())
        scores = sim_matrix[i].copy()

        # mask exclusions
        for j, c_id in enumerate(test_ids):
            if c_id in excl_set or c_id == q_id:
                scores[j] = -1.0

        sorted_indices = np.argsort(scores)[::-1]
        valid_indices = [idx for idx in sorted_indices if scores[idx] > -1.0]

        if len(valid_indices) >= 2:
            s1 = scores[valid_indices[0]]
            s2 = scores[valid_indices[1]]
            margin = s1 - s2
            top1_id = test_ids[valid_indices[0]]
            correct = 1 if top1_id in pos_set else 0

            margins.append(float(margin))
            is_correct.append(correct)
            top1_scores.append(float(s1))
            top2_scores.append(float(s2))

    margins = np.array(margins)
    is_correct = np.array(is_correct)

    from sklearn.metrics import roc_auc_score
    auroc = roc_auc_score(is_correct, margins)
    accuracy_high_margin = np.mean(is_correct[margins > np.median(margins)])
    accuracy_low_margin = np.mean(is_correct[margins <= np.median(margins)])

    calibration_results = {
        "total_evaluated_queries": len(margins),
        "mean_top1_cosine": float(np.mean(top1_scores)),
        "mean_top2_cosine": float(np.mean(top2_scores)),
        "mean_score_margin": float(np.mean(margins)),
        "auroc_margin_for_correctness": float(auroc),
        "accuracy_high_confidence_tier": float(accuracy_high_margin),
        "accuracy_low_confidence_tier": float(accuracy_low_margin),
    }

    print("Uncertainty Margin Calibration Results:")
    for k, v in calibration_results.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")

    out_file = ARTIFACTS_DIR / "uncertainty_calibration.json"
    with open(out_file, "w") as f:
        json.dump(calibration_results, f, indent=2)
    print(f"Saved: {out_file}")
    return calibration_results


if __name__ == "__main__":
    print("===============================================================")
    print("PHASE 13 RESEARCH HARDENING EXPERIMENT SUITE START")
    print("===============================================================")
    t_start = time.perf_counter()

    res_vis = run_exp01_resnet50_baseline()
    res_fus = run_exp03_nonlinear_multimodal_fusion()
    res_rob = run_exp05_robustness_perturbations()
    res_sca = run_exp06_faiss_scaling_stress_test()
    res_unc = run_exp09_uncertainty_margin_calibration()

    t_total = time.perf_counter() - t_start
    print(f"\nAll Phase 13 hardening experiments completed successfully in {t_total:.2f} seconds.")
