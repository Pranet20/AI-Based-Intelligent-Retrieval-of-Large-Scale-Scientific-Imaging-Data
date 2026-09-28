"""Loss functions for representation adaptation."""

from __future__ import annotations

from typing import Optional, Tuple
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.adaptation.relationship_builder import RelationshipBuilder


class AcquisitionAwareSupConLoss(nn.Module):
    """Supervised contrastive loss with acquisition-aware positive and exclusion masking.

    Formulation based on Khosla et al. (NeurIPS 2020), adapted for cross-acquisition
    invariance:
      - Valid positive: Same material condition AND different acquisition condition.
      - Masked neutral: Same material condition AND same acquisition condition (excluded from
        positive numerator to prevent reinforcing acquisition bias).
      - Negative: Different material condition.
    """

    def __init__(
        self,
        temperature: float = 0.07,
        mask_same_acquisition: bool = True,
    ) -> None:
        super().__init__()
        self.temperature = temperature
        self.mask_same_acquisition = mask_same_acquisition

    def forward(
        self,
        embeddings: torch.Tensor,
        material_labels: torch.Tensor,
        acquisition_labels: torch.Tensor,
    ) -> torch.Tensor:
        """Compute acquisition-aware supervised contrastive loss.

        Args:
            embeddings: Normalized embeddings of shape (B, D).
            material_labels: Material condition integer labels of shape (B,).
            acquisition_labels: Acquisition condition integer labels of shape (B,).

        Returns:
            Scalar loss Tensor.
        """
        device = embeddings.device
        B = embeddings.shape[0]

        if B <= 1:
            return torch.tensor(0.0, device=device, requires_grad=True)

        # 1. Build positive and valid comparison masks
        pos_mask, valid_mask = RelationshipBuilder.build_batch_masks(
            material_labels=material_labels,
            acquisition_labels=acquisition_labels,
            mask_same_acquisition=self.mask_same_acquisition,
        )

        # 2. Compute cosine similarity matrix scaled by temperature
        sim_matrix = torch.matmul(embeddings, embeddings.T) / self.temperature

        # 3. For numerical stability, subtract max per row over valid entries
        sim_max, _ = torch.max(sim_matrix * valid_mask - 1e9 * (1.0 - valid_mask), dim=1, keepdim=True)
        logits = sim_matrix - sim_max.detach()

        # 4. Denominator: sum of exp(logits) over valid comparisons
        exp_logits = torch.exp(logits) * valid_mask
        log_prob_denom = torch.log(exp_logits.sum(1, keepdim=True) + 1e-12)

        # 5. Log-probabilities: log(exp(S_ip) / sum_a exp(S_ia)) = S_ip - log_prob_denom
        log_prob = logits - log_prob_denom

        # 6. Mean over positives for each anchor with at least 1 positive
        num_pos_per_anchor = pos_mask.sum(1)
        valid_anchors = num_pos_per_anchor > 0

        if not valid_anchors.any():
            return torch.tensor(0.0, device=device, requires_grad=True)

        mean_log_prob_pos = (pos_mask * log_prob).sum(1)[valid_anchors] / num_pos_per_anchor[valid_anchors]

        # 7. Loss is negative mean over valid anchors
        loss = -mean_log_prob_pos.mean()
        return loss
