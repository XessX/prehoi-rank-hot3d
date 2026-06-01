"""HOT3D-Clips/WebDataset inspection adapter.

This module intentionally stops at metadata inspection. It does not decode
training tensors or invent action/contact labels.
"""

from __future__ import annotations

import json
import re
import tarfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CLIPS_SPLIT_DIRS = ("train_aria", "train_quest3", "test_aria", "test_quest3")
CLIPS_ROOT_FILES = ("clip_definitions.json", "clip_splits.json")
OBJECT_MODEL_DIRS = ("object_models", "object_models_eval")
FRAME_KEY_PATTERN = re.compile(r"^(?P<frame_id>\d{1,8})\.(?P<field>.+)$")


@dataclass(frozen=True)
class HOT3DClipsConfig:
    """Small config object for HOT3D-Clips inspection."""

    clips_root: Path
    max_shards_for_inspection: int = 2
    max_samples_for_inspection: int = 5


class HOT3DClipsAdapter:
    """Inspect HOT3D-Clips shards and expose structured metadata."""

    def __init__(
        self,
        clips_root: str | Path,
        max_shards_for_inspection: int = 2,
        max_samples_for_inspection: int = 5,
    ) -> None:
        self.config = HOT3DClipsConfig(
            clips_root=Path(clips_root),
            max_shards_for_inspection=max_shards_for_inspection,
            max_samples_for_inspection=max_samples_for_inspection,
        )

    @property
    def clips_root(self) -> Path:
        return self.config.clips_root

    def inspect(self, use_webdataset: bool = False) -> dict[str, Any]:
        """Return a dry-run summary of a HOT3D-Clips root."""
        if not self.clips_root.exists():
            return {
                "clips_root": str(self.clips_root),
                "exists": False,
                "message": "HOT3D-Clips root does not exist. Keep synthetic mode enabled.",
            }

        shards = self.discover_shards()
        shard_summaries = [
            self.inspect_tar_shard(path)
            for path in shards[: self.config.max_shards_for_inspection]
        ]

        summary = {
            "clips_root": str(self.clips_root),
            "exists": True,
            "data_format": "webdataset",
            "root_files": self.inspect_root_files(),
            "object_model_dirs": {
                name: (self.clips_root / name).exists() for name in OBJECT_MODEL_DIRS
            },
            "split_shard_counts": self.count_split_shards(),
            "num_shards": len(shards),
            "sample_shards": shard_summaries,
            "availability": self.summarize_availability(shard_summaries),
            "webdataset": self.inspect_with_webdataset(shards) if use_webdataset else {
                "requested": False,
                "message": "Pass use_webdataset=True or --use-webdataset for optional WebDataset iteration.",
            },
            "note": (
                "Inspection only. No action labels, contact labels, or real training "
                "samples are created here."
            ),
            "remaining_todos": [
                "Decode clip images from <FRAME-ID>.image_<STREAM-ID>.jpg.",
                "Decode per-frame cameras.json, hands.json, objects.json, and info.json.",
                "Convert MANO/UmeTrack hand annotations into 3D hand-joint tensors.",
                "Define target-object, action, and contact/pre-contact labels from real annotations or documented proxies.",
                "Create a supervised sample index only after labels and splits are validated.",
            ],
        }
        return summary

    def discover_shards(self) -> list[Path]:
        """Find HOT3D-Clips tar shards, preferring official split folders."""
        shards: list[Path] = []
        for split_dir in CLIPS_SPLIT_DIRS:
            split_path = self.clips_root / split_dir
            if split_path.exists():
                shards.extend(sorted(split_path.glob("*.tar")))

        if not shards:
            shards = sorted(self.clips_root.rglob("*.tar"))
        return shards

    def inspect_root_files(self) -> dict[str, Any]:
        """Inspect root-level clip definition and split files."""
        result: dict[str, Any] = {}
        for name in CLIPS_ROOT_FILES:
            path = self.clips_root / name
            entry: dict[str, Any] = {"exists": path.exists()}
            if path.exists():
                payload = self._load_json(path)
                entry["top_level_type"] = type(payload).__name__
                entry["num_entries"] = len(payload) if hasattr(payload, "__len__") else None
                if isinstance(payload, dict):
                    entry["sample_keys"] = list(payload.keys())[:10]
            result[name] = entry
        return result

    def count_split_shards(self) -> dict[str, int]:
        """Count tar shards per official split folder."""
        counts: dict[str, int] = {}
        for split_dir in CLIPS_SPLIT_DIRS:
            split_path = self.clips_root / split_dir
            counts[split_dir] = len(list(split_path.glob("*.tar"))) if split_path.exists() else 0
        return counts

    def inspect_tar_shard(self, tar_path: Path) -> dict[str, Any]:
        """Inspect a clip tar without decoding full image or annotation payloads."""
        try:
            with tarfile.open(tar_path, mode="r") as tar:
                member_names = [member.name for member in tar.getmembers() if member.isfile()]
        except tarfile.TarError as exc:
            return {
                "shard": str(tar_path),
                "readable": False,
                "error": str(exc),
            }

        frame_to_fields: dict[str, set[str]] = defaultdict(set)
        field_counts: Counter[str] = Counter()
        image_stream_counts: Counter[str] = Counter()
        non_frame_members: list[str] = []

        for name in member_names:
            match = FRAME_KEY_PATTERN.match(Path(name).name)
            if not match:
                non_frame_members.append(name)
                continue

            frame_id = match.group("frame_id")
            field = match.group("field")
            frame_to_fields[frame_id].add(field)
            field_counts[field] += 1
            if field.startswith("image_") and field.endswith(".jpg"):
                stream_id = field.removeprefix("image_").removesuffix(".jpg")
                image_stream_counts[stream_id] += 1

        sample_frame_ids = sorted(frame_to_fields.keys())[: self.config.max_samples_for_inspection]
        sample_keys = {
            frame_id: sorted(frame_to_fields[frame_id])
            for frame_id in sample_frame_ids
        }

        return {
            "shard": str(tar_path),
            "readable": True,
            "num_members": len(member_names),
            "num_frame_ids": len(frame_to_fields),
            "field_counts": dict(sorted(field_counts.items())),
            "image_stream_counts": dict(sorted(image_stream_counts.items())),
            "has_hand_shapes": "__hand_shapes.json__" in {Path(name).name for name in member_names},
            "non_frame_members": non_frame_members[:20],
            "sample_keys": sample_keys,
            "availability": {
                "frames": any(field.startswith("image_") for field in field_counts),
                "camera_annotations": "cameras.json" in field_counts,
                "hand_annotations": "hands.json" in field_counts,
                "object_annotations": "objects.json" in field_counts,
                "hand_crops": "hand_crops.json" in field_counts,
                "metadata": "info.json" in field_counts,
                "gaze": any("gaze" in field for field in field_counts),
            },
        }

    def summarize_availability(self, shard_summaries: list[dict[str, Any]]) -> dict[str, bool]:
        """Aggregate whether key modalities appear in inspected shards."""
        keys = (
            "frames",
            "camera_annotations",
            "hand_annotations",
            "object_annotations",
            "hand_crops",
            "metadata",
            "gaze",
        )
        availability = {key: False for key in keys}
        for summary in shard_summaries:
            shard_availability = summary.get("availability", {})
            for key in keys:
                availability[key] = availability[key] or bool(shard_availability.get(key))
        return availability

    def inspect_with_webdataset(self, shards: list[Path]) -> dict[str, Any]:
        """Optionally iterate shards with webdataset if the package is installed."""
        try:
            import webdataset as wds
        except ImportError:
            return {
                "requested": True,
                "installed": False,
                "message": "webdataset is not installed. Tar inspection still completed safely.",
            }

        sample_summaries: list[dict[str, Any]] = []
        for shard in shards[: self.config.max_shards_for_inspection]:
            try:
                dataset = wds.WebDataset(str(shard)).decode(False)
                for sample_index, sample in enumerate(dataset):
                    if sample_index >= self.config.max_samples_for_inspection:
                        break
                    sample_summaries.append(
                        {
                            "shard": str(shard),
                            "sample_index": sample_index,
                            "keys": sorted(str(key) for key in sample.keys()),
                        }
                    )
            except Exception as exc:  # pragma: no cover - depends on external package/data.
                sample_summaries.append({"shard": str(shard), "error": str(exc)})

        return {
            "requested": True,
            "installed": True,
            "samples": sample_summaries,
            "message": (
                "WebDataset grouping is shown only for inspection; HOT3D-Clips "
                "frame-level grouping still needs a validated adapter."
            ),
        }

    def _load_json(self, path: Path) -> Any:
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            return {"_error": f"Invalid JSON: {exc}"}

