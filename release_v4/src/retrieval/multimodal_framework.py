"""Modular Multimodal Scientific Search & Cross-Modal Retrieval Framework.

Features:
- Decoupled, independently inspectable modalities (visual, metadata, spectral)
- Configurable fusion schemes (visual-only, visual+metadata, visual+EDS, etc.)
- Transparent score breakdown per retrieved candidate
- Strict research integrity: distinguishes EXPERIMENTALLY_VALIDATED from IMPLEMENTED_EXPERIMENTAL
"""

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np


@dataclass
class CandidateExplanation:
    image_id: int
    composite_score: float
    visual_similarity: float
    metadata_similarity: Optional[float]
    spectral_similarity: Optional[float]
    fusion_mode: str
    weight_allocation: Dict[str, float]
    validation_status: str
    explanation_summary: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModularSearchFramework:
    """Decoupled retrieval framework combining visual, metadata, and spectral signals."""

    SUPPORTED_FUSION_MODES = [
        "visual_only",
        "visual_plus_metadata",
        "visual_plus_eds",
        "visual_plus_metadata_eds",
    ]

    @classmethod
    def compute_composite_score(
        cls,
        visual_sim: float,
        metadata_sim: Optional[float] = None,
        spectral_sim: Optional[float] = None,
        fusion_mode: str = "visual_only",
        weights: Optional[Dict[str, float]] = None,
    ) -> Tuple[float, Dict[str, float], str]:
        """Calculates composite score while reporting exact component breakdown."""
        if fusion_mode == "visual_only":
            return visual_sim, {"visual": 1.0, "metadata": 0.0, "spectral": 0.0}, "EXPERIMENTALLY_VALIDATED"

        elif fusion_mode == "visual_plus_metadata":
            w = weights or {"visual": 0.8, "metadata": 0.2}
            m_score = metadata_sim if metadata_sim is not None else 0.0
            comp = (w.get("visual", 0.8) * visual_sim) + (w.get("metadata", 0.2) * m_score)
            return comp, {"visual": w.get("visual", 0.8), "metadata": w.get("metadata", 0.2)}, "EXPERIMENTALLY_VALIDATED"

        elif fusion_mode == "visual_plus_eds":
            w = weights or {"visual": 0.7, "spectral": 0.3}
            s_score = spectral_sim if spectral_sim is not None else 0.0
            comp = (w.get("visual", 0.7) * visual_sim) + (w.get("spectral", 0.3) * s_score)
            return comp, {"visual": w.get("visual", 0.7), "spectral": w.get("spectral", 0.3)}, "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA"

        elif fusion_mode == "visual_plus_metadata_eds":
            w = weights or {"visual": 0.6, "metadata": 0.2, "spectral": 0.2}
            m_score = metadata_sim if metadata_sim is not None else 0.0
            s_score = spectral_sim if spectral_sim is not None else 0.0
            comp = (w.get("visual", 0.6) * visual_sim) + (w.get("metadata", 0.2) * m_score) + (w.get("spectral", 0.2) * s_score)
            return comp, w, "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA"

        else:
            raise ValueError(f"Unknown fusion mode: {fusion_mode}")


class CrossModalSearchEngine:
    """Manages cross-modal query dispatching across scientific data modalities."""

    CROSS_MODAL_MATRICES = {
        ("image", "image"): "EXPERIMENTALLY_VALIDATED",
        ("image", "metadata"): "EXPERIMENTALLY_VALIDATED",
        ("metadata", "image"): "EXPERIMENTALLY_VALIDATED",
        ("image", "spectrum"): "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA",
        ("spectrum", "image"): "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA",
        ("spectrum", "spectrum"): "IMPLEMENTED_AWAITING_PHYSICAL_SPECTRA",
    }

    @classmethod
    def get_query_status(cls, source_modality: str, target_modality: str) -> str:
        key = (source_modality.lower(), target_modality.lower())
        return cls.CROSS_MODAL_MATRICES.get(key, "UNSUPPORTED_MODALITY_PAIR")

    @classmethod
    def explain_candidate(
        cls,
        image_id: int,
        visual_sim: float,
        metadata_sim: Optional[float] = None,
        spectral_sim: Optional[float] = None,
        fusion_mode: str = "visual_only",
        weights: Optional[Dict[str, float]] = None,
        metadata_dict: Optional[Dict[str, Any]] = None,
    ) -> CandidateExplanation:
        """Constructs an explainable retrieval response grounded in retrieval evidence."""
        comp_score, weight_alloc, val_status = ModularSearchFramework.compute_composite_score(
            visual_sim=visual_sim,
            metadata_sim=metadata_sim,
            spectral_sim=spectral_sim,
            fusion_mode=fusion_mode,
            weights=weights,
        )

        # Build empirical explanation
        parts = [f"Visual Cosine: {visual_sim:.4f}"]
        if metadata_sim is not None:
            parts.append(f"Metadata Jaccard/Value Sim: {metadata_sim:.4f}")
        if spectral_sim is not None:
            parts.append(f"Spectral Cosine Sim: {spectral_sim:.4f}")
        if metadata_dict:
            det = metadata_dict.get("detector", "N/A")
            kv = metadata_dict.get("accelerating_voltage_kv", "N/A")
            parts.append(f"Instrument: {det} @ {kv} kV")

        summary = " | ".join(parts)

        return CandidateExplanation(
            image_id=image_id,
            composite_score=round(comp_score, 4),
            visual_similarity=round(visual_sim, 4),
            metadata_similarity=round(metadata_sim, 4) if metadata_sim is not None else None,
            spectral_similarity=round(spectral_sim, 4) if spectral_sim is not None else None,
            fusion_mode=fusion_mode,
            weight_allocation=weight_alloc,
            validation_status=val_status,
            explanation_summary=summary,
        )
