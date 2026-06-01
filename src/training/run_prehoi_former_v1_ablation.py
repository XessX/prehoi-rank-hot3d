"""Run controlled PreHOI-Former v1 pilot ablations."""

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
from src.models.prehoi_former_v1 import PreHOIFormerV1
from src.training.train_hot3d_candidate_ranker import (
    PILOT_NOTICE,
    print_position_baseline_warning,
    ranking_coverage,
    set_seed,
)
from src.training.train_hot3d_vl_candidate_ranker import (
    evaluate,
    load_text_feature_cache,
    make_loader,
    tensor_shape_preview,
    train_one_epoch,
)
from src.training.train_prehoi_former_v1 import count_parameters
from src.utils.config import load_yaml


SUMMARY_FIELDS = (
    "variant",
    "use_text",
    "use_candidate_attention",
    "pose_loss_weight",
    "epochs",
    "top1",
    "top3",
    "mrr",
    "pose_mae",
    "pose_mse",
    "ranking_loss",
    "pose_loss",
    "metrics_path",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run PreHOI-Former v1 ablation sweep.")
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


def merged_config(base: dict[str, Any], run: dict[str, Any]) -> dict[str, Any]:
    config = dict(base)
    config.update(run)
    return config


def make_model(config: dict[str, Any], train_dataset: HOT3DClipsDataset, text_dim: int) -> PreHOIFormerV1:
    return PreHOIFormerV1(
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
    )


def model_summary(model: torch.nn.Module, config: dict[str, Any], train_dataset: HOT3DClipsDataset, text_dim: int) -> dict[str, Any]:
    return {
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


def run_variant(
    config: dict[str, Any],
    train_dataset: HOT3DClipsDataset,
    val_dataset: HOT3DClipsDataset,
    test_dataset: HOT3DClipsDataset,
    text_cache: dict[str, Any],
    coverage: dict[str, Any],
    batch_shapes: dict[str, list[int]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    variant = str(config["name"])
    set_seed(int(config.get("seed", 42)))
    requested_device = str(config.get("device", "cpu"))
    device = torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")

    batch_size = int(config.get("batch_size", 64))
    num_workers = int(config.get("num_workers", 0))
    train_loader = make_loader(train_dataset, text_cache, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    val_loader = make_loader(val_dataset, text_cache, batch_size=batch_size, shuffle=False, num_workers=num_workers)
    test_loader = make_loader(test_dataset, text_cache, batch_size=batch_size, shuffle=False, num_workers=num_workers)

    text_dim = int(text_cache["text_features"].shape[-1])
    model = make_model(config, train_dataset, text_dim).to(device)
    summary = model_summary(model, config, train_dataset, text_dim)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config.get("learning_rate", 7e-4)),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )
    pose_loss_weight = float(config.get("pose_loss_weight", 0.1))
    ranking_loss_weight = float(config.get("ranking_loss_weight", 1.0))
    epochs = int(config.get("epochs", 5))

    history: list[dict[str, Any]] = []
    best_val_mrr = float("-inf")
    best_epoch = 0
    print(
        f"variant={variant} "
        f"use_text={summary['use_text']} "
        f"use_candidate_attention={summary['use_candidate_attention']} "
        f"pose_loss_weight={pose_loss_weight}"
    )
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
        if val_metrics["mean_reciprocal_rank"] > best_val_mrr:
            best_val_mrr = val_metrics["mean_reciprocal_rank"]
            best_epoch = epoch
        print(
            f"  epoch={epoch} "
            f"train_loss={train_metrics['loss']:.4f} "
            f"val_top1={val_metrics['candidate_top1_accuracy']:.4f} "
            f"val_mrr={val_metrics['mean_reciprocal_rank']:.4f} "
            f"val_pose_mae={val_metrics['pose_mae']:.4f}"
        )

    test_metrics = evaluate(model, test_loader, device, pose_loss_weight, ranking_loss_weight)
    metrics_payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "mode": "prehoi_former_v1_ablation",
        "variant": variant,
        "config": config,
        "model_summary": summary,
        "text_features": {
            "path": text_cache["path"],
            "feature_shape": list(text_cache["text_features"].shape),
            "metadata": text_cache["metadata"],
        },
        "dataset": {
            "train": {"num_samples": len(train_dataset), "class_distribution": class_distribution(train_dataset.samples)},
            "val": {"num_samples": len(val_dataset), "class_distribution": class_distribution(val_dataset.samples)},
            "test": {"num_samples": len(test_dataset), "class_distribution": class_distribution(test_dataset.samples)},
        },
        "ranking_coverage": coverage,
        "batch_shapes": batch_shapes,
        "history": history,
        "best_val_mrr_epoch": best_epoch,
        "test": test_metrics,
    }

    metrics_dir = Path(config.get("metrics_dir", "results/logs/ablation"))
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = metrics_dir / f"prehoi_former_v1_{variant}.json"
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)

    row = {
        "variant": variant,
        "use_text": str(bool(config.get("use_text", True))).lower(),
        "use_candidate_attention": str(bool(config.get("use_candidate_attention", True))).lower(),
        "pose_loss_weight": pose_loss_weight,
        "epochs": epochs,
        "top1": test_metrics["candidate_top1_accuracy"],
        "top3": test_metrics["candidate_top3_accuracy"],
        "mrr": test_metrics["mean_reciprocal_rank"],
        "pose_mae": test_metrics["pose_mae"],
        "pose_mse": test_metrics["pose_mse"],
        "ranking_loss": test_metrics["ranking_loss"],
        "pose_loss": test_metrics["pose_loss"],
        "metrics_path": str(metrics_path),
    }
    print(
        f"  test top1={row['top1']:.4f} top3={row['top3']:.4f} "
        f"mrr={row['mrr']:.4f} pose_mae={row['pose_mae']:.4f}"
    )
    return metrics_payload, row


def write_summary(summary_path: Path, rows: list[dict[str, Any]]) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_summary_table(rows: list[dict[str, Any]]) -> None:
    print("variant,top1,top3,MRR,pose_MAE,pose_MSE")
    for row in rows:
        print(
            f"{row['variant']},"
            f"{float(row['top1']):.4f},"
            f"{float(row['top3']):.4f},"
            f"{float(row['mrr']):.4f},"
            f"{float(row['pose_mae']):.4f},"
            f"{float(row['pose_mse']):.4f}"
        )


def main() -> None:
    args = parse_args()
    payload = load_yaml(args.config)
    base = payload.get("base", {})
    runs = payload.get("runs", [])
    if not isinstance(base, dict) or not isinstance(runs, list) or not runs:
        raise ValueError("Ablation config must contain a base mapping and non-empty runs list.")

    candidate_order = str(base.get("candidate_order", "stable_uid"))
    if candidate_order != "stable_uid":
        raise ValueError("PreHOI-Former ablations require candidate_order: stable_uid.")
    print(PILOT_NOTICE)
    print("PreHOI-Former v1 controlled ablation pilot. Not a final paper result.")
    print("Proxy target labels are derived labels, not direct HOT3D ground truth.")
    print(f"candidate_order={candidate_order}")

    set_seed(int(base.get("seed", 42)))
    text_cache = load_text_feature_cache(base["text_features_path"])
    label_map_path = base.get("label_map_path", "data/processed/hot3d_target_object_label_map.json")
    max_candidates = int(base.get("max_candidates", 8))
    dataset_kwargs = {
        "mode": "object_metadata",
        "label_map_path": label_map_path,
        "max_candidates": max_candidates,
        "candidate_order": candidate_order,
        "candidate_order_seed": int(base.get("candidate_order_seed", base.get("seed", 42))),
    }
    train_dataset = HOT3DClipsDataset(base["train_index"], **dataset_kwargs)
    val_dataset = HOT3DClipsDataset(base["val_index"], **dataset_kwargs)
    test_dataset = HOT3DClipsDataset(base["test_index"], **dataset_kwargs)

    coverage = {
        "train": ranking_coverage(train_dataset, "train"),
        "val": ranking_coverage(val_dataset, "val"),
        "test": ranking_coverage(test_dataset, "test"),
    }
    print("ranking_coverage=" + json.dumps(coverage, sort_keys=True))
    print_position_baseline_warning(coverage)

    preview_loader = make_loader(
        train_dataset,
        text_cache,
        batch_size=int(base.get("batch_size", 64)),
        shuffle=False,
        num_workers=int(base.get("num_workers", 0)),
    )
    batch_shapes = tensor_shape_preview(preview_loader)
    print("batch_shapes=" + json.dumps(batch_shapes, sort_keys=True))

    rows: list[dict[str, Any]] = []
    for run in runs:
        if not isinstance(run, dict) or "name" not in run:
            raise ValueError("Every ablation run must be a mapping with a name.")
        run_config = merged_config(base, run)
        _, row = run_variant(
            run_config,
            train_dataset,
            val_dataset,
            test_dataset,
            text_cache,
            coverage,
            batch_shapes,
        )
        rows.append(row)

    summary_path = Path(base.get("summary_csv", "results/tables/prehoi_former_v1_ablation_summary.csv"))
    write_summary(summary_path, rows)
    print_summary_table(rows)
    print(f"saved_summary_csv={summary_path}")


if __name__ == "__main__":
    main()
