"""Dataset adapters and registry for scientific image platform."""

from src.datasets.base import BaseDatasetAdapter
from src.datasets.registry import DatasetRegistry, DatasetRegistryEntry
from src.datasets.hcci import HCCIDatasetAdapter
from src.datasets.carinthia import CarinthiaDatasetAdapter
from src.datasets.sem_nanoscience import SemNanoscienceAdapter
from src.datasets.atomagined import AtomaginedAdapter
from src.datasets.cigrocksem import CigRockSEMAdapter
from src.datasets.microal import MicroAlAdapter

ADAPTER_MAPPING = {
    "hcci": HCCIDatasetAdapter,
    "carinthia": CarinthiaDatasetAdapter,
    "sem_nanoscience": SemNanoscienceAdapter,
    "atomagined": AtomaginedAdapter,
    "cigrocksem": CigRockSEMAdapter,
    "microal": MicroAlAdapter,
}

__all__ = [
    "BaseDatasetAdapter",
    "DatasetRegistry",
    "DatasetRegistryEntry",
    "HCCIDatasetAdapter",
    "CarinthiaDatasetAdapter",
    "SemNanoscienceAdapter",
    "AtomaginedAdapter",
    "CigRockSEMAdapter",
    "MicroAlAdapter",
    "ADAPTER_MAPPING",
]
