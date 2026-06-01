"""Hand feature helpers."""

from __future__ import annotations

import torch


def flatten_hand_pose_sequence(hand_pose_3d: torch.Tensor) -> torch.Tensor:
    """Flatten hand joints from [T, J, 3] or [B, T, J, 3] into feature vectors."""
    if hand_pose_3d.ndim not in (3, 4):
        raise ValueError(
            "hand_pose_3d must have shape [T, J, 3] or [B, T, J, 3], "
            f"got {tuple(hand_pose_3d.shape)}"
        )
    if hand_pose_3d.shape[-1] != 3:
        raise ValueError("Last hand-pose dimension must contain xyz coordinates.")
    return hand_pose_3d.flatten(start_dim=-2)

