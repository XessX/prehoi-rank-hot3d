"""Collect pilot/debug experiment metrics into one registry table."""

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


SUMMARY_FIELDS = (
    "experiment_name",
    "experiment_type",
    "status",
    "top1_or_accuracy",
    "top3",
    "MRR",
    "macro_f1",
    "pose_MSE",
    "pose_MAE",
    "notes",
)


EXPERIMENT_SPECS = (
    {
        "experiment_name": "metadata_only_baseline",
        "experiment_type": "global_proxy_classification",
        "path": "results/logs/hot3d_metadata_baseline_pilot.json",
        "status": "valid_pilot",
        "notes": "Metadata-only pipeline check; no image/object candidate input; proxy labels are derived.",
    },
    {
        "experiment_name": "object_aware_metadata_baseline",
        "experiment_type": "global_proxy_classification",
        "path": "results/logs/hot3d_object_aware_baseline_pilot.json",
        "status": "valid_pilot",
        "notes": "Leakage-safe object metadata run; inputs use observation-frame candidates only.",
    },
    {
        "experiment_name": "image_stats_visual_object_baseline",
        "experiment_type": "global_proxy_classification",
        "path": "results/logs/hot3d_visual_object_baseline_pilot.json",
        "status": "valid_pilot",
        "notes": "Uses cached observation-frame image statistics, not deep visual embeddings.",
    },
    {
        "experiment_name": "frozen_clip_visual_object_baseline",
        "experiment_type": "global_proxy_classification",
        "path": "results/logs/hot3d_clip_visual_object_baseline_pilot.json",
        "status": "valid_pilot",
        "notes": "Uses cached frozen CLIP observation-frame image features; CLIP is not trained.",
    },
    {
        "experiment_name": "candidate_ranker_non_vl",
        "experiment_type": "candidate_ranking",
        "path": "results/logs/hot3d_candidate_ranker_pilot.json",
        "status": "valid_pilot",
        "notes": "Order-safe candidate ranking with stable_uid ordering; candidate metrics are not global classification.",
    },
    {
        "experiment_name": "candidate_ranker_vl",
        "experiment_type": "candidate_ranking",
        "path": "results/logs/hot3d_vl_candidate_ranker_pilot.json",
        "status": "valid_pilot",
        "notes": "Adds frozen CLIP text features for object names; candidate_order remains stable_uid.",
    },
    {
        "experiment_name": "prehoi_former_v1",
        "experiment_type": "candidate_ranking",
        "path": "results/logs/prehoi_former_v1_pilot.json",
        "status": "valid_pilot",
        "notes": "V1 model-development run with candidate attention/text enabled; compare against ablations.",
    },
    {
        "experiment_name": "prehoi_former_v2",
        "experiment_type": "candidate_ranking",
        "path": "results/logs/prehoi_former_v2_pilot.json",
        "status": "valid_pilot",
        "notes": "Dual-branch v2 with validation-MRR checkpointing; default geometry-only/no-attention config.",
    },
)


