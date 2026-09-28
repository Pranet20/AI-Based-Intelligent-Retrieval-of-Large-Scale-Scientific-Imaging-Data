"""CLI subcommand and module for Phase 7 publication benchmark reproducibility."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import click

from src.evaluation.dataset_registry import DatasetEvidenceRegistry
from src.evaluation.experiment_registry import ExperimentRegistry
from src.evaluation.leakage_audit import LeakageAuditor
from src.evaluation.master_benchmark import MasterBenchmarkRunner
from src.utils.logging import get_logger

logger = get_logger("cli.phase7")


@click.group(name="phase7", help="Phase 7: Publication-grade unified benchmark, ablation, and statistical validation.")
def phase7_group() -> None:
    pass


@phase7_group.command(name="reproduce", help="Regenerate all metrics, tables, and reports from frozen artifacts.")
def reproduce_command() -> None:
    """Regenerate all Phase 7 benchmark metrics, audit records, tables, and figures from frozen Phase 1-6 artifacts."""
    click.echo("============================================================")
    click.echo("PHASE 7 REPRODUCIBILITY PIPELINE — MASTER EXECUTION")
    click.echo("============================================================")

    # 1. Export Dataset Registry
    click.echo("[1/5] Updating Dataset Evidence Registry...")
    ds_reg = DatasetEvidenceRegistry()
    ds_out = ds_reg.export_json("artifacts/phase7/dataset_registry.json")
    click.echo(f"  -> Exported to {ds_out}")

    # 2. Export Experiment Registry
    click.echo("[2/5] Updating Unified Experiment Registry...")
    exp_reg = ExperimentRegistry()
    exp_out = exp_reg.export_json("artifacts/phase7/experiment_registry.json")
    click.echo(f"  -> Exported to {exp_out}")

    # 3. Formal Leakage Audit
    click.echo("[3/5] Executing 10-point Formal Leakage Audit...")
    auditor = LeakageAuditor()
    auditor.run_all_checks()
    auditor.export_json("artifacts/phase7/leakage_audit.json")
    auditor.generate_report("reports/phase7/LEAKAGE_AUDIT.md")
    click.echo("  -> Exported leakage audit records.")

    # 4. Master Benchmark Execution & Cryptographic Verification
    click.echo("[4/5] Executing Master Benchmark Runner...")
    runner = MasterBenchmarkRunner()
    results = runner.run_all_benchmarks()
    click.echo(f"  -> Successfully generated MASTER_RESULTS.json ({len(results)} metrics).")

    # 5. Publication Tables, Figures, and Master Report
    click.echo("[5/5] Generating Publication Tables, Figures, and Final Paper Report...")
    cmd = [sys.executable, "scripts/generate_phase7_publication_assets.py"]
    subprocess.run(cmd, check=True)

    click.echo("============================================================")
    click.echo("PHASE 7 REPRODUCIBILITY PIPELINE COMPLETED SUCCESSFULLY.")
    click.echo("============================================================")


if __name__ == "__main__":
    phase7_group()
