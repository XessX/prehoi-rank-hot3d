"""Inspect candidate-ranking coverage for HOT3D-Clips split indexes."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import HOT3DClipsDataset

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HOT3D-Clips candidate-ranking coverage.")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--label-map-path", type=Path, default=Path("data/processed/hot3d_target_object_label_map.json"))
    parser.add_argument("--max-candidates", type=int, default=8)
    parser.add_argument(
        "--candidate-order",
        choices=("stable_uid", "random_seeded", "as_is"),
        default="stable_uid",
    )
    parser.add_argument("--candidate-order-seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dataset = HOT3DClipsDataset(
        args.index,
        mode="object_metadata",
        label_map_path=args.label_map_path,
        max_candidates=args.max_candidates,
        candidate_order=args.candidate_order,
        candidate_order_seed=args.candidate_order_seed,
    )

    rankable_count = 0
    non_rankable_count = 0
    candidate_counts: Counter[int] = Counter()
    target_positions: Counter[int] = Counter()
    rankable_classes: Counter[str] = Counter()

    iterator = range(len(dataset))
    if tqdm is not None:
        iterator = tqdm(iterator, desc=f"inspect {args.index.name}")  # type: ignore[assignment]

    for index in iterator:
        item = dataset[index]
        candidate_count = int(item["candidate_mask"].sum().item())
        candidate_counts[candidate_count] += 1
        if bool(item["rankable"].item()):
            rankable_count += 1
            target_index = int(item["candidate_target_index"].item())
            target_positions[target_index] += 1
            rankable_classes[str(item["target_object_name"])] += 1
        else:
            non_rankable_count += 1

    sample_count = len(dataset)
    summary: dict[str, Any] = {
        "index": str(args.index),
        "num_samples": sample_count,
        "rankable_sample_count": rankable_count,
        "non_rankable_count": non_rankable_count,
        "target_present_percentage": rankable_count / max(1, sample_count),
        "candidate_count_distribution": {str(key): value for key, value in sorted(candidate_counts.items())},
        "target_candidate_position_distribution": {
            str(key): value for key, value in sorted(target_positions.items())
        },
        "class_distribution_rankable_samples": dict(rankable_classes.most_common()),
        "max_candidates": args.max_candidates,
        "candidate_order": args.candidate_order,
        "candidate_order_seed": args.candidate_order_seed,
        "label_status": "target proxy labels are derived labels, not direct HOT3D ground truth",
        "input_safety": "candidate features are computed from observation frames only",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
