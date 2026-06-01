"""Loss composition for pre-contact forecasting."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F


def compute_forecasting_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, Any],
    loss_weights: dict[str, float] | None = None,
) -> tuple[torch.Tensor, dict[str, float]]:
    """Compute object, action, and future-pose losses."""
    weights = {
        "object": 1.0,
        "action": 1.0,
        "pose": 1.0,
    }
    if loss_weights:
        weights.update(loss_weights)

    object_loss = F.cross_entropy(outputs["object_logits"], batch["object_id"].long())
    action_loss = F.cross_entropy(outputs["action_logits"], batch["interaction_label"].long())
    pose_loss = F.mse_loss(outputs["future_hand_pose_3d"], batch["future_hand_pose_3d"])

    total = (
        weights["object"] * object_loss
        + weights["action"] * action_loss
        + weights["pose"] * pose_loss
    )

    values = {
        "loss": float(total.detach().cpu()),
        "object_loss": float(object_loss.detach().cpu()),
        "action_loss": float(action_loss.detach().cpu()),
        "pose_loss": float(pose_loss.detach().cpu()),
    }
    return total, values

