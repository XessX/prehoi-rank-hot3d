"""Visual-object pilot baseline for HOT3D-Clips proxy targets."""

from __future__ import annotations

import torch
from torch import nn


class HOT3DVisualObjectBaseline(nn.Module):
    """Fuse metadata, cached visual statistics, and object candidates."""

    def __init__(
        self,
        metadata_dim: int,
        visual_dim: int,
        candidate_dim: int,
        hidden_dim: int,
        visual_hidden_dim: int,
        candidate_hidden_dim: int,
        fusion_hidden_dim: int,
        num_layers: int,
        num_classes: int,
        pose_dim: int = 42,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.metadata_encoder = nn.GRU(
            input_size=metadata_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.metadata_norm = nn.LayerNorm(hidden_dim)

        self.visual_encoder = nn.GRU(
            input_size=visual_dim,
            hidden_size=visual_hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.visual_norm = nn.LayerNorm(visual_hidden_dim)

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
            nn.Linear(hidden_dim + visual_hidden_dim + candidate_hidden_dim, fusion_hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.LayerNorm(fusion_hidden_dim),
        )
        self.object_head = nn.Linear(fusion_hidden_dim, num_classes)
        self.pose_head = nn.Linear(fusion_hidden_dim, pose_dim)

    def forward(
        self,
        metadata_features: torch.Tensor,
        visual_features: torch.Tensor,
        observation_object_candidates: torch.Tensor,
        candidate_mask: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        if metadata_features.ndim != 3:
            raise ValueError(
                f"metadata_features must have shape [B, T, C], got {tuple(metadata_features.shape)}"
            )
        if visual_features.ndim != 3:
            raise ValueError(f"visual_features must have shape [B, T, C], got {tuple(visual_features.shape)}")
        if observation_object_candidates.ndim != 3:
            raise ValueError(
                "observation_object_candidates must have shape [B, K, C], "
                f"got {tuple(observation_object_candidates.shape)}"
            )
        if candidate_mask.ndim != 2:
            raise ValueError(f"candidate_mask must have shape [B, K], got {tuple(candidate_mask.shape)}")

        _, metadata_hidden = self.metadata_encoder(metadata_features)
        metadata_context = self.metadata_norm(metadata_hidden[-1])

        _, visual_hidden = self.visual_encoder(visual_features)
        visual_context = self.visual_norm(visual_hidden[-1])

        encoded_candidates = self.candidate_encoder(observation_object_candidates)
        candidate_context = self._masked_attention_pool(encoded_candidates, candidate_mask)
        candidate_context = self.candidate_norm(candidate_context)

        fused = self.fusion(torch.cat([metadata_context, visual_context, candidate_context], dim=-1))
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
