"""Evaluation loop for the MVP forecasting task."""

from __future__ import annotations

from typing import Any

import torch
from torch.utils.data import DataLoader

from src.training.losses import compute_forecasting_loss
from src.utils.metrics import accuracy, mpjpe


def move_batch_to_device(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    """Move tensor values in a dataloader batch to a device."""
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        moved[key] = value.to(device) if torch.is_tensor(value) else value
    return moved


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    dataloader: DataLoader,
    device: torch.device,
    loss_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Evaluate the model and return averaged metrics."""
    model.eval()

    totals = {
        "loss": 0.0,
        "object_loss": 0.0,
        "action_loss": 0.0,
        "pose_loss": 0.0,
        "object_accuracy": 0.0,
        "action_accuracy": 0.0,
        "mpjpe": 0.0,
    }
    total_samples = 0

    for batch in dataloader:
        batch = move_batch_to_device(batch, device)
        outputs = model(batch["features"])
        _, loss_values = compute_forecasting_loss(outputs, batch, loss_weights)

        batch_size = int(batch["features"].shape[0])
        total_samples += batch_size

        totals["loss"] += loss_values["loss"] * batch_size
        totals["object_loss"] += loss_values["object_loss"] * batch_size
        totals["action_loss"] += loss_values["action_loss"] * batch_size
        totals["pose_loss"] += loss_values["pose_loss"] * batch_size
        totals["object_accuracy"] += (
            accuracy(outputs["object_logits"], batch["object_id"]) * batch_size
        )
        totals["action_accuracy"] += (
            accuracy(outputs["action_logits"], batch["interaction_label"]) * batch_size
        )
        totals["mpjpe"] += (
            mpjpe(outputs["future_hand_pose_3d"], batch["future_hand_pose_3d"]) * batch_size
        )

    if total_samples == 0:
        return totals

    return {key: value / total_samples for key, value in totals.items()}

