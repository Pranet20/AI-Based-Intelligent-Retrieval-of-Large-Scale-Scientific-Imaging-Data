"""Tests for CLI commands using click.testing.CliRunner."""

from click.testing import CliRunner
from src.cli.main import cli


def test_cli_version() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "AI-Powered Scientific Image Data Management Platform" in result.output


def test_cli_environment() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["environment"])
    assert result.exit_code == 0
    assert "PLATFORM ENVIRONMENT REPRODUCIBILITY SNAPSHOT" in result.output
    assert "Installed Scientific Packages" in result.output


def test_cli_dataset_list() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["dataset", "list"])
    assert result.exit_code == 0
    assert "hcci" in result.output
    assert "carinthia" in result.output
    assert "atomagined" in result.output


def test_cli_dataset_register() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["dataset", "register"])
    assert result.exit_code == 0
    assert "Validated 6 dataset configurations" in result.output


def test_cli_dataset_download_help() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["dataset", "download", "--help"])
    assert result.exit_code == 0
    assert "--id" in result.output