EXCLUDED_ROWS = (
    {
        "experiment_name": "object_aware_metadata_pre_leakage_audit",
        "experiment_type": "excluded_debug_attempt",
        "status": "invalid_excluded",
        "top1_or_accuracy": "",
        "top3": "",
        "MRR": "",
        "macro_f1": "",
        "pose_MSE": "",
        "pose_MAE": "",
        "notes": (
            "Superseded by the leakage-safe object-aware run. Forecast-frame object/proxy features were "
            "treated as a scientific risk and must not be used as inputs."
        ),
    },
    {
        "experiment_name": "candidate_ranker_as_is_order_debug",
        "experiment_type": "excluded_debug_attempt",
        "status": "invalid_excluded",
        "top1_or_accuracy": "",
        "top3": "",
        "MRR": "",
        "macro_f1": "",
        "pose_MSE": "",
        "pose_MAE": "",
        "notes": (
            "Excluded because raw/as-is candidate ordering can leak target position. Use stable_uid runs "
            "and candidate-position baselines instead."
        ),
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect pilot experiment metrics into CSV and Markdown tables.")
    parser.add_argument("--logs-dir", type=Path, default=Path("results/logs"))
    parser.add_argument("--ablation-summary", type=Path, default=Path("results/tables/prehoi_former_v1_ablation_summary.csv"))
    parser.add_argument("--output-csv", type=Path, default=Path("results/tables/pilot_experiment_summary.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("paper/pilot_experiment_summary.md"))
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else None


def metric_value(test: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = test.get(key)
        if value is not None:
            return value
    return ""


def normalize_json_experiment(spec: dict[str, str]) -> dict[str, Any]:
    payload = load_json(Path(spec["path"]))
    if payload is None:
        return {
            "experiment_name": spec["experiment_name"],
            "experiment_type": spec["experiment_type"],
            "status": "missing_log",
            "top1_or_accuracy": "",
            "top3": "",
            "MRR": "",
            "macro_f1": "",
            "pose_MSE": "",
            "pose_MAE": "",
            "notes": f"Metrics log missing: {spec['path']}. {spec['notes']}",
        }
    test = payload.get("test", {})
    if not isinstance(test, dict):
        test = {}
    return {
        "experiment_name": spec["experiment_name"],
        "experiment_type": spec["experiment_type"],
        "status": spec["status"],
        "top1_or_accuracy": metric_value(test, "candidate_top1_accuracy", "object_accuracy"),
        "top3": metric_value(test, "candidate_top3_accuracy", "top3_accuracy"),
        "MRR": metric_value(test, "mean_reciprocal_rank"),
        "macro_f1": metric_value(test, "macro_f1"),
        "pose_MSE": metric_value(test, "pose_mse", "pose_MSE"),
        "pose_MAE": metric_value(test, "pose_mae", "pose_MAE"),
        "notes": spec["notes"],
    }


def normalize_ablation_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return [
            {
                "experiment_name": "prehoi_former_v1_ablation_summary",
                "experiment_type": "candidate_ranking_ablation",
                "status": "missing_log",
                "top1_or_accuracy": "",
                "top3": "",
                "MRR": "",
                "macro_f1": "",
                "pose_MSE": "",
                "pose_MAE": "",
                "notes": f"Ablation summary missing: {path}",
            }
        ]
    rows: list[dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            variant = row.get("variant", "unknown")
            rows.append(
                {
                    "experiment_name": f"prehoi_former_v1_ablation/{variant}",
                    "experiment_type": "candidate_ranking_ablation",
                    "status": "valid_pilot",
                    "top1_or_accuracy": row.get("top1", ""),
                    "top3": row.get("top3", ""),
                    "MRR": row.get("mrr", ""),
                    "macro_f1": "",
                    "pose_MSE": row.get("pose_mse", ""),
                    "pose_MAE": row.get("pose_mae", ""),
                    "notes": (
                        "Controlled v1 ablation; pilot/debug only. "
                        f"use_text={row.get('use_text')}, "
                        f"use_candidate_attention={row.get('use_candidate_attention')}, "
                        f"pose_loss_weight={row.get('pose_loss_weight')}."
                    ),
                }
            )
    return rows


def collect_rows(ablation_summary: Path) -> list[dict[str, Any]]:
    rows = [normalize_json_experiment(spec) for spec in EXPERIMENT_SPECS]
    rows.extend(normalize_ablation_rows(ablation_summary))
    rows.extend(dict(row) for row in EXCLUDED_ROWS)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in SUMMARY_FIELDS})


def format_metric(value: Any) -> str:
    if value in ("", None):
        return ""
    try:
        return f"{float(value):.4f}"
    except (TypeError, ValueError):
        return str(value)


def markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = SUMMARY_FIELDS
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        cells = []
        for field in headers:
            value = row.get(field, "")
            if field in {"top1_or_accuracy", "top3", "MRR", "macro_f1", "pose_MSE", "pose_MAE"}:
                value = format_metric(value)
            cells.append(str(value).replace("|", "/"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(
        [
            "# Pilot Experiment Summary",
            "",
            "This file is generated by `src/training/collect_pilot_results.py`.",
            "",
            "All rows are pilot/debug evidence only. Target-object labels are derived proxy labels, not direct HOT3D ground truth. Candidate-ranking metrics and global object-classification metrics are not directly interchangeable.",
            "",
            "Dataset context: HOT3D-Clips local subset, 25 shards, 3250 proxy samples before optimized filtering; optimized split uses 2673 samples across 16 eligible classes.",
            "",
            markdown_table(rows),
            "",
        ]
    )
    path.write_text(content, encoding="utf-8")


def print_compact_table(rows: list[dict[str, Any]]) -> None:
    print("experiment_name,status,top1_or_accuracy,top3,MRR,pose_MAE")
    for row in rows:
        print(
            ",".join(
                [
                    str(row["experiment_name"]),
                    str(row["status"]),
                    format_metric(row.get("top1_or_accuracy")),
                    format_metric(row.get("top3")),
                    format_metric(row.get("MRR")),
                    format_metric(row.get("pose_MAE")),
                ]
            )
        )


def main() -> None:
    args = parse_args()
    rows = collect_rows(args.ablation_summary)
    write_csv(args.output_csv, rows)
    write_markdown(args.output_md, rows)
    print_compact_table(rows)
    print(f"saved_csv={args.output_csv}")
    print(f"saved_markdown={args.output_md}")


if __name__ == "__main__":
    main()
