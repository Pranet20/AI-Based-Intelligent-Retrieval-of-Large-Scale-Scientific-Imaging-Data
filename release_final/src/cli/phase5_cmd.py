"""CLI subcommands for Phase 5 hybrid visual + metadata retrieval."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import click

from src.utils.logging import get_logger

logger = get_logger("cli.phase5")


@click.group(name="phase5", help="Phase 5: Hybrid visual + scientific metadata retrieval.")
def phase5_group() -> None:
    pass


@phase5_group.command(name="audit", help="Run Phase 5 metadata availability & leakage audit.")
def audit_command() -> None:
    """Run metadata availability & leakage audit."""
    click.echo("Running Phase 5 metadata audit...")
    cmd = [sys.executable, "scripts/audit_phase5_data.py"]
    subprocess.run(cmd, check=True)


@phase5_group.command(name="run", help="Run full Phase 5 hybrid retrieval benchmark.")
@click.option("--config", default="configs/phase5.yaml", help="Path to config file.")
def run_command(config: str) -> None:
    """Run full Phase 5 evaluation."""
    click.echo("Running Phase 5 hybrid retrieval benchmark...")
    cmd = [sys.executable, "scripts/run_phase5.py", "--config", config]
    subprocess.run(cmd, check=True)


@phase5_group.command(name="report", help="Generate Phase 5 figures and master report.")
@click.option("--config", default="configs/phase5.yaml", help="Path to config file.")
def report_command(config: str) -> None:
    """Generate Phase 5 report."""
    click.echo("Generating Phase 5 report and publication figures...")
    cmd = [sys.executable, "scripts/generate_phase5_report.py", "--config", config]
    subprocess.run(cmd, check=True)
