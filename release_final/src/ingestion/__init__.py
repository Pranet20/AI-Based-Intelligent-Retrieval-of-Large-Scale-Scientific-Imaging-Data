"""Ingestion modules: readers, manifests, integrity checks."""

from src.ingestion.reader import ScientificImageReader, ImageIntegrityResult, compute_sha256
from src.ingestion.manifest import ManifestManager, ManifestRecord, MANIFEST_COLUMNS

__all__ = [
    "ScientificImageReader",
    "ImageIntegrityResult",
    "compute_sha256",
    "ManifestManager",
    "ManifestRecord",
    "MANIFEST_COLUMNS",
]
