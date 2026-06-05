"""Run pilot seed-stability checks for selected HOT3D-Clips models."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import HOT3DClipsDataset, class_distribution
from src.models.hot3d_candidate_ranker import HOT3DCandidateRanker
from src.models.prehoi_former_v1 import PreHOIFormerV1
from src.training.train_hot3d_candidate_ranker import (
    PILOT_NOTICE,
    evaluate as evaluate_candidate,
    make_loader as make_candidate_loader,
    ranking_coverage,
    set_seed,
    train_one_epoch as train_candidate_one_epoch,
)
from src.training.train_hot3d_vl_candidate_ranker import (
    evaluate as evaluate_prehoi,
    load_text_feature_cache,
    make_loader as make_prehoi_loader,
    tensor_shape_preview as prehoi_shape_preview,
    train_one_epoch as train_prehoi_one_epoch,
)
from src.training.train_prehoi_former_v1 import count_parameters
from src.utils.config import load_yaml


SUMMARY_FIELDS = ("model_name", "seed", "top1", "top3", "MRR", "pose_MSE", "pose_MAE", "notes")
DEFAULT_MODELS = (
    "candidate_ranker_non_vl",
    "prehoi_former_v1",
    "prehoi_former_v1_geometry_only_no_attention",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pilot seed-stability checks.")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026])
    parser.add_argument("--models", nargs="+", default=list(DEFAULT_MODELS), choices=list(DEFAULT_MODELS))
    parser.add_argument("--output-dir", type=Path, default=Path("results/logs/seed_stability"))
    parser.add_argument("--summary-csv", type=Path, default=Path("results/tables/pilot_seed_stability_summary.csv"))
    return parser.parse_args()


def clone_config(config: dict[str, Any], seed: int) -> dict[str, Any]:
    cloned = dict(config)
    cloned["seed"] = int(seed)
    # stable_uid does not use this value, but keeping it fixed removes one extra source of change.
    cloned["candidate_order_seed"] = int(config.get("candidate_order_seed", 42))
    return cloned


def load_geometry_no_attention_config(seed: int) -> dict[str, Any]:
    payload = load_yaml("configs/prehoi_former_v1_ablation.yaml")
    base = payload.get("base", {})
    runs = payload.get("runs", [])
    if not isinstance(base, dict) or not isinstance(runs, list):
        raise ValueError("Invalid PreHOI-Former v1 ablation config.")
    selected = None
    for run in runs:
        if isinstance(run, dict) and run.get("name") == "geometry_only_no_attention":
            selected = run
            break
    if selected is None:
        raise ValueError("geometry_only_no_attention run not found in ablation config.")
    config = dict(base)
    config.update(selected)
    return clone_config(config, seed)


def ensure_order_safe(config: dict[str, Any], model_name: str) -> None:
    candidate_order = str(config.get("candidate_order", "stable_uid"))
    if candidate_order != "stable_uid":
        raise ValueError(f"{model_name} requires candidate_order: stable_uid, got {candidate_order!r}.")


def dataset_kwargs(config: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": "object_metadata",
        "label_map_path": config.get("label_map_path", "data/processed/hot3d_target_object_label_map.json"),
        "max_candidates": int(config.get("max_candidates", 8)),
        "candidate_order": str(config.get("candidate_order", "stable_uid")),
        "candidate_order_seed": int(config.get("candidate_order_seed", 42)),
    }


def load_datasets(config: dict[str, Any]) -> tuple[HOT3DClipsDataset, HOT3DClipsDataset, HOT3DClipsDataset]:
    kwargs = dataset_kwargs(config)
    datasets = (
        HOT3DClipsDataset(config["train_index"], **kwargs),
        HOT3DClipsDataset(config["val_index"], **kwargs),
        HOT3DClipsDataset(config["test_index"], **kwargs),
    )
    for split_name, dataset in zip(("train", "val", "test"), datasets):
        summary = dataset.summary()
        if bool(summary.get("input_uses_forecast_frame")):
            raise RuntimeError(f"{split_name} split uses forecast-frame inputs.")
    return datasets


def device_from_config(config: dict[str, Any]) -> torch.device:
    requested_device = str(config.get("device", "cpu"))
    return torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")


def candidate_shape_preview(loader: torch.utils.data.DataLoader) -> dict[str, list[int]]:
    batch = next(iter(loader))
    return {
        "features": list(batch["features"].shape),
        "observation_object_candidates": list(batch["observation_object_candidates"].shape),
        "candidate_mask": list(batch["candidate_mask"].shape),
        "candidate_target_index": list(batch["candidate_target_index"].shape),
        "candidate_target_mask": list(batch["candidate_target_mask"].shape),
        "rankable": list(batch["rankable"].shape),
        "future_hand_pose": list(batch["future_hand_pose"].shape),
    }


def row_from_metrics(model_name: str, seed: int, metrics: dict[str, float], notes: str) -> dict[str, Any]:
    return {
        "model_name": model_name,
        "seed": seed,
        "top1": metrics.get("candidate_top1_accuracy", ""),
        "top3": metrics.get("candidate_top3_accuracy", ""),
        "MRR": metrics.get("mean_reciprocal_rank", ""),
        "pose_MSE": metrics.get("pose_mse", ""),
        "pose_MAE": metrics.get("pose_mae", ""),
        "notes": notes,
    }


def save_metrics(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def run_candidate_ranker(seed: int, output_dir: Path) -> dict[str, Any]:
    config = clone_config(load_yaml("configs/hot3d_candidate_ranker.yaml"), seed)
    ensure_order_safe(config, "candidate_ranker_non_vl")
    set_seed(seed)
    device = device_from_config(config)
    train_dataset, val_dataset, test_dataset = load_datasets(config)

    batch_size = int(config.get("batch_size", 64))
    num_workers = int(config.get("num_workers", 0))
    train_loader = make_candidate_loader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = make_candidate_loader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = make_candidate_loader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    model = HOT3DCandidateRanker(
        metadata_dim=train_dataset.frame_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        hidden_dim=int(config.get("hidden_dim", 64)),
        candidate_hidden_dim=int(config.get("candidate_hidden_dim", 64)),
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

    history: list[dict[str, Any]] = []
    for epoch in range(1, int(config.get("epochs", 5)) + 1):
        train_metrics = train_candidate_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            pose_loss_weight,
            ranking_loss_weight,
        )
        val_metrics = evaluate_candidate(model, val_loader, device, pose_loss_weight, ranking_loss_weight)
        history.append({"epoch": epoch, "train": train_metrics, "val": val_metrics})
        print(
            f"model=candidate_ranker_non_vl seed={seed} epoch={epoch} "
            f"val_mrr={val_metrics['mean_reciprocal_rank']:.4f} "
            f"val_pose_mae={val_metrics['pose_mae']:.4f}"
        )

    test_metrics = evaluate_candidate(model, test_loader, device, pose_loss_weight, ranking_loss_weight)
    coverage = {
        "train": ranking_coverage(train_dataset, "train"),
        "val": ranking_coverage(val_dataset, "val"),
        "test": ranking_coverage(test_dataset, "test"),
    }
    payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "model_name": "candidate_ranker_non_vl",
        "seed": seed,
        "config": config,
        "dataset": {
            "train": {"num_samples": len(train_dataset), "class_distribution": class_distribution(train_dataset.samples)},
            "val": {"num_samples": len(val_dataset), "class_distribution": class_distribution(val_dataset.samples)},
            "test": {"num_samples": len(test_dataset), "class_distribution": class_distribution(test_dataset.samples)},
        },
        "batch_shapes": candidate_shape_preview(train_loader),
        "ranking_coverage": coverage,
        "history": history,
        "test": test_metrics,
    }
    metrics_path = output_dir / f"candidate_ranker_non_vl_seed{seed}.json"
    save_metrics(metrics_path, payload)
    print(
        f"finished model=candidate_ranker_non_vl seed={seed} "
        f"top1={test_metrics['candidate_top1_accuracy']:.4f} "
        f"mrr={test_metrics['mean_reciprocal_rank']:.4f} "
        f"pose_mae={test_metrics['pose_mae']:.4f}"
    )
    return row_from_metrics(
        "candidate_ranker_non_vl",
        seed,
        test_metrics,
        f"PILOT DEBUG RUN only; metrics_path={metrics_path}",
    )


def make_prehoi_config(model_name: str, seed: int) -> dict[str, Any]:
    if model_name == "prehoi_former_v1":
        return clone_config(load_yaml("configs/prehoi_former_v1.yaml"), seed)
    if model_name == "prehoi_former_v1_geometry_only_no_attention":
        return load_geometry_no_attention_config(seed)
    raise ValueError(f"Unsupported PreHOI model: {model_name}")


def run_prehoi_v1(model_name: str, seed: int, output_dir: Path) -> dict[str, Any]:
    config = make_prehoi_config(model_name, seed)
    ensure_order_safe(config, model_name)
    set_seed(seed)
    device = device_from_config(config)
    text_cache = load_text_feature_cache(config["text_features_path"])
    train_dataset, val_dataset, test_dataset = load_datasets(config)

    batch_size = int(config.get("batch_size", 64))
    num_workers = int(config.get("num_workers", 0))
    train_loader = make_prehoi_loader(train_dataset, text_cache, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = make_prehoi_loader(val_dataset, text_cache, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = make_prehoi_loader(test_dataset, text_cache, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    text_dim = int(text_cache["text_features"].shape[-1])
    model = PreHOIFormerV1(
        metadata_dim=train_dataset.frame_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        text_dim=text_dim,
        hidden_dim=int(config.get("hidden_dim", 96)),
        num_heads=int(config.get("num_heads", 4)),
        num_layers=int(config.get("num_layers", 2)),
        pose_dim=train_dataset.future_hand_pose_dim,
        dropout=float(config.get("dropout", 0.1)),
        use_text=bool(config.get("use_text", True)),
        use_candidate_attention=bool(config.get("use_candidate_attention", True)),
    ).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config.get("learning_rate", 7e-4)),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )
    pose_loss_weight = float(config.get("pose_loss_weight", 0.1))
    ranking_loss_weight = float(config.get("ranking_loss_weight", 1.0))

    history: list[dict[str, Any]] = []
    best_val_mrr = float("-inf")
    best_epoch = 0
    for epoch in range(1, int(config.get("epochs", 5)) + 1):
        train_metrics = train_prehoi_one_epoch(
            model,
            train_loader,
            optimizer,
            device,
            pose_loss_weight,
            ranking_loss_weight,
        )
        val_metrics = evaluate_prehoi(model, val_loader, device, pose_loss_weight, ranking_loss_weight)
        history.append({"epoch": epoch, "train": train_metrics, "val": val_metrics})
        if val_metrics["mean_reciprocal_rank"] > best_val_mrr:
            best_val_mrr = val_metrics["mean_reciprocal_rank"]
            best_epoch = epoch
        print(
            f"model={model_name} seed={seed} epoch={epoch} "
            f"val_mrr={val_metrics['mean_reciprocal_rank']:.4f} "
            f"val_pose_mae={val_metrics['pose_mae']:.4f}"
        )

    test_metrics = evaluate_prehoi(model, test_loader, device, pose_loss_weight, ranking_loss_weight)
    coverage = {
        "train": ranking_coverage(train_dataset, "train"),
        "val": ranking_coverage(val_dataset, "val"),
        "test": ranking_coverage(test_dataset, "test"),
    }
    model_summary = {
        "model": "PreHOIFormerV1",
        "metadata_dim": train_dataset.frame_feature_dim,
        "candidate_dim": train_dataset.object_candidate_feature_dim,
        "text_dim": text_dim,
        "hidden_dim": int(config.get("hidden_dim", 96)),
        "num_heads": int(config.get("num_heads", 4)),
        "num_layers": int(config.get("num_layers", 2)),
        "use_text": bool(config.get("use_text", True)),
        "use_candidate_attention": bool(config.get("use_candidate_attention", True)),
        **count_parameters(model),
    }
    payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "model_name": model_name,
        "seed": seed,
        "config": config,
        "model_summary": model_summary,
        "dataset": {
            "train": {"num_samples": len(train_dataset), "class_distribution": class_distribution(train_dataset.samples)},
            "val": {"num_samples": len(val_dataset), "class_distribution": class_distribution(val_dataset.samples)},
            "test": {"num_samples": len(test_dataset), "class_distribution": class_distribution(test_dataset.samples)},
        },
        "batch_shapes": prehoi_shape_preview(train_loader),
        "ranking_coverage": coverage,
        "history": history,
        "best_val_mrr_epoch": best_epoch,
        "test": test_metrics,
    }
    safe_name = "prehoi_v1_geometry_only_no_attention" if model_name.endswith("geometry_only_no_attention") else model_name
    metrics_path = output_dir / f"{safe_name}_seed{seed}.json"
    save_metrics(metrics_path, payload)
    print(
        f"finished model={model_name} seed={seed} "
        f"top1={test_metrics['candidate_top1_accuracy']:.4f} "
        f"mrr={test_metrics['mean_reciprocal_rank']:.4f} "
        f"pose_mae={test_metrics['pose_mae']:.4f}"
    )
    return row_from_metrics(
        model_name,
        seed,
        test_metrics,
        f"PILOT DEBUG RUN only; best_val_mrr_epoch={best_epoch}; metrics_path={metrics_path}",
    )


def write_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_summary(rows: list[dict[str, Any]]) -> None:
    print("model_name,seed,top1,top3,MRR,pose_MSE,pose_MAE")
    for row in rows:
        print(
            f"{row['model_name']},{row['seed']},"
            f"{float(row['top1']):.4f},{float(row['top3']):.4f},"
            f"{float(row['MRR']):.4f},{float(row['pose_MSE']):.4f},"
            f"{float(row['pose_MAE']):.4f}"
        )


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    print(PILOT_NOTICE)
    print("Seed-stability pilot only. Proxy labels are derived labels, not HOT3D ground truth.")
    print("candidate_order=stable_uid")

    rows: list[dict[str, Any]] = []
    for model_name in args.models:
        for seed in args.seeds:
            if model_name == "candidate_ranker_non_vl":
                row = run_candidate_ranker(seed, args.output_dir)
            else:
                row = run_prehoi_v1(model_name, seed, args.output_dir)
            rows.append(row)
            write_summary(args.summary_csv, rows)

    write_summary(args.summary_csv, rows)
    print_summary(rows)
    print(f"saved_summary_csv={args.summary_csv}")
    print(f"saved_metrics_dir={args.output_dir}")
    print(PILOT_NOTICE)


if __name__ == "__main__":
    main()
