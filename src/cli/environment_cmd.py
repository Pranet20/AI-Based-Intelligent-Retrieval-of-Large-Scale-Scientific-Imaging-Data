"""CLI commands for environment, provenance, and platform version inspection."""

from __future__ import annotations

import json
from pathlib import Path
import click

from src import __version__
from src.utils.reproducibility import create_reproducibility_snapshot


@click.command(name="version", help="Show current scientific platform software version.")
def version_cmd() -> None:
    click.echo(f"AI-Powered Scientific Image Data Management Platform v{__version__} (Phase 1 Foundation)")


@click.command(name="environment", help="Inspect and record complete runtime, OS, and package environment.")
@click.option("--output", default=None, help="Optional output JSON path to save reproducibility snapshot.")
def environment_cmd(output: str | None) -> None:
    snapshot = create_reproducibility_snapshot(experiment_id="environment_audit")

    click.echo("=" * 70)
    click.echo(f"PLATFORM ENVIRONMENT REPRODUCIBILITY SNAPSHOT (v{__version__})")
    click.echo("=" * 70)
    click.echo(f"Timestamp (UTC): {snapshot['timestamp_utc']}")
    click.echo(f"Git Commit:      {snapshot['git_commit'] or 'NOT_A_GIT_REPO'}")
    click.echo(f"Python Version:  {snapshot['system_environment']['python_version'].split()[0]}")
    click.echo(f"OS Platform:     {snapshot['system_environment']['platform']}")
    click.echo("-" * 70)
    click.echo("Installed Scientific Packages:")
    for pkg, ver in snapshot["package_versions"].items():
        click.echo(f"  {pkg:<18}: {ver}")
    click.echo("-" * 70)
    click.echo("Configuration Checksums (SHA-256):")
    for cfg, chash in snapshot["configuration_hashes"].items():
        click.echo(f"  {cfg:<24}: {chash[:16]}...")
    click.echo("=" * 70)

    if output:
        out_p = Path(output)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2)
        click.echo(f"Saved snapshot to: {out_p.resolve()}")
