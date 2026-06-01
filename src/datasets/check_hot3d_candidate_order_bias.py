"""Check candidate-position bias for HOT3D-Clips ranking splits."""

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
    parser = argparse.ArgumentParser(description="Check HOT3D-Clips candidate-order bias.")
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

    rankable = 0
    top1 = 0
    top3 = 0
    reciprocal_rank_sum = 0.0
    random_top1_sum = 0.0
    random_top3_sum = 0.0
    positions: Counter[int] = Counter()
    candidate_counts: Counter[int] = Counter()
    class_counts: Counter[str] = Counter()

    iterator = range(len(dataset))
    if tqdm is not None:
        iterator = tqdm(iterator, desc=f"candidate order {args.index.name}")  # type: ignore[assignment]

    for index in iterator:
        item = dataset[index]
        candidate_count = int(item["candidate_mask"].sum().item())
        candidate_counts[candidate_count] += 1
        if not bool(item["rankable"].item()):
            continue
        target_position = int(item["candidate_target_index"].item())
        rankable += 1
        positions[target_position] += 1
        class_counts[str(item["target_object_name"])] += 1
        if target_position == 0:
            top1 += 1
        if target_position < 3:
            top3 += 1
        reciprocal_rank_sum += 1.0 / float(target_position + 1)
        random_top1_sum += 1.0 / max(1, candidate_count)
        random_top3_sum += min(3, candidate_count) / max(1, candidate_count)

    total = len(dataset)
    summary: dict[str, Any] = {
        "index": str(args.index),
        "candidate_order": args.candidate_order,
        "candidate_order_seed": args.candidate_order_seed,
        "num_samples": total,
        "rankable_count": rankable,
        "non_rankable_count": total - rankable,
        "target_present_percentage": rankable / max(1, total),
        "candidate_count_distribution": {str(key): value for key, value in sorted(candidate_counts.items())},
        "target_candidate_position_distribution": {
            str(key): value for key, value in sorted(positions.items())
        },
        "candidate_0_top1_baseline": top1 / max(1, rankable),
        "first_3_top3_baseline": top3 / max(1, rankable),
        "position_only_mrr": reciprocal_rank_sum / max(1, rankable),
        "expected_random_top1": random_top1_sum / max(1, rankable),
        "expected_random_top3": random_top3_sum / max(1, rankable),
        "class_distribution_rankable_samples": dict(class_counts.most_common()),
        "label_status": "target proxy labels are derived labels, not direct HOT3D ground truth",
        "input_safety": "candidate features are computed from observation frames only",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
