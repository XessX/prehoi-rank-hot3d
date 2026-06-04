"""Train PreHOI-Former v2 as a dual-branch pilot/model-development run."""

from __future__ import annotations

import argparse
import csv
import json
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
from src.models.prehoi_former_v2 import PreHOIFormerV2
from src.training.train_hot3d_candidate_ranker import (
    PILOT_NOTICE,
    compute_loss,
    print_position_baseline_warning,
    ranking_coverage,
    set_seed,
)
from src.training.train_hot3d_vl_candidate_ranker import (
    assert_no_forecast_input,
    load_text_feature_cache,
    move_batch,
)
from src.training.train_prehoi_former_v1 import count_parameters
from src.utils.config import load_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PreHOI-Former v2 pilot model.")
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


class OptionalCandidateTextCollator:
    """Collate candidate samples and attach frozen text only when requested."""

    def __init__(self, text_cache: dict[str, Any] | None, fallback_text_dim: int = 1) -> None:
        self.text_cache = text_cache
        if text_cache is None:
            self.text_features = None
            self.object_to_index: dict[str, int] = {}
            self.text_dim = int(fallback_text_dim)
        else:
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
        if self.text_features is not None:
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
    text_cache: dict[str, Any] | None,
    batch_size: int,
    shuffle: bool,
    num_workers: int,
) -> DataLoader:
    return DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        collate_fn=OptionalCandidateTextCollator(text_cache),
    )


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


def model_summary(
    model: torch.nn.Module,
    config: dict[str, Any],
    train_dataset: HOT3DClipsDataset,
    text_dim: int,
) -> dict[str, Any]:
    return {
        "model": "PreHOIFormerV2",
        "metadata_dim": train_dataset.frame_feature_dim,
        "candidate_dim": train_dataset.object_candidate_feature_dim,
        "text_dim": text_dim,
        "hidden_dim": int(config.get("hidden_dim", 96)),
        "num_heads": int(config.get("num_heads", 4)),
        "num_layers": int(config.get("num_layers", 2)),
        "use_text": bool(config.get("use_text", False)),
        "use_attention": bool(config.get("use_attention", False)),
        "pose_uses_candidates": bool(config.get("pose_uses_candidates", True)),
        "detach_pose_from_ranking": bool(config.get("detach_pose_from_ranking", False)),
        "detach_ranking_from_pose": bool(config.get("detach_ranking_from_pose", False)),
        **count_parameters(model),
    }


def clone_state_dict(model: torch.nn.Module) -> dict[str, torch.Tensor]:
    return {key: value.detach().cpu().clone() for key, value in model.state_dict().items()}


def load_best_v1_ablation(summary_path: str | Path) -> dict[str, Any]:
    path = Path(summary_path)
    if not path.exists():
        return {"available": False, "path": str(path)}
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return {"available": False, "path": str(path), "reason": "empty summary"}

    def as_float(row: dict[str, str], key: str) -> float:
        try:
            return float(row[key])
        except (KeyError, TypeError, ValueError):
            return float("nan")

    best_ranking = max(rows, key=lambda row: as_float(row, "mrr"))
    best_pose = min(rows, key=lambda row: as_float(row, "pose_mae"))
    return {
        "available": True,
        "path": str(path),
        "best_ranking": {
            "variant": best_ranking.get("variant"),
            "top1": as_float(best_ranking, "top1"),
            "top3": as_float(best_ranking, "top3"),
            "mrr": as_float(best_ranking, "mrr"),
            "pose_mae": as_float(best_ranking, "pose_mae"),
        },
        "best_pose": {
            "variant": best_pose.get("variant"),
            "top1": as_float(best_pose, "top1"),
            "top3": as_float(best_pose, "top3"),
            "mrr": as_float(best_pose, "mrr"),
            "pose_mae": as_float(best_pose, "pose_mae"),
        },
    }


