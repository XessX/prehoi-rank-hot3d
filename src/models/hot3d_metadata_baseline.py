"""Metadata-only pilot baseline for HOT3D-Clips proxy targets."""

from __future__ import annotations

import torch
from torch import nn


class HOT3DMetadataBaseline(nn.Module):
    """Small GRU encoder with object-class and MANO-pose heads."""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int,
        num_classes: int,
        pose_dim: int = 42,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.encoder = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=False,
        )
        self.norm = nn.LayerNorm(hidden_dim)
        self.dropout = nn.Dropout(dropout)
        self.object_head = nn.Linear(hidden_dim, num_classes)
        self.pose_head = nn.Linear(hidden_dim, pose_dim)

    def forward(self, features: torch.Tensor) -> dict[str, torch.Tensor]:
        if features.ndim != 3:
            raise ValueError(f"features must have shape [B, T, C], got {tuple(features.shape)}")
        _, hidden = self.encoder(features)
        pooled = hidden[-1]
        pooled = self.dropout(self.norm(pooled))
        return {
            "object_logits": self.object_head(pooled),
            "future_hand_pose": self.pose_head(pooled),
        }
