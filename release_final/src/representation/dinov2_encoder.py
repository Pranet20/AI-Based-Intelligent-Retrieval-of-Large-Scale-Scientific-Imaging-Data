"""Official Meta DINOv2 visual representation feature encoder."""

from __future__ import annotations

import sys
from typing import Any, Dict, Optional
import numpy as np
import torch
import torchvision


class DINOv2Encoder:
    """Pretrained DINOv2 Vision Transformer encoder for scientific image representations."""

    def __init__(
        self,
        model_name: str = "dinov2_vits14",
        hub_repo: str = "facebookresearch/dinov2",
        device: Optional[str] = None,
    ) -> None:
        self.model_name = model_name
        self.hub_repo = hub_repo

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

        self._load_model()

    def _load_model(self) -> None:
        """Load pretrained DINOv2 model from official torch hub and freeze weights."""
        # Using official Meta repository
        self.model = torch.hub.load(self.hub_repo, self.model_name, pretrained=True)
        self.model.to(self.device)
        self.model.eval()

        # Strictly freeze all parameters (Phase 2 baseline is representation only)
        for param in self.model.parameters():
            param.requires_grad = False

        self.embedding_dimension = getattr(self.model, "embed_dim", 384)
        self.parameter_count = sum(p.numel() for p in self.model.parameters())

    def extract_features(
        self,
        batch_tensors: torch.Tensor,
        normalize: bool = True,
    ) -> np.ndarray:
        """Extract visual representations from preprocessed batch tensors.

        Args:
            batch_tensors: Tensor of shape (B, 3, H, W) normalized for DINOv2.
            normalize: If True, applies L2 normalization to output vectors.

        Returns:
            NumPy array of shape (B, embedding_dimension).
        """
        if batch_tensors.ndim != 4 or batch_tensors.shape[1] != 3:
            raise ValueError(
                f"Expected 4D tensor with shape (B, 3, H, W), got shape {batch_tensors.shape}"
            )

        tensors = batch_tensors.to(self.device)
        with torch.no_grad():
            features = self.model(tensors)
            if normalize:
                features = torch.nn.functional.normalize(features, p=2, dim=-1)

        return features.cpu().numpy()

    def get_model_info(self) -> Dict[str, Any]:
        """Return runtime model and hardware provenance metadata."""
        return {
            "model_name": self.model_name,
            "model_source": f"https://github.com/{self.hub_repo}",
            "model_architecture": self.model.__class__.__name__,
            "embedding_dimension": int(self.embedding_dimension),
            "parameter_count": int(self.parameter_count),
            "weights_identifier": f"{self.model_name}_pretrain",
            "torch_version": torch.__version__,
            "torchvision_version": torchvision.__version__,
            "python_version": sys.version.split()[0],
            "device": str(self.device),
            "cuda_available": bool(torch.cuda.is_available()),
            "cuda_device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        }
