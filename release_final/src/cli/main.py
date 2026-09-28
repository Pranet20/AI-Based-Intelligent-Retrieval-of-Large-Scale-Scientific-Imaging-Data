"""Main Click CLI entry point for the scientific platform."""

import click

from src import __version__
from src.cli.dataset_cmd import dataset_group
from src.cli.environment_cmd import environment_cmd, version_cmd
from src.cli.phase2_cmd import phase2_group
from src.cli.phase3_cmd import phase3_group
from src.cli.phase4_cmd import phase4_group
from src.cli.phase5_cmd import phase5_group
from src.cli.phase7_cmd import phase7_group


@click.group(
    help="AI-Powered Scientific Image Data Management Platform - Command Line Interface."
)
@click.version_option(__version__, message="%(prog)s version %(version)s")
def cli() -> None:
    pass


cli.add_command(dataset_group)
cli.add_command(environment_cmd)
cli.add_command(version_cmd)
cli.add_command(phase2_group)
cli.add_command(phase3_group)
cli.add_command(phase4_group)
cli.add_command(phase5_group)
cli.add_command(phase7_group)

if __name__ == "__main__":
    cli()
