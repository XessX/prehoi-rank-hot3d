"""Select diverse HOT3D-Clips shards for later download.

This script reads local metadata, avoids already downloaded clips, writes a
selection JSON, and prints commands. It does not download unless
--confirm-download is explicitly passed.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clip_metadata import (
    downloaded_clip_ids,
    expected_shard_path,
    load_clip_definitions,
    load_clip_splits,
    object_metadata_distribution,
    participant_from_sequence,
    split_lookup,
)


OBJECT_KEYS = ("objects", "object_names", "object_ids", "object_uids", "object_name", "object_id", "object_uid")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Select diverse HOT3D-Clips shards for download.")
    parser.add_argument("--root", type=Path, default=Path("data/raw/hot3d_clips"))
    parser.add_argument("--num-clips", type=int, default=8)
    parser.add_argument("--output", type=Path, default=Path("data/processed/hot3d_diverse_clip_selection.json"))
    parser.add_argument("--preferred-split", default="train")
    parser.add_argument("--repo-id", default="bop-benchmark/hot3d")
    parser.add_argument("--python-executable", default="python")
    parser.add_argument("--max-total-gb", type=float, default=2.0)
    parser.add_argument(
        "--confirm-download",
        action="store_true",
        help="Execute generated downloader commands. Omit for dry-run command generation.",
    )
    parser.add_argument(
        "--allow-large-files",
        action="store_true",
        default=True,
        help="Pass --allow-large-files to generated downloader commands for tar shards.",
    )
    parser.add_argument(
        "--allow-downloaded-sequences",
        action="store_true",
        help="Allow selecting clips from sequences that already have a downloaded clip.",
    )
    return parser.parse_args()


def extract_object_metadata(definition: dict[str, Any]) -> dict[str, list[str]]:
    values: dict[str, list[str]] = {"object_names": [], "object_ids": [], "object_uids": []}
    for key in OBJECT_KEYS:
        raw = definition.get(key)
        if raw is None:
            continue
        if key in ("object_name", "object_names"):
            bucket = "object_names"
        elif key in ("object_uid", "object_uids"):
            bucket = "object_uids"
        else:
            bucket = "object_ids"

        if isinstance(raw, list):
            values[bucket].extend(str(item) for item in raw)
        elif isinstance(raw, dict):
            values[bucket].extend(str(item) for item in raw.keys())
        else:
            values[bucket].append(str(raw))

    return {key: sorted(set(items)) for key, items in values.items()}


def build_candidate_records(
    clip_definitions: dict[str, dict[str, Any]],
    clip_splits: dict[str, dict[str, list[int]]],
    preferred_split: str,
    downloaded: set[str],
    avoided_sequences: set[str],
) -> list[dict[str, Any]]:
    lookup = split_lookup(clip_splits)
    candidates: list[dict[str, Any]] = []
    for clip_id, split_info in lookup.items():
        if split_info["split"] != preferred_split:
            continue
        if clip_id in downloaded:
            continue
        definition = clip_definitions.get(clip_id)
        if definition is None:
            continue
        sequence_id = definition.get("sequence_id")
        if isinstance(sequence_id, str) and sequence_id in avoided_sequences:
            continue
        device = split_info["device"]
        object_metadata = extract_object_metadata(definition)
        candidates.append(
            {
                "clip_id": clip_id,
                "split": split_info["split"],
                "device": device,
                "participant_id": participant_from_sequence(sequence_id),
                "sequence_id": sequence_id,
                "expected_shard_path": expected_shard_path(clip_id, split_info["split"], device),
                **object_metadata,
            }
        )

    return sorted(candidates, key=lambda item: int(item["clip_id"]))


def candidate_gain(
    candidate: dict[str, Any],
    selected: list[dict[str, Any]],
    seen_participants: set[str],
    seen_devices: set[str],
    seen_sequences: set[str],
    seen_objects: set[str],
) -> tuple[int, list[str]]:
    reasons: list[str] = []
    score = 0

    participant = candidate.get("participant_id")
    if participant and participant not in seen_participants:
        score += 5
        reasons.append(f"adds participant {participant}")

    device = candidate.get("device")
    if device and device not in seen_devices:
        score += 3
        reasons.append(f"adds device {device}")
    elif device:
        device_counts = Counter(str(item.get("device")) for item in selected if item.get("device"))
        if device_counts:
            lowest_count = min(device_counts.values())
            current_count = device_counts.get(str(device), 0)
            if current_count <= lowest_count:
                score += 2
                reasons.append(f"helps balance device {device}")

    sequence_id = candidate.get("sequence_id")
    if sequence_id and sequence_id not in seen_sequences:
        score += 2
        reasons.append(f"adds sequence {sequence_id}")

    object_values = set(candidate.get("object_names", [])) | set(candidate.get("object_ids", []))
    new_objects = object_values - seen_objects
    if new_objects:
        score += 4 + len(new_objects)
        reasons.append(f"adds object metadata {sorted(new_objects)[:4]}")

    if not reasons:
        score += max(0, 1 - len(selected))
        reasons.append("fills requested count after higher-diversity candidates")

    return score, reasons


def select_candidates(candidates: list[dict[str, Any]], num_clips: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    remaining = list(candidates)
    seen_participants: set[str] = set()
    seen_devices: set[str] = set()
    seen_sequences: set[str] = set()
    seen_objects: set[str] = set()

    while remaining and len(selected) < num_clips:
        ranked: list[tuple[int, int, dict[str, Any], list[str]]] = []
        for candidate in remaining:
            score, reasons = candidate_gain(
                candidate,
                selected,
                seen_participants,
                seen_devices,
                seen_sequences,
                seen_objects,
            )
            ranked.append((score, -int(candidate["clip_id"]), candidate, reasons))

        ranked.sort(key=lambda item: (item[0], item[1]), reverse=True)
        _, _, chosen, reasons = ranked[0]
        chosen = dict(chosen)
        chosen["reason_selected"] = "; ".join(reasons)
        selected.append(chosen)
        remaining = [candidate for candidate in remaining if candidate["clip_id"] != chosen["clip_id"]]

        if chosen.get("participant_id"):
            seen_participants.add(str(chosen["participant_id"]))
        if chosen.get("device"):
            seen_devices.add(str(chosen["device"]))
        if chosen.get("sequence_id"):
            seen_sequences.add(str(chosen["sequence_id"]))
        seen_objects.update(chosen.get("object_names", []))
        seen_objects.update(chosen.get("object_ids", []))

    return selected


def make_download_command(args: argparse.Namespace, shard_path: str) -> list[str]:
    command = [
        args.python_executable,
        "src/datasets/download_hot3d_clips_sample.py",
        "--repo-id",
        args.repo_id,
        "--pattern",
        shard_path,
        "--max-files",
        "1",
        "--output-dir",
        str(args.root),
        "--max-total-gb",
        str(args.max_total_gb),
        "--confirm-download",
    ]
    if args.allow_large_files:
        command.append("--allow-large-files")
    return command


def command_to_string(command: list[str]) -> str:
    return " ".join(shlex.quote(part) if any(char in part for char in " *\\") else part for part in command)


def write_selection(args: argparse.Namespace, selected: list[dict[str, Any]], commands: list[str], metadata: dict[str, Any]) -> None:
    payload = {
        "metadata": metadata,
        "selected_clips": selected,
        "download_commands": commands,
        "notes": [
            "No training was run.",
            "No real labels are inferred by this script.",
            "Commands are generated for review and are not executed unless --confirm-download is passed.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def maybe_download(args: argparse.Namespace, command_lists: list[list[str]]) -> None:
    if not args.confirm_download:
        return
    for command in command_lists:
        subprocess.run(command, cwd=PROJECT_ROOT, check=True)


def main() -> None:
    args = parse_args()
    if args.num_clips <= 0:
        raise ValueError("--num-clips must be positive.")

    clip_definitions = load_clip_definitions(args.root)
    clip_splits = load_clip_splits(args.root)
    downloaded = downloaded_clip_ids(args.root)
    downloaded_sequences = {
        str(clip_definitions[clip_id]["sequence_id"])
        for clip_id in downloaded
        if clip_id in clip_definitions and clip_definitions[clip_id].get("sequence_id")
    }
    avoided_sequences = set() if args.allow_downloaded_sequences else downloaded_sequences
    candidates = build_candidate_records(
        clip_definitions=clip_definitions,
        clip_splits=clip_splits,
        preferred_split=args.preferred_split,
        downloaded=downloaded,
        avoided_sequences=avoided_sequences,
    )
    selected = select_candidates(candidates, num_clips=args.num_clips)
    command_lists = [make_download_command(args, item["expected_shard_path"]) for item in selected]
    commands = [command_to_string(command) for command in command_lists]
    object_distribution = object_metadata_distribution(clip_definitions)

    metadata = {
        "root": str(args.root),
        "preferred_split": args.preferred_split,
        "requested_num_clips": args.num_clips,
        "num_candidates_after_download_filter": len(candidates),
        "num_selected": len(selected),
        "already_downloaded_clip_ids": sorted(downloaded, key=lambda value: int(value)),
        "avoided_downloaded_sequence_ids": sorted(avoided_sequences),
        "object_metadata_available": object_distribution["available"],
        "selection_basis": "object metadata if available; otherwise participant, device, and sequence diversity",
    }
    write_selection(args, selected, commands, metadata)

    summary = {
        "output": str(args.output),
        "metadata": metadata,
        "selected_clips": selected,
        "download_commands": commands,
        "download_executed": args.confirm_download,
    }
    print(json.dumps(summary, indent=2))
    maybe_download(args, command_lists)


if __name__ == "__main__":
    main()
