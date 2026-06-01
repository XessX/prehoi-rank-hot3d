"""Inspect a local HOT3D root without training or requiring the full dataset.

This script checks for the official full HOT3D VRS layout and the HOT3D-Clips
tar/WebDataset layout. It does not load images, VRS streams, MANO models, or
training tensors.
"""

from __future__ import annotations

import argparse
import json
import tarfile
from collections import Counter
from pathlib import Path
from typing import Any


VRS_COMMON_FILES = (
    "metadata.json",
    "recording.vrs",
    "dynamic_objects.csv",
    "headset_trajectory.csv",
    "mano_hand_pose_trajectory.jsonl",
)
VRS_OPTIONAL_FILES = (
    "umetrack_hand_pose_trajectory.jsonl",
    "umetrack_hand_user_profile.json",
    "box2d_objects.csv",
    "box2d_hands.csv",
)
VRS_QUEST_FILES = ("camera_models.json",)
VRS_ARIA_DIRS = ("mps",)
MASK_FILES = (
    "mask_object_pose_available.csv",
    "mask_hand_pose_available.csv",
    "mask_headset_pose_available.csv",
    "mask_object_visible.csv",
    "mask_hand_visible.csv",
    "mask_good_exposure.csv",
    "mask_qa_pass.csv",
)
CLIPS_SPLIT_DIRS = ("train_aria", "train_quest3", "test_aria", "test_quest3")
CLIPS_ROOT_FILES = ("clip_definitions.json", "clip_splits.json")
CLIP_REQUIRED_SUFFIXES = (
    ".info.json",
    ".cameras.json",
    ".hands.json",
    ".objects.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HOT3D dataset files safely.")
    parser.add_argument(
        "dataset_root",
        type=Path,
        help="Path to a full HOT3D VRS root or a HOT3D-Clips root.",
    )
    parser.add_argument(
        "--max-tars",
        type=int,
        default=2,
        help="Maximum HOT3D-Clips tar archives to inspect lightly.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError as exc:
        return {"_error": f"Invalid JSON: {exc}"}


def discover_vrs_sequences(root: Path) -> list[Path]:
    sequence_dirs: list[Path] = []
    for metadata_path in root.rglob("metadata.json"):
        sequence_dir = metadata_path.parent
        if (sequence_dir / "recording.vrs").exists() or (
            sequence_dir / "dynamic_objects.csv"
        ).exists():
            sequence_dirs.append(sequence_dir)
    return sorted(set(sequence_dirs))


def inspect_vrs_sequence(sequence_dir: Path) -> dict[str, Any]:
    metadata = load_json(sequence_dir / "metadata.json")
    headset = metadata.get("headset", "unknown")
    required = list(VRS_COMMON_FILES)
    if headset == "Quest3":
        required.extend(VRS_QUEST_FILES)

    masks_dir = sequence_dir / "masks"
    mps_dir = sequence_dir / "mps"
    return {
        "sequence_id": sequence_dir.name,
        "headset": headset,
        "participant_id": metadata.get("participant_id"),
        "recording_name": metadata.get("recording_name"),
        "gt_available_status": metadata.get("gt_available_status", {}),
        "missing_required": [
            filename for filename in required if not (sequence_dir / filename).exists()
        ],
        "optional_present": [
            filename for filename in VRS_OPTIONAL_FILES if (sequence_dir / filename).exists()
        ],
        "mask_files_present": [
            filename for filename in MASK_FILES if (masks_dir / filename).exists()
        ],
        "has_mps": mps_dir.exists(),
        "has_eye_gaze": (mps_dir / "eye_gaze").exists(),
    }


def inspect_vrs_root(root: Path) -> dict[str, Any]:
    sequence_dirs = discover_vrs_sequences(root)
    summaries = [inspect_vrs_sequence(path) for path in sequence_dirs]
    headset_counts = Counter(item["headset"] for item in summaries)
    sequences_missing_required = [
        item["sequence_id"] for item in summaries if item["missing_required"]
    ]
    return {
        "detected": bool(sequence_dirs),
        "num_sequences": len(sequence_dirs),
        "headset_counts": dict(headset_counts),
        "sequences_missing_required": sequences_missing_required,
        "sequences": summaries,
    }


def tar_member_summary(tar_path: Path) -> dict[str, Any]:
    try:
        with tarfile.open(tar_path, mode="r") as tar:
            names = tar.getnames()
    except tarfile.TarError as exc:
        return {"tar": str(tar_path), "error": str(exc)}

    suffix_counts = Counter()
    image_stream_counts = Counter()
    for name in names:
        for suffix in CLIP_REQUIRED_SUFFIXES:
            if name.endswith(suffix):
                suffix_counts[suffix] += 1
        if ".image_" in name and name.endswith(".jpg"):
            stream_id = name.split(".image_", maxsplit=1)[1].rsplit(".jpg", maxsplit=1)[0]
            image_stream_counts[stream_id] += 1

    return {
        "tar": str(tar_path),
        "num_members": len(names),
        "frame_info_count": suffix_counts[".info.json"],
        "json_suffix_counts": dict(suffix_counts),
        "image_stream_counts": dict(image_stream_counts),
        "has_hand_shapes": "__hand_shapes.json__" in names,
    }


def inspect_clips_root(root: Path, max_tars: int) -> dict[str, Any]:
    split_counts: dict[str, int] = {}
    tar_paths: list[Path] = []
    for split_dir in CLIPS_SPLIT_DIRS:
        path = root / split_dir
        split_tars = sorted(path.glob("*.tar")) if path.exists() else []
        split_counts[split_dir] = len(split_tars)
        tar_paths.extend(split_tars[:max(0, max_tars - len(tar_paths))])

    return {
        "detected": any(count > 0 for count in split_counts.values())
        or any((root / name).exists() for name in CLIPS_ROOT_FILES),
        "root_files": {name: (root / name).exists() for name in CLIPS_ROOT_FILES},
        "split_tar_counts": split_counts,
        "sample_tars": [tar_member_summary(path) for path in tar_paths[:max_tars]],
    }


def main() -> None:
    args = parse_args()
    root = args.dataset_root.resolve()
    if not root.exists():
        print(
            json.dumps(
                {
                    "dataset_root": str(root),
                    "exists": False,
                    "message": "Path does not exist. Keep synthetic mode enabled until HOT3D is downloaded.",
                },
                indent=2,
            )
        )
        return

    summary = {
        "dataset_root": str(root),
        "exists": True,
        "vrs": inspect_vrs_root(root),
        "hot3d_clips": inspect_clips_root(root, args.max_tars),
        "note": (
            "Inspection only. This script does not train, does not create labels, "
            "and does not prove real-result readiness."
        ),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

