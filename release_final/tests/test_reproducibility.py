"""Tests for reproducibility and provenance tracking."""

from pathlib import Path
from src.utils.reproducibility import create_reproducibility_snapshot, set_seed
from src.utils.versioning import DatasetVersionManager
from src.datasets.registry import DatasetRegistry


def test_reproducibility_snapshot() -> None:
    snapshot = create_reproducibility_snapshot(experiment_id="test_exp_01")
    assert snapshot["experiment_id"] == "test_exp_01"
    assert "timestamp_utc" in snapshot
    assert "system_environment" in snapshot
    assert "package_versions" in snapshot
    assert "configuration_hashes" in snapshot
    # Verify core packages tracked
    pkgs = snapshot["package_versions"]
    assert "numpy" in pkgs
    assert "pandas" in pkgs
    assert "tifffile" in pkgs
    assert "pyarrow" in pkgs


def test_dataset_version_manager(tmp_test_dir: Path) -> None:
    v_file = tmp_test_dir / "dataset_versions.json"
    vm = DatasetVersionManager(versions_path=v_file)

    registry = DatasetRegistry()
    entry = registry.get("hcci")

    mock_manifest = tmp_test_dir / "mock_manifest.parquet"
    mock_manifest.write_text("dummy manifest content")

    rec = vm.record_version(
        entry=entry,
        manifest_path=mock_manifest,
        file_count=777,
        total_size_bytes=4500000000,
    )

    assert rec["dataset_id"] == "hcci"
    assert rec["file_count"] == 777
    assert vm.get_version("hcci") is not None
    assert v_file.is_file()
