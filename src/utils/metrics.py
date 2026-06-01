"""Metrics for the pre-contact forecasting MVP."""

from __future__ import annotations

import torch


def accuracy(logits: torch.Tensor, targets: torch.Tensor) -> float:
    """Compute top-1 classification accuracy."""
    if logits.ndim != 2:
        raise ValueError(f"logits must have shape [B, C], got {tuple(logits.shape)}")
    if targets.ndim != 1:
        targets = targets.view(-1)
    predictions = logits.argmax(dim=-1)
    return float((predictions == targets.long()).float().mean().detach().cpu())


def top_k_accuracy(logits: torch.Tensor, targets: torch.Tensor, k: int = 5) -> float:
    """Compute top-k classification accuracy."""
    if logits.ndim != 2:
        raise ValueError(f"logits must have shape [B, C], got {tuple(logits.shape)}")
    if k <= 0:
        raise ValueError("k must be positive.")
    k = min(k, logits.shape[-1])
    if targets.ndim != 1:
        targets = targets.view(-1)
    topk = logits.topk(k, dim=-1).indices
    correct = topk.eq(targets.long().unsqueeze(-1)).any(dim=-1)
    return float(correct.float().mean().detach().cpu())


def mpjpe(predicted: torch.Tensor, target: torch.Tensor, reduction: str = "mean") -> float:
    """Mean per-joint position error for 3D hand-pose prediction."""
    if predicted.shape != target.shape:
        raise ValueError(
            f"predicted and target must have the same shape, got "
            f"{tuple(predicted.shape)} and {tuple(target.shape)}"
        )
    if predicted.shape[-1] != 3:
        raise ValueError("Last dimension must be xyz coordinates.")

    error = torch.linalg.norm(predicted - target, dim=-1)
    if reduction == "mean":
        return float(error.mean().detach().cpu())
    if reduction == "sum":
        return float(error.sum().detach().cpu())
    if reduction == "none":
        return error.detach().cpu()
    raise ValueError("reduction must be 'mean', 'sum', or 'none'.")

