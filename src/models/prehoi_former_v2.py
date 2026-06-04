"""PreHOI-Former v2 dual-branch pilot model for HOT3D-Clips."""

from __future__ import annotations

import torch
from torch import nn


class PreHOIFormerV2(nn.Module):
    """Dual-branch candidate ranker with a separate future-pose decoder."""

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
        use_text: bool = False,
        use_attention: bool = False,
        pose_uses_candidates: bool = True,
        detach_pose_from_ranking: bool = False,
        detach_ranking_from_pose: bool = False,
    ) -> None:
        super().__init__()
        self.use_text = bool(use_text)
        self.use_attention = bool(use_attention)
        self.pose_uses_candidates = bool(pose_uses_candidates)
        self.detach_pose_from_ranking = bool(detach_pose_from_ranking)
        self.detach_ranking_from_pose = bool(detach_ranking_from_pose)

        self.temporal_encoder = nn.GRU(
            input_size=metadata_dim,
            hidden_size=hidden_dim,
            num_layers=max(1, num_layers),
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.temporal_norm = nn.LayerNorm(hidden_dim)
        self.ranking_context = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_dim),
        )
        self.pose_context = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.LayerNorm(hidden_dim),
        )

        self.rank_candidate_geometry = nn.Sequential(
            nn.Linear(candidate_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
        )
        self.pose_candidate_geometry = nn.Sequential(
            nn.Linear(candidate_dim, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
        )

        if self.use_text:
            self.rank_candidate_text = nn.Sequential(
                nn.Linear(text_dim, hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
            )
            self.pose_candidate_text = nn.Sequential(
                nn.Linear(text_dim, hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(hidden_dim, hidden_dim),
                nn.LayerNorm(hidden_dim),
            )
        else:
            self.rank_candidate_text = None
            self.pose_candidate_text = None

        if self.use_attention:
            attention_layer = nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=hidden_dim * 4,
                dropout=dropout,
                activation="gelu",
                batch_first=True,
                norm_first=True,
            )
            self.ranking_attention = nn.TransformerEncoder(
                attention_layer,
                num_layers=max(1, num_layers),
            )
        else:
            self.ranking_attention = None

        self.rank_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )
        pose_input_dim = hidden_dim * (2 if self.pose_uses_candidates else 1)
        self.pose_head = nn.Sequential(
            nn.Linear(pose_input_dim, hidden_dim * 2),
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

        _, hidden = self.temporal_encoder(metadata_features)
        temporal_context = self.temporal_norm(hidden[-1])

        ranking_source = temporal_context.detach() if self.detach_ranking_from_pose else temporal_context
        pose_source = temporal_context.detach() if self.detach_pose_from_ranking else temporal_context
        ranking_context = self.ranking_context(ranking_source)
        pose_context = self.pose_context(pose_source)

        ranking_candidates = self.rank_candidate_geometry(observation_object_candidates)
        pose_candidates = self.pose_candidate_geometry(observation_object_candidates)
        if self.use_text:
            if self.rank_candidate_text is None or self.pose_candidate_text is None:
                raise RuntimeError("Text encoders are not initialized.")
            text_rank = self.rank_candidate_text(candidate_text_features)
            text_pose = self.pose_candidate_text(candidate_text_features)
            ranking_candidates = ranking_candidates + text_rank
            pose_candidates = pose_candidates + text_pose

        if self.ranking_attention is not None:
            context_token = ranking_context.unsqueeze(1)
            attention_tokens = torch.cat([context_token, ranking_candidates], dim=1)
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
            attention_tokens = self.ranking_attention(attention_tokens, src_key_padding_mask=padding_mask)
            ranking_context = attention_tokens[:, 0]
            ranking_candidates = attention_tokens[:, 1:]

        repeated_context = ranking_context.unsqueeze(1).expand(-1, ranking_candidates.shape[1], -1)
        rank_features = torch.cat([repeated_context, ranking_candidates], dim=-1)
        candidate_scores = self.rank_head(rank_features).squeeze(-1)
        candidate_scores = candidate_scores.masked_fill(candidate_mask <= 0, -1.0e9)

        if self.pose_uses_candidates:
            pooled_pose_candidates = self._masked_mean(pose_candidates, candidate_mask)
            pose_features = torch.cat([pose_context, pooled_pose_candidates], dim=-1)
        else:
            pose_features = pose_context

        return {
            "candidate_scores": candidate_scores,
            "future_hand_pose": self.pose_head(pose_features),
        }

    def _masked_mean(self, values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        weights = mask.to(dtype=values.dtype).unsqueeze(-1)
        total = torch.sum(values * weights, dim=1)
        denom = torch.sum(weights, dim=1).clamp_min(1.0)
        return total / denom
