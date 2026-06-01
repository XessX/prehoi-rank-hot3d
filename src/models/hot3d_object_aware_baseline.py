"""Object-aware pilot baseline for HOT3D-Clips proxy targets."""

from __future__ import annotations

import torch
from torch import nn


class HOT3DObjectAwareBaseline(nn.Module):
    """Fuse temporal hand metadata with padded object-candidate features."""

    def __init__(
        self,
        input_dim: int,
        candidate_dim: int,
        hidden_dim: int,
        candidate_hidden_dim: int,
        fusion_hidden_dim: int,
        num_layers: int,
        num_classes: int,
        pose_dim: int = 42,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.temporal_encoder = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=False,
        )
        self.temporal_norm = nn.LayerNorm(hidden_dim)

        self.candidate_encoder = nn.Sequential(
            nn.Linear(candidate_dim, candidate_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(candidate_hidden_dim, candidate_hidden_dim),
            nn.ReLU(),
        )
        self.candidate_attention = nn.Linear(candidate_hidden_dim, 1)
        self.candidate_norm = nn.LayerNorm(candidate_hidden_dim)

        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim + candidate_hidden_dim, fusion_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.LayerNorm(fusion_hidden_dim),
        )
        self.object_head = nn.Linear(fusion_hidden_dim, num_classes)
        self.pose_head = nn.Linear(fusion_hidden_dim, pose_dim)

    def forward(
        self,
        features: torch.Tensor,
        observation_object_candidates: torch.Tensor,
        candidate_mask: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        if features.ndim != 3:
            raise ValueError(f"features must have shape [B, T, C], got {tuple(features.shape)}")
        if observation_object_candidates.ndim != 3:
            raise ValueError(
                "observation_object_candidates must have shape [B, K, C], "
                f"got {tuple(observation_object_candidates.shape)}"
            )
        if candidate_mask.ndim != 2:
            raise ValueError(f"candidate_mask must have shape [B, K], got {tuple(candidate_mask.shape)}")

        _, hidden = self.temporal_encoder(features)
        temporal = self.temporal_norm(hidden[-1])

        encoded_candidates = self.candidate_encoder(observation_object_candidates)
        candidate_context = self._masked_attention_pool(encoded_candidates, candidate_mask)
        candidate_context = self.candidate_norm(candidate_context)

        fused = self.fusion(torch.cat([temporal, candidate_context], dim=-1))
        return {
            "object_logits": self.object_head(fused),
            "future_hand_pose": self.pose_head(fused),
        }

    def _masked_attention_pool(self, encoded: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        mask = mask.to(dtype=encoded.dtype)
        valid = mask > 0
        logits = self.candidate_attention(encoded).squeeze(-1)
        logits = logits.masked_fill(~valid, -1.0e9)
        attention = torch.softmax(logits, dim=1) * mask
        attention = attention / attention.sum(dim=1, keepdim=True).clamp_min(1.0e-6)
        return torch.sum(encoded * attention.unsqueeze(-1), dim=1)
