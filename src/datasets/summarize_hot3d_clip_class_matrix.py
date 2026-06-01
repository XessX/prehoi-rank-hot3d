"""Summarize clip-by-class proxy label coverage for HOT3D-Clips."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import load_index_payload
from src.datasets.hot3d_split_optimization import (
    class_clip_coverage,
    class_totals,
    clip_class_matrix,
    eligible_classes,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize HOT3D-Clips clip/class matrix.")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--min-class-samples", type=int, default=30)
    parser.add_argument("--min-class-clips", type=int, default=3)
    return parser.parse_args()


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    payload = load_index_payload(args.index)
    samples = [sample for sample in payload["samples"] if isinstance(sample, dict)]
    matrix = clip_class_matrix(samples)
    totals = class_totals(matrix)
    coverage = class_clip_coverage(matrix)
    classes_1 = sorted(label for label, clips in coverage.items() if len(clips) == 1)
    classes_2 = sorted(label for label, clips in coverage.items() if len(clips) == 2)
    classes_3_plus = sorted(label for label, clips in coverage.items() if len(clips) >= 3)
    recommended = sorted(
        eligible_classes(
            matrix,
            min_class_samples=args.min_class_samples,
            min_class_clips=args.min_class_clips,
        )
    )

    return {
        "index": str(args.index),
        "number_of_clips": len(matrix),
        "number_of_samples": len(samples),
        "number_of_classes": len(totals),
        "per_clip_class_distribution": {
            clip_id: dict(counts.most_common()) for clip_id, counts in sorted(matrix.items())
        },
        "per_class_total_samples": dict(totals.most_common()),
        "per_class_clip_coverage": {label: coverage[label] for label in sorted(coverage)},
        "classes_appearing_in_only_1_clip": classes_1,
        "classes_appearing_in_2_clips": classes_2,
        "classes_appearing_in_3_plus_clips": classes_3_plus,
        "recommended_classes_for_serious_evaluation": recommended,
        "recommendation_rule": {
            "min_class_samples": args.min_class_samples,
            "min_class_clips": args.min_class_clips,
        },
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "note": "Matrix summary only. No training was run.",
    }


def main() -> None:
    args = parse_args()
    print(json.dumps(build_summary(args), indent=2))


if __name__ == "__main__":
    main()
