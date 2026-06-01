"""Train PreHOI-Former v1 as a pilot/model-development run."""

from __future__ import annotations

import argparse
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
    load_test_metrics,
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
from src.utils.config import load_yaml


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train PreHOI-Former v1 pilot model.")
    parser.add_argument("--config", type=Path, required=True)
    return parser.parse_args()


def count_parameters(model: torch.nn.Module) -> dict[str, int]:
    total = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    return {"total_parameters": total, "trainable_parameters": trainable}


def comparison_table(
    current: dict[str, float],
    candidate_ranker: dict[str, Any] | None,
    vl_candidate_ranker: dict[str, Any] | None,
) -> dict[str, Any]:
    return {
        "notice": "Pilot/debug comparison only. Proxy labels are derived labels, not direct HOT3D ground truth.",
        "candidate_ranker": candidate_ranker or {"available": False},
        "vl_candidate_ranker": vl_candidate_ranker or {"available": False},
        "prehoi_former_v1": current,
        "summary": {
            "candidate_ranker_top1": None if candidate_ranker is None else candidate_ranker.get("candidate_top1_accuracy"),
            "vl_candidate_ranker_top1": None if vl_candidate_ranker is None else vl_candidate_ranker.get("candidate_top1_accuracy"),
            "prehoi_former_v1_top1": current.get("candidate_top1_accuracy"),
            "candidate_ranker_top3": None if candidate_ranker is None else candidate_ranker.get("candidate_top3_accuracy"),
            "vl_candidate_ranker_top3": None if vl_candidate_ranker is None else vl_candidate_ranker.get("candidate_top3_accuracy"),
            "prehoi_former_v1_top3": current.get("candidate_top3_accuracy"),
            "candidate_ranker_mrr": None if candidate_ranker is None else candidate_ranker.get("mean_reciprocal_rank"),
            "vl_candidate_ranker_mrr": None if vl_candidate_ranker is None else vl_candidate_ranker.get("mean_reciprocal_rank"),
            "prehoi_former_v1_mrr": current.get("mean_reciprocal_rank"),
            "candidate_ranker_pose_mae": None if candidate_ranker is None else candidate_ranker.get("pose_mae"),
            "vl_candidate_ranker_pose_mae": None if vl_candidate_ranker is None else vl_candidate_ranker.get("pose_mae"),
            "prehoi_former_v1_pose_mae": current.get("pose_mae"),
        },
    }


def main() -> None:
    args = parse_args()
    config = load_yaml(args.config)
    set_seed(int(config.get("seed", 42)))

    candidate_order = str(config.get("candidate_order", "stable_uid"))
    if candidate_order != "stable_uid":
        raise ValueError("PreHOI-Former v1 requires candidate_order: stable_uid.")
    candidate_order_seed = int(config.get("candidate_order_seed", config.get("seed", 42)))

    requested_device = str(config.get("device", "cpu"))
    device = torch.device(requested_device if requested_device == "cuda" and torch.cuda.is_available() else "cpu")
    print(PILOT_NOTICE)
    print("PreHOI-Former v1 pilot/model-development run.")
    print("Proxy target labels are derived labels, not direct HOT3D ground truth.")
    print("Inputs use observation-frame metadata/object candidates and frozen text embeddings only.")
    print("CLIP is not trained; image CLIP features are not used in v1.")
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

    model = PreHOIFormerV1(
        metadata_dim=train_dataset.frame_feature_dim,
        candidate_dim=train_dataset.object_candidate_feature_dim,
        text_dim=int(text_cache["text_features"].shape[-1]),
        hidden_dim=int(config.get("hidden_dim", 96)),
        num_heads=int(config.get("num_heads", 4)),
        num_layers=int(config.get("num_layers", 2)),
        pose_dim=train_dataset.future_hand_pose_dim,
        dropout=float(config.get("dropout", 0.1)),
        use_text=bool(config.get("use_text", True)),
        use_candidate_attention=bool(config.get("use_candidate_attention", True)),
    ).to(device)
    model_summary = {
        "model": "PreHOIFormerV1",
        "metadata_dim": train_dataset.frame_feature_dim,
        "candidate_dim": train_dataset.object_candidate_feature_dim,
        "text_dim": int(text_cache["text_features"].shape[-1]),
        "hidden_dim": int(config.get("hidden_dim", 96)),
        "num_heads": int(config.get("num_heads", 4)),
        "num_layers": int(config.get("num_layers", 2)),
        "use_text": bool(config.get("use_text", True)),
        "use_candidate_attention": bool(config.get("use_candidate_attention", True)),
        **count_parameters(model),
    }
    print("model_summary=" + json.dumps(model_summary, sort_keys=True))

    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(config.get("learning_rate", 7e-4)),
        weight_decay=float(config.get("weight_decay", 0.0)),
    )
    pose_loss_weight = float(config.get("pose_loss_weight", 0.1))
    ranking_loss_weight = float(config.get("ranking_loss_weight", 1.0))
    epochs = int(config.get("epochs", 8))

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
    comparison = comparison_table(
        test_metrics,
        load_test_metrics(config.get("candidate_ranker_metrics_path", "results/logs/hot3d_candidate_ranker_pilot.json")),
        load_test_metrics(config.get("vl_candidate_ranker_metrics_path", "results/logs/hot3d_vl_candidate_ranker_pilot.json")),
    )

    metrics_payload = {
        "notice": PILOT_NOTICE,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "mode": "prehoi_former_v1",
        "config": config,
        "model_summary": model_summary,
        "text_features": {
            "path": text_cache["path"],
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
        "comparison": comparison,
    }

    metrics_path = Path(config.get("metrics_path", "results/logs/prehoi_former_v1_pilot.json"))
    checkpoint_path = Path(config.get("checkpoint_path", "results/checkpoints/prehoi_former_v1_pilot.pt"))
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with metrics_path.open("w", encoding="utf-8") as handle:
        json.dump(metrics_payload, handle, indent=2)
    torch.save(best_state or {"model_state_dict": model.state_dict(), "config": config}, checkpoint_path)

    print("test_metrics=" + json.dumps(test_metrics, sort_keys=True))
    print("comparison=" + json.dumps(comparison["summary"], sort_keys=True))
    print(f"saved_metrics_path={metrics_path}")
    print(f"saved_checkpoint_path={checkpoint_path}")
    print(PILOT_NOTICE)


if __name__ == "__main__":
    main()
