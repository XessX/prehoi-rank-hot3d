"""Build a HOT3D-Clips sample index without training.

The generated index records observation frame member names, future hand pose
representations, and visible object candidates. It does not pick a final target
object, create action labels, or define contact labels.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_parser import (
    get_frame_member_names,
    list_frame_keys_from_tar,
    list_frame_ids_from_tar,
    list_shards,
    read_json_member,
)
from src.datasets.hot3d_proxy_labels import TARGET_OBJECT_PROXY_V1_RULE, select_target_object_proxy


IMAGE_STREAM_KEYS = ("image_214-1", "image_1201-1", "image_1201-2")
HAND_NAMES = ("left", "right")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a HOT3D-Clips sample index.")
    parser.add_argument("--root", type=Path, required=True, help="HOT3D-Clips root.")
    parser.add_argument("--output", type=Path, required=True, help="Output sample-index JSON.")
    parser.add_argument("--observation-frames", type=int, default=16)
    parser.add_argument("--forecast-horizon", type=int, default=5)
    parser.add_argument(
        "--hand-source",
        choices=("mano_pose", "umetrack_pose", "auto"),
        default="mano_pose",
        help="Hand representation to store as future target payload.",
    )
    parser.add_argument(
        "--min-visibility",
        type=float,
        default=0.0,
        help="Minimum hand/object visibility required in at least one stream.",
    )
    parser.add_argument(
        "--max-shards",
        type=int,
        default=0,
        help="Optional shard limit. Use 0 for all local shards.",
    )
    parser.add_argument(
        "--assign-target-proxy",
        action="store_true",
        help="Assign derived target-object proxy labels from forecast-frame hand/object box proximity.",
    )
    return parser.parse_args()


def clip_id_from_shard(shard: Path) -> str:
    match = re.search(r"clip-(\d+)", shard.stem)
    return match.group(1) if match else shard.stem


def max_visibility(record: dict[str, Any]) -> float:
    values = record.get("visibilities_modeled", {})
    if isinstance(values, dict) and values:
        numeric = [float(value) for value in values.values() if isinstance(value, (int, float))]
        return max(numeric) if numeric else 0.0
    return 0.0


def is_visible(record: dict[str, Any], min_visibility: float) -> bool:
    return max_visibility(record) > min_visibility


def choose_hand_payload(hand_record: dict[str, Any], hand_source: str) -> tuple[str | None, Any]:
    if hand_source == "auto":
        for candidate in ("mano_pose", "umetrack_pose"):
            if candidate in hand_record:
                return candidate, hand_record[candidate]
        return None, None

    if hand_source in hand_record:
        return hand_source, hand_record[hand_source]
    return None, None


def extract_future_hand_pose(
    hands_json: dict[str, Any],
    hand_source: str,
    min_visibility: float,
) -> tuple[dict[str, Any], list[str], Counter[str], str | None]:
    future_hand_pose: dict[str, Any] = {}
    available_hands: list[str] = []
    missing = Counter()
    source_used: str | None = None

    for hand_name in HAND_NAMES:
        hand_record = hands_json.get(hand_name)
        if not isinstance(hand_record, dict):
            missing[f"missing_{hand_name}_hand"] += 1
            continue
        if not is_visible(hand_record, min_visibility):
            missing[f"not_visible_{hand_name}_hand"] += 1
            continue

        resolved_source, payload = choose_hand_payload(hand_record, hand_source)
        if resolved_source is None or payload is None:
            missing[f"missing_{hand_name}_{hand_source}"] += 1
            continue

        available_hands.append(hand_name)
        source_used = source_used or resolved_source
        future_hand_pose[hand_name] = {
            "source": resolved_source,
            "payload": payload,
            "visibility": max_visibility(hand_record),
            "boxes_amodal": hand_record.get("boxes_amodal", {}),
        }

    return future_hand_pose, available_hands, missing, source_used


def extract_object_candidates(
    objects_json: dict[str, Any],
    min_visibility: float,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    candidates: list[dict[str, Any]] = []
    missing = Counter()

    for object_group_key, instances in objects_json.items():
        if not isinstance(instances, list):
            missing["non_list_object_group"] += 1
            continue
        for instance_index, instance in enumerate(instances):
            if not isinstance(instance, dict):
                missing["non_dict_object_instance"] += 1
                continue
            if not is_visible(instance, min_visibility):
                missing["object_not_visible"] += 1
                continue

            candidates.append(
                {
                    "object_group_key": str(object_group_key),
                    "instance_index": instance_index,
                    "object_uid": instance.get("object_uid"),
                    "object_bop_id": instance.get("object_bop_id"),
                    "object_name": instance.get("object_name"),
                    "visibility": max_visibility(instance),
                    "visibilities_modeled": instance.get("visibilities_modeled", {}),
                    "boxes_amodal": instance.get("boxes_amodal", {}),
                    "has_pose": "T_world_from_object" in instance,
                    "T_world_from_object": instance.get("T_world_from_object"),
                }
            )

    return candidates, missing


def image_stream_keys_for_shard(shard: Path, frame_id: str) -> list[str]:
    frame_keys = list_frame_keys_from_tar(shard, frame_id)
    image_streams = [
        key.removesuffix(".jpg")
        for key in frame_keys
        if key.startswith("image_") and key.endswith(".jpg")
    ]
    return sorted(image_streams) if image_streams else list(IMAGE_STREAM_KEYS)


def observation_image_streams(frame_ids: list[str], image_stream_keys: list[str]) -> dict[str, list[str]]:
    streams = {key: [] for key in image_stream_keys}
    for frame_id in frame_ids:
        for key in image_stream_keys:
            streams[key].append(f"{frame_id}.{key}.jpg")
    return streams


class ShardJsonCache:
    """Read JSON members from one opened shard and cache repeated frame access."""

    def __init__(self, shard: Path) -> None:
        self.shard = shard
        self.tar = tarfile.open(shard, mode="r")
        self.cache: dict[str, Any] = {}

    def close(self) -> None:
        self.tar.close()

    def read(self, member_name: str) -> Any:
        if member_name not in self.cache:
            file_obj = self.tar.extractfile(member_name)
            if file_obj is None:
                raise FileNotFoundError(f"Tar member not found or not a file: {member_name}")
            self.cache[member_name] = json.load(file_obj)
        return self.cache[member_name]


def build_samples_for_shard(
    shard: Path,
    root: Path,
    observation_frames: int,
    forecast_horizon: int,
    hand_source: str,
    min_visibility: float,
    assign_target_proxy: bool,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    frame_ids = list_frame_ids_from_tar(shard)
    samples: list[dict[str, Any]] = []
    skipped = Counter()
    clip_id = clip_id_from_shard(shard)
    shard_rel = str(shard.relative_to(root)) if shard.is_relative_to(root) else str(shard)
    max_start = len(frame_ids) - observation_frames - forecast_horizon

    if max_start < 0:
        skipped["too_few_frames"] += 1
        return samples, skipped

    image_stream_keys = image_stream_keys_for_shard(shard, frame_ids[0])
    json_reader = ShardJsonCache(shard)

    try:
        for start_index in range(max_start + 1):
            observation_ids = frame_ids[start_index : start_index + observation_frames]
            end_frame = observation_ids[-1]
            forecast_index = start_index + observation_frames + forecast_horizon - 1
            forecast_frame = frame_ids[forecast_index]
            object_input_frame = end_frame
            forecast_members = get_frame_member_names(forecast_frame)
            object_input_members = get_frame_member_names(object_input_frame)

            try:
                hands_json = json_reader.read(forecast_members["hands"])
                objects_json = json_reader.read(forecast_members["objects"])
                info_json = json_reader.read(forecast_members["info"])
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                skipped[f"read_error:{type(exc).__name__}"] += 1
                continue

            cameras_json: dict[str, Any] = {}
            if assign_target_proxy:
                try:
                    cameras_json = json_reader.read(forecast_members["cameras"])
                except (FileNotFoundError, json.JSONDecodeError) as exc:
                    skipped[f"proxy_camera_read_error:{type(exc).__name__}"] += 1

            future_hand_pose, available_hands, hand_missing, source_used = extract_future_hand_pose(
                hands_json=hands_json,
                hand_source=hand_source,
                min_visibility=min_visibility,
            )
            skipped.update(hand_missing)
            if not available_hands:
                skipped["skipped_no_visible_future_hand"] += 1
                continue

            object_candidates, object_missing = extract_object_candidates(
                objects_json=objects_json,
                min_visibility=min_visibility,
            )
            skipped.update(object_missing)
            if not object_candidates:
                skipped["skipped_no_visible_object"] += 1
                continue

            observation_object_candidates: list[dict[str, Any]] = []
            observation_object_candidate_scores: list[dict[str, Any]] = []
            try:
                input_hands_json = json_reader.read(object_input_members["hands"])
                input_objects_json = json_reader.read(object_input_members["objects"])
                input_cameras_json = json_reader.read(object_input_members["cameras"])
                observation_object_candidates, input_object_missing = extract_object_candidates(
                    input_objects_json,
                    min_visibility=min_visibility,
                )
                skipped.update(input_object_missing)
                if observation_object_candidates:
                    observation_object_proxy = select_target_object_proxy(
                        {
                            "hands_json": input_hands_json,
                            "cameras_json": input_cameras_json,
                            "target_object_candidates": observation_object_candidates,
                            "min_visibility": min_visibility,
                        }
                    )
                    candidate_scores = observation_object_proxy.get("candidate_scores", [])
                    if isinstance(candidate_scores, list):
                        observation_object_candidate_scores = [
                            score for score in candidate_scores if isinstance(score, dict)
                        ]
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                skipped[f"object_input_read_error:{type(exc).__name__}"] += 1

            sample = {
                "sample_id": f"{clip_id}_{observation_ids[0]}_{end_frame}_f{forecast_frame}",
                "shard": shard_rel,
                "clip_id": clip_id,
                "observation_frame_ids": observation_ids,
                "forecast_frame_id": forecast_frame,
                "target_object_proxy_frame": forecast_frame,
                "object_input_frame": object_input_frame,
                "input_uses_forecast_frame": object_input_frame == forecast_frame,
                "image_streams": observation_image_streams(observation_ids, image_stream_keys),
                "image_stream_keys": image_stream_keys,
                "hand_source": source_used or hand_source,
                "available_hands": available_hands,
                "future_hand_pose": future_hand_pose,
                "target_object_candidates": object_candidates,
                "observation_object_candidates": observation_object_candidates,
                "observation_object_candidate_scores": observation_object_candidate_scores,
                "target_object_label": None,
                "target_object_proxy_label": None,
                "target_object_selection_rule": "TODO: choose a documented rule; candidates only for now.",
                "action_label": None,
                "contact_label": None,
                "metadata": {
                    "sequence_id": info_json.get("sequence_id"),
                    "participant_id": info_json.get("participant_id"),
                    "device": info_json.get("device"),
                    "start_frame": observation_ids[0],
                    "end_frame": end_frame,
                    "forecast_frame": forecast_frame,
                    "ref_timestamp_ns": info_json.get("ref_timestamp_ns"),
                    "image_timestamps_ns": info_json.get("image_timestamps_ns", {}),
                },
            }

            if assign_target_proxy:
                target_object_proxy = select_target_object_proxy(
                    {
                        "hands_json": hands_json,
                        "cameras_json": cameras_json,
                        "target_object_candidates": object_candidates,
                        "min_visibility": min_visibility,
                    }
                )
                sample["target_object_proxy"] = target_object_proxy
                sample["target_object_selection_rule"] = TARGET_OBJECT_PROXY_V1_RULE
                sample["target_object_proxy_label"] = (
                    target_object_proxy.get("selected_object_name")
                    if target_object_proxy.get("assigned", False)
                    else None
                )
                if not target_object_proxy.get("assigned", False):
                    reason = target_object_proxy.get("reason", "unknown")
                    skipped[f"proxy_unassigned:{reason}"] += 1

            samples.append(sample)
    finally:
        json_reader.close()

    return samples, skipped


def build_index(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    shards = list_shards(root)
    if args.max_shards > 0:
        shards = shards[: args.max_shards]

    all_samples: list[dict[str, Any]] = []
    skipped = Counter()
    for shard in shards:
        shard_samples, shard_skipped = build_samples_for_shard(
            shard=shard,
            root=root,
            observation_frames=args.observation_frames,
            forecast_horizon=args.forecast_horizon,
            hand_source=args.hand_source,
            min_visibility=args.min_visibility,
            assign_target_proxy=args.assign_target_proxy,
        )
        all_samples.extend(shard_samples)
        skipped.update(shard_skipped)

    proxy_assignment_count = sum(
        1 for sample in all_samples if sample.get("target_object_proxy", {}).get("assigned", False)
    )
    return {
        "schema_version": "hot3d_clips_sample_index_v0",
        "metadata": {
            "dataset": "HOT3D-Clips",
            "root": str(root),
            "num_shards": len(shards),
            "shards": [str(shard.relative_to(root)) if shard.is_relative_to(root) else str(shard) for shard in shards],
            "observation_frames": args.observation_frames,
            "forecast_horizon": args.forecast_horizon,
            "hand_source_requested": args.hand_source,
            "min_visibility": args.min_visibility,
            "assign_target_proxy": args.assign_target_proxy,
            "target_object_proxy_rule": TARGET_OBJECT_PROXY_V1_RULE if args.assign_target_proxy else None,
            "target_object_proxy_assignment_count": proxy_assignment_count,
            "num_samples": len(all_samples),
            "skipped_counts": dict(skipped),
            "notes": [
                "No action labels are created.",
                "No contact labels are created.",
                "Target object is stored as visible candidates; optional proxy labels are derived labels only.",
                "Target-object proxy labels are computed at the forecast frame.",
                "Object-aware input candidates and scores are computed from the last observation frame only.",
                "Future hand pose is stored as MANO/UmeTrack representation, not converted 3D joints yet.",
            ],
            "todos": [
                "Define and validate a target-object selection rule before training.",
                "Convert MANO/UmeTrack hand parameters to the model's 3D joint tensor format.",
                "Define action/contact proxies or add external annotations before claiming pre-contact labels.",
            ],
        },
        "samples": all_samples,
    }


def main() -> None:
    args = parse_args()
    if args.observation_frames <= 0:
        raise ValueError("--observation-frames must be positive.")
    if args.forecast_horizon <= 0:
        raise ValueError("--forecast-horizon must be positive.")

    payload = build_index(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(
        json.dumps(
            {
                "output": str(args.output),
                "num_samples": payload["metadata"]["num_samples"],
                "num_shards": payload["metadata"]["num_shards"],
                "observation_frames": args.observation_frames,
                "forecast_horizon": args.forecast_horizon,
                "assign_target_proxy": args.assign_target_proxy,
                "target_object_proxy_assignment_count": payload["metadata"][
                    "target_object_proxy_assignment_count"
                ],
                "skipped_counts": payload["metadata"]["skipped_counts"],
                "note": "Sample index only. No training or real-result reporting was performed.",
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
