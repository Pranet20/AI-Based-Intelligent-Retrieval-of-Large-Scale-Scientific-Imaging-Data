"""Production Model Serving Service for Scientific Image Embeddings.

Features:
- Singleton lifecycle (loads model weights once)
- Startup cryptographic checksum verification
- Device selection (CUDA / CPU auto-selection)
- Single-image and batch inference
- Exact unit L2-normalization
- Comprehensive embedding metadata provenance:
  (model_id, model_version, checkpoint_hash, preprocessing_version, timestamp, source_image_hash)
"""

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import torch
from PIL import Image as PILImage

from app.core.config import settings
from app.ml.model_registry import ModelRegistryService, ModelVerificationError


@dataclass
class EmbeddingProvenanceRecord:
    vector: List[float]
    dimension: int
    l2_normalized: bool
    model_id: str
    model_version: str
    checkpoint_hash: str
    preprocessing_version: str
    source_image_hash: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ModelServer:
    """Production inference server for foundation and adapted representations."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelServer, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self, force_cpu: bool = False):
        if self._initialized:
            return

        # 1. Device configuration
        if force_cpu or not torch.cuda.is_available():
            self.device = torch.device("cpu")
        else:
            self.device = torch.device("cuda")

        # 2. Checksum verification of frozen weights
        ModelRegistryService.verify_checkpoint_hash(
            settings.PHASE4_CHECKPOINT_PATH,
            settings.EXPECTED_PHASE4_HASH,
        )

        # 3. Load DINOv2 backbone
        from src.representation.dinov2_encoder import DINOv2Encoder
        from src.representation.preprocessing import ScientificImagePreprocessor
        self.encoder = DINOv2Encoder(model_name=settings.DINOV2_MODEL_NAME, device=str(self.device))
        self.preprocessor = ScientificImagePreprocessor(
            image_size=(settings.IMAGE_TARGET_SIZE, settings.IMAGE_TARGET_SIZE)
        )

        # 4. Load Phase 4 contrastive adapter using ProjectionHead
        from src.adaptation.projection_head import ProjectionHead
        ckpt = torch.load(settings.PHASE4_CHECKPOINT_PATH, map_location=self.device)
        self.adapter = ProjectionHead(
            input_dim=settings.DINOV2_EMBEDDING_DIM,
            hidden_dim=settings.DINOV2_EMBEDDING_DIM,
            output_dim=settings.DINOV2_EMBEDDING_DIM,
            head_type="linear",
            normalize_output=True
        )
        self.adapter.load_state_dict(ckpt["model_state_dict"] if "model_state_dict" in ckpt else ckpt)
        self.adapter.to(self.device)
        self.adapter.eval()
        for p in self.adapter.parameters():
            p.requires_grad = False

        self.phase4_hash = settings.EXPECTED_PHASE4_HASH
        self.dino_hash = "torch_hub_facebookresearch_dinov2_vits14"
        self.preprocessing_version = settings.PREPROCESSING_VERSION
        self._initialized = True
        print(f"[ModelServer] Initialized on device: {self.device}. Checkpoints verified.")

    def embed_single(
        self,
        image_input: Union[str, Path, np.ndarray, bytes],
        use_adapter: bool = False,
        source_image_hash: Optional[str] = None,
    ) -> EmbeddingProvenanceRecord:
        """Single-image inference with provenance tagging."""
        self.initialize()
        from src.ingestion.reader import ScientificImageReader

        if isinstance(image_input, (str, Path)):
            arr, _ = ScientificImageReader.load_array(image_input)
            if source_image_hash is None:
                source_image_hash = hashlib.sha256(Path(image_input).read_bytes()).hexdigest()
        elif isinstance(image_input, bytes):
            source_image_hash = hashlib.sha256(image_input).hexdigest()
            # Parse bytes to numpy
            import io
            pil_img = PILImage.open(io.BytesIO(image_input)).convert("RGB")
            arr = np.array(pil_img)
        elif isinstance(image_input, np.ndarray):
            arr = image_input
            if source_image_hash is None:
                source_image_hash = hashlib.sha256(arr.tobytes()).hexdigest()
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        tensor, _ = self.preprocessor.preprocess_array(arr)
        batch = tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.encoder.extract_features(batch, normalize=True)
            if use_adapter:
                features_t = torch.from_numpy(features).float().to(self.device)
                adapted_t = self.adapter(features_t)
                adapted_t = torch.nn.functional.normalize(adapted_t, p=2, dim=-1)
                vec = adapted_t[0].cpu().numpy()
                model_id = "phase4_acquisition_adapter_seed42"
                model_version = "1.0.0"
                ckpt_hash = self.phase4_hash
            else:
                vec = features[0]
                model_id = "dinov2_vits14_phase2"
                model_version = "1.0.0"
                ckpt_hash = self.dino_hash

        # Guarantee exact unit normalization
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        return EmbeddingProvenanceRecord(
            vector=vec.tolist(),
            dimension=len(vec),
            l2_normalized=True,
            model_id=model_id,
            model_version=model_version,
            checkpoint_hash=ckpt_hash,
            preprocessing_version=self.preprocessing_version,
            source_image_hash=source_image_hash or "UNKNOWN",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def embed_batch(
        self,
        image_arrays: List[np.ndarray],
        use_adapter: bool = False,
        source_hashes: Optional[List[str]] = None,
    ) -> List[EmbeddingProvenanceRecord]:
        """High-throughput batch inference."""
        self.initialize()
        if not image_arrays:
            return []

        tensors = []
        for arr in image_arrays:
            t, _ = self.preprocessor.preprocess_array(arr)
            tensors.append(t)
        batch = torch.stack(tensors).to(self.device)

        with torch.no_grad():
            features = self.encoder.extract_features(batch, normalize=True)
            if use_adapter:
                features_t = torch.from_numpy(features).float().to(self.device)
                adapted_t = self.adapter(features_t)
                adapted_t = torch.nn.functional.normalize(adapted_t, p=2, dim=-1)
                vecs = adapted_t.cpu().numpy()
                model_id = "phase4_acquisition_adapter_seed42"
                model_version = "1.0.0"
                ckpt_hash = self.phase4_hash
            else:
                vecs = features
                model_id = "dinov2_vits14_phase2"
                model_version = "1.0.0"
                ckpt_hash = self.dino_hash

        records = []
        now = datetime.now(timezone.utc).isoformat()
        for idx, vec in enumerate(vecs):
            norm = np.linalg.norm(vec)
            if norm > 0:
                vec = vec / norm
            h = source_hashes[idx] if source_hashes and idx < len(source_hashes) else "BATCH_INFERRED"
            records.append(
                EmbeddingProvenanceRecord(
                    vector=vec.tolist(),
                    dimension=len(vec),
                    l2_normalized=True,
                    model_id=model_id,
                    model_version=model_version,
                    checkpoint_hash=ckpt_hash,
                    preprocessing_version=self.preprocessing_version,
                    source_image_hash=h,
                    timestamp=now,
                )
            )
        return records
