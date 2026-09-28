"""Versioned Scientific Representation Registry.

Manages representations across the research platform.
Preserves frozen baselines (DINOv2 ViT-S/14 baseline and Phase 4 adapted head)
and allows versioned registration of new models.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RepresentationDescriptor:
    representation_id: str
    model_name: str
    version: str
    checkpoint_path: Optional[str]
    checkpoint_hash: str
    preprocessing_version: str
    embedding_dimension: int
    training_data: str
    training_objective: str
    registration_date: str
    is_baseline: bool
    status: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RepresentationRegistry:
    """Registry maintaining immutable frozen baselines and versioned models."""

    def __init__(self, registry_file: Optional[Path] = None):
        self.registry_file = registry_file or Path("configs/representation_registry.json")
        self._registry: Dict[str, RepresentationDescriptor] = {}
        self._init_defaults()

    def _init_defaults(self):
        # 1. Authoritative Frozen DINOv2 Baseline (Cannot be replaced)
        dinov2 = RepresentationDescriptor(
            representation_id="dinov2_vits14_phase2",
            model_name="DINOv2 ViT-S/14",
            version="1.0.0",
            checkpoint_path="torch.hub:facebookresearch/dinov2",
            checkpoint_hash="torch_hub_facebookresearch_dinov2_vits14",
            preprocessing_version="1.0.0",
            embedding_dimension=384,
            training_data="LVD-142M (Pre-trained Foundation)",
            training_objective="Self-Supervised DINOv2 (iBOT + DINO)",
            registration_date="2026-09-25T19:53:00Z",
            is_baseline=True,
            status="FROZEN_AUTHORITATIVE",
            metadata={"source_phase": "Phase 2", "patch_size": 14, "backbone_parameters": "22.06M"},
        )
        self._registry[dinov2.representation_id] = dinov2

        # 2. Authoritative Frozen Phase 4 Contrastive Adapter
        phase4 = RepresentationDescriptor(
            representation_id="phase4_acquisition_adapter_seed42",
            model_name="Acquisition-Aware SupCon Linear Projection",
            version="1.0.0",
            checkpoint_path="data/processed/phase4/checkpoints/best_checkpoint_seed42.pt",
            checkpoint_hash="53ba60a317a140ceaebdf2e152dea88fd78f2a8bffbec378fc14c84010fd0e62",
            preprocessing_version="1.0.0",
            embedding_dimension=384,
            training_data="HCCI (High-Chromium Cast Iron SEM Micrographs)",
            training_objective="Supervised Contrastive InfoNCE (Cross-Detector/Voltage Pairs)",
            registration_date="2026-09-25T23:44:00Z",
            is_baseline=False,
            status="FROZEN_AUTHORITATIVE",
            metadata={"source_phase": "Phase 4", "gap_reduction": "68.15%", "p_value": "1.42e-12"},
        )
        self._registry[phase4.representation_id] = phase4

        if self.registry_file.exists():
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for rep_id, d in data.items():
                    # Protect frozen baselines from overwrite
                    if rep_id not in self._registry or not self._registry[rep_id].is_baseline:
                        self._registry[rep_id] = RepresentationDescriptor(**d)
            except Exception:
                pass

    def register(self, descriptor: RepresentationDescriptor) -> None:
        """Registers new versioned representation without overwriting frozen baselines."""
        if descriptor.representation_id in self._registry and self._registry[descriptor.representation_id].is_baseline:
            raise ValueError(f"Cannot overwrite frozen authoritative baseline: {descriptor.representation_id}")
        self._registry[descriptor.representation_id] = descriptor
        self.save()

    def get(self, representation_id: str) -> Optional[RepresentationDescriptor]:
        return self._registry.get(representation_id)

    def list_all(self) -> List[RepresentationDescriptor]:
        return list(self._registry.values())

    def save(self) -> None:
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: v.to_dict() for k, v in self._registry.items()}
        with open(self.registry_file, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2)
