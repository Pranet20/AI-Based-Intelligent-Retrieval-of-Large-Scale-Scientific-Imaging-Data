"""Scientific reproducibility and provenance tracking module for Phase 1."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import random
import subprocess
import sys
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


DEFAULT_TRACKED_PACKAGES = [
    "numpy",
    "pandas",
    "pillow",
    "tifffile",
    "imagehash",
    "pyarrow",
    "scipy",
    "scikit-learn",
    "h5py",
    "matplotlib",
    "click",
    "pydantic",
    "pyyaml",
]


def set_seed(seed: int = 42) -> None:
    """Set global random seeds for deterministic execution."""
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import numpy as np

        np.random.seed(seed)
    except ImportError:
        pass


def get_git_commit(cwd: Optional[Path] = None) -> Optional[str]:
    """Retrieve current git commit hash if running in a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd or Path.cwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


def get_package_versions(packages: Optional[List[str]] = None) -> Dict[str, str]:
    """Extract installed versions of key scientific dependencies."""
    pkgs = packages or DEFAULT_TRACKED_PACKAGES
    versions: Dict[str, str] = {}
    for pkg in pkgs:
        try:
            versions[pkg] = version(pkg)
        except PackageNotFoundError:
            versions[pkg] = "NOT_INSTALLED"
    return versions


def compute_file_sha256(file_path: str | Path, chunk_size: int = 65536) -> str:
    """Compute standard SHA-256 hash of a file."""
    p = Path(file_path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found for hash calculation: {file_path}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def compute_config_hash(config_dir: str | Path = "configs") -> Dict[str, str]:
    """Compute sha256 checksums of all configuration files."""
    cdir = Path(config_dir)
    hashes: Dict[str, str] = {}
    if not cdir.exists():
        return hashes
    for cfg in sorted(cdir.glob("*.yaml")):
        hashes[cfg.name] = compute_file_sha256(cfg)
    return hashes


def get_system_environment() -> Dict[str, Any]:
    """Capture complete OS, hardware, and runtime environment details."""
    return {
        "os_name": os.name,
        "platform": platform.platform(),
        "platform_system": platform.system(),
        "platform_release": platform.release(),
        "platform_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": sys.version,
        "python_executable": sys.executable,
    }


def create_reproducibility_snapshot(
    experiment_id: str,
    random_seed: int = 42,
    dataset_versions: Optional[Dict[str, Any]] = None,
    configs_dir: str | Path = "configs",
    tracked_packages: Optional[List[str]] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create a complete, serializable research reproducibility snapshot."""
    set_seed(random_seed)

    snapshot = {
        "experiment_id": experiment_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "random_seed": random_seed,
        "git_commit": get_git_commit(),
        "system_environment": get_system_environment(),
        "package_versions": get_package_versions(tracked_packages),
        "configuration_hashes": compute_config_hash(configs_dir),
        "dataset_versions": dataset_versions or {},
        "extra_metadata": extra_metadata or {},
    }
    return snapshot


def save_reproducibility_snapshot(
    snapshot: Dict[str, Any],
    output_path: str | Path,
) -> None:
    """Save snapshot to JSON file for experiment provenance tracking."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
