"""CLI subcommands for Phase 2 DINOv2 representation baseline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional
import click
import yaml

from src.evaluation.evaluator import Phase2Evaluator
from src.representation.analyzer import EmbeddingDistributionAnalyzer
from src.representation.dinov2_encoder import DINOv2Encoder
from src.representation.extractor import EmbeddingExtractor
from src.representation.validator import EmbeddingValidator


@click.group(name="phase2", help="Phase 2 DINOv2 visual representation baseline commands.")
def phase2_group() -> None:
    pass


@phase2_group.command(name="environment", help="Inspect and report runtime environment, torch, device, and DINOv2 model.")
@click.option("--config", default="configs/phase2.yaml", help="Path to Phase 2 configuration.")
def show_environment(config: str) -> None:
    try:
        with open(config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        model_name = cfg.get("model", {}).get("name", "dinov2_vits14")
        click.echo("=" * 80)
        click.echo("PHASE 2 DINOv2 RUNTIME ENVIRONMENT INSPECTION")
        click.echo("=" * 80)

        encoder = DINOv2Encoder(model_name=model_name)
        info = encoder.get_model_info()

        for k, v in info.items():
            click.echo(f"  {k:<24}: {v}")
        click.echo("=" * 80)
        click.echo("Model loaded and parameters frozen successfully.")
    except Exception as e:
        click.echo(f"Error inspecting Phase 2 environment: {e}", err=True)


@phase2_group.command(name="extract", help="Extract DINOv2 representations for registered datasets with checkpoint/resume.")
@click.option("--dataset", "dataset_id", default=None, help="Optional specific dataset (hcci or carinthia). Default: all.")
@click.option("--limit", default=None, type=int, help="Optional limit for rapid testing.")
@click.option("--config", default="configs/phase2.yaml", help="Path to Phase 2 configuration.")
def extract_embeddings(dataset_id: Optional[str], limit: Optional[int], config: str) -> None:
    try:
        extractor = EmbeddingExtractor(config_path=config)
        datasets = [dataset_id] if dataset_id else extractor.config.get("datasets", ["hcci", "carinthia"])

        for ds in datasets:
            click.echo(f"\n--- Extracting embeddings for dataset: {ds} ---")
            res = extractor.extract_dataset(dataset_id=ds, limit=limit)
            click.echo(f"  Extracted: {res['successful_embeddings']} / {res['total_images']} (failed: {res['failed_images']})")
            click.echo(f"  Elapsed:   {res['elapsed_seconds']:.2f}s ({res['images_per_second']:.2f} images/sec)")
            click.echo(f"  Saved to:  {res['output_path']}")

        master_path = extractor.update_master_manifest()
        click.echo(f"\nMaster embedding manifest updated: {master_path}")
    except Exception as e:
        click.echo(f"Error extracting embeddings: {e}", err=True)


@phase2_group.command(name="validate", help="Validate numerical integrity and L2 norm constraints of extracted embeddings.")
@click.option("--config", default="configs/phase2.yaml", help="Path to Phase 2 configuration.")
def validate_embeddings(config: str) -> None:
    try:
        with open(config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
        emb_dir = Path(cfg.get("embedding", {}).get("storage_dir", "data/processed/embeddings"))
        dim = int(cfg.get("model", {}).get("expected_embedding_dimension", 384))

        results = []
        for emb_file in sorted(emb_dir.glob("*_embeddings.parquet")):
            # Look up manifest to get expected count
            ds_name = emb_file.stem.split("_")[0]
            manifest_file = Path(f"data/manifests/{ds_name}_manifest.parquet")
            import pandas as pd
            expected = len(pd.read_parquet(manifest_file)) if manifest_file.is_file() else len(pd.read_parquet(emb_file))

            res = EmbeddingValidator.validate_dataset_embeddings(
                emb_file, expected_count=expected, expected_dimension=dim, check_normalized=True
            )
            results.append(res)
            click.echo(f"Dataset '{res['dataset']}': status={res['validation_status']}, valid={res['successful_count']}/{res['expected_count']}, NaNs={res['nan_count']}, Infs={res['inf_count']}, norm={res['mean_norm']}±{res['std_norm']}")

        rep_path = EmbeddingValidator.save_validation_report(results)
        click.echo(f"\nSaved embedding validation report to: {rep_path}")
    except Exception as e:
        click.echo(f"Error validating embeddings: {e}", err=True)


@phase2_group.command(name="analyze", help="Analyze embedding distributions, cosine similarity, and generate PCA figures.")
@click.option("--config", default="configs/phase2.yaml", help="Path to Phase 2 configuration.")
def analyze_embeddings(config: str) -> None:
    try:
        analyzer = EmbeddingDistributionAnalyzer()
        hcci_p = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
        car_p = Path("data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet")

        if not hcci_p.is_file() or not car_p.is_file():
            click.echo("Both HCCI and Carinthia embeddings must be extracted before analysis.", err=True)
            return

        click.echo("Loading embedding matrices...")
        hcci_mat, _, _ = analyzer.load_matrix(hcci_p)
        car_mat, _, _ = analyzer.load_matrix(car_p)

        click.echo(f"Computing distribution statistics (HCCI: {len(hcci_mat)}, Carinthia: {len(car_mat)})...")
        stats = analyzer.compute_distribution_statistics(hcci_mat, car_mat)
        click.echo(f"  Within HCCI cosine similarity:      {stats['hcci_within_cosine_similarity']['mean']:.4f} ± {stats['hcci_within_cosine_similarity']['std']:.4f}")
        click.echo(f"  Within Carinthia cosine similarity: {stats['carinthia_within_cosine_similarity']['mean']:.4f} ± {stats['carinthia_within_cosine_similarity']['std']:.4f}")
        click.echo(f"  Cross-dataset cosine similarity:    {stats['cross_dataset_cosine_similarity']['mean']:.4f} ± {stats['cross_dataset_cosine_similarity']['std']:.4f}")

        click.echo("Generating research figures in reports/phase2/figures/...")
        figs = analyzer.generate_research_plots(hcci_mat, car_mat)
        for f in figs:
            click.echo(f"  Figure saved: {f}")
    except Exception as e:
        click.echo(f"Error during embedding analysis: {e}", err=True)


@phase2_group.command(name="evaluate", help="Execute zero-shot retrieval benchmarks with strict anti-leakage controls.")
def evaluate_retrieval() -> None:
    try:
        evaluator = Phase2Evaluator()
        hcci_p = Path("data/processed/embeddings/hcci_dinov2_vits14_embeddings.parquet")
        car_p = Path("data/processed/embeddings/carinthia_dinov2_vits14_embeddings.parquet")

        if not hcci_p.is_file() or not car_p.is_file():
            click.echo("Both HCCI and Carinthia embeddings must be extracted before evaluation.", err=True)
            return

        click.echo("=" * 80)
        click.echo("RUNNING ZERO-SHOT RETRIEVAL BENCHMARKS (NO FAISS)")
        click.echo("=" * 80)

        # 1. HCCI Evaluation
        hcci_res = evaluator.evaluate_hcci(hcci_p)
        h_sum = hcci_res["summary"]
        click.echo("\nHCCI Condition-Invariance Retrieval (Same-Specimen):")
        click.echo(f"  Evaluated Queries: {h_sum['evaluated_queries']} / {h_sum['total_queries']} (No positive queries: {h_sum['no_valid_positive_queries']})")
        click.echo(f"  Recall@1:          {h_sum['recall_at_1']:.4f}")
        click.echo(f"  Recall@5:          {h_sum['recall_at_5']:.4f}")
        click.echo(f"  Recall@10:         {h_sum['recall_at_10']:.4f}")
        click.echo(f"  MRR:               {h_sum['mrr']:.4f}")
        click.echo(f"  Precision@5:       {h_sum['precision_at_5']:.4f}")

        # 2. Carinthia Evaluation
        car_res = evaluator.evaluate_carinthia(car_p)
        c_sum = car_res["summary"]
        click.echo("\nCarinthia Defect Class Retrieval (6 defect classes):")
        click.echo(f"  Evaluated Queries: {c_sum['evaluated_queries']} / {c_sum['total_queries']}")
        click.echo(f"  Recall@1:          {c_sum['recall_at_1']:.4f}")
        click.echo(f"  Recall@5:          {c_sum['recall_at_5']:.4f}")
        click.echo(f"  Recall@10:         {c_sum['recall_at_10']:.4f}")
        click.echo(f"  MRR:               {c_sum['mrr']:.4f}")
        click.echo(f"  Precision@5:       {c_sum['precision_at_5']:.4f}")

        click.echo("\nRetrieval benchmark tables exported to reports/phase2/tables/")
    except Exception as e:
        click.echo(f"Error during retrieval evaluation: {e}", err=True)


@phase2_group.command(name="report", help="Generate the comprehensive Phase 2 baseline report.")
def generate_report() -> None:
    try:
        from scripts.generate_phase2_report import create_phase2_report
        out_p = create_phase2_report()
        click.echo(f"Phase 2 baseline report generated at: {out_p}")
    except Exception as e:
        click.echo(f"Error generating report: {e}", err=True)
