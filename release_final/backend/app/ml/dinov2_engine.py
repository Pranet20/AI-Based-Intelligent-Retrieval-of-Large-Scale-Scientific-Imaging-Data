"""DINOv2 Visual Feature Extraction Engine with Lazy Loading."""

from pathlib import Path
from typing import Optional, Union
import numpy as np
import torch

from app.core.config import settings


class DINOv2Engine:
    """Lazy-loaded singleton wrapper for frozen DINOv2 ViT-S/14 representation."""

    _instance = None
    _encoder = None
    _preprocessor = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DINOv2Engine, cls).__new__(cls)
            cls._instance.dimension = settings.DINOV2_EMBEDDING_DIM
        return cls._instance

    def _ensure_loaded(self):
        if self._encoder is None:
            from src.representation.dinov2_encoder import DINOv2Encoder
            from src.representation.preprocessing import ScientificImagePreprocessor
            self._encoder = DINOv2Encoder(model_name=settings.DINOV2_MODEL_NAME)
            self._preprocessor = ScientificImagePreprocessor(
                image_size=(settings.IMAGE_TARGET_SIZE, settings.IMAGE_TARGET_SIZE)
            )

    def embed_image(self, image_path: Union[str, Path]) -> np.ndarray:
        """Extract L2-normalized 384-dimensional DINOv2 embedding from image file."""
        self._ensure_loaded()
        from src.ingestion.reader import ScientificImageReader
        arr, _ = ScientificImageReader.load_array(image_path)
        tensor, _ = self._preprocessor.preprocess_array(arr)
        batch = tensor.unsqueeze(0).to(self._encoder.device)
        features = self._encoder.extract_features(batch, normalize=True)
        return features[0]
