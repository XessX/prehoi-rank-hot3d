"""PreHOI-Former v1 pilot model for HOT3D-Clips candidate forecasting."""

from __future__ import annotations

import torch
from torch import nn


class PreHOIFormerV1(nn.Module):
    """Candidate-level multimodal attention model for pre-contact HOI forecasting."""

    def __init__(
        self,
        metadata_dim: int,
        candidate_dim: int,
        text_dim: int,
        hidden_dim: int,
        num_heads: int,
        num_layers: int,
        pose_dim: int = 42,
        dropout: float = 0.1,
        use_text: bool = True,
        use_candidate_attention: bool = True,
    ) -> None:
        super().__init__()
        self.use_text = bool(use_text)
        self.use_candidate_attention = bool(use_candidate_attention)

        self.temporal_projection = nn.Linear(metadata_dim, hidden_dim)
        temporal_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.temporal_encoder = nn.TransformerEncoder(temporal_layer, num_layers=max(1, num_layers))
        self.temporal_norm = nn.LayerNorm(hidden_dim)

        self.candidate_geometry_encoder = nn.Sequential(
            nn.Linear(candidate_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.candidate_text_encoder = nn.Sequential(
            nn.Linear(text_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
        )
        self.candidate_norm = nn.LayerNorm(hidden_dim)

        if self.use_candidate_attention:
            fusion_layer = nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=hidden_dim * 4,
                dropout=dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.candidate_fusion = nn.TransformerEncoder(fusion_layer, num_layers=max(1, num_layers))
        else:
            self.candidate_fusion = None

        self.rank_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )
        self.pose_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim * 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_dim * 2),
            nn.Linear(hidden_dim * 2, pose_dim),
        )

    def forward(
        self,
        metadata_features: torch.Tensor,
        observation_object_candidates: torch.Tensor,
        candidate_text_features: torch.Tensor,
        candidate_mask: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        if metadata_features.ndim != 3:
            raise ValueError(f"metadata_features must have shape [B, T, C], got {tuple(metadata_features.shape)}")
        if observation_object_candidates.ndim != 3:
            raise ValueError(
                "observation_object_candidates must have shape [B, K, C], "
                f"got {tuple(observation_object_candidates.shape)}"
            )
        if candidate_text_features.ndim != 3:
            raise ValueError(
                "candidate_text_features must have shape [B, K, C], "
                f"got {tuple(candidate_text_features.shape)}"
            )
        if candidate_mask.ndim != 2:
            raise ValueError(f"candidate_mask must have shape [B, K], got {tuple(candidate_mask.shape)}")

        temporal_tokens = self.temporal_projection(metadata_features)
        temporal_tokens = self.temporal_encoder(temporal_tokens)
        temporal_context = self.temporal_norm(temporal_tokens.mean(dim=1))

        geometry_tokens = self.candidate_geometry_encoder(observation_object_candidates)
        if self.use_text:
            text_tokens = self.candidate_text_encoder(candidate_text_features)
            candidate_tokens = geometry_tokens + text_tokens
        else:
            candidate_tokens = geometry_tokens
        candidate_tokens = self.candidate_norm(candidate_tokens)

        if self.candidate_fusion is not None:
            context_token = temporal_context.unsqueeze(1)
            fusion_tokens = torch.cat([context_token, candidate_tokens], dim=1)
            padding_mask = torch.cat(
                [
                    torch.zeros(
                        (candidate_mask.shape[0], 1),
                        dtype=torch.bool,
                        device=candidate_mask.device,
                    ),
                    candidate_mask <= 0,
                ],
                dim=1,
            )
            fused_tokens = self.candidate_fusion(fusion_tokens, src_key_padding_mask=padding_mask)
            fused_context = fused_tokens[:, 0]
            fused_candidates = fused_tokens[:, 1:]
        else:
            fused_context = temporal_context
            fused_candidates = candidate_tokens

        repeated_context = fused_context.unsqueeze(1).expand(-1, fused_candidates.shape[1], -1)
        rank_features = torch.cat([repeated_context, fused_candidates], dim=-1)
        candidate_scores = self.rank_head(rank_features).squeeze(-1)
        candidate_scores = candidate_scores.masked_fill(candidate_mask <= 0, -1.0e9)

        pooled_candidates = self._masked_mean(fused_candidates, candidate_mask)
        pose_features = torch.cat([fused_context, pooled_candidates], dim=-1)
        return {
            "candidate_scores": candidate_scores,
            "future_hand_pose": self.pose_head(pose_features),
        }

    def _masked_mean(self, values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        weights = mask.to(dtype=values.dtype).unsqueeze(-1)
        total = torch.sum(values * weights, dim=1)
        denom = torch.sum(weights, dim=1).clamp_min(1.0)
        return total / denom
