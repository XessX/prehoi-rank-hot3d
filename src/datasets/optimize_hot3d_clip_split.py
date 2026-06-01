"""Optimize clip-level HOT3D-Clips splits from actual proxy class coverage."""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import (
    DEFAULT_LABEL_MAP_PATH,
    build_label_map,
    class_distribution,
    load_index_payload,
    save_label_map,
    selected_object_name,
)
from src.datasets.hot3d_split_optimization import (
    class_clip_coverage,
    class_distribution_for_clips,
    class_totals,
    clip_class_matrix,
    eligible_classes,
    filter_samples_to_classes,
    sample_count_for_clips,
    samples_by_clip,
)


SPLIT_NAMES = ("train", "val", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Optimize HOT3D-Clips clip-level split.")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--min-class-samples", type=int, default=30)
    parser.add_argument("--min-class-clips", type=int, default=2)
    parser.add_argument("--num-attempts", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=123)
    parser.add_argument("--label-map", type=Path, default=DEFAULT_LABEL_MAP_PATH)
    return parser.parse_args()


def compute_targets(num_clips: int, ratios: dict[str, float]) -> dict[str, int]:
    ratio_sum = sum(ratios.values())
    if ratio_sum <= 0:
        raise ValueError("Split ratios must sum to a positive value.")
    train = round(num_clips * ratios["train"] / ratio_sum)
    val = round(num_clips * ratios["val"] / ratio_sum)
    test = num_clips - train - val
    if num_clips >= 3:
        train = max(1, train)
        val = max(1, val)
        test = max(1, test)
    while train + val + test > num_clips:
        if train >= val and train >= test and train > 1:
            train -= 1
        elif test > 1:
            test -= 1
        else:
            val -= 1
    while train + val + test < num_clips:
        train += 1
    return {"train": train, "val": val, "test": test}


def random_assignment(clip_ids: list[str], targets: dict[str, int], rng: random.Random) -> dict[str, list[str]]:
    shuffled = list(clip_ids)
    rng.shuffle(shuffled)
    train_end = targets["train"]
    val_end = train_end + targets["val"]
    return {
        "train": sorted(shuffled[:train_end]),
        "val": sorted(shuffled[train_end:val_end]),
        "test": sorted(shuffled[val_end:]),
    }


def split_classes(matrix: dict[str, Counter[str]], clip_ids: list[str]) -> set[str]:
    classes: set[str] = set()
    for clip_id in clip_ids:
        classes.update(matrix[clip_id])
    return classes


def score_assignment(
    assignment: dict[str, list[str]],
    matrix: dict[str, Counter[str]],
    grouped: dict[str, list[dict[str, Any]]],
    allowed_classes: set[str],
    ratios: dict[str, float],
) -> tuple[float, dict[str, Any]]:
    train_classes = split_classes(matrix, assignment["train"])
    val_classes = split_classes(matrix, assignment["val"])
    test_classes = split_classes(matrix, assignment["test"])
    shared_classes = train_classes & val_classes & test_classes
    train_covers_eval = (val_classes | test_classes).issubset(train_classes)
    val_missing = allowed_classes - val_classes
    test_missing = allowed_classes - test_classes
    train_missing = allowed_classes - train_classes

    total_samples = sum(len(samples) for samples in grouped.values())
    split_samples = {
        name: sample_count_for_clips(grouped, assignment[name]) for name in SPLIT_NAMES
    }
    ratio_error = sum(
        abs((split_samples[name] / total_samples) - ratios[name]) for name in SPLIT_NAMES
    )

    score = 0.0
    score += 1000.0 * len(shared_classes)
    score += 200.0 * min(len(val_classes), len(test_classes))
    score += 100.0 * len(train_classes)
    score -= 5000.0 * len(train_missing)
    score -= 500.0 * len(val_missing)
    score -= 500.0 * len(test_missing)
    score -= 1000.0 if not train_covers_eval else 0.0
    score -= 250.0 * ratio_error

    details = {
        "score": score,
        "shared_classes": sorted(shared_classes),
        "num_shared_classes": len(shared_classes),
        "train_classes": sorted(train_classes),
        "val_classes": sorted(val_classes),
        "test_classes": sorted(test_classes),
        "classes_missing_from_train": sorted(train_missing),
        "classes_missing_from_val": sorted(val_missing),
        "classes_missing_from_test": sorted(test_missing),
        "train_covers_val_test_classes": train_covers_eval,
        "sample_counts": split_samples,
        "sample_ratio_error": ratio_error,
    }
    return score, details


def optimize_assignment(
    grouped: dict[str, list[dict[str, Any]]],
    matrix: dict[str, Counter[str]],
    allowed_classes: set[str],
    ratios: dict[str, float],
    num_attempts: int,
    seed: int,
) -> tuple[dict[str, list[str]], dict[str, Any]]:
    clip_ids = sorted(grouped)
    targets = compute_targets(len(clip_ids), ratios)
    rng = random.Random(seed)
    best_assignment: dict[str, list[str]] | None = None
    best_details: dict[str, Any] | None = None
    best_score: float | None = None

    deterministic = coverage_seed_assignment(clip_ids, matrix, targets, allowed_classes)
    candidates = [deterministic]
    for _ in range(max(0, num_attempts)):
        candidates.append(random_assignment(clip_ids, targets, rng))

    for assignment in candidates:
        score, details = score_assignment(assignment, matrix, grouped, allowed_classes, ratios)
        if best_score is None or score > best_score:
            best_score = score
            best_assignment = assignment
            best_details = details

    assert best_assignment is not None and best_details is not None
    best_details["clip_targets"] = targets
    best_details["num_attempts"] = num_attempts
    best_details["seed"] = seed
    return best_assignment, best_details


