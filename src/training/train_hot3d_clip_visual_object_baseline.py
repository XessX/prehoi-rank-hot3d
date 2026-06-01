"""Pilot frozen-CLIP visual-object HOT3D-Clips baseline training."""

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

from src.datasets.hot3d_clips_dataset import HOT3DClipsDataset, class_distribution
from src.models.hot3d_visual_object_baseline import HOT3DVisualObjectBaseline
from src.utils.config import load_yaml

try:
    from sklearn.metrics import f1_score
except ImportError:  # pragma: no cover
    f1_score = None


PILOT_NOTICE = "PILOT DEBUG RUN -- NOT FINAL PAPER RESULT"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train frozen-CLIP HOT3D-Clips pilot baseline.")
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
        collate_fn=collate_hot3d_clip_visual_object_batch,
    )


def collate_hot3d_clip_visual_object_batch(items: list[dict[str, Any]]) -> dict[str, Any]:
    tensor_keys = (
        "features",
        "frame_features",
        "visual_features",
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
        "selected_stream",
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
        outputs = model(
            batch["features"],
            batch["visual_features"],
            batch["observation_object_candidates"],
            batch["candidate_mask"],
        )
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
        outputs = model(
            batch["features"],
            batch["visual_features"],
            batch["observation_object_candidates"],
            batch["candidate_mask"],
        )
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


def verify_feature_files(config: dict[str, Any]) -> None:
    for key in ("train_visual_features", "val_visual_features", "test_visual_features"):
        path = Path(config[key])
        if not path.exists():
            raise FileNotFoundError(f"Required CLIP feature file not found: {path}")


def verify_visual_alignment(dataset: HOT3DClipsDataset, split_name: str) -> dict[str, Any]:
    cache = dataset.visual_feature_cache
    if cache is None:
        raise RuntimeError(f"{split_name}: visual feature cache is not loaded.")
    sample_ids = [str(sample.get("sample_id")) for sample in dataset.samples]
    cached_ids = set(cache["sample_id_to_index"].keys())
    missing = [sample_id for sample_id in sample_ids if sample_id not in cached_ids]
    if missing:
        raise RuntimeError(f"{split_name}: missing cached CLIP features for {len(missing)} samples.")

    forecast_input = [
        str(sample.get("sample_id"))
        for sample in dataset.samples
        if dataset._object_input_frame_id(sample) == dataset._target_proxy_frame_id(sample)
        or sample.get("input_uses_forecast_frame") is True
    ]
    if forecast_input:
        raise RuntimeError(f"{split_name}: {len(forecast_input)} samples would use forecast-frame input.")

    metadata = cache.get("metadata", {})
    if metadata.get("feature_type") != "clip":
        raise ValueError(f"{split_name}: expected CLIP features, got {metadata.get('feature_type')!r}.")

    return {
        "split": split_name,
        "samples": len(sample_ids),
        "cache_rows": int(cache["features"].shape[0]),
        "cache_feature_shape": list(cache["features"].shape),
        "missing_cached_features": 0,
        "input_uses_forecast_frame": False,
        "feature_type": metadata.get("feature_type"),
        "model_name": metadata.get("model_name"),
        "pretrained": metadata.get("pretrained"),
        "missing_image_count": int(metadata.get("missing_image_count", 0)),
    }


def lightweight_dataset_summary(dataset: HOT3DClipsDataset, name: str) -> dict[str, Any]:
    cache = dataset.visual_feature_cache or {}
    features = cache.get("features")
    metadata = cache.get("metadata", {})
    return {
        "split": name,
        "num_samples": len(dataset),
        "num_object_classes": len(dataset.class_to_idx),
        "metadata_feature_dim": dataset.frame_feature_dim,
        "visual_feature_dim": dataset.visual_feature_dim,
        "object_candidate_feature_dim": dataset.object_candidate_feature_dim,
        "future_hand_pose_dim": dataset.future_hand_pose_dim,
        "mode": dataset.mode,
        "visual_features_path": str(dataset.visual_features_path),
        "class_distribution": class_distribution(dataset.samples),
        "visual_feature_cache": {
            "feature_shape": list(features.shape) if isinstance(features, np.ndarray) else None,
            "feature_type": metadata.get("feature_type"),
            "model_name": metadata.get("model_name"),
            "pretrained": metadata.get("pretrained"),
            "selected_stream_distribution": metadata.get("selected_stream_distribution", {}),
            "missing_image_count": int(metadata.get("missing_image_count", 0)),
            "note": metadata.get("note", ""),
        },
    }


def tensor_shape_preview(loader: DataLoader) -> dict[str, list[int]]:
    batch = next(iter(loader))
    return {
        "features": list(batch["features"].shape),
        "visual_features": list(batch["visual_features"].shape),
        "observation_object_candidates": list(batch["observation_object_candidates"].shape),
        "candidate_mask": list(batch["candidate_mask"].shape),
        "future_hand_pose": list(batch["future_hand_pose"].shape),
        "target_object_proxy_label": list(batch["target_object_proxy_label"].shape),
    }


def class_distribution_warning(dataset: HOT3DClipsDataset, min_samples: int = 20) -> list[str]:
    warnings: list[str] = []
    for label, count in class_distribution(dataset.samples).items():
        if int(count) < min_samples:
            warnings.append(f"{label} has only {count} train samples")
    return warnings


def load_test_metrics(path: str | Path) -> dict[str, Any] | None:
    metrics_path = Path(path)
    if not metrics_path.exists():
        return None
    with metrics_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    test_metrics = payload.get("test", {})
    return test_metrics if isinstance(test_metrics, dict) else None


def comparison_table(current: dict[str, float], baselines: dict[str, dict[str, Any] | None]) -> dict[str, Any]:
    keys = ("object_accuracy", "top3_accuracy", "macro_f1", "pose_mse", "pose_mae")
    table: dict[str, Any] = {
        "notice": "Pilot/debug comparison only. Not a final paper comparison.",
        "current_clip_visual_object": {key: float(current[key]) for key in keys if key in current},
        "baselines": {},
    }
    for name, metrics in baselines.items():
        if metrics is None:
            table["baselines"][name] = {"available": False}
            continue
        row: dict[str, Any] = {"available": True}
        for key in keys:
            if key in metrics and key in current:
                baseline_value = float(metrics[key])
                current_value = float(current[key])
                row[key] = {
                    "baseline": baseline_value,
                    "clip_visual_object": current_value,
                    "delta": current_value - baseline_value,
                }
        table["baselines"][name] = row
    return table


def main() -> None:
    args = parse_args()
    config = load_yaml(args.config)
    set_seed(int(config.get("seed", 42)))
    verify_feature_files(config)

    requested_device = str(config.get("device", "cpu"))
    device = torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")
    print(PILOT_NOTICE)
    print("Proxy target labels are derived labels, not direct HOT3D ground truth.")
    print("Using cached frozen CLIP features from observation frames only. CLIP is not trained.")

    if bool(config.get("allow_forecast_object_input", False)):
        raise ValueError("Frozen-CLIP visual-object pilot refuses allow_forecast_object_input=true.")

    label_map_path = config.get("label_map_path", "data/processed/hot3d_target_object_label_map.json")
    max_candidates = int(config.get("max_candidates", 8))
    train_dataset = HOT3DClipsDataset(
        config["train_index"],
        mode="object_visual_metadata",
        label_map_path=label_map_path,
        max_candidates=max_candidates,
        visual_features_path=config["train_visual_features"],
    )
    val_dataset = HOT3DClipsDataset(
        config["val_index"],
        mode="object_visual_metadata",
        label_map_path=label_map_path,
        max_candidates=max_candidates,
        visual_features_path=config["val_visual_features"],
    )
    test_dataset = HOT3DClipsDataset(
        config["test_index"],
        mode="object_visual_metadata",
        label_map_path=label_map_path,
        max_candidates=max_candidates,
        visual_features_path=config["test_visual_features"],
    )

    expected_visual_dim = int(config.get("visual_dim", train_dataset.visual_feature_dim))
    if train_dataset.visual_feature_dim != expected_visual_dim:
        raise ValueError(
            f"Expected visual_dim={expected_visual_dim}, got train visual_dim={train_dataset.visual_feature_dim}"
        )

    alignment_audit = {
        "train": verify_visual_alignment(train_dataset, "train"),
        "val": verify_visual_alignment(val_dataset, "val"),
        "test": verify_visual_alignment(test_dataset, "test"),
    }
    print("visual_alignment_audit=" + json.dumps(alignment_audit, sort_keys=True))

    batch_size = int(config.get("batch_size", 32))
    num_workers = int(config.get("num_workers", 0))
    train_loader = make_loader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = make_loader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = make_loader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    dataset_summaries = {
        "train": lightweight_dataset_summary(train_dataset, "train"),
        "val": lightweight_dataset_summary(val_dataset, "val"),
        "test": lightweight_dataset_summary(test_dataset, "test"),
    }
    batch_shapes = tensor_shape_preview(train_loader)
    print("dataset_shapes=" + json.dumps(dataset_summaries, sort_keys=True))
    print("batch_shapes=" + json.dumps(batch_shapes, sort_keys=True))

    model = HOT3DVisualObjectBaseline(
        metadata_dim=train_dataset.frame_feature_dim,
        visual_dim=train_dataset.visual_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        hidden_dim=int(config.get("hidden_dim", 64)),
        visual_hidden_dim=int(config.get("visual_hidden_dim", 64)),
        candidate_hidden_dim=int(config.get("candidate_hidden_dim", 64)),
        fusion_hidden_dim=int(config.get("fusion_hidden_dim", 160)),
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
        history.append({"epoch": epoch, "train": train_metrics, "val": val_metrics})
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
    comparisons = comparison_table(
        test_metrics,
        {
            "object_aware_metadata": load_test_metrics(
                config.get("object_aware_metrics_path", "results/logs/hot3d_object_aware_baseline_pilot.json")
            ),
            "visual_object_image_stats": load_test_metrics(
                config.get("image_stats_metrics_path", "results/logs/hot3d_visual_object_baseline_pilot.json")
            ),
        },
    )
    metrics_payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "mode": "object_visual_metadata_clip",
        "config": config,
        "dataset": dataset_summaries,
        "batch_shapes": batch_shapes,
        "visual_alignment_audit": alignment_audit,
        "class_distribution_warnings": warnings,
        "history": history,
        "test": test_metrics,
        "pilot_comparison_table": comparisons,
    }

    metrics_path = Path(config.get("metrics_path", "results/logs/hot3d_clip_visual_object_baseline_pilot.json"))
    checkpoint_path = Path(
        config.get("checkpoint_path", "results/checkpoints/hot3d_clip_visual_object_baseline_pilot.pt")
    )
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)
    torch.save(best_state or {"model_state_dict": model.state_dict(), "config": config}, checkpoint_path)

    print("test_metrics=" + json.dumps(test_metrics, sort_keys=True))
    print("pilot_comparison_table=" + json.dumps(comparisons, sort_keys=True))
    print(f"saved_metrics_path={metrics_path}")
    print(f"saved_checkpoint_path={checkpoint_path}")
    print(PILOT_NOTICE)


if __name__ == "__main__":
    main()