def compare_with_v1(current: dict[str, float], v1_summary: dict[str, Any]) -> dict[str, Any]:
    if not v1_summary.get("available"):
        return v1_summary
    best_ranking = v1_summary["best_ranking"]
    best_pose = v1_summary["best_pose"]
    return {
        "available": True,
        "notice": "Pilot/debug comparison only. Proxy labels are derived labels, not direct HOT3D ground truth.",
        "v2_top1": current.get("candidate_top1_accuracy"),
        "v2_top3": current.get("candidate_top3_accuracy"),
        "v2_mrr": current.get("mean_reciprocal_rank"),
        "v2_pose_mae": current.get("pose_mae"),
        "best_v1_ranking": best_ranking,
        "best_v1_pose": best_pose,
        "delta_mrr_vs_best_v1_ranking": current.get("mean_reciprocal_rank", 0.0) - float(best_ranking["mrr"]),
        "delta_pose_mae_vs_best_v1_pose": current.get("pose_mae", 0.0) - float(best_pose["pose_mae"]),
    }


def main() -> None:
    args = parse_args()
    config = load_yaml(args.config)
    set_seed(int(config.get("seed", 42)))

    candidate_order = str(config.get("candidate_order", "stable_uid"))
    if candidate_order != "stable_uid":
        raise ValueError("PreHOI-Former v2 requires candidate_order: stable_uid.")
    candidate_order_seed = int(config.get("candidate_order_seed", config.get("seed", 42)))

    requested_device = str(config.get("device", "cpu"))
    device = torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")
    print(PILOT_NOTICE)
    print("PreHOI-Former v2 dual-branch pilot/model-development run.")
    print("Proxy target labels are derived labels, not direct HOT3D ground truth.")
    print("Inputs use observation-frame metadata and observation-frame object candidates only.")
    print(f"candidate_order={candidate_order}")

    use_text = bool(config.get("use_text", False))
    text_cache: dict[str, Any] | None = None
    text_dim = 1
    if use_text:
        text_cache = load_text_feature_cache(config["text_features_path"])
        text_dim = int(text_cache["text_features"].shape[-1])
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
    else:
        print("text_feature_summary={\"enabled\": false, \"loaded\": false}")

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
    for split_name, dataset in (("train", train_dataset), ("val", val_dataset), ("test", test_dataset)):
        summary = dataset.summary()
        if bool(summary.get("input_uses_forecast_frame")):
            raise RuntimeError(f"{split_name} dataset summary indicates forecast-frame input use.")

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

    model = PreHOIFormerV2(
        metadata_dim=train_dataset.frame_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        text_dim=text_dim,
        hidden_dim=int(config.get("hidden_dim", 96)),
        num_heads=int(config.get("num_heads", 4)),
        num_layers=int(config.get("num_layers", 2)),
        pose_dim=train_dataset.future_hand_pose_dim,
        dropout=float(config.get("dropout", 0.1)),
        use_text=use_text,
        use_attention=bool(config.get("use_attention", False)),
        pose_uses_candidates=bool(config.get("pose_uses_candidates", True)),
        detach_pose_from_ranking=bool(config.get("detach_pose_from_ranking", False)),
        detach_ranking_from_pose=bool(config.get("detach_ranking_from_pose", False)),
    ).to(device)
    summary = model_summary(model, config, train_dataset, text_dim)
    print("model_summary=" + json.dumps(summary, sort_keys=True))

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config.get("learning_rate", 7e-4)),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )
    pose_loss_weight = float(config.get("pose_loss_weight", 0.1))
    ranking_loss_weight = float(config.get("ranking_loss_weight", 1.0))
    epochs = int(config.get("epochs", 10))
    patience = int(config.get("early_stopping_patience", 3))

    history: list[dict[str, Any]] = []
    best_val_mrr = float("-inf")
    best_epoch = 0
    epochs_without_improvement = 0
    best_state: dict[str, Any] | None = None
    best_model_state: dict[str, torch.Tensor] | None = None
    early_stopped = False

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
        improved = val_metrics["mean_reciprocal_rank"] > best_val_mrr
        if improved:
            best_val_mrr = val_metrics["mean_reciprocal_rank"]
            best_epoch = epoch
            epochs_without_improvement = 0
            best_model_state = clone_state_dict(model)
            best_state = {
                "model_state_dict": best_model_state,
                "config": config,
                "epoch": epoch,
                "val_metrics": val_metrics,
                "notice": PILOT_NOTICE,
            }
        else:
            epochs_without_improvement += 1
        print(
            f"epoch={epoch} "
            f"train_loss={train_metrics['loss']:.4f} "
            f"train_rank_loss={train_metrics['ranking_loss']:.4f} "
            f"train_pose={train_metrics['pose_loss']:.4f} "
            f"val_top1={val_metrics['candidate_top1_accuracy']:.4f} "
            f"val_top3={val_metrics['candidate_top3_accuracy']:.4f} "
            f"val_mrr={val_metrics['mean_reciprocal_rank']:.4f} "
            f"val_pose_mae={val_metrics['pose_mae']:.4f} "
            f"best_epoch={best_epoch}"
        )
        if patience > 0 and epochs_without_improvement >= patience:
            early_stopped = True
            print(
                f"early_stopping_triggered=true epoch={epoch} "
                f"patience={patience} best_epoch={best_epoch} best_val_mrr={best_val_mrr:.4f}"
            )
            break

    if best_model_state is not None:
        model.load_state_dict({key: value.to(device) for key, value in best_model_state.items()})
    test_metrics = evaluate(model, test_loader, device, pose_loss_weight, ranking_loss_weight)
    v1_summary = load_best_v1_ablation(config.get("v1_ablation_summary", "results/tables/prehoi_former_v1_ablation_summary.csv"))
    comparison = compare_with_v1(test_metrics, v1_summary)

    early_stopping_summary = {
        "enabled": patience > 0,
        "patience": patience,
        "early_stopped": early_stopped,
        "best_epoch": best_epoch,
        "best_val_mrr": best_val_mrr,
        "epochs_run": len(history),
    }
    metrics_payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "mode": "prehoi_former_v2",
        "variant_name": config.get("variant_name", "v2_geometry_only"),
        "config": config,
        "model_summary": summary,
        "dataset": {
            "train": {"num_samples": len(train_dataset), "class_distribution": class_distribution(train_dataset.samples)},
            "val": {"num_samples": len(val_dataset), "class_distribution": class_distribution(val_dataset.samples)},
            "test": {"num_samples": len(test_dataset), "class_distribution": class_distribution(test_dataset.samples)},
        },
        "ranking_coverage": coverage,
        "batch_shapes": batch_shapes,
        "early_stopping": early_stopping_summary,
        "history": history,
        "test": test_metrics,
        "comparison_with_v1_ablation": comparison,
    }
    if text_cache is not None:
        metrics_payload["text_features"] = {
            "path": text_cache["path"],
            "feature_shape": list(text_cache["text_features"].shape),
            "metadata": text_cache["metadata"],
        }

    metrics_path = Path(config.get("metrics_path", "results/logs/prehoi_former_v2_pilot.json"))
    checkpoint_path = Path(config.get("checkpoint_path", "results/checkpoints/prehoi_former_v2_pilot.pt"))
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)
    torch.save(best_state or {"model_state_dict": clone_state_dict(model), "config": config}, checkpoint_path)

    print("early_stopping=" + json.dumps(early_stopping_summary, sort_keys=True))
    print("test_metrics=" + json.dumps(test_metrics, sort_keys=True))
    print("comparison_with_v1_ablation=" + json.dumps(comparison, sort_keys=True))
    print(f"saved_metrics_path={metrics_path}")
    print(f"saved_checkpoint_path={checkpoint_path}")
    print(PILOT_NOTICE)


if __name__ == "__main__":
    main()
