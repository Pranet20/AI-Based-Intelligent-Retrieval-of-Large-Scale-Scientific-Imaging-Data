"""Script to unpack local research archives (10715190.zip and HCCI Dataset .zip) to data/raw/."""

from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

from src.datasets.downloader import DatasetDownloader
from src.utils.logging import get_logger

logger = get_logger("scripts.extract_local_zips")


def main() -> None:
    workspace = Path(".")
    downloader = DatasetDownloader()

    logger.info("Checking local archives in workspace: %s", workspace.resolve())

    # 1. Carinthia
    c_unpacked = downloader.unpack_local_archive_if_available("carinthia", workspace_root=workspace)
    if c_unpacked:
        logger.info("Successfully extracted Carinthia SEM dataset to data/raw/carinthia")
    else:
        logger.warning("Carinthia local archive (10715190.zip) not found or already unpacked.")

    # 2. HCCI
    h_unpacked = downloader.unpack_local_archive_if_available("hcci", workspace_root=workspace)
    if h_unpacked:
        logger.info("Successfully extracted HCCI SEM dataset to data/raw/hcci")
    else:
        logger.warning("HCCI local archive (*HCCI*.zip) not found or already unpacked.")

    logger.info("Extraction check completed.")


if __name__ == "__main__":
    main()
