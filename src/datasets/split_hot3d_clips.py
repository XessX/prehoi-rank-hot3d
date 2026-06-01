"""Create clip-level HOT3D-Clips train/val/test split files."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
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


SPLIT_NAMES = ("train", "val", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split HOT3D-Clips samples by clip_id.")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--val-ratio", type=float, default=0.15)
    parser.add_argument("--test-ratio", type=float, default=0.15)
    parser.add_argument("--label-map", type=Path, default=DEFAULT_LABEL_MAP_PATH)
    return parser.parse_args()


def samples_by_clip(samples: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sample in samples:
        clip_id = str(sample.get("clip_id"))
        grouped[clip_id].append(sample)
    return dict(grouped)


def clip_class_counts(samples: list[dict[str, Any]]) -> Counter[str]:
    counts: Counter[str] = Counter()
    for sample in samples:
        name = selected_object_name(sample)
        if name:
            counts[name] += 1
    return counts


def compute_clip_targets(num_clips: int, train_ratio: float, val_ratio: float, test_ratio: float) -> dict[str, int]:
    ratio_sum = train_ratio + val_ratio + test_ratio
    if ratio_sum <= 0:
        raise ValueError("Split ratios must sum to a positive value.")

    train = round(num_clips * train_ratio / ratio_sum)
    val = round(num_clips * val_ratio / ratio_sum)
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


def distribution_distance(counts: Counter[str], total: int, global_counts: Counter[str], global_total: int) -> float:
    if total <= 0 or global_total <= 0:
        return 0.0
    labels = set(counts) | set(global_counts)
    return sum(abs((counts[label] / total) - (global_counts[label] / global_total)) for label in labels)


def assign_clips(
    grouped: dict[str, list[dict[str, Any]]],
    targets: dict[str, int],
) -> dict[str, list[str]]:
    clip_counts = {clip_id: clip_class_counts(samples) for clip_id, samples in grouped.items()}
    clip_sizes = {clip_id: len(samples) for clip_id, samples in grouped.items()}
    global_counts: Counter[str] = Counter()
    for counts in clip_counts.values():
        global_counts.update(counts)
    global_total = sum(global_counts.values())

    split_clip_ids: dict[str, list[str]] = {name: [] for name in SPLIT_NAMES}
    split_counts: dict[str, Counter[str]] = {name: Counter() for name in SPLIT_NAMES}
    split_sizes: dict[str, int] = {name: 0 for name in SPLIT_NAMES}
    target_sample_sizes = {
        name: (sum(clip_sizes.values()) * targets[name] / max(1, len(grouped))) for name in SPLIT_NAMES
    }

    remaining = set(grouped)
    seen_train_labels: set[str] = set()
    while remaining and len(split_clip_ids["train"]) < targets["train"]:
        chosen = max(
            remaining,
            key=lambda clip_id: (
                _train_coverage_gain(clip_counts[clip_id], seen_train_labels, global_counts),
                len(clip_counts[clip_id]),
                clip_sizes[clip_id],
                -int(clip_id),
            ),
        )
        split_clip_ids["train"].append(chosen)
        split_counts["train"].update(clip_counts[chosen])
        split_sizes["train"] += clip_sizes[chosen]
        seen_train_labels.update(clip_counts[chosen])
        remaining.remove(chosen)

    ordered_clips = sorted(
        remaining,
        key=lambda clip_id: (-clip_sizes[clip_id], _dominant_label(clip_counts[clip_id]), int(clip_id)),
    )

    for clip_id in ordered_clips:
        best_split = None
        best_score = None
        for split_name in ("val", "test"):
            if len(split_clip_ids[split_name]) >= targets[split_name]:
                continue
            projected_counts = split_counts[split_name] + clip_counts[clip_id]
            projected_size = split_sizes[split_name] + clip_sizes[clip_id]
            class_score = distribution_distance(
                projected_counts,
                projected_size,
                global_counts,
                global_total,
            )
            size_score = abs(projected_size - target_sample_sizes[split_name]) / max(1, sum(clip_sizes.values()))
            score = class_score + size_score
            if best_score is None or score < best_score:
                best_score = score
                best_split = split_name

        if best_split is None:
            best_split = "train"
        split_clip_ids[best_split].append(clip_id)
        split_counts[best_split].update(clip_counts[clip_id])
        split_sizes[best_split] += clip_sizes[clip_id]

    return split_clip_ids


def build_split_payload(
    source_payload: dict[str, Any],
    split_name: str,
    clip_ids: list[str],
    samples: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, Any]:
    source_metadata = source_payload.get("metadata", {})
    metadata = dict(source_metadata) if isinstance(source_metadata, dict) else {}
    metadata.update(
        {
            "split": split_name,
            "source_index": str(args.index),
            "split_method": "clip_level_train_coverage_then_greedy_balance",
            "split_ratios": {
                "train": args.train_ratio,
                "val": args.val_ratio,
                "test": args.test_ratio,
            },
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


def split_samples(args: argparse.Namespace) -> dict[str, Any]:
    source_payload = load_index_payload(args.index)
    samples = [sample for sample in source_payload["samples"] if isinstance(sample, dict)]
    grouped = samples_by_clip(samples)
    targets = compute_clip_targets(len(grouped), args.train_ratio, args.val_ratio, args.test_ratio)
    split_clip_ids = assign_clips(grouped, targets)

    label_map = build_label_map(samples)
    save_label_map(label_map, args.label_map)

    output_files: dict[str, str] = {}
    split_summary: dict[str, Any] = {}
    for split_name in SPLIT_NAMES:
        clip_ids = split_clip_ids[split_name]
        split_samples_flat = [sample for clip_id in clip_ids for sample in grouped[clip_id]]
        output_path = args.output_dir / f"hot3d_clips_{split_name}.json"
        write_json(
            output_path,
            build_split_payload(source_payload, split_name, clip_ids, split_samples_flat, args),
        )
        output_files[split_name] = str(output_path)
        split_summary[split_name] = {
            "num_clips": len(clip_ids),
            "clip_ids": clip_ids,
            "num_samples": len(split_samples_flat),
            "class_distribution": class_distribution(split_samples_flat),
        }

    return {
        "source_index": str(args.index),
        "output_files": output_files,
        "label_map_path": str(args.label_map),
        "label_map": label_map,
        "split_targets_by_clip": targets,
        "split_summary": split_summary,
        "note": "Split is by clip_id to avoid sample-level leakage. No training was run.",
    }


def _dominant_label(counts: Counter[str]) -> str:
    if not counts:
        return ""
    return counts.most_common(1)[0][0]


def _train_coverage_gain(
    counts: Counter[str],
    seen_train_labels: set[str],
    global_counts: Counter[str],
) -> int:
    return sum(global_counts[label] for label in counts if label not in seen_train_labels)


def main() -> None:
    args = parse_args()
    summary = split_samples(args)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
