"""Temporal transformer baseline for pre-contact forecasting."""

from __future__ import annotations

import torch
from torch import nn


class BaselineTransformer(nn.Module):
    """Simple transformer over per-frame feature sequences.

    Input:
        features: Tensor[B, T, input_dim]

    Outputs:
        object_logits: Tensor[B, num_objects]
        action_logits: Tensor[B, num_actions]
        future_hand_pose_3d: Tensor[B, future_steps, num_hand_joints, 3]
    """

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        num_layers: int,
        num_heads: int,
        dropout: float,
        num_objects: int,
        num_actions: int,
        future_steps: int,
        num_hand_joints: int,
        max_seq_len: int = 64,
        pooling: str = "last",
    ) -> None:
        super().__init__()
        if hidden_dim % num_heads != 0:
            raise ValueError("hidden_dim must be divisible by num_heads.")
        if pooling not in {"last", "mean"}:
            raise ValueError("pooling must be 'last' or 'mean'.")

        self.future_steps = future_steps
        self.num_hand_joints = num_hand_joints
        self.max_seq_len = max_seq_len
        self.pooling = pooling

        self.input_projection = nn.Linear(input_dim, hidden_dim)
        self.position_embedding = nn.Parameter(torch.zeros(1, max_seq_len, hidden_dim))

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dim_feedforward=hidden_dim * 4,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.norm = nn.LayerNorm(hidden_dim)

        self.object_head = nn.Linear(hidden_dim, num_objects)
        self.action_head = nn.Linear(hidden_dim, num_actions)
        self.pose_head = nn.Linear(hidden_dim, future_steps * num_hand_joints * 3)

        self._reset_parameters()

    def _reset_parameters(self) -> None:
        nn.init.normal_(self.position_embedding, mean=0.0, std=0.02)

    def forward(self, features: torch.Tensor) -> dict[str, torch.Tensor]:
        if features.ndim != 3:
            raise ValueError(f"features must have shape [B, T, C], got {tuple(features.shape)}")

        batch_size, seq_len, _ = features.shape
        if seq_len > self.max_seq_len:
            raise ValueError(
                f"Sequence length {seq_len} exceeds max_seq_len {self.max_seq_len}."
            )

        x = self.input_projection(features)
        x = x + self.position_embedding[:, :seq_len, :]
        x = self.encoder(x)
        x = self.norm(x)

        if self.pooling == "mean":
            pooled = x.mean(dim=1)
        else:
            pooled = x[:, -1, :]

        pose = self.pose_head(pooled).view(
            batch_size,
            self.future_steps,
            self.num_hand_joints,
            3,
        )

        return {
            "object_logits": self.object_head(pooled),
            "action_logits": self.action_head(pooled),
            "future_hand_pose_3d": pose,
        }

