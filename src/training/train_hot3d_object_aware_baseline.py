"""Pilot object-aware HOT3D-Clips baseline training.

This script validates the object-candidate metadata path only. It uses derived
proxy labels and must not be reported as a final paper result.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch.utils.data import DataLoader


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import HOT3DClipsDataset
from src.models.hot3d_object_aware_baseline import HOT3DObjectAwareBaseline
from src.utils.config import load_yaml

try:
    from sklearn.metrics import f1_score
except ImportError:  # pragma: no cover
    f1_score = None


PILOT_NOTICE = "PILOT DEBUG RUN -- NOT FINAL PAPER RESULT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train object-aware HOT3D-Clips pilot baseline.")
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def make_loader(dataset: HOT3DClipsDataset, batch_size: int, shuffle: bool, num_workers: int) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=collate_hot3d_object_batch,
    )


def collate_hot3d_object_batch(items: list[dict[str, Any]]) -> dict[str, Any]:
    tensor_keys = (
        "features",
        "frame_features",
        "observation_object_candidates",
        "object_candidates",
        "candidate_mask",
        "future_hand_pose",
        "target_object_proxy_label",
        "target_object_label",
        "proxy_confidence",
    )
    batch: dict[str, Any] = {
        key: torch.stack([item[key] for item in items], dim=0) for key in tensor_keys
    }
    for key in (
        "target_object_name",
        "candidate_object_names",
        "proxy_label_status",
        "clip_id",
        "sample_id",
        "object_input_frame",
        "target_object_proxy_frame",
        "input_uses_forecast_frame",
        "metadata",
    ):
        batch[key] = [item[key] for item in items]
    return batch


def move_batch(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        moved[key] = value.to(device) if isinstance(value, torch.Tensor) else value
    return moved


def compute_loss(
    outputs: dict[str, torch.Tensor],
    batch: dict[str, Any],
    pose_loss_weight: float,
) -> tuple[torch.Tensor, dict[str, float]]:
    class_loss = torch.nn.functional.cross_entropy(outputs["object_logits"], batch["target_object_proxy_label"])
    pose_loss = torch.nn.functional.mse_loss(outputs["future_hand_pose"], batch["future_hand_pose"])
    loss = class_loss + pose_loss_weight * pose_loss
    return loss, {
        "loss": float(loss.detach().cpu()),
        "classification_loss": float(class_loss.detach().cpu()),
        "pose_loss": float(pose_loss.detach().cpu()),
    }


def train_one_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    pose_loss_weight: float,
) -> dict[str, float]:
    model.train()
    totals = Counter()
    total_samples = 0
    for batch in loader:
        batch = move_batch(batch, device)
        batch_size = int(batch["features"].shape[0])
        optimizer.zero_grad(set_to_none=True)
        outputs = model(batch["features"], batch["observation_object_candidates"], batch["candidate_mask"])
        loss, loss_values = compute_loss(outputs, batch, pose_loss_weight)
        loss.backward()
        optimizer.step()

        total_samples += batch_size
        for key, value in loss_values.items():
            totals[key] += value * batch_size

    return {key: value / max(1, total_samples) for key, value in totals.items()}


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    pose_loss_weight: float,
) -> dict[str, float]:
    model.eval()
    totals = Counter()
    total_samples = 0
    correct = 0
    top3_correct = 0
    y_true: list[int] = []
    y_pred: list[int] = []

    for batch in loader:
        batch = move_batch(batch, device)
        batch_size = int(batch["features"].shape[0])
        outputs = model(batch["features"], batch["observation_object_candidates"], batch["candidate_mask"])
        _, loss_values = compute_loss(outputs, batch, pose_loss_weight)

        logits = outputs["object_logits"]
        labels = batch["target_object_proxy_label"]
        predictions = logits.argmax(dim=1)
        k = min(3, logits.shape[1])
        top3 = logits.topk(k=k, dim=1).indices

        pose_error = outputs["future_hand_pose"] - batch["future_hand_pose"]
        pose_mse = torch.mean(pose_error.square()).item()
        pose_mae = torch.mean(pose_error.abs()).item()

        total_samples += batch_size
        correct += int((predictions == labels).sum().item())
        top3_correct += int((top3 == labels.unsqueeze(1)).any(dim=1).sum().item())
        y_true.extend(int(item) for item in labels.cpu().tolist())
        y_pred.extend(int(item) for item in predictions.cpu().tolist())

        for key, value in loss_values.items():
            totals[key] += value * batch_size
        totals["pose_mse"] += pose_mse * batch_size
        totals["pose_mae"] += pose_mae * batch_size

    metrics = {key: value / max(1, total_samples) for key, value in totals.items()}
    metrics["object_accuracy"] = correct / max(1, total_samples)
    metrics["top3_accuracy"] = top3_correct / max(1, total_samples)
    metrics["macro_f1"] = (
        float(f1_score(y_true, y_pred, average="macro", zero_division=0))
        if f1_score is not None and y_true
        else float("nan")
    )
    return metrics


def class_distribution_warning(dataset: HOT3DClipsDataset, min_samples: int = 20) -> list[str]:
    warnings: list[str] = []
    for label, count in dataset.summary()["class_distribution"].items():
        if int(count) < min_samples:
            warnings.append(f"{label} has only {count} train samples")
    return warnings


def tensor_shape_preview(loader: DataLoader) -> dict[str, list[int]]:
    batch = next(iter(loader))
    return {
        "features": list(batch["features"].shape),
        "observation_object_candidates": list(batch["observation_object_candidates"].shape),
        "object_candidates": list(batch["object_candidates"].shape),
        "candidate_mask": list(batch["candidate_mask"].shape),
        "future_hand_pose": list(batch["future_hand_pose"].shape),
        "target_object_proxy_label": list(batch["target_object_proxy_label"].shape),
        "target_object_label": list(batch["target_object_label"].shape),
    }


def main() -> None:
    args = parse_args()
    config = load_yaml(args.config)
    set_seed(int(config.get("seed", 42)))

    requested_device = str(config.get("device", "cpu"))
    device = torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")
    print(PILOT_NOTICE)
    print("Proxy target labels are derived labels, not direct HOT3D ground truth.")
    print("No image tensors are used in this object-aware metadata pilot baseline.")

    label_map_path = config.get("label_map_path", "data/processed/hot3d_target_object_label_map.json")
    max_candidates = int(config.get("max_candidates", 8))
    allow_forecast_object_input = bool(config.get("allow_forecast_object_input", False))
    train_dataset = HOT3DClipsDataset(
        config["train_index"],
        mode="object_metadata",
        label_map_path=label_map_path,
        max_candidates=max_candidates,
        allow_forecast_object_input=allow_forecast_object_input,
    )
    val_dataset = HOT3DClipsDataset(
        config["val_index"],
        mode="object_metadata",
        label_map_path=label_map_path,
        max_candidates=max_candidates,
        allow_forecast_object_input=allow_forecast_object_input,
    )
    test_dataset = HOT3DClipsDataset(
        config["test_index"],
        mode="object_metadata",
        label_map_path=label_map_path,
        max_candidates=max_candidates,
        allow_forecast_object_input=allow_forecast_object_input,
    )

    batch_size = int(config.get("batch_size", 64))
    num_workers = int(config.get("num_workers", 0))
    train_loader = make_loader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = make_loader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = make_loader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    print("train_dataset_summary=" + json.dumps(train_dataset.summary(), sort_keys=True))
    print("tensor_shapes=" + json.dumps(tensor_shape_preview(train_loader), sort_keys=True))
    leakage_audit = {
        "object_input_source": "last_observation_frame",
        "allow_forecast_object_input": allow_forecast_object_input,
        "train": train_dataset.candidate_coverage_stats(),
        "val": val_dataset.candidate_coverage_stats(),
        "test": test_dataset.candidate_coverage_stats(),
    }
    print("candidate_coverage_stats=" + json.dumps(train_dataset.candidate_coverage_stats(), sort_keys=True))
    print("input_leakage_audit=" + json.dumps(leakage_audit, sort_keys=True))

    model = HOT3DObjectAwareBaseline(
        input_dim=train_dataset.frame_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        hidden_dim=int(config.get("hidden_dim", 64)),
        candidate_hidden_dim=int(config.get("candidate_hidden_dim", 64)),
        fusion_hidden_dim=int(config.get("fusion_hidden_dim", 128)),
        num_layers=int(config.get("num_layers", 1)),
        num_classes=len(train_dataset.class_to_idx),
        pose_dim=train_dataset.future_hand_pose_dim,
        dropout=float(config.get("dropout", 0.1)),
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config.get("learning_rate", 1e-3)),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )
    pose_loss_weight = float(config.get("pose_loss_weight", 0.1))
    epochs = int(config.get("epochs", 5))

    warnings = class_distribution_warning(train_dataset)
    if warnings:
        print("class_distribution_warning=" + json.dumps(warnings))

    history: list[dict[str, Any]] = []
    best_val_loss = float("inf")
    best_state: dict[str, Any] | None = None
    for epoch in range(1, epochs + 1):
        train_metrics = train_one_epoch(model, train_loader, optimizer, device, pose_loss_weight)
        val_metrics = evaluate(model, val_loader, device, pose_loss_weight)
        row = {"epoch": epoch, "train": train_metrics, "val": val_metrics}
        history.append(row)
        print(
            f"epoch={epoch} "
            f"train_loss={train_metrics['loss']:.4f} "
            f"train_cls={train_metrics['classification_loss']:.4f} "
            f"train_pose={train_metrics['pose_loss']:.4f} "
            f"val_loss={val_metrics['loss']:.4f} "
            f"val_acc={val_metrics['object_accuracy']:.4f} "
            f"val_top3={val_metrics['top3_accuracy']:.4f} "
            f"val_macro_f1={val_metrics['macro_f1']:.4f} "
            f"val_pose_mae={val_metrics['pose_mae']:.4f}"
        )
        if val_metrics["loss"] < best_val_loss:
            best_val_loss = val_metrics["loss"]
            best_state = {
                "model_state_dict": model.state_dict(),
                "config": config,
                "epoch": epoch,
                "val_metrics": val_metrics,
                "label_map": train_dataset.label_map,
                "notice": PILOT_NOTICE,
            }

    test_metrics = evaluate(model, test_loader, device, pose_loss_weight)
    metrics_payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "mode": "object_metadata",
        "config": config,
        "dataset": {
            "train": train_dataset.summary(),
            "val": val_dataset.summary(),
            "test": test_dataset.summary(),
        },
        "candidate_coverage_stats": leakage_audit,
        "input_leakage_audit": leakage_audit,
        "class_distribution_warnings": warnings,
        "history": history,
        "test": test_metrics,
    }

    metrics_path = Path(config.get("metrics_path", "results/logs/hot3d_object_aware_baseline_pilot.json"))
    checkpoint_path = Path(
        config.get("checkpoint_path", "results/checkpoints/hot3d_object_aware_baseline_pilot.pt")
    )
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)
    torch.save(best_state or {"model_state_dict": model.state_dict(), "config": config}, checkpoint_path)

    print("test_metrics=" + json.dumps(test_metrics, sort_keys=True))
    print(f"saved_metrics_path={metrics_path}")
    print(f"saved_checkpoint_path={checkpoint_path}")
    print(PILOT_NOTICE)


if __name__ == "__main__":
    main()
