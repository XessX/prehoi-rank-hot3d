"""Pilot vision-language candidate-ranking HOT3D-Clips baseline training."""

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
from src.models.hot3d_vl_candidate_ranker import HOT3DVLCandidateRanker
from src.training.train_hot3d_candidate_ranker import (
    PILOT_NOTICE,
    compute_loss,
    load_test_metrics,
    print_position_baseline_warning,
    ranking_coverage,
    set_seed,
)
from src.utils.config import load_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train HOT3D-Clips vision-language candidate ranker.")
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


def load_text_feature_cache(path: str | Path) -> dict[str, Any]:
    feature_path = Path(path)
    if not feature_path.exists():
        raise FileNotFoundError(f"Text feature cache not found: {feature_path}")
    with np.load(feature_path, allow_pickle=True) as npz:
        object_names = [str(item) for item in npz["object_names"].tolist()]
        text_features = np.array(npz["text_features"], dtype=np.float32)
        metadata_json = str(npz["metadata_json"].item()) if "metadata_json" in npz else "{}"
    if text_features.ndim != 2:
        raise ValueError(f"Expected text features with shape [N, C], got {tuple(text_features.shape)}")
    if text_features.shape[0] != len(object_names):
        raise ValueError("Text feature row count does not match object_names length.")
    if int(np.isnan(text_features).sum()) > 0:
        raise ValueError("Text feature cache contains NaN values.")
    try:
        metadata = json.loads(metadata_json)
    except json.JSONDecodeError:
        metadata = {"metadata_json": metadata_json}
    return {
        "path": str(feature_path),
        "object_names": object_names,
        "text_features": text_features,
        "object_to_index": {name: index for index, name in enumerate(object_names)},
        "metadata": metadata,
    }


class CandidateTextCollator:
    """Collate HOT3D candidate-ranker samples and attach frozen text features."""

    def __init__(self, text_cache: dict[str, Any]) -> None:
        self.text_features = torch.tensor(text_cache["text_features"], dtype=torch.float32)
        self.object_to_index = {str(key): int(value) for key, value in text_cache["object_to_index"].items()}
        self.text_dim = int(self.text_features.shape[-1])

    def __call__(self, items: list[dict[str, Any]]) -> dict[str, Any]:
        tensor_keys = (
            "features",
            "frame_features",
            "observation_object_candidates",
            "object_candidates",
            "candidate_mask",
            "candidate_target_index",
            "candidate_target_mask",
            "rankable",
            "future_hand_pose",
            "target_object_proxy_label",
            "target_object_label",
            "proxy_confidence",
        )
        batch: dict[str, Any] = {
            key: torch.stack([item[key] for item in items], dim=0) for key in tensor_keys
        }
        candidate_text = torch.zeros(
            (
                len(items),
                int(batch["candidate_mask"].shape[1]),
                self.text_dim,
            ),
            dtype=torch.float32,
        )
        missing_names: Counter[str] = Counter()
        for batch_index, item in enumerate(items):
            names = [str(name) for name in item["candidate_object_names"]]
            mask = item["candidate_mask"]
            for candidate_index in range(int(mask.shape[0])):
                if float(mask[candidate_index].item()) <= 0.0:
                    continue
                if candidate_index >= len(names):
                    missing_names["<missing-name>"] += 1
                    continue
                name = names[candidate_index]
                text_index = self.object_to_index.get(name)
                if text_index is None:
                    missing_names[name] += 1
                    continue
                candidate_text[batch_index, candidate_index] = self.text_features[text_index]
        if missing_names:
            raise KeyError(
                "Candidate object names missing from text feature cache: "
                + json.dumps(dict(missing_names.most_common()), sort_keys=True)
            )
        batch["candidate_text_features"] = candidate_text

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


def make_loader(
    dataset: HOT3DClipsDataset,
    text_cache: dict[str, Any],
    batch_size: int,
    shuffle: bool,
    num_workers: int,
) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=CandidateTextCollator(text_cache),
    )


def move_batch(batch: dict[str, Any], device: torch.device) -> dict[str, Any]:
    moved: dict[str, Any] = {}
    for key, value in batch.items():
        moved[key] = value.to(device) if isinstance(value, torch.Tensor) else value
    return moved


