"""CLI commands for Phase 3 FAISS scalable vector retrieval."""

from __future__ import annotations

from pathlib import Path
import click
import yaml

from src.retrieval.benchmark import FAISSLatencyBenchmark
from src.retrieval.evaluator import Phase3RetrievalEvaluator
from src.retrieval.faiss_index import FAISSVectorIndex, IndexType


@click.group(name="phase3", help="Phase 3: FAISS Scalable Vector Retrieval commands.")
def phase3_group() -> None:
    """Phase 3 command group."""
    pass


@phase3_group.command(name="build", help="Build and serialize FAISS indexes.")
@click.option("--config", default="configs/phase3.yaml", help="Path to Phase 3 configuration.")
def build_indexes(config: str) -> None:
    try:
        with open(config, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        evaluator = Phase3RetrievalEvaluator()
        storage_dir = Path(cfg.get("index_storage_dir", "data/processed/indexes"))
        storage_dir.mkdir(parents=True, exist_ok=True)

        click.echo("=" * 80)
        click.echo("BUILDING FAISS INDEXES")
        click.echo("=" * 80)

        # 1. HCCI Index
        h_mat, h_ids, _ = evaluator.load_embeddings(cfg["datasets"]["hcci"]["embeddings_path"])
        h_idx = FAISSVectorIndex(384, IndexType.FLAT_IP)
        h_idx.build(h_mat, h_ids)
        h_idx.save(storage_dir / "hcci_IndexFlatIP.faiss")
        click.echo(f"Built HCCI IndexFlatIP: {len(h_ids)} vectors.")

        # 2. Carinthia Index
        c_mat, c_ids, _ = evaluator.load_embeddings(cfg["datasets"]["carinthia"]["embeddings_path"])
        c_idx = FAISSVectorIndex(384, IndexType.FLAT_IP)
        c_idx.build(c_mat, c_ids)
        c_idx.save(storage_dir / "carinthia_IndexFlatIP.faiss")
        click.echo(f"Built Carinthia IndexFlatIP: {len(c_ids)} vectors.")

        # 3. Combined Index
        import numpy as np
        comb_mat = np.vstack([h_mat, c_mat])
        comb_ids = h_ids + c_ids
        comb_idx = FAISSVectorIndex(384, IndexType.HNSW_FLAT, hnsw_m=16, ef_search=32)
        comb_idx.build(comb_mat, comb_ids)
        comb_idx.save(storage_dir / "combined_IndexHNSWFlat.faiss")
        click.echo(f"Built Combined IndexHNSWFlat: {len(comb_ids)} vectors.")

        click.echo(f"\nIndexes saved to: {storage_dir}")
    except Exception as e:
        click.echo(f"Error building indexes: {e}", err=True)


@phase3_group.command(name="evaluate", help="Evaluate FAISS retrieval indexes against exact reference.")
@click.option("--config", default="configs/phase3.yaml", help="Path to Phase 3 configuration.")
def evaluate_faiss(config: str) -> None:
    try:
        from scripts.generate_phase3_report import run_full_phase3_pipeline
        click.echo("=" * 80)
        click.echo("RUNNING FAISS RETRIEVAL EVALUATION & EXACT AGREEMENT VERIFICATION")
        click.echo("=" * 80)
        res = run_full_phase3_pipeline(config_path=config)
        click.echo(f"Evaluation complete. Reports and tables saved to: {res['reports_dir']}")
    except Exception as e:
        click.echo(f"Error evaluating FAISS: {e}", err=True)


@phase3_group.command(name="benchmark", help="Run high-resolution query latency and memory benchmarks.")
@click.option("--config", default="configs/phase3.yaml", help="Path to Phase 3 configuration.")
def benchmark_latency(config: str) -> None:
    try:
        from scripts.generate_phase3_report import run_full_phase3_pipeline
        click.echo("=" * 80)
        click.echo("RUNNING LATENCY, THROUGHPUT, AND MEMORY BENCHMARK")
        click.echo("=" * 80)
        res = run_full_phase3_pipeline(config_path=config)
        click.echo(f"Benchmark complete. Results available in: {res['reports_dir']}")
    except Exception as e:
        click.echo(f"Error during latency benchmark: {e}", err=True)


@phase3_group.command(name="report", help="Generate the comprehensive Phase 3 FAISS report.")
@click.option("--config", default="configs/phase3.yaml", help="Path to Phase 3 configuration.")
def generate_report(config: str) -> None:
    try:
        from scripts.generate_phase3_report import run_full_phase3_pipeline
        res = run_full_phase3_pipeline(config_path=config)
        click.echo(f"Phase 3 report generated at: {res['reports_dir']}/PHASE3_FAISS_REPORT.md")
    except Exception as e:
        click.echo(f"Error generating Phase 3 report: {e}", err=True)


@phase3_group.command(name="all", help="Execute complete Phase 3 build, evaluate, benchmark, and report.")
@click.option("--config", default="configs/phase3.yaml", help="Path to Phase 3 configuration.")
def run_all(config: str) -> None:
    try:
        from scripts.generate_phase3_report import run_full_phase3_pipeline
        click.echo("=" * 80)
        click.echo("EXECUTING FULL PHASE 3 PIPELINE (BUILD, EVALUATE, BENCHMARK, REPORT)")
        click.echo("=" * 80)
        res = run_full_phase3_pipeline(config_path=config)
        click.echo(f"Phase 3 pipeline completed successfully: {res['reports_dir']}")
    except Exception as e:
        click.echo(f"Error running Phase 3 pipeline: {e}", err=True)
