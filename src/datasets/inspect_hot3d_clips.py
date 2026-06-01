"""Inspect HOT3D-Clips/WebDataset shards without training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_loader import HOT3DClipsAdapter
from src.datasets.hot3d_clips_parser import (
    count_tar_members,
    get_frame_member_names,
    get_member_sizes,
    image_shape_summary,
    list_frame_ids_from_tar,
    list_frame_keys_from_tar,
    list_shards,
    read_image_member,
    read_json_member,
    summarize_json_structure,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HOT3D-Clips tar shards safely.")
    parser.add_argument(
        "clips_root",
        type=Path,
        help="Path to a HOT3D-Clips root containing split folders or tar shards.",
    )
    parser.add_argument(
        "--max-shards",
        type=int,
        default=2,
        help="Maximum tar shards to inspect.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=5,
        help="Maximum frame/sample keys to show per inspected shard.",
    )
    parser.add_argument(
        "--use-webdataset",
        action="store_true",
        help="Optionally try WebDataset iteration if webdataset is installed.",
    )
    parser.add_argument(
        "--no-deep",
        action="store_true",
        help="Skip deep inspection of the first shard.",
    )
    return parser.parse_args()


def deep_inspect_first_shard(clips_root: Path, max_samples: int) -> dict[str, Any]:
    """Inspect the first local shard and summarize actual keys and payloads."""
    shards = list_shards(clips_root)
    if not shards:
        return {
            "available": False,
            "message": "No tar shards found for deep inspection.",
        }

    shard = shards[0]
    frame_ids = list_frame_ids_from_tar(shard)
    if not frame_ids:
        return {
            "available": False,
            "shard": str(shard),
            "message": "No frame IDs found in first shard.",
        }

    first_frame_id = frame_ids[0]
    first_frame_members = get_frame_member_names(first_frame_id)
    json_members = {
        "hands": first_frame_members["hands"],
        "objects": first_frame_members["objects"],
        "cameras": first_frame_members["cameras"],
        "info": first_frame_members["info"],
        "hand_shapes": "__hand_shapes.json__",
    }
    image_members = {
        "214-1": first_frame_members["image_214-1"],
        "1201-1": first_frame_members["image_1201-1"],
        "1201-2": first_frame_members["image_1201-2"],
    }

    sample_json_structures: dict[str, Any] = {}
    for label, member_name in json_members.items():
        try:
            sample_json_structures[label] = summarize_json_structure(
                read_json_member(shard, member_name)
            )
        except Exception as exc:
            sample_json_structures[label] = {"error": str(exc)}

    image_sizes: dict[str, Any] = {}
    for stream_id, member_name in image_members.items():
        try:
            image_sizes[stream_id] = {
                "member": member_name,
                **image_shape_summary(read_image_member(shard, member_name)),
            }
        except Exception as exc:
            image_sizes[stream_id] = {"member": member_name, "error": str(exc)}

    first_n = frame_ids[:max_samples]
    first_frame_member_sizes = get_member_sizes(
        shard,
        [
            *first_frame_members.values(),
            "__hand_shapes.json__",
        ],
    )

    return {
        "available": True,
        "shard_filename": shard.name,
        "shard_path": str(shard),
        "total_tar_members": count_tar_members(shard),
        "number_of_frame_ids": len(frame_ids),
        "first_5_frame_ids": frame_ids[:5],
        "keys_per_first_frames": {
            frame_id: list_frame_keys_from_tar(shard, frame_id)
            for frame_id in first_n[:3]
        },
        "file_sizes_bytes_for_first_frame": first_frame_member_sizes,
        "sample_json_structures": sample_json_structures,
        "image_sizes_for_first_frame": image_sizes,
    }


def main() -> None:
    args = parse_args()
    clips_root = args.clips_root.resolve()
    adapter = HOT3DClipsAdapter(
        clips_root=clips_root,
        max_shards_for_inspection=args.max_shards,
        max_samples_for_inspection=args.max_samples,
    )
    summary = adapter.inspect(use_webdataset=args.use_webdataset)
    if not args.no_deep:
        summary["deep_inspection"] = deep_inspect_first_shard(
            clips_root=clips_root,
            max_samples=args.max_samples,
        )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
