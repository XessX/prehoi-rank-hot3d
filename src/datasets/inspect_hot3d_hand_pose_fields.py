"""Inspect HOT3D-Clips hand-pose fields without converting them to joints."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HAND_SHAPES_MEMBER = "__hand_shapes.json__"
HAND_NAMES = ("left", "right")
FRAME_MEMBER_RE = re.compile(r"^(?P<frame_id>\d{1,8})\.(?P<key>.+)$")
OFFICIAL_SPLIT_DIRS = ("train_aria", "train_quest3", "test_aria", "test_quest3")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HOT3D-Clips hand-pose JSON fields.")
    parser.add_argument("--root", type=Path, required=True, help="HOT3D-Clips root directory.")
    parser.add_argument("--max-shards", type=int, default=3)
    parser.add_argument("--max-frames", type=int, default=3)
    return parser.parse_args()


def summarize_value(value: Any, *, max_items: int = 5) -> dict[str, Any]:
    """Return a short type/shape/value summary without dumping large arrays."""
    if isinstance(value, dict):
        return {
            "type": "dict",
            "num_keys": len(value),
            "keys": list(value.keys())[:max_items],
            "truncated_keys": max(0, len(value) - max_items),
        }
    if isinstance(value, list):
        numeric = [float(item) for item in value if isinstance(item, (int, float)) and not isinstance(item, bool)]
        summary: dict[str, Any] = {
            "type": "list",
            "length": len(value),
            "example": value[:max_items],
            "truncated_items": max(0, len(value) - max_items),
        }
        if numeric:
            summary.update(
                {
                    "numeric_count": len(numeric),
                    "numeric_min": min(numeric),
                    "numeric_max": max(numeric),
                }
            )
        return summary
    if isinstance(value, str):
        return {"type": "str", "example": value[:120]}
    if isinstance(value, bool):
        return {"type": "bool", "example": value}
    if value is None:
        return {"type": "null", "example": None}
    if isinstance(value, (int, float)):
        return {"type": type(value).__name__, "example": value}
    return {"type": type(value).__name__, "example": repr(value)[:120]}


def list_shards(root: str | Path) -> list[Path]:
    root = Path(root)
    shards: list[Path] = []
    for split_dir in OFFICIAL_SPLIT_DIRS:
        split_path = root / split_dir
        if split_path.exists():
            shards.extend(sorted(split_path.glob("*.tar")))
    return shards if shards else sorted(root.rglob("*.tar")) if root.exists() else []


def list_frame_ids_from_tar(tar_path: str | Path) -> list[str]:
    frame_ids: set[str] = set()
    with tarfile.open(tar_path, mode="r") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            match = FRAME_MEMBER_RE.match(Path(member.name).name)
            if match:
                frame_ids.add(match.group("frame_id"))
    return sorted(frame_ids)


def get_frame_member_names(frame_id: str) -> dict[str, str]:
    frame_id = str(frame_id).zfill(6)
    return {"hands": f"{frame_id}.hands.json"}


def read_json_member(tar_path: str | Path, member_name: str) -> Any:
    with tarfile.open(tar_path, mode="r") as tar:
        file_obj = tar.extractfile(member_name)
        if file_obj is None:
            raise FileNotFoundError(f"Tar member not found or not a file: {member_name}")
        return json.load(file_obj)


def summarize_mapping(mapping: Any) -> dict[str, Any]:
    if not isinstance(mapping, dict):
        return summarize_value(mapping)
    return {str(key): summarize_value(value) for key, value in mapping.items()}


def record_pose_fields(
    hands_json: dict[str, Any],
    aggregate: dict[str, Counter[str]],
    examples: dict[str, Any],
) -> None:
    for hand_name in HAND_NAMES:
        hand_record = hands_json.get(hand_name)
        if not isinstance(hand_record, dict):
            aggregate[f"{hand_name}.presence"]["missing"] += 1
            continue

        aggregate[f"{hand_name}.presence"]["present"] += 1
        for key in hand_record:
            aggregate[f"{hand_name}.hand_keys"][str(key)] += 1

        mano_pose = hand_record.get("mano_pose")
        if isinstance(mano_pose, dict):
            aggregate[f"{hand_name}.mano_pose"]["present"] += 1
            for key, value in mano_pose.items():
                aggregate[f"{hand_name}.mano_pose.keys"][str(key)] += 1
                examples.setdefault(f"{hand_name}.mano_pose.{key}", summarize_value(value))
            if isinstance(mano_pose.get("wrist_xform"), list) and len(mano_pose["wrist_xform"]) >= 6:
                aggregate[f"{hand_name}.mano_pose.has_global_orientation"]["yes"] += 1
                aggregate[f"{hand_name}.mano_pose.has_translation"]["yes"] += 1
            if isinstance(mano_pose.get("thetas"), list):
                aggregate[f"{hand_name}.mano_pose.theta_lengths"][str(len(mano_pose["thetas"]))] += 1
        else:
            aggregate[f"{hand_name}.mano_pose"]["missing"] += 1

        umetrack_pose = hand_record.get("umetrack_pose")
        if isinstance(umetrack_pose, dict):
            aggregate[f"{hand_name}.umetrack_pose"]["present"] += 1
            for key, value in umetrack_pose.items():
                aggregate[f"{hand_name}.umetrack_pose.keys"][str(key)] += 1
                examples.setdefault(f"{hand_name}.umetrack_pose.{key}", summarize_value(value))
            if isinstance(umetrack_pose.get("joint_angles"), list):
                aggregate[f"{hand_name}.umetrack_pose.joint_angle_lengths"][str(len(umetrack_pose["joint_angles"]))] += 1
            if isinstance(umetrack_pose.get("wrist_xform"), list):
                aggregate[f"{hand_name}.umetrack_pose.has_wrist_xform"]["yes"] += 1
            if isinstance(umetrack_pose.get("T_world_from_wrist"), list):
                aggregate[f"{hand_name}.umetrack_pose.has_T_world_from_wrist"]["yes"] += 1
        else:
            aggregate[f"{hand_name}.umetrack_pose"]["missing"] += 1

        examples.setdefault(f"{hand_name}.boxes_amodal", summarize_value(hand_record.get("boxes_amodal")))
        examples.setdefault(f"{hand_name}.visibilities_modeled", summarize_value(hand_record.get("visibilities_modeled")))


def inspect_shard(shard: Path, max_frames: int) -> dict[str, Any]:
    frame_ids = list_frame_ids_from_tar(shard)[:max(0, max_frames)]
    aggregate: dict[str, Counter[str]] = defaultdict(Counter)
    examples: dict[str, Any] = {}

    hand_shapes_summary: dict[str, Any]
    try:
        hand_shapes = read_json_member(shard, HAND_SHAPES_MEMBER)
        hand_shapes_summary = summarize_mapping(hand_shapes)
        if isinstance(hand_shapes, dict):
            mano = hand_shapes.get("mano")
            if isinstance(mano, dict):
                hand_shapes_summary["mano_nested"] = summarize_mapping(mano)
            aggregate["hand_shapes.keys"].update(str(key) for key in hand_shapes.keys())
            if isinstance(hand_shapes.get("mano"), list):
                aggregate["hand_shapes.mano_lengths"][str(len(hand_shapes["mano"]))] += 1
            if isinstance(hand_shapes.get("mano"), dict):
                for key, value in hand_shapes["mano"].items():
                    aggregate["hand_shapes.mano.keys"][str(key)] += 1
                    if isinstance(value, list):
                        aggregate[f"hand_shapes.mano.{key}.lengths"][str(len(value))] += 1
            if "umetrack" in hand_shapes:
                aggregate["hand_shapes.umetrack"]["present"] += 1
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        hand_shapes_summary = {"read_error": type(exc).__name__, "message": str(exc)}
        aggregate["hand_shapes.read_error"][type(exc).__name__] += 1

    for frame_id in frame_ids:
        member = get_frame_member_names(frame_id)["hands"]
        try:
            hands_json = read_json_member(shard, member)
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            aggregate["hands.read_error"][type(exc).__name__] += 1
            continue
        if isinstance(hands_json, dict):
            record_pose_fields(hands_json, aggregate, examples)

    return {
        "shard": str(shard),
        "frames_inspected": frame_ids,
        "hand_shapes": hand_shapes_summary,
        "field_counts": {key: dict(counter) for key, counter in sorted(aggregate.items())},
        "examples": examples,
    }


def main() -> None:
    args = parse_args()
    shards = list_shards(args.root)[: max(0, args.max_shards)]
    if not shards:
        raise FileNotFoundError(f"No HOT3D-Clips tar shards found under {args.root}")

    payload = {
        "root": str(args.root),
        "max_shards": args.max_shards,
        "max_frames": args.max_frames,
        "shards_found": len(list_shards(args.root)),
        "shards_inspected": [inspect_shard(shard, args.max_frames) for shard in shards],
        "note": "Inspection only. No MANO/UmeTrack-to-joint conversion was performed.",
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
