"""Candidate-ranking pilot model for HOT3D-Clips proxy targets."""

from __future__ import annotations

import torch
from torch import nn


class HOT3DCandidateRanker(nn.Module):
    """Score observed object candidates and regress future MANO pose."""

    def __init__(
        self,
        metadata_dim: int,
        candidate_dim: int,
        hidden_dim: int,
        candidate_hidden_dim: int,
        fusion_hidden_dim: int,
        num_layers: int,
        pose_dim: int = 42,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.temporal_encoder = nn.GRU(
            input_size=metadata_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.temporal_norm = nn.LayerNorm(hidden_dim)

        self.candidate_encoder = nn.Sequential(
            nn.Linear(candidate_dim, candidate_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(candidate_hidden_dim, candidate_hidden_dim),
            nn.ReLU(),
        )
        self.rank_head = nn.Sequential(
            nn.Linear(hidden_dim + candidate_hidden_dim, fusion_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(fusion_hidden_dim, 1),
        )
        self.pose_head = nn.Sequential(
            nn.Linear(hidden_dim + candidate_hidden_dim, fusion_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.LayerNorm(fusion_hidden_dim),
            nn.Linear(fusion_hidden_dim, pose_dim),
        )

    def forward(
        self,
        metadata_features: torch.Tensor,
        observation_object_candidates: torch.Tensor,
        candidate_mask: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        if metadata_features.ndim != 3:
            raise ValueError(f"metadata_features must have shape [B, T, C], got {tuple(metadata_features.shape)}")
        if observation_object_candidates.ndim != 3:
            raise ValueError(
                "observation_object_candidates must have shape [B, K, C], "
                f"got {tuple(observation_object_candidates.shape)}"
            )
        if candidate_mask.ndim != 2:
            raise ValueError(f"candidate_mask must have shape [B, K], got {tuple(candidate_mask.shape)}")

        _, hidden = self.temporal_encoder(metadata_features)
        temporal_context = self.temporal_norm(hidden[-1])

        candidate_context = self.candidate_encoder(observation_object_candidates)
        repeated_temporal = temporal_context.unsqueeze(1).expand(-1, candidate_context.shape[1], -1)
        rank_features = torch.cat([repeated_temporal, candidate_context], dim=-1)
        candidate_scores = self.rank_head(rank_features).squeeze(-1)
        candidate_scores = candidate_scores.masked_fill(candidate_mask <= 0, -1.0e9)

        pooled_candidates = self._masked_mean(candidate_context, candidate_mask)
        pose_features = torch.cat([temporal_context, pooled_candidates], dim=-1)
        return {
            "candidate_scores": candidate_scores,
            "future_hand_pose": self.pose_head(pose_features),
        }

    def _masked_mean(self, values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        weights = mask.to(dtype=values.dtype).unsqueeze(-1)
        total = torch.sum(values * weights, dim=1)
        denom = torch.sum(weights, dim=1).clamp_min(1.0)
        return total / denom
