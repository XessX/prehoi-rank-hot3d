"""Summarize pilot seed-stability metrics."""

from __future__ import annotations

import argparse
import csv
import math
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize pilot seed-stability metrics.")
    parser.add_argument("--summary", type=Path, default=Path("results/tables/pilot_seed_stability_summary.csv"))
    return parser.parse_args()


def parse_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def load_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Seed-stability summary not found: {path}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def mean_std(values: list[float]) -> tuple[float, float]:
    if not values:
        return float("nan"), float("nan")
    mean = sum(values) / len(values)
    if len(values) == 1:
        return mean, 0.0
    variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
    return mean, math.sqrt(variance)


def format_mean_std(values: list[float]) -> str:
    mean, std = mean_std(values)
    if math.isnan(mean):
        return "n/a"
    return f"{mean:.4f} +/- {std:.4f}"


def grouped_metrics(rows: list[dict[str, str]]) -> dict[str, dict[str, list[float]]]:
    grouped: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        model = row.get("model_name", "unknown")
        for metric in ("top1", "top3", "MRR", "pose_MSE", "pose_MAE"):
            value = parse_float(row.get(metric))
            if value is not None:
                grouped[model][metric].append(value)
    return grouped


def best_by_mean(grouped: dict[str, dict[str, list[float]]], metric: str, higher_is_better: bool) -> tuple[str, float] | None:
    scored: list[tuple[str, float]] = []
    for model, metrics in grouped.items():
        values = metrics.get(metric, [])
        if not values:
            continue
        mean, _ = mean_std(values)
        scored.append((model, mean))
    if not scored:
        return None
    return (max if higher_is_better else min)(scored, key=lambda item: item[1])


def main() -> None:
    args = parse_args()
    rows = load_rows(args.summary)
    grouped = grouped_metrics(rows)
    print("PILOT SEED-STABILITY SUMMARY -- NOT FINAL PAPER RESULTS")
    print("Proxy labels are derived proxy labels, not direct HOT3D ground truth.")
    print(f"summary={args.summary}")
    print("model_name,n,top1_mean_std,MRR_mean_std,pose_MAE_mean_std")
    for model in sorted(grouped):
        metrics = grouped[model]
        n = len(metrics.get("MRR", []))
        print(
            f"{model},{n},"
            f"{format_mean_std(metrics.get('top1', []))},"
            f"{format_mean_std(metrics.get('MRR', []))},"
            f"{format_mean_std(metrics.get('pose_MAE', []))}"
        )

    best_ranking = best_by_mean(grouped, "MRR", higher_is_better=True)
    best_top1 = best_by_mean(grouped, "top1", higher_is_better=True)
    best_pose = best_by_mean(grouped, "pose_MAE", higher_is_better=False)
    if best_ranking:
        print(f"best stable ranking model by mean MRR: {best_ranking[0]} ({best_ranking[1]:.4f})")
    if best_top1:
        print(f"best stable top-1 model: {best_top1[0]} ({best_top1[1]:.4f})")
    if best_pose:
        print(f"best stable pose model by mean MAE: {best_pose[0]} ({best_pose[1]:.4f})")
    print("Use these as pilot stability diagnostics only, not final paper claims.")


if __name__ == "__main__":
    main()