def assert_no_forecast_input(batch: dict[str, Any]) -> None:
    if any(bool(value) for value in batch.get("input_uses_forecast_frame", [])):
        raise RuntimeError("VL candidate ranker received forecast-frame input features.")


def train_one_epoch(
    model: torch.nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    pose_loss_weight: float,
    ranking_loss_weight: float,
) -> dict[str, float]:
    model.train()
    totals = Counter()
    total_samples = 0
    for batch in loader:
        assert_no_forecast_input(batch)
        batch = move_batch(batch, device)
        batch_size = int(batch["features"].shape[0])
        optimizer.zero_grad(set_to_none=True)
        outputs = model(
            batch["features"],
            batch["observation_object_candidates"],
            batch["candidate_text_features"],
            batch["candidate_mask"],
        )
        loss, loss_values = compute_loss(outputs, batch, pose_loss_weight, ranking_loss_weight)
        loss.backward()
        optimizer.step()

        total_samples += batch_size
        for key, value in loss_values.items():
            totals[key] += value * (batch_size if key != "rankable_count" else 1)

    metrics = {
        key: value / max(1, total_samples)
        for key, value in totals.items()
        if key != "rankable_count"
    }
    metrics["rankable_count"] = float(totals["rankable_count"])
    return metrics


@torch.no_grad()
def evaluate(
    model: torch.nn.Module,
    loader: DataLoader,
    device: torch.device,
    pose_loss_weight: float,
    ranking_loss_weight: float,
) -> dict[str, float]:
    model.eval()
    totals = Counter()
    total_samples = 0
    rankable_total = 0
    top1_correct = 0
    top3_correct = 0
    reciprocal_rank_sum = 0.0

    for batch in loader:
        assert_no_forecast_input(batch)
        batch = move_batch(batch, device)
        batch_size = int(batch["features"].shape[0])
        outputs = model(
            batch["features"],
            batch["observation_object_candidates"],
            batch["candidate_text_features"],
            batch["candidate_mask"],
        )
        _, loss_values = compute_loss(outputs, batch, pose_loss_weight, ranking_loss_weight)

        scores = outputs["candidate_scores"]
        target = batch["candidate_target_index"]
        rankable = batch["rankable"].bool()
        if bool(rankable.any()):
            rankable_scores = scores[rankable]
            rankable_target = target[rankable]
            predictions = rankable_scores.argmax(dim=1)
            k = min(3, rankable_scores.shape[1])
            top3 = rankable_scores.topk(k=k, dim=1).indices
            sorted_indices = rankable_scores.argsort(dim=1, descending=True)
            target_positions = (sorted_indices == rankable_target.unsqueeze(1)).nonzero(as_tuple=False)
            reciprocal_rank_sum += float(torch.sum(1.0 / (target_positions[:, 1].float() + 1.0)).item())
            rankable_total += int(rankable.sum().item())
            top1_correct += int((predictions == rankable_target).sum().item())
            top3_correct += int((top3 == rankable_target.unsqueeze(1)).any(dim=1).sum().item())

        pose_error = outputs["future_hand_pose"] - batch["future_hand_pose"]
        pose_mse = torch.mean(pose_error.square()).item()
        pose_mae = torch.mean(pose_error.abs()).item()

        total_samples += batch_size
        for key, value in loss_values.items():
            totals[key] += value * (batch_size if key != "rankable_count" else 1)
        totals["pose_mse"] += pose_mse * batch_size
        totals["pose_mae"] += pose_mae * batch_size

    metrics = {
        key: value / max(1, total_samples)
        for key, value in totals.items()
        if key != "rankable_count"
    }
    metrics["rankable_count"] = float(rankable_total)
    metrics["candidate_top1_accuracy"] = top1_correct / max(1, rankable_total)
    metrics["candidate_top3_accuracy"] = top3_correct / max(1, rankable_total)
    metrics["mean_reciprocal_rank"] = reciprocal_rank_sum / max(1, rankable_total)
    return metrics


