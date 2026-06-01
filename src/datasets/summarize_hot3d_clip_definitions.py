"""Summarize HOT3D-Clips root metadata without downloading or training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clip_metadata import (
    downloaded_clip_ids,
    expected_shard_path,
    grouped_clip_ids,
    load_clip_definitions,
    load_clip_splits,
    object_metadata_distribution,
    sequence_distribution,
    split_counts,
    split_lookup,
    top_level_definition_keys,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize HOT3D-Clips clip metadata.")
    parser.add_argument("--root", type=Path, default=Path("data/raw/hot3d_clips"))
    parser.add_argument("--max-ids-per-group", type=int, default=8)
    parser.add_argument("--max-mapping-examples", type=int, default=12)
    return parser.parse_args()


def build_summary(args: argparse.Namespace) -> dict[str, object]:
    clip_definitions = load_clip_definitions(args.root)
    clip_splits = load_clip_splits(args.root)
    lookup = split_lookup(clip_splits)
    downloaded = downloaded_clip_ids(args.root)

    mapping_examples: list[dict[str, object]] = []
    for clip_id in sorted(lookup, key=lambda value: int(value))[: args.max_mapping_examples]:
        split_info = lookup[clip_id]
        expected_path = expected_shard_path(clip_id, split_info["split"], split_info["device"])
        mapping_examples.append(
            {
                "clip_id": clip_id,
                "split": split_info["split"],
                "device": split_info["device"],
                "expected_shard_path": expected_path,
                "already_downloaded": clip_id in downloaded,
            }
        )

    definition_keys = top_level_definition_keys(clip_definitions)
    object_distribution = object_metadata_distribution(clip_definitions)
    return {
        "root": str(args.root),
        "total_number_of_clips": len(clip_definitions),
        "split_counts": split_counts(clip_splits),
        "available_top_level_metadata_keys": dict(definition_keys.most_common()),
        "sequence_metadata_summary": sequence_distribution(clip_definitions),
        "object_metadata_summary": object_distribution,
        "clip_ids_grouped_by_split": grouped_clip_ids(
            clip_splits,
            max_per_group=max(1, args.max_ids_per_group),
        ),
        "downloaded_clip_ids": sorted(downloaded, key=lambda value: int(value)),
        "expected_shard_mapping_examples": mapping_examples,
        "notes": [
            "Expected shard paths are inferred from clip_splits.json split/device groups.",
            "No shard is downloaded by this script.",
            "Object names/IDs are reported only if present in clip_definitions.json.",
        ],
    }


def main() -> None:
    args = parse_args()
    summary = build_summary(args)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
