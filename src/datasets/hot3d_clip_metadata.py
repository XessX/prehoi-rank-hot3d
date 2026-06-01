"""Utilities for reading HOT3D-Clips root metadata files."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required metadata file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_clip_definitions(root: str | Path) -> dict[str, dict[str, Any]]:
    data = load_json(Path(root) / "clip_definitions.json")
    if not isinstance(data, dict):
        raise ValueError("Expected clip_definitions.json to contain a JSON object keyed by clip ID.")
    return {str(clip_id): clip for clip_id, clip in data.items() if isinstance(clip, dict)}


def load_clip_splits(root: str | Path) -> dict[str, dict[str, list[int]]]:
    data = load_json(Path(root) / "clip_splits.json")
    if not isinstance(data, dict):
        raise ValueError("Expected clip_splits.json to contain a JSON object keyed by split.")
    normalized: dict[str, dict[str, list[int]]] = {}
    for split_name, split_payload in data.items():
        if not isinstance(split_payload, dict):
            continue
        normalized[str(split_name)] = {}
        for device_name, clip_ids in split_payload.items():
            if not isinstance(clip_ids, list):
                continue
            normalized[str(split_name)][str(device_name)] = [int(clip_id) for clip_id in clip_ids]
    return normalized


def participant_from_sequence(sequence_id: Any) -> str | None:
    if not isinstance(sequence_id, str) or not sequence_id:
        return None
    return sequence_id.split("_", maxsplit=1)[0]


def device_to_dir_name(device: str) -> str:
    return device.strip().lower().replace(" ", "")


def split_device_to_shard_dir(split: str, device: str) -> str:
    split_prefix = "train" if split == "train" else "test"
    return f"{split_prefix}_{device_to_dir_name(device)}"


def expected_shard_path(clip_id: str | int, split: str, device: str) -> str:
    clip_int = int(clip_id)
    shard_dir = split_device_to_shard_dir(split, device)
    return f"{shard_dir}/clip-{clip_int:06d}.tar"


def downloaded_clip_ids(root: str | Path) -> set[str]:
    root = Path(root)
    downloaded: set[str] = set()
    if not root.exists():
        return downloaded
    for shard in root.rglob("clip-*.tar"):
        match = re.search(r"clip-(\d+)\.tar$", shard.name)
        if match:
            downloaded.add(str(int(match.group(1))))
    return downloaded


def split_lookup(clip_splits: dict[str, dict[str, list[int]]]) -> dict[str, dict[str, str]]:
    lookup: dict[str, dict[str, str]] = {}
    for split_name, by_device in clip_splits.items():
        for device_name, clip_ids in by_device.items():
            for clip_id in clip_ids:
                lookup[str(int(clip_id))] = {"split": split_name, "device": device_name}
    return lookup


def top_level_definition_keys(clip_definitions: dict[str, dict[str, Any]]) -> Counter[str]:
    keys: Counter[str] = Counter()
    for definition in clip_definitions.values():
        keys.update(definition.keys())
    return keys


def split_counts(clip_splits: dict[str, dict[str, list[int]]]) -> dict[str, Any]:
    counts: dict[str, Any] = {}
    for split_name, by_device in clip_splits.items():
        device_counts = {device: len(clip_ids) for device, clip_ids in by_device.items()}
        counts[split_name] = {"total": sum(device_counts.values()), "by_device": device_counts}
    return counts


def grouped_clip_ids(clip_splits: dict[str, dict[str, list[int]]], max_per_group: int) -> dict[str, Any]:
    grouped: dict[str, Any] = {}
    for split_name, by_device in clip_splits.items():
        grouped[split_name] = {}
        for device_name, clip_ids in by_device.items():
            ids = [int(clip_id) for clip_id in clip_ids]
            grouped[split_name][device_name] = {
                "count": len(ids),
                "first_ids": ids[:max_per_group],
            }
    return grouped


def sequence_distribution(clip_definitions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    device_counter: Counter[str] = Counter()
    participant_counter: Counter[str] = Counter()
    sequence_counter: Counter[str] = Counter()
    timestamp_lengths: Counter[int] = Counter()

    for definition in clip_definitions.values():
        device = definition.get("device")
        if device:
            device_counter[str(device)] += 1
        participant = participant_from_sequence(definition.get("sequence_id"))
        if participant:
            participant_counter[participant] += 1
        sequence_id = definition.get("sequence_id")
        if sequence_id:
            sequence_counter[str(sequence_id)] += 1
        timestamps = definition.get("per_frame_timestamps_ns")
        if isinstance(timestamps, list):
            timestamp_lengths[len(timestamps)] += 1

    return {
        "device_distribution": dict(device_counter.most_common()),
        "participant_distribution_top20": dict(participant_counter.most_common(20)),
        "num_unique_participants": len(participant_counter),
        "num_unique_sequences": len(sequence_counter),
        "per_frame_timestamp_length_distribution": dict(timestamp_lengths.most_common()),
    }


def object_metadata_distribution(clip_definitions: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidate_keys = (
        "objects",
        "object_names",
        "object_ids",
        "object_uids",
        "object_name",
        "object_id",
        "object_uid",
    )
    found_keys = sorted({key for item in clip_definitions.values() for key in item if key in candidate_keys})
    if not found_keys:
        return {
            "available": False,
            "found_object_like_keys": [],
            "note": "No object/object_uid/object_name metadata was found in clip_definitions.json.",
        }

    value_counter: Counter[str] = Counter()
    for definition in clip_definitions.values():
        for key in found_keys:
            value = definition.get(key)
            if isinstance(value, list):
                value_counter.update(str(item) for item in value)
            elif isinstance(value, dict):
                value_counter.update(str(item) for item in value.keys())
            elif value is not None:
                value_counter[str(value)] += 1

    return {
        "available": True,
        "found_object_like_keys": found_keys,
        "distribution_top50": dict(value_counter.most_common(50)),
    }


def definitions_by_participant(
    clip_definitions: dict[str, dict[str, Any]],
    clip_splits: dict[str, dict[str, list[int]]],
    preferred_split: str,
) -> dict[str, list[dict[str, Any]]]:
    lookup = split_lookup(clip_splits)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for clip_id, definition in clip_definitions.items():
        split_info = lookup.get(str(int(clip_id)))
        if split_info is None or split_info["split"] != preferred_split:
            continue
        participant = participant_from_sequence(definition.get("sequence_id")) or "unknown"
        grouped[participant].append(
            {
                "clip_id": str(int(clip_id)),
                "definition": definition,
                "split": split_info["split"],
                "device": split_info["device"],
            }
        )
    for records in grouped.values():
        records.sort(key=lambda item: int(item["clip_id"]))
    return dict(grouped)