def tensor_shape_preview(loader: DataLoader) -> dict[str, list[int]]:
    batch = next(iter(loader))
    assert_no_forecast_input(batch)
    return {
        "features": list(batch["features"].shape),
        "observation_object_candidates": list(batch["observation_object_candidates"].shape),
        "candidate_text_features": list(batch["candidate_text_features"].shape),
        "candidate_mask": list(batch["candidate_mask"].shape),
        "candidate_target_index": list(batch["candidate_target_index"].shape),
        "candidate_target_mask": list(batch["candidate_target_mask"].shape),
        "rankable": list(batch["rankable"].shape),
        "future_hand_pose": list(batch["future_hand_pose"].shape),
    }


def comparison_with_candidate_ranker(current: dict[str, float], previous: dict[str, Any] | None) -> dict[str, Any]:
    if previous is None:
        return {"available": False}
    return {
        "available": True,
        "notice": "Pilot/debug comparison only. Both runs use derived proxy labels, not direct HOT3D ground truth.",
        "candidate_ranker_top1": previous.get("candidate_top1_accuracy"),
        "vl_candidate_ranker_top1": current.get("candidate_top1_accuracy"),
        "candidate_ranker_top3": previous.get("candidate_top3_accuracy"),
        "vl_candidate_ranker_top3": current.get("candidate_top3_accuracy"),
        "candidate_ranker_mrr": previous.get("mean_reciprocal_rank"),
        "vl_candidate_ranker_mrr": current.get("mean_reciprocal_rank"),
        "candidate_ranker_pose_mse": previous.get("pose_mse"),
        "vl_candidate_ranker_pose_mse": current.get("pose_mse"),
        "candidate_ranker_pose_mae": previous.get("pose_mae"),
        "vl_candidate_ranker_pose_mae": current.get("pose_mae"),
    }


