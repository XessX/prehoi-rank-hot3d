"""Training loop for the MVP transformer baseline."""

from __future__ import annotations

from typing import Any

import torch
from torch.utils.data import DataLoader

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover - used only in minimal local environments.
    class tqdm:  # type: ignore[no-redef]
        """Tiny tqdm fallback so the smoke test can run before dependencies install."""

        def __init__(self, iterable, *args, **kwargs) -> None:
            self.iterable = iterable

        def __iter__(self):
            return iter(self.iterable)

        def set_postfix(self, *args, **kwargs) -> None:
            return None

from src.training.evaluate import evaluate, move_batch_to_device
from src.training.losses import compute_forecasting_loss


def train_one_epoch(
    model: torch.nn.Module,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    loss_weights: dict[str, float] | None = None,
) -> dict[str, float]:
    """Train for one epoch and return averaged loss values."""
    model.train()

    totals = {
        "loss": 0.0,
        "object_loss": 0.0,
        "action_loss": 0.0,
        "pose_loss": 0.0,
    }
    total_samples = 0

    progress = tqdm(dataloader, desc="train", leave=False)
    for batch in progress:
        batch = move_batch_to_device(batch, device)
        batch_size = int(batch["features"].shape[0])

        optimizer.zero_grad(set_to_none=True)
        outputs = model(batch["features"])
        loss, loss_values = compute_forecasting_loss(outputs, batch, loss_weights)
        loss.backward()
        optimizer.step()

        total_samples += batch_size
        for key in totals:
            totals[key] += loss_values[key] * batch_size

        progress.set_postfix(loss=f"{loss_values['loss']:.4f}")

    if total_samples == 0:
        return totals

    return {key: value / total_samples for key, value in totals.items()}


def fit(
    model: torch.nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epochs: int,
    loss_weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Run a small train/eval loop and return epoch history."""
    history: list[dict[str, Any]] = []
    for epoch in range(1, epochs + 1):
        train_metrics = train_one_epoch(model, train_loader, optimizer, device, loss_weights)
        val_metrics = evaluate(model, val_loader, device, loss_weights)
        row = {
            "epoch": epoch,
            "train": train_metrics,
            "val": val_metrics,
        }
        history.append(row)
        print(
            f"epoch={epoch} "
            f"train_loss={train_metrics['loss']:.4f} "
            f"val_loss={val_metrics['loss']:.4f} "
            f"val_obj_acc={val_metrics['object_accuracy']:.4f} "
            f"val_action_acc={val_metrics['action_accuracy']:.4f} "
            f"val_mpjpe={val_metrics['mpjpe']:.4f}"
        )
    return history
