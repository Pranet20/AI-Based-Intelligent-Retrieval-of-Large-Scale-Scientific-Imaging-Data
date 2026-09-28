"""CLI subcommands for Phase 4 representation adaptation and evaluation."""

from __future__ import annotations

import json
from pathlib import Path
import click
import yaml

from src.utils.logging import get_logger

logger = get_logger("cli.phase4")


@click.group(name="phase4", help="Phase 4: Acquisition-aware representation adaptation.")
def phase4_group() -> None:
    pass


@phase4_group.command(name="audit", help="Run Phase 4 data-relationship audit.")
def audit_command() -> None:
    """Run data relationship audit and verify relationship definitions."""
    click.echo("Running Phase 4 data relationship audit...")
    from src.adaptation.split_builder import SplitBuilder
    from src.adaptation.relationship_builder import RelationshipBuilder

    sb = SplitBuilder()
    df = sb.load_data()
    RelationshipBuilder.validate_no_fabricated_roi(df)
    click.echo(f"Audit passed: {len(df)} images verified without fabricated ROI pairs.")


@phase4_group.command(name="split", help="Generate and validate leakage-safe splits.")
@click.option("--config", default="configs/phase4.yaml", help="Path to config file.")
def split_command(config: str) -> None:
    """Generate and validate leakage-safe splits."""
    with open(config, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    from src.adaptation.split_builder import SplitBuilder

    sb = SplitBuilder(
        hcci_manifest_path=cfg["data"]["hcci_manifest"],
        output_dir=cfg["data"]["splits_dir"],
    )
    splits = sb.build_instrument_split()
    sb.save_splits(splits)
    click.echo("Splits generated and verified successfully.")


@phase4_group.command(name="train", help="Train Phase 4 adapted representation model.")
@click.option("--config", default="configs/phase4.yaml", help="Path to config file.")
@click.option("--seed", default=42, type=int, help="Random seed for training.")
def train_command(config: str, seed: int) -> None:
    """Train Phase 4 model on training split."""
    click.echo(f"Training Phase 4 model with seed {seed}...")
    import subprocess
    import sys
    cmd = [sys.executable, "scripts/train_phase4.py", "--config", config, "--seed", str(seed)]
    subprocess.run(cmd, check=True)


@phase4_group.command(name="evaluate", help="Evaluate Phase 4 retrieval and probe metrics.")
@click.option("--config", default="configs/phase4.yaml", help="Path to config file.")
def evaluate_command(config: str) -> None:
    """Evaluate Phase 4 models against Phase 2 baseline."""
    click.echo("Evaluating Phase 4 models and baselines...")
    import subprocess
    import sys
    cmd = [sys.executable, "scripts/evaluate_phase4.py", "--config", config]
    subprocess.run(cmd, check=True)


@phase4_group.command(name="report", help="Generate official Phase 4 report.")
@click.option("--config", default="configs/phase4.yaml", help="Path to config file.")
def report_command(config: str) -> None:
    """Generate official Phase 4 research report."""
    click.echo("Generating Phase 4 research report...")
    import subprocess
    import sys
    cmd = [sys.executable, "scripts/generate_phase4_report.py", "--config", config]
    subprocess.run(cmd, check=True)


@phase4_group.command(name="all", help="Run full Phase 4 pipeline.")
@click.option("--config", default="configs/phase4.yaml", help="Path to config file.")
@click.pass_context
def all_command(ctx: click.Context, config: str) -> None:
    """Run full Phase 4 adaptation and evaluation pipeline."""
    ctx.invoke(split_command, config=config)
    ctx.invoke(train_command, config=config, seed=42)
    ctx.invoke(evaluate_command, config=config)
    ctx.invoke(report_command, config=config)