def main() -> None:
    args = parse_args()
    config = load_yaml(args.config)
    set_seed(int(config.get("seed", 42)))

    candidate_order = str(config.get("candidate_order", "stable_uid"))
    if candidate_order != "stable_uid":
        raise ValueError("Vision-language candidate ranker requires candidate_order: stable_uid.")
    candidate_order_seed = int(config.get("candidate_order_seed", config.get("seed", 42)))

    requested_device = str(config.get("device", "cpu"))
    device = torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")
    print(PILOT_NOTICE)
    print("Proxy target labels are derived labels, not direct HOT3D ground truth.")
    print("Frozen CLIP text features are used. CLIP is not trained.")
    print("Candidate features and text features are observation-frame candidate inputs only.")
    print(f"candidate_order={candidate_order}")

    text_cache = load_text_feature_cache(config["text_features_path"])
    print(
        "text_feature_summary="
        + json.dumps(
            {
                "path": text_cache["path"],
                "num_object_classes": len(text_cache["object_names"]),
                "text_feature_shape": list(text_cache["text_features"].shape),
                "metadata": text_cache["metadata"],
            },
            sort_keys=True,
        )
    )

    label_map_path = config.get("label_map_path", "data/processed/hot3d_target_object_label_map.json")
    max_candidates = int(config.get("max_candidates", 8))
    dataset_kwargs = {
        "mode": "object_metadata",
        "label_map_path": label_map_path,
        "max_candidates": max_candidates,
        "candidate_order": candidate_order,
        "candidate_order_seed": candidate_order_seed,
    }
    train_dataset = HOT3DClipsDataset(config["train_index"], **dataset_kwargs)
    val_dataset = HOT3DClipsDataset(config["val_index"], **dataset_kwargs)
    test_dataset = HOT3DClipsDataset(config["test_index"], **dataset_kwargs)

    coverage = {
        "train": ranking_coverage(train_dataset, "train"),
        "val": ranking_coverage(val_dataset, "val"),
        "test": ranking_coverage(test_dataset, "test"),
    }
    print("ranking_coverage=" + json.dumps(coverage, sort_keys=True))
    print_position_baseline_warning(coverage)

    batch_size = int(config.get("batch_size", 64))
    num_workers = int(config.get("num_workers", 0))
    train_loader = make_loader(train_dataset, text_cache, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = make_loader(val_dataset, text_cache, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = make_loader(test_dataset, text_cache, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    batch_shapes = tensor_shape_preview(train_loader)
    print("batch_shapes=" + json.dumps(batch_shapes, sort_keys=True))

    model = HOT3DVLCandidateRanker(
        metadata_dim=train_dataset.frame_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        text_dim=int(text_cache["text_features"].shape[-1]),
        hidden_dim=int(config.get("hidden_dim", 64)),
        candidate_hidden_dim=int(config.get("candidate_hidden_dim", 64)),
        text_hidden_dim=int(config.get("text_hidden_dim", 64)),
        fusion_hidden_dim=int(config.get("fusion_hidden_dim", 128)),
        num_layers=int(config.get("num_layers", 1)),
        pose_dim=train_dataset.future_hand_pose_dim,
        dropout=float(config.get("dropout", 0.1)),
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config.get("learning_rate", 1e-3)),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )
    pose_loss_weight = float(config.get("pose_loss_weight", 0.1))
    ranking_loss_weight = float(config.get("ranking_loss_weight", 1.0))
    epochs = int(config.get("epochs", 5))

    history: list[dict[str, Any]] = []
    best_val_mrr = float("-inf")
    best_state: dict[str, Any] | None = None
    for epoch in range(1, epochs + 1):
        train_metrics = train_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            pose_loss_weight,
            ranking_loss_weight,
        )
        val_metrics = evaluate(model, val_loader, device, pose_loss_weight, ranking_loss_weight)
        history.append({"epoch": epoch, "train": train_metrics, "val": val_metrics})
        print(
            f"epoch={epoch} "
            f"train_loss={train_metrics['loss']:.4f} "
            f"train_rank_loss={train_metrics['ranking_loss']:.4f} "
            f"train_pose={train_metrics['pose_loss']:.4f} "
            f"val_top1={val_metrics['candidate_top1_accuracy']:.4f} "
            f"val_top3={val_metrics['candidate_top3_accuracy']:.4f} "
            f"val_mrr={val_metrics['mean_reciprocal_rank']:.4f} "
            f"val_pose_mae={val_metrics['pose_mae']:.4f}"
        )
        if val_metrics["mean_reciprocal_rank"] > best_val_mrr:
            best_val_mrr = val_metrics["mean_reciprocal_rank"]
            best_state = {
                "model_state_dict": model.state_dict(),
                "config": config,
                "epoch": epoch,
                "val_metrics": val_metrics,
                "notice": PILOT_NOTICE,
            }

    test_metrics = evaluate(model, test_loader, device, pose_loss_weight, ranking_loss_weight)
    comparison = comparison_with_candidate_ranker(
        test_metrics,
        load_test_metrics(config.get("candidate_ranker_metrics_path", "results/logs/hot3d_candidate_ranker_pilot.json")),
    )

    metrics_payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "mode": "vision_language_candidate_ranking",
        "config": config,
        "text_features": {
            "path": text_cache["path"],
            "object_names": text_cache["object_names"],
            "feature_shape": list(text_cache["text_features"].shape),
            "metadata": text_cache["metadata"],
        },
        "dataset": {
            "train": {
                "num_samples": len(train_dataset),
                "class_distribution": class_distribution(train_dataset.samples),
            },
            "val": {"num_samples": len(val_dataset), "class_distribution": class_distribution(val_dataset.samples)},
            "test": {"num_samples": len(test_dataset), "class_distribution": class_distribution(test_dataset.samples)},
        },
        "ranking_coverage": coverage,
        "batch_shapes": batch_shapes,
        "history": history,
        "test": test_metrics,
        "comparison_with_candidate_ranker": comparison,
    }

    metrics_path = Path(config.get("metrics_path", "results/logs/hot3d_vl_candidate_ranker_pilot.json"))
    checkpoint_path = Path(config.get("checkpoint_path", "results/checkpoints/hot3d_vl_candidate_ranker_pilot.pt"))
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)
    torch.save(best_state or {"model_state_dict": model.state_dict(), "config": config}, checkpoint_path)

    print("test_metrics=" + json.dumps(test_metrics, sort_keys=True))
    print("comparison_with_candidate_ranker=" + json.dumps(comparison, sort_keys=True))
    print(f"saved_metrics_path={metrics_path}")
    print(f"saved_checkpoint_path={checkpoint_path}")
    print(PILOT_NOTICE)


if __name__ == "__main__":
    main()
