"""Object feature helpers."""

from __future__ import annotations

import torch


def object_pose_to_feature(object_pose: torch.Tensor) -> torch.Tensor:
    """Flatten a 4x4 object pose matrix into a compact numeric feature."""
    if object_pose.shape[-2:] != (4, 4):
        raise ValueError(f"object_pose must end with [4, 4], got {tuple(object_pose.shape)}")
    return object_pose.flatten(start_dim=-2)

