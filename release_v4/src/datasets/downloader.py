"""Dataset download helper and acquisition guide."""

from __future__ import annotations

import io
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from tqdm import tqdm

from src.datasets.registry import DatasetRegistry, DatasetRegistryEntry
from src.utils.logging import get_logger

logger = get_logger("dataset.downloader")


class DatasetDownloader:
    """Manages acquisition, verification, and manual retrieval instructions."""

    def __init__(self, registry: Optional[DatasetRegistry] = None) -> None:
        self.registry = registry or DatasetRegistry()

    def get_acquisition_info(self, dataset_id: str) -> Dict[str, Any]:
        """Retrieve acquisition guidance, license, and size parameters for a dataset."""
        entry = self.registry.get(dataset_id)
        dest = Path(entry.local_path)

        # Check if already present or if local archive exists
        is_extracted = dest.is_dir() and any(dest.iterdir())

        return {
            "dataset_id": entry.dataset_id,
            "name": entry.name,
            "source_url": entry.source_url,
            "doi": entry.doi,
            "expected_size": entry.archive_size_if_known or "UNKNOWN",
            "destination": str(dest.resolve()),
            "license": entry.license,
            "access_notes": entry.access_notes,
            "is_extracted": is_extracted,
        }

    def unpack_local_archive_if_available(self, dataset_id: str, workspace_root: Path = Path(".")) -> bool:
        """Check for local workspace archives (e.g. 10715190.zip or HCCI Dataset .zip) and unpack."""
        entry = self.registry.get(dataset_id)
        target_dir = Path(entry.local_path)
        target_dir.mkdir(parents=True, exist_ok=True)

        if dataset_id == "carinthia":
            archive = workspace_root / "10715190.zip"
            if archive.is_file():
                logger.info("Extracting Carinthia from local archive: %s", archive)
                with zipfile.ZipFile(archive) as z1:
                    if "data.zip" in z1.namelist():
                        data_bytes = z1.read("data.zip")
                        with zipfile.ZipFile(io.BytesIO(data_bytes)) as z2:
                            z2.extractall(target_dir)
                    else:
                        z1.extractall(target_dir)
                logger.info("Carinthia extracted successfully to %s", target_dir)
                return True

        if dataset_id == "hcci":
            # Search for HCCI archive
            matches = list(workspace_root.glob("*HCCI*.zip"))
            if matches:
                archive = matches[0]
                logger.info("Extracting HCCI from local archive: %s", archive)
                with zipfile.ZipFile(archive) as z:
                    z.extractall(target_dir)
                logger.info("HCCI extracted successfully to %s", target_dir)
                return True

        return False

    def get_manual_instructions(self, dataset_id: str) -> str:
        """Provide detailed manual acquisition instructions where direct automated download is restricted."""
        entry = self.registry.get(dataset_id)
        return f"""
================================================================================
MANUAL ACQUISITION INSTRUCTIONS: {entry.name} ({entry.dataset_id})
================================================================================
Source URL: {entry.source_url}
DOI:        {entry.doi}
Expected:   {entry.archive_size_if_known or 'Variable'}
Target Dir: {entry.local_path}

INSTRUCTIONS:
1. Navigate in your browser to: {entry.source_url}
2. Review the access conditions and license: {entry.license}
   Note: {entry.access_notes}
3. Download the research archive or clone the repository into:
   {Path(entry.local_path).resolve()}
4. Verify files are placed such that images are discoverable.
5. Run: research dataset audit --id {entry.dataset_id}
================================================================================
"""
