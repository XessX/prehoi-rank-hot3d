"""Entry point for the PreHOI-Former MVP pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import torch
from torch.utils.data import DataLoader, random_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_loader import HOT3DPreContactDataset
from src.models.baseline_transformer import BaselineTransformer
from src.training.evaluate import evaluate
from src.training.train import fit
from src.utils.config import load_yaml, merge_dicts
from src.utils.seed import seed_everything


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PreHOI-Former MVP smoke pipeline")
    parser.add_argument("--config", default="configs/model_config.yaml", help="Model/training config")
    parser.add_argument(
        "--dataset-config",
        default="configs/hot3d_config.yaml",
        help="Dataset-specific config",
    )
    parser.add_argument("--eval-only", action="store_true", help="Skip training and only evaluate")
    return parser.parse_args()


def resolve_device(configured_device: str) -> torch.device:
    if configured_device == "auto":
        return torch.device("cuda" if torch.cuda.is_available() else "cpu")
    return torch.device(configured_device)


def build_dataloaders(
    dataset: HOT3DPreContactDataset,
    batch_size: int,
    val_fraction: float,
    num_workers: int,
    seed: int,
) -> tuple[DataLoader, DataLoader]:
    if len(dataset) < 2:
        raise ValueError("Need at least two samples to build train/validation splits.")

    val_size = max(1, int(round(len(dataset) * val_fraction)))
    train_size = len(dataset) - val_size
    if train_size < 1:
        raise ValueError("Validation fraction leaves no training samples.")

    generator = torch.Generator().manual_seed(seed)
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size], generator=generator)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
    )
    return train_loader, val_loader


def build_model(config: dict[str, Any], dataset_config: dict[str, Any]) -> BaselineTransformer:
    model_config = config["model"]
    return BaselineTransformer(
        input_dim=int(model_config.get("input_dim", dataset_config["feature_dim"])),
        hidden_dim=int(model_config["hidden_dim"]),
        num_layers=int(model_config["num_layers"]),
        num_heads=int(model_config["num_heads"]),
        dropout=float(model_config["dropout"]),
        num_objects=int(dataset_config["num_objects"]),
        num_actions=int(dataset_config["num_actions"]),
        future_steps=int(dataset_config["future_steps"]),
        num_hand_joints=int(dataset_config["num_hand_joints"]),
        max_seq_len=int(model_config.get("max_seq_len", dataset_config["seq_len"])),
        pooling=str(model_config.get("pooling", "last")),
    )


def save_run_artifacts(
    history: list[dict[str, Any]],
    final_metrics: dict[str, float],
    config: dict[str, Any],
    dataset_config: dict[str, Any],
    model: torch.nn.Module,
) -> None:
    training_config = config["training"]
    log_dir = PROJECT_ROOT / training_config.get("log_dir", "results/logs")
    checkpoint_dir = PROJECT_ROOT / training_config.get("checkpoint_dir", "results/checkpoints")
    log_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "timestamp_utc": timestamp,
        "synthetic_data": bool(dataset_config.get("use_synthetic", True)),
        "note": "Synthetic smoke-test metrics only; not real HOT3D results.",
        "history": history,
        "final_metrics": final_metrics,
        "config": config,
        "dataset_config": dataset_config,
    }

    log_path = log_dir / f"mvp_run_{timestamp}.json"
    with log_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    checkpoint_path = checkpoint_dir / f"baseline_transformer_{timestamp}.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": config,
            "dataset_config": dataset_config,
            "synthetic_data": bool(dataset_config.get("use_synthetic", True)),
        },
        checkpoint_path,
    )
    print(f"saved_log={log_path}")
    print(f"saved_checkpoint={checkpoint_path}")


def main() -> None:
    args = parse_args()
    config = load_yaml(PROJECT_ROOT / args.config)
    raw_dataset_config = load_yaml(PROJECT_ROOT / args.dataset_config)
    dataset_config = merge_dicts(raw_dataset_config, config.get("dataset", {}))

    seed = int(config.get("seed", 42))
    seed_everything(seed)
    device = resolve_device(str(config.get("device", "auto")))

    dataset = HOT3DPreContactDataset(dataset_config, split="all")
    dataset.print_summary()
    training_config = config["training"]
    train_loader, val_loader = build_dataloaders(
        dataset=dataset,
        batch_size=int(training_config["batch_size"]),
        val_fraction=float(training_config["val_fraction"]),
        num_workers=int(training_config["num_workers"]),
        seed=seed,
    )

    model = build_model(config, dataset_config).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=float(training_config["learning_rate"]),
        weight_decay=float(training_config["weight_decay"]),
    )
    loss_weights = training_config.get("loss_weights", {})

    print(f"device={device}")
    print(f"synthetic_data={dataset_config.get('use_synthetic', True)}")
    print("warning=Metrics from this run are synthetic smoke-test metrics only.")

    history: list[dict[str, Any]] = []
    if not args.eval_only:
        history = fit(
            model=model,
            train_loader=train_loader,
            val_loader=val_loader,
            optimizer=optimizer,
            device=device,
            epochs=int(training_config["epochs"]),
            loss_weights=loss_weights,
        )

    final_metrics = evaluate(model, val_loader, device, loss_weights)
    print(f"final_metrics={json.dumps(final_metrics, indent=2)}")
    save_run_artifacts(history, final_metrics, config, dataset_config, model)


if __name__ == "__main__":
    main()
