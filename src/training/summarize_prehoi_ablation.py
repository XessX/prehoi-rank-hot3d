"""Summarize PreHOI-Former v1 ablation results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize PreHOI-Former ablation CSV.")
    parser.add_argument("--summary", type=Path, required=True)
    return parser.parse_args()


def load_rows(summary_path: Path) -> list[dict[str, Any]]:
    if not summary_path.exists():
        raise FileNotFoundError(f"Ablation summary CSV not found: {summary_path}")
    with summary_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"No rows found in ablation summary CSV: {summary_path}")
    for row in rows:
        for key in ("top1", "top3", "mrr", "pose_mae", "pose_mse", "ranking_loss", "pose_loss", "pose_loss_weight"):
            row[key] = float(row[key])
        row["epochs"] = int(float(row["epochs"]))
        row["use_text"] = str(row["use_text"]).lower() == "true"
        row["use_candidate_attention"] = str(row["use_candidate_attention"]).lower() == "true"
    return rows


def by_variant(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row["variant"]): row for row in rows}


def delta(a: dict[str, Any] | None, b: dict[str, Any] | None, key: str) -> float | None:
    if a is None or b is None:
        return None
    return float(a[key]) - float(b[key])


def trend_text(value: float | None, *, higher_is_better: bool = True) -> str:
    if value is None:
        return "unavailable"
    if abs(value) < 1.0e-9:
        return "no change"
    helped = value > 0 if higher_is_better else value < 0
    return "helped" if helped else "hurt"


def main() -> None:
    args = parse_args()
    rows = load_rows(args.summary)
    lookup = by_variant(rows)

    best_ranking = max(rows, key=lambda row: row["mrr"])
    best_pose = min(rows, key=lambda row: row["pose_mae"])

    text_attention_delta = delta(
        lookup.get("geometry_text_attention"),
        lookup.get("geometry_only_attention"),
        "mrr",
    )
    text_no_attention_delta = delta(
        lookup.get("geometry_text_no_attention"),
        lookup.get("geometry_only_no_attention"),
        "mrr",
    )
    attention_with_text_delta = delta(
        lookup.get("geometry_text_attention"),
        lookup.get("geometry_text_no_attention"),
        "mrr",
    )
    attention_without_text_delta = delta(
        lookup.get("geometry_only_attention"),
        lookup.get("geometry_only_no_attention"),
        "mrr",
    )
    rank_pose_delta = delta(
        lookup.get("rank_focused"),
        lookup.get("pose_focused"),
        "mrr",
    )
    pose_rank_delta = delta(
        lookup.get("rank_focused"),
        lookup.get("pose_focused"),
        "pose_mae",
    )

    summary = {
        "summary_csv": str(args.summary),
        "best_ranking_model_by_mrr": {
            "variant": best_ranking["variant"],
            "mrr": best_ranking["mrr"],
            "top1": best_ranking["top1"],
            "top3": best_ranking["top3"],
            "pose_mae": best_ranking["pose_mae"],
        },
        "best_pose_model_by_mae": {
            "variant": best_pose["variant"],
            "pose_mae": best_pose["pose_mae"],
            "mrr": best_pose["mrr"],
            "top1": best_pose["top1"],
        },
        "text_effect": {
            "with_attention_mrr_delta": text_attention_delta,
            "with_attention": trend_text(text_attention_delta, higher_is_better=True),
            "without_attention_mrr_delta": text_no_attention_delta,
            "without_attention": trend_text(text_no_attention_delta, higher_is_better=True),
        },
        "attention_effect": {
            "with_text_mrr_delta": attention_with_text_delta,
            "with_text": trend_text(attention_with_text_delta, higher_is_better=True),
            "without_text_mrr_delta": attention_without_text_delta,
            "without_text": trend_text(attention_without_text_delta, higher_is_better=True),
        },
        "loss_weight_tradeoff": {
            "rank_focused_minus_pose_focused_mrr": rank_pose_delta,
            "rank_focused_minus_pose_focused_pose_mae": pose_rank_delta,
            "ranking": trend_text(rank_pose_delta, higher_is_better=True),
            "pose": trend_text(pose_rank_delta, higher_is_better=False),
        },
        "rows": rows,
        "notice": "Pilot/debug ablation only. Proxy labels are derived labels, not direct HOT3D ground truth.",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