def coverage_seed_assignment(
    clip_ids: list[str],
    matrix: dict[str, Counter[str]],
    targets: dict[str, int],
    allowed_classes: set[str],
) -> dict[str, list[str]]:
    remaining = set(clip_ids)
    assignment = {name: [] for name in SPLIT_NAMES}
    for split_name in ("val", "test", "train"):
        covered: set[str] = set()
        while remaining and len(assignment[split_name]) < targets[split_name]:
            chosen = max(
                remaining,
                key=lambda clip_id: (
                    len((set(matrix[clip_id]) & allowed_classes) - covered),
                    sum(matrix[clip_id][label] for label in allowed_classes),
                    -int(clip_id),
                ),
            )
            assignment[split_name].append(chosen)
            covered.update(set(matrix[chosen]) & allowed_classes)
            remaining.remove(chosen)
    for clip_id in sorted(remaining):
        assignment["train"].append(clip_id)
    return {name: sorted(ids) for name, ids in assignment.items()}


def build_split_payload(
    source_payload: dict[str, Any],
    split_name: str,
    clip_ids: list[str],
    samples: list[dict[str, Any]],
    args: argparse.Namespace,
    allowed_classes: set[str],
) -> dict[str, Any]:
    metadata = dict(source_payload.get("metadata", {}))
    metadata.update(
        {
            "split": split_name,
            "source_index": str(args.index),
            "split_method": "optimized_clip_level_proxy_class_coverage",
            "split_ratios": {
                "train": args.train_ratio,
                "val": args.val_ratio,
                "test": args.test_ratio,
            },
            "min_class_samples": args.min_class_samples,
            "min_class_clips": args.min_class_clips,
            "eligible_classes": sorted(allowed_classes),
            "clip_ids": clip_ids,
            "num_clips": len(clip_ids),
            "num_samples": len(samples),
            "class_distribution": class_distribution(samples),
            "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        }
    )
    return {
        "schema_version": source_payload.get("schema_version", "hot3d_clips_sample_index_v0"),
        "metadata": metadata,
        "samples": samples,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def main() -> None:
    args = parse_args()
    payload = load_index_payload(args.index)
    raw_samples = [sample for sample in payload["samples"] if isinstance(sample, dict)]
    raw_matrix = clip_class_matrix(raw_samples)
    allowed_classes = eligible_classes(
        raw_matrix,
        min_class_samples=args.min_class_samples,
        min_class_clips=args.min_class_clips,
    )
    filtered_samples = filter_samples_to_classes(raw_samples, allowed_classes)
    grouped = samples_by_clip(filtered_samples)
    matrix = clip_class_matrix(filtered_samples)
    ratios = {"train": args.train_ratio, "val": args.val_ratio, "test": args.test_ratio}
    assignment, details = optimize_assignment(
        grouped=grouped,
        matrix=matrix,
        allowed_classes=allowed_classes,
        ratios=ratios,
        num_attempts=args.num_attempts,
        seed=args.seed,
    )

    output_files = {
        "train": args.output_dir / "hot3d_clips_train_optimized.json",
        "val": args.output_dir / "hot3d_clips_val_optimized.json",
        "test": args.output_dir / "hot3d_clips_test_optimized.json",
    }

    split_summary: dict[str, Any] = {}
    for split_name in SPLIT_NAMES:
        split_samples = [sample for clip_id in assignment[split_name] for sample in grouped[clip_id]]
        write_json(
            output_files[split_name],
            build_split_payload(payload, split_name, assignment[split_name], split_samples, args, allowed_classes),
        )
        split_summary[split_name] = {
            "path": str(output_files[split_name]),
            "clip_ids": assignment[split_name],
            "num_clips": len(assignment[split_name]),
            "num_samples": len(split_samples),
            "class_distribution": class_distribution(split_samples),
        }

    label_map = build_label_map(filtered_samples)
    save_label_map(label_map, args.label_map)
    report = {
        "source_index": str(args.index),
        "raw_num_samples": len(raw_samples),
        "filtered_num_samples": len(filtered_samples),
        "raw_num_classes": len(class_totals(raw_matrix)),
        "eligible_num_classes": len(allowed_classes),
        "eligible_classes": sorted(allowed_classes),
        "filtered_out_classes": sorted(set(class_totals(raw_matrix)) - allowed_classes),
        "per_class_clip_coverage": class_clip_coverage(matrix),
        "optimization": details,
        "split_summary": split_summary,
        "label_map_path": str(args.label_map),
        "label_map": label_map,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "note": "Optimized split only. No training was run.",
    }
    report_path = args.output_dir / "hot3d_optimized_split_report.json"
    write_json(report_path, report)
    report["report_path"] = str(report_path)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
