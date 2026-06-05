"""Define and optionally run the PreHOI-Rank final candidate-ranker protocol."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import load_yaml


PROTOCOL_NOTICE = (
    "FINAL-PROTOCOL CANDIDATE RUN -- REVIEW REQUIRED BEFORE ANY PAPER CLAIM"
)
LABEL_NOTICE = "Target-object labels are derived proxy labels, not direct HOT3D ground truth."
SUMMARY_FIELDS = ("model_name", "seed", "top1", "top3", "MRR", "pose_MSE", "pose_MAE", "notes")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or execute the PreHOI-Rank final candidate-ranker protocol."
    )
    parser.add_argument("--config", type=Path, default=Path("configs/hot3d_candidate_ranker.yaml"))
    parser.add_argument("--model", default="candidate_ranker_non_vl", choices=["candidate_ranker_non_vl"])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 123, 2026, 7, 99])
    parser.add_argument("--logs-dir", type=Path, default=Path("results/logs/final_protocol"))
    parser.add_argument(
        "--summary-csv",
        type=Path,
        default=Path("results/tables/final_candidate_ranker_summary.csv"),
    )
    parser.add_argument("--dry-run", action="store_true", help="Print the planned workflow without training.")
    return parser.parse_args()


def require_path(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Required {label} not found: {path}")


def load_and_validate_config(config_path: Path) -> dict[str, Any]:
    require_path(config_path, "config")
    config = load_yaml(config_path)
    candidate_order = str(config.get("candidate_order", ""))
    if candidate_order != "stable_uid":
        raise ValueError(f"Final protocol requires candidate_order: stable_uid, got {candidate_order!r}.")
    for key in ("train_index", "val_index", "test_index", "label_map_path"):
        value = config.get(key)
        if not value:
            raise ValueError(f"Missing required config entry: {key}")
        require_path(Path(value), key)
    return config


def split_preview(index_path: Path) -> dict[str, Any]:
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        samples = payload.get("samples", [])
    elif isinstance(payload, list):
        samples = payload
    else:
        samples = []
    if not isinstance(samples, list):
        samples = []
    clip_ids = sorted({str(sample.get("clip_id", "")) for sample in samples if isinstance(sample, dict)})
    unsafe_count = sum(
        1
        for sample in samples
        if isinstance(sample, dict) and bool(sample.get("input_uses_forecast_frame", False))
    )
    return {
        "path": str(index_path),
        "samples": len(samples),
        "clips": len([clip_id for clip_id in clip_ids if clip_id]),
        "input_uses_forecast_frame_count": unsafe_count,
    }


def build_plan(args: argparse.Namespace, config: dict[str, Any]) -> dict[str, Any]:
    split_paths = {
        "train": Path(config["train_index"]),
        "val": Path(config["val_index"]),
        "test": Path(config["test_index"]),
    }
    split_summaries = {name: split_preview(path) for name, path in split_paths.items()}
    return {
        "notice": PROTOCOL_NOTICE,
        "label_notice": LABEL_NOTICE,
        "model": args.model,
        "config": str(args.config),
        "candidate_order": config.get("candidate_order"),
        "input_safety_required": "input_uses_forecast_frame=false",
        "seeds": args.seeds,
        "logs_dir": str(args.logs_dir),
        "summary_csv": str(args.summary_csv),
        "split_summaries": split_summaries,
        "commands": [
            "python src/datasets/check_hot3d_split_quality.py "
            "--train data/processed/hot3d_clips_train_optimized.json "
            "--val data/processed/hot3d_clips_val_optimized.json "
            "--test data/processed/hot3d_clips_test_optimized.json "
            "--label-map data/processed/hot3d_target_object_label_map.json",
            "python src/datasets/check_hot3d_candidate_order_bias.py "
            "--index data/processed/hot3d_clips_test_optimized.json --candidate-order stable_uid",
            "python src/training/run_final_candidate_ranker_protocol.py "
            "--seeds " + " ".join(str(seed) for seed in args.seeds),
        ],
    }


def assert_split_safety(plan: dict[str, Any]) -> None:
    unsafe = {
        name: summary["input_uses_forecast_frame_count"]
        for name, summary in plan["split_summaries"].items()
        if int(summary["input_uses_forecast_frame_count"]) > 0
    }
    if unsafe:
        raise RuntimeError(f"Final protocol refuses forecast-frame inputs: {unsafe}")


def write_summary_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def run_protocol(args: argparse.Namespace) -> list[dict[str, Any]]:
    from src.training.run_pilot_seed_stability import run_candidate_ranker

    args.logs_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for seed in args.seeds:
        row = run_candidate_ranker(seed, args.logs_dir)
        row["notes"] = (
            f"{PROTOCOL_NOTICE}; {LABEL_NOTICE}; candidate_order=stable_uid; "
            f"metrics_path={args.logs_dir / ('candidate_ranker_non_vl_seed' + str(seed) + '.json')}"
        )
        rows.append(row)
    write_summary_csv(args.summary_csv, rows)
    return rows


def main() -> None:
    args = parse_args()
    config = load_and_validate_config(args.config)
    plan = build_plan(args, config)
    assert_split_safety(plan)

    print(PROTOCOL_NOTICE)
    print(LABEL_NOTICE)
    print(json.dumps(plan, indent=2))

    if args.dry_run:
        print("dry_run=true; no training was run.")
        return

    rows = run_protocol(args)
    print("dry_run=false; protocol candidate runs completed.")
    print(f"saved_summary_csv={args.summary_csv}")
    print("model_name,seed,top1,top3,MRR,pose_MSE,pose_MAE")
    for row in rows:
        print(
            f"{row['model_name']},{row['seed']},"
            f"{float(row['top1']):.4f},{float(row['top3']):.4f},"
            f"{float(row['MRR']):.4f},{float(row['pose_MSE']):.4f},"
            f"{float(row['pose_MAE']):.4f}"
        )
    print(PROTOCOL_NOTICE)


if __name__ == "__main__":
    main()
