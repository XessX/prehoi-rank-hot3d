"""Print best valid pilot candidate models from the collected summary CSV."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print best valid pilot candidate models.")
    parser.add_argument("--summary", type=Path, default=Path("results/tables/pilot_experiment_summary.csv"))
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
        raise FileNotFoundError(f"Pilot summary not found: {path}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def valid_candidate_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in rows
        if row.get("status") == "valid_pilot"
        and row.get("experiment_type") in {"candidate_ranking", "candidate_ranking_ablation"}
    ]


def best_max(rows: list[dict[str, str]], metric: str) -> dict[str, str] | None:
    scored = [(parse_float(row.get(metric)), row) for row in rows]
    scored = [(score, row) for score, row in scored if score is not None]
    if not scored:
        return None
    return max(scored, key=lambda item: item[0])[1]


def best_min(rows: list[dict[str, str]], metric: str) -> dict[str, str] | None:
    scored = [(parse_float(row.get(metric)), row) for row in rows]
    scored = [(score, row) for score, row in scored if score is not None]
    if not scored:
        return None
    return min(scored, key=lambda item: item[0])[1]


def metric(row: dict[str, str] | None, key: str) -> str:
    if row is None:
        return "n/a"
    value = parse_float(row.get(key))
    if value is None:
        return "n/a"
    return f"{value:.4f}"


def print_row(label: str, row: dict[str, str] | None, primary_metric: str) -> None:
    if row is None:
        print(f"{label}: unavailable")
        return
    print(
        f"{label}: {row.get('experiment_name')} "
        f"({primary_metric}={metric(row, primary_metric)}, "
        f"top1={metric(row, 'top1_or_accuracy')}, "
        f"top3={metric(row, 'top3')}, "
        f"MRR={metric(row, 'MRR')}, "
        f"pose_MAE={metric(row, 'pose_MAE')})"
    )


def main() -> None:
    args = parse_args()
    rows = load_rows(args.summary)
    candidates = valid_candidate_rows(rows)
    print("PILOT DEBUG SUMMARY -- NOT FINAL PAPER RESULTS")
    print("Proxy labels are derived proxy labels, not direct HOT3D ground truth.")
    print("Only valid candidate-ranking pilot rows are considered below.")
    print(f"summary={args.summary}")
    print(f"valid_candidate_rows={len(candidates)}")
    print_row("best ranking by MRR", best_max(candidates, "MRR"), "MRR")
    print_row("best top-1 candidate model", best_max(candidates, "top1_or_accuracy"), "top1_or_accuracy")
    print_row("best pose MAE candidate model", best_min(candidates, "pose_MAE"), "pose_MAE")
    excluded = [row for row in rows if row.get("status") == "invalid_excluded"]
    if excluded:
        print("excluded_rows=" + ", ".join(row.get("experiment_name", "") for row in excluded))


if __name__ == "__main__":
    main()
