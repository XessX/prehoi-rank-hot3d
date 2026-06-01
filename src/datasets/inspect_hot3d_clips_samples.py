"""Inspect a generated HOT3D-Clips sample index without training."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


REQUIRED_SAMPLE_FIELDS = (
    "sample_id",
    "shard",
    "clip_id",
    "observation_frame_ids",
    "forecast_frame_id",
    "image_streams",
    "hand_source",
    "available_hands",
    "future_hand_pose",
    "target_object_candidates",
    "metadata",
)

REQUIRED_METADATA_FIELDS = (
    "sequence_id",
    "participant_id",
    "device",
    "start_frame",
    "end_frame",
    "forecast_frame",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a HOT3D-Clips sample index JSON.")
    parser.add_argument("index_path", type=Path, help="Path to hot3d_clips_sample_index.json.")
    parser.add_argument("--preview-count", type=int, default=2, help="Number of sample previews to print.")
    return parser.parse_args()


def load_index(index_path: Path) -> dict[str, Any]:
    if not index_path.exists():
        raise FileNotFoundError(f"Sample index not found: {index_path}")
    with index_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected top-level JSON object in {index_path}")
    return payload


def hands_key(sample: dict[str, Any]) -> str:
    hands = sample.get("available_hands", [])
    if not isinstance(hands, list) or not hands:
        return "none"
    return "+".join(sorted(str(hand) for hand in hands))


def object_candidate_frequency(samples: list[dict[str, Any]]) -> Counter[str]:
    frequency: Counter[str] = Counter()
    for sample in samples:
        candidates = sample.get("target_object_candidates", [])
        if not isinstance(candidates, list):
            frequency["invalid_candidates"] += 1
            continue
        for candidate in candidates:
            if not isinstance(candidate, dict):
                frequency["invalid_candidate"] += 1
                continue
            label = candidate.get("object_name") or candidate.get("object_uid") or candidate.get("object_bop_id")
            frequency[str(label) if label is not None else "unknown_object"] += 1
    return frequency


def count_missing_fields(samples: list[dict[str, Any]]) -> Counter[str]:
    missing: Counter[str] = Counter()
    for sample in samples:
        for field in REQUIRED_SAMPLE_FIELDS:
            if field not in sample:
                missing[f"sample.{field}"] += 1

        observation_ids = sample.get("observation_frame_ids")
        if not isinstance(observation_ids, list) or not observation_ids:
            missing["sample.observation_frame_ids.empty"] += 1

        image_streams = sample.get("image_streams")
        if not isinstance(image_streams, dict) or not image_streams:
            missing["sample.image_streams.empty"] += 1
        else:
            for stream_name, members in image_streams.items():
                if not isinstance(members, list) or not members:
                    missing[f"sample.image_streams.{stream_name}.empty"] += 1

        if not sample.get("available_hands"):
            missing["sample.available_hands.empty"] += 1
        if not sample.get("future_hand_pose"):
            missing["sample.future_hand_pose.empty"] += 1
        if not sample.get("target_object_candidates"):
            missing["sample.target_object_candidates.empty"] += 1

        metadata = sample.get("metadata", {})
        if not isinstance(metadata, dict):
            missing["sample.metadata.invalid"] += 1
            continue
        for field in REQUIRED_METADATA_FIELDS:
            if metadata.get(field) in (None, ""):
                missing[f"sample.metadata.{field}"] += 1
    return missing


def preview_sample(sample: dict[str, Any]) -> dict[str, Any]:
    observation_ids = sample.get("observation_frame_ids", [])
    image_streams = sample.get("image_streams", {})
    candidates = sample.get("target_object_candidates", [])
    return {
        "sample_id": sample.get("sample_id"),
        "shard": sample.get("shard"),
        "clip_id": sample.get("clip_id"),
        "observation_frame_ids": {
            "count": len(observation_ids) if isinstance(observation_ids, list) else 0,
            "first": observation_ids[:3] if isinstance(observation_ids, list) else [],
            "last": observation_ids[-3:] if isinstance(observation_ids, list) else [],
        },
        "forecast_frame_id": sample.get("forecast_frame_id"),
        "image_stream_counts": {
            stream: len(members) if isinstance(members, list) else 0
            for stream, members in image_streams.items()
        }
        if isinstance(image_streams, dict)
        else {},
        "hand_source": sample.get("hand_source"),
        "available_hands": sample.get("available_hands"),
        "future_hand_pose_keys": sorted(sample.get("future_hand_pose", {}).keys())
        if isinstance(sample.get("future_hand_pose"), dict)
        else [],
        "target_object_candidates": [
            {
                "object_uid": candidate.get("object_uid"),
                "object_bop_id": candidate.get("object_bop_id"),
                "object_name": candidate.get("object_name"),
                "visibility": candidate.get("visibility"),
            }
            for candidate in candidates[:5]
            if isinstance(candidate, dict)
        ]
        if isinstance(candidates, list)
        else [],
        "num_target_object_candidates": len(candidates) if isinstance(candidates, list) else 0,
        "metadata": sample.get("metadata"),
    }


def build_summary(payload: dict[str, Any], preview_count: int) -> dict[str, Any]:
    metadata = payload.get("metadata", {})
    samples = payload.get("samples", [])
    if not isinstance(samples, list):
        raise ValueError("Expected payload['samples'] to be a list.")

    shards = {sample.get("shard") for sample in samples if sample.get("shard")}
    clips = {sample.get("clip_id") for sample in samples if sample.get("clip_id")}
    observation_lengths = Counter(
        len(sample.get("observation_frame_ids", []))
        for sample in samples
        if isinstance(sample.get("observation_frame_ids"), list)
    )
    forecast_horizons = metadata.get("forecast_horizon")
    hands_distribution = Counter(hands_key(sample) for sample in samples)
    missing = count_missing_fields(samples)
    candidate_frequency = object_candidate_frequency(samples)

    return {
        "index_metadata": {
            "schema_version": payload.get("schema_version"),
            "dataset": metadata.get("dataset"),
            "root": metadata.get("root"),
            "observation_frames": metadata.get("observation_frames"),
            "forecast_horizon": forecast_horizons,
            "hand_source_requested": metadata.get("hand_source_requested"),
            "min_visibility": metadata.get("min_visibility"),
        },
        "num_samples": len(samples),
        "num_shards": len(shards),
        "num_clips": len(clips),
        "observation_length_distribution": dict(observation_lengths),
        "available_hands_distribution": dict(hands_distribution),
        "object_candidate_frequency_top20": dict(candidate_frequency.most_common(20)),
        "missing_field_counts": dict(missing),
        "builder_skipped_counts": metadata.get("skipped_counts", {}),
        "notes": metadata.get("notes", []),
        "todos": metadata.get("todos", []),
        "first_sample_previews": [preview_sample(sample) for sample in samples[:preview_count]],
    }


def main() -> None:
    args = parse_args()
    payload = load_index(args.index_path)
    summary = build_summary(payload, preview_count=max(0, args.preview_count))
    print(json.dumps(summary, indent=2))
    print("No training was run. This is a sample-index inspection only.")


if __name__ == "__main__":
    main()
