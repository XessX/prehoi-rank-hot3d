"""HOT3D dataset integration point.

The MVP intentionally uses synthetic tensors by default. Real HOT3D parsing is
scaffolded here, but real results must not be reported until the official data
layout, labels, splits, and preprocessing are verified.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

import torch
import torch.nn.functional as F
from torch.utils.data import Dataset


DEFAULT_FRAME_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp")
OFFICIAL_VRS_COMMON_FILES = (
    "metadata.json",
    "recording.vrs",
    "dynamic_objects.csv",
    "headset_trajectory.csv",
    "mano_hand_pose_trajectory.jsonl",
)
OFFICIAL_VRS_OPTIONAL_FILES = (
    "umetrack_hand_pose_trajectory.jsonl",
    "umetrack_hand_user_profile.json",
    "box2d_objects.csv",
    "box2d_hands.csv",
)
OFFICIAL_VRS_ARIA_HINTS = ("mps",)
OFFICIAL_VRS_QUEST_FILES = ("camera_models.json",)
HOT3D_CLIPS_SPLIT_DIRS = ("train_aria", "train_quest3", "test_aria", "test_quest3")
HOT3D_CLIPS_REQUIRED_ROOT_FILES = ("clip_definitions.json", "clip_splits.json")
DEFAULT_ANNOTATION_CANDIDATES = (
    "annotations.json",
    "annotation.json",
    "sequence.json",
    "metadata.json",
    "events.json",
    "frames.json",
)
POSE_KEYS = ("hand_pose_3d", "hand_joints_3d", "joints_3d", "mano_joints_3d")
OBJECT_ID_KEYS = ("object_id", "target_object_id", "object_class", "object")
ACTION_KEYS = ("action_label", "interaction_label", "action", "interaction")
OBJECT_POSE_KEYS = ("object_pose", "object_pose_4x4", "object_T_world", "world_T_object")
CONTACT_REGION_KEYS = ("contact_region", "affordance_region", "contact_label")


class HOT3DPreContactDataset(Dataset):
    """PyTorch Dataset for HOT3D-style pre-contact forecasting samples.

    Synthetic mode is for pipeline testing only. It produces deterministic
    dummy tensors with the same keys the real parser should return.

    Real mode is aligned with two official HOT3D access patterns:
    full VRS sequences loaded through the official Hot3dDataProvider, and
    HOT3D-Clips WebDataset/tar clips. The current loader can inspect these
    layouts and build safe metadata, but it will not create training samples
    until action/contact event definitions and 3D hand-joint conversion are
    implemented from official providers.
    """

    def __init__(self, config: dict[str, Any], split: str = "train") -> None:
        self.config = config
        self.split = split
        self.use_synthetic = bool(config.get("synthetic_mode", config.get("use_synthetic", True)))

        self.root_dir = self._resolve_path(
            config.get("dataset_root", config.get("root_dir", "data/raw/hot3d"))
        )
        self.annotation_dir = self._resolve_path(
            config.get("annotation_dir", self.root_dir / "annotations")
        )
        self.index_file = self._resolve_path(
            config.get(
                "index_path",
                config.get("index_file", "data/processed/hot3d_sample_index.json"),
            )
        )
        self.rebuild_index = bool(config.get("rebuild_index", False))
        self.use_official_toolkit = bool(config.get("use_official_toolkit", False))
        self.data_format = str(config.get("data_format", "unknown")).lower()

        self.seq_len = int(config.get("observation_frames", config.get("seq_len", 16)))
        self.feature_dim = int(config.get("feature_dim", 128))
        self.image_size = int(config.get("image_size", 32))
        self.future_steps = int(config.get("forecast_horizon", config.get("future_steps", 5)))
        self.num_hand_joints = int(config.get("num_hand_joints", 21))
        self.num_objects = int(config.get("num_objects", 33))
        self.num_actions = int(config.get("num_actions", 8))
        self.synthetic_num_samples = int(config.get("synthetic_num_samples", 64))
        self.synthetic_seed = int(config.get("synthetic_seed", 123))

        self.frame_extensions = tuple(
            str(ext).lower() for ext in config.get("frame_extensions", DEFAULT_FRAME_EXTENSIONS)
        )
        self.annotation_candidates = tuple(
            str(name) for name in config.get("annotation_candidates", DEFAULT_ANNOTATION_CANDIDATES)
        )
        self.action_taxonomy = list(config.get("action_taxonomy", []))
        self.load_frames = bool(config.get("load_frames", False))
        self.allow_placeholder_features = bool(config.get("allow_placeholder_features", False))

        self.require_object_id = bool(config.get("require_object_id", True))
        self.require_action_label = bool(config.get("require_action_label", True))
        self.require_hand_pose = bool(config.get("require_hand_pose", True))
        self.require_future_hand_pose = bool(config.get("require_future_hand_pose", True))

        self.index_metadata: dict[str, Any] = {}

        if self.use_synthetic:
            self.samples = list(range(self.synthetic_num_samples))
            self.index_metadata = {
                "mode": "synthetic",
                "num_samples": self.synthetic_num_samples,
                "note": "Synthetic tensors only; not real HOT3D data.",
            }
            return

        if not self.root_dir.exists():
            raise FileNotFoundError(
                f"HOT3D root directory does not exist: {self.root_dir}. "
                "Set use_synthetic: true for the MVP smoke test, or configure "
                "root_dir after downloading HOT3D."
            )

        self.samples = self._load_or_build_real_index()
        if not self.samples:
            raise RuntimeError(
                "No usable HOT3D samples were found. Keep use_synthetic: true until "
                "the real HOT3D path and annotation parser are verified. Missing-field "
                "counts are written in the sample-index metadata when an index can be built."
            )

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        if self.use_synthetic:
            return self._make_synthetic_sample(index)
        return self._load_real_sample(index)

    def print_summary(self) -> None:
        """Print a compact dataset summary for smoke runs and integration checks."""
        print(f"dataset_summary={json.dumps(self.summary(), sort_keys=True)}")

    def summary(self) -> dict[str, Any]:
        if self.use_synthetic:
            return {
                "dataset": "HOT3D",
                "mode": "synthetic",
                "num_samples": len(self.samples),
                "seq_len": self.seq_len,
                "future_steps": self.future_steps,
                "note": "Synthetic tensors only; not real HOT3D results.",
            }

        missing_counts = Counter()
        for sample in self.samples:
            missing_counts.update(sample.get("missing_fields", []))
        return {
            "dataset": "HOT3D",
            "mode": "real",
            "num_samples": len(self.samples),
            "root_dir": str(self.root_dir),
            "index_file": str(self.index_file),
            "missing_field_counts": dict(missing_counts),
            "index_metadata": self.index_metadata,
        }

    def validate_frame_paths(self, sample: dict[str, Any]) -> list[str]:
        """Return missing frame paths for a real indexed sample."""
        missing: list[str] = []
        for path_value in sample.get("frame_paths", []):
            if not Path(path_value).exists():
                missing.append(str(path_value))
        for path_value in sample.get("target_frame_paths", []):
            if not Path(path_value).exists():
                missing.append(str(path_value))
        return missing

    def validate_missing_annotations(self, sample: dict[str, Any]) -> list[str]:
        """Return fields that were unavailable when the sample index was built."""
        return list(sample.get("missing_fields", []))

    def validate_tensor_shapes(self, sample: dict[str, Any]) -> None:
        """Validate the tensor contract consumed by the baseline pipeline."""
        expected = {
            "features": (self.seq_len, self.feature_dim),
            "hand_pose_3d": (self.seq_len, self.num_hand_joints, 3),
            "future_hand_pose_3d": (self.future_steps, self.num_hand_joints, 3),
            "object_pose": (4, 4),
        }
        for key, shape in expected.items():
            value = sample[key]
            if tuple(value.shape) != shape:
                raise ValueError(f"{key} must have shape {shape}, got {tuple(value.shape)}")

        if sample["object_id"].ndim != 0:
            raise ValueError("object_id must be a scalar tensor.")
        if sample["interaction_label"].ndim != 0:
            raise ValueError("interaction_label must be a scalar tensor.")

    def _make_synthetic_sample(self, index: int) -> dict[str, Any]:
        generator = torch.Generator().manual_seed(self.synthetic_seed + int(index))

        features = torch.randn(self.seq_len, self.feature_dim, generator=generator)
        frames = torch.randn(
            self.seq_len,
            3,
            self.image_size,
            self.image_size,
            generator=generator,
        )
        hand_pose_3d = torch.randn(
            self.seq_len,
            self.num_hand_joints,
            3,
            generator=generator,
        )

        final_pose = hand_pose_3d[-1:].repeat(self.future_steps, 1, 1)
        future_noise = 0.05 * torch.randn(
            self.future_steps,
            self.num_hand_joints,
            3,
            generator=generator,
        )
        future_hand_pose_3d = final_pose + future_noise

        object_pose = torch.eye(4, dtype=torch.float32)
        object_id = torch.randint(self.num_objects, size=(), generator=generator)
        action_label = torch.randint(self.num_actions, size=(), generator=generator)

        sample = {
            "features": features.float(),
            "frames": frames.float(),
            "hand_pose_3d": hand_pose_3d.float(),
            "object_id": object_id.long(),
            "object_pose": object_pose,
            "future_hand_pose_3d": future_hand_pose_3d.float(),
            "action_label": action_label.long(),
            "interaction_label": action_label.long(),
            "contact_region": torch.empty(0, dtype=torch.float32),
            "has_contact_region": torch.tensor(False),
            "has_object_pose": torch.tensor(True),
            "has_hand_pose_3d": torch.tensor(True),
            "has_placeholder_features": torch.tensor(False),
            "sample_id": f"synthetic-{index}",
            "is_synthetic": torch.tensor(True),
            "metadata": {
                "sequence_id": "synthetic",
                "frame_start": 0,
                "frame_end": self.seq_len - 1,
                "forecast_frame": self.seq_len + self.future_steps - 1,
            },
        }
        self.validate_tensor_shapes(sample)
        return sample

    def _load_or_build_real_index(self) -> list[dict[str, Any]]:
        if self.index_file.exists() and not self.rebuild_index:
            with self.index_file.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            self.index_metadata = dict(payload.get("metadata", {}))
            return list(payload.get("samples", []))

        samples, metadata = self._build_real_index()
        self.index_metadata = metadata
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with self.index_file.open("w", encoding="utf-8") as handle:
            json.dump({"metadata": metadata, "samples": samples}, handle, indent=2)
        return samples

    def _build_real_index(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        data_format = self._infer_data_format()
        if data_format == "vrs":
            return self._build_official_vrs_index()
        if data_format == "webdataset":
            return self._build_hot3d_clips_index()
        return self._build_legacy_json_index()

    def _build_official_vrs_index(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Inspect official VRS sequences without creating fake samples.

        TODO:
        - Instantiate the official Hot3dDataProvider for each sequence.
        - Use device_data_provider timestamps/stream_ids for camera frames.
        - Use mano_hand_data_provider or umetrack_hand_data_provider for 3D hands.
        - Use object_pose_data_provider and object_library for object_uid labels.
        - Define contact/event frames from a verified label source or documented proxy.
        """
        sequence_dirs = self._discover_official_vrs_sequence_dirs()
        sequence_summaries = [self._summarize_official_vrs_sequence(path) for path in sequence_dirs]
        metadata = {
            "mode": "real",
            "data_format": "vrs",
            "root_dir": str(self.root_dir),
            "num_sequence_dirs": len(sequence_dirs),
            "num_samples": 0,
            "sequence_summaries": sequence_summaries,
            "note": (
                "Official HOT3D VRS layout detected/inspected. No forecasting samples "
                "were built because HOT3D does not directly provide this repo's "
                "action/contact-event labels, and hand-joint conversion must be done "
                "through the official providers before real training."
            ),
            "remaining_todos": [
                "Install/use facebookresearch/hot3d Hot3dDataProvider with projectaria_tools and vrs.",
                "Load recording.vrs image streams by timestamp_ns and stream_id.",
                "Convert MANO/UmeTrack provider output into 21-joint tensors.",
                "Map object_uid and instance_bop_id to target-object IDs.",
                "Define pre-contact event frames from annotations or a documented distance/contact proxy.",
            ],
        }
        return [], metadata

    def _build_hot3d_clips_index(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Inspect HOT3D-Clips tar/WebDataset layout without creating fake labels."""
        split_counts: dict[str, int] = {}
        for split_dir in HOT3D_CLIPS_SPLIT_DIRS:
            path = self.root_dir / split_dir
            split_counts[split_dir] = len(list(path.glob("*.tar"))) if path.exists() else 0

        metadata = {
            "mode": "real",
            "data_format": "webdataset",
            "root_dir": str(self.root_dir),
            "num_samples": 0,
            "split_tar_counts": split_counts,
            "root_files": {
                name: (self.root_dir / name).exists()
                for name in HOT3D_CLIPS_REQUIRED_ROOT_FILES
            },
            "note": (
                "HOT3D-Clips layout detected/inspected. Clips provide per-frame "
                "images, cameras, hand annotations, and object annotations, but this "
                "project still needs a verified pre-contact/action-label definition "
                "before creating supervised forecasting samples."
            ),
            "remaining_todos": [
                "Read tar members <FRAME-ID>.image_<STREAM-ID>.jpg, cameras.json, hands.json, objects.json, info.json.",
                "Use clip_definitions.json and clip_splits.json for provenance and splits.",
                "Derive or import event/action labels before training.",
                "Convert MANO/UmeTrack clip hand annotations into future 3D hand-pose targets.",
            ],
        }
        return [], metadata

    def _build_legacy_json_index(self) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        sequence_dirs = self._discover_sequence_dirs()
        samples: list[dict[str, Any]] = []
        skipped: Counter[str] = Counter()

        for sequence_dir in sequence_dirs:
            frame_paths = self._list_frame_paths(sequence_dir)
            if len(frame_paths) < self.seq_len + self.future_steps:
                skipped["too_few_frames"] += 1
                continue

            annotation_path, annotation = self._load_sequence_annotation(sequence_dir)
            if annotation is None:
                skipped["missing_annotation_json"] += 1
                continue

            frame_numbers = [
                self._frame_number_from_path(path, fallback=index)
                for index, path in enumerate(frame_paths)
            ]
            position_by_frame = {frame: position for position, frame in enumerate(frame_numbers)}
            events = self._extract_events(annotation, frame_numbers)
            if not events:
                skipped["missing_contact_or_event_frame"] += 1
                continue

            for event in events:
                event_frame = event["event_frame"]
                if event_frame in position_by_frame:
                    event_position = position_by_frame[event_frame]
                elif 0 <= event_frame < len(frame_paths):
                    event_position = event_frame
                    event_frame = frame_numbers[event_position]
                else:
                    skipped["event_frame_out_of_range"] += 1
                    continue

                input_start = event_position - self.seq_len
                input_end = event_position - 1
                target_start = event_position
                target_end = event_position + self.future_steps - 1
                if input_start < 0 or target_end >= len(frame_paths):
                    skipped["window_out_of_range"] += 1
                    continue

                input_positions = list(range(input_start, input_end + 1))
                target_positions = list(range(target_start, target_end + 1))
                input_frames = [frame_numbers[position] for position in input_positions]
                target_frames = [frame_numbers[position] for position in target_positions]
                label_info = self._inspect_sample_annotations(
                    annotation=annotation,
                    event=event,
                    event_frame=event_frame,
                    input_frames=input_frames,
                    input_positions=input_positions,
                    target_frames=target_frames,
                    target_positions=target_positions,
                )

                sample = {
                    "sample_id": f"{sequence_dir.name}:{input_frames[0]}-{input_frames[-1]}->{target_frames[-1]}",
                    "sequence_id": sequence_dir.name,
                    "sequence_dir": str(sequence_dir),
                    "annotation_path": str(annotation_path) if annotation_path else "",
                    "frame_paths": [str(frame_paths[position]) for position in input_positions],
                    "target_frame_paths": [str(frame_paths[position]) for position in target_positions],
                    "frame_indices": input_frames,
                    "target_frame_indices": target_frames,
                    "frame_positions": input_positions,
                    "target_frame_positions": target_positions,
                    "event_frame": event_frame,
                    "frame_start": input_frames[0],
                    "frame_end": input_frames[-1],
                    "forecast_frame": target_frames[-1],
                    **label_info,
                }

                if self.validate_frame_paths(sample):
                    skipped["missing_frame_path"] += 1
                    continue

                missing_fields = sample.get("missing_fields", [])
                if self._sample_has_required_fields(missing_fields):
                    samples.append(sample)
                else:
                    skipped["missing_required_fields"] += 1
                    for field in missing_fields:
                        skipped[f"missing_{field}"] += 1

        metadata = {
            "mode": "real",
            "root_dir": str(self.root_dir),
            "num_sequence_dirs": len(sequence_dirs),
            "num_samples": len(samples),
            "seq_len": self.seq_len,
            "future_steps": self.future_steps,
            "skipped_counts": dict(skipped),
            "note": (
                "Index is built from a legacy extracted-frame JSON path, not the "
                "official VRS/WebDataset path. Use only for local parser debugging "
                "unless documented in a real experiment."
            ),
        }
        return samples, metadata

    def _load_real_sample(self, index: int) -> dict[str, Any]:
        indexed = self.samples[index]
        annotation_path = Path(indexed["annotation_path"])
        if not annotation_path.exists():
            raise FileNotFoundError(f"Missing annotation file for sample: {annotation_path}")
        with annotation_path.open("r", encoding="utf-8") as handle:
            annotation = json.load(handle)

        hand_pose_3d = self._extract_pose_sequence(
            annotation,
            frame_numbers=indexed["frame_indices"],
            frame_positions=indexed["frame_positions"],
        )
        future_hand_pose_3d = self._extract_pose_sequence(
            annotation,
            frame_numbers=indexed["target_frame_indices"],
            frame_positions=indexed["target_frame_positions"],
        )

        if hand_pose_3d is None:
            if self.require_hand_pose:
                raise ValueError(f"Missing hand_pose_3d for sample {indexed['sample_id']}")
            hand_pose_3d = torch.zeros(self.seq_len, self.num_hand_joints, 3)

        if future_hand_pose_3d is None:
            raise ValueError(
                f"Missing future_hand_pose_3d target for sample {indexed['sample_id']}. "
                "Do not train or report results without real future hand targets."
            )

        features = self._features_from_hand_pose(hand_pose_3d)
        placeholder_features = False
        if features is None:
            if not self.allow_placeholder_features:
                raise ValueError(
                    f"Cannot build features for sample {indexed['sample_id']}. "
                    "Implement image/pose feature extraction or set "
                    "allow_placeholder_features only for parser debugging."
                )
            features = torch.zeros(self.seq_len, self.feature_dim)
            placeholder_features = True

        object_pose_value = indexed.get("object_pose")
        if object_pose_value is None:
            object_pose = torch.eye(4, dtype=torch.float32)
            has_object_pose = False
        else:
            object_pose = torch.tensor(object_pose_value, dtype=torch.float32)
            has_object_pose = True

        contact_region_value = indexed.get("contact_region")
        if contact_region_value is None:
            contact_region = torch.empty(0, dtype=torch.float32)
            has_contact_region = False
        else:
            contact_region = torch.as_tensor(contact_region_value, dtype=torch.float32)
            has_contact_region = True

        frames = (
            self._load_frame_tensor(indexed["frame_paths"])
            if self.load_frames
            else torch.empty(0, dtype=torch.float32)
        )

        sample = {
            "features": features.float(),
            "frames": frames.float(),
            "frame_paths": indexed["frame_paths"],
            "hand_pose_3d": hand_pose_3d.float(),
            "object_id": torch.tensor(int(indexed["object_id"]), dtype=torch.long),
            "object_pose": object_pose.float(),
            "future_hand_pose_3d": future_hand_pose_3d.float(),
            "action_label": torch.tensor(int(indexed["action_label"]), dtype=torch.long),
            "interaction_label": torch.tensor(int(indexed["action_label"]), dtype=torch.long),
            "contact_region": contact_region,
            "has_contact_region": torch.tensor(has_contact_region),
            "has_object_pose": torch.tensor(has_object_pose),
            "has_hand_pose_3d": torch.tensor(True),
            "has_placeholder_features": torch.tensor(placeholder_features),
            "sample_id": indexed["sample_id"],
            "is_synthetic": torch.tensor(False),
            "metadata": {
                "sequence_id": indexed["sequence_id"],
                "frame_start": indexed["frame_start"],
                "frame_end": indexed["frame_end"],
                "event_frame": indexed["event_frame"],
                "forecast_frame": indexed["forecast_frame"],
                "annotation_path": indexed["annotation_path"],
            },
        }
        self.validate_tensor_shapes(sample)
        return sample

    def _inspect_sample_annotations(
        self,
        annotation: dict[str, Any],
        event: dict[str, Any],
        event_frame: int,
        input_frames: list[int],
        input_positions: list[int],
        target_frames: list[int],
        target_positions: list[int],
    ) -> dict[str, Any]:
        missing: list[str] = []

        object_id = self._coerce_int(
            self._first_available(
                event,
                self._frame_record(annotation, event_frame),
                annotation,
                keys=OBJECT_ID_KEYS,
            )
        )
        if object_id is None:
            missing.append("object_id")

        action_label = self._coerce_action_label(
            self._first_available(
                event,
                self._frame_record(annotation, event_frame),
                annotation,
                keys=ACTION_KEYS,
            )
        )
        if action_label is None:
            missing.append("action_label")

        object_pose = self._normalize_object_pose(
            self._first_available(
                event,
                self._frame_record(annotation, event_frame),
                annotation,
                keys=OBJECT_POSE_KEYS,
            )
        )
        if object_pose is None:
            missing.append("object_pose")

        contact_region = self._first_available(
            event,
            self._frame_record(annotation, event_frame),
            annotation,
            keys=CONTACT_REGION_KEYS,
        )
        if contact_region is None:
            missing.append("contact_region")

        if not self._has_pose_sequence(annotation, input_frames, input_positions):
            missing.append("hand_pose_3d")

        if not self._has_pose_sequence(annotation, target_frames, target_positions):
            missing.append("future_hand_pose_3d")

        return {
            "object_id": object_id,
            "action_label": action_label,
            "object_pose": object_pose,
            "contact_region": contact_region,
            "missing_fields": missing,
        }

    def _sample_has_required_fields(self, missing_fields: list[str]) -> bool:
        required = []
        if self.require_object_id:
            required.append("object_id")
        if self.require_action_label:
            required.append("action_label")
        if self.require_hand_pose:
            required.append("hand_pose_3d")
        if self.require_future_hand_pose:
            required.append("future_hand_pose_3d")
        return not any(field in missing_fields for field in required)

    def _infer_data_format(self) -> str:
        if self.data_format in {"vrs", "webdataset"}:
            return self.data_format
        if self._discover_official_vrs_sequence_dirs():
            return "vrs"
        if any((self.root_dir / split_dir).exists() for split_dir in HOT3D_CLIPS_SPLIT_DIRS):
            return "webdataset"
        if any(self.root_dir.rglob("*.tar")):
            return "webdataset"
        return "legacy_json"

    def _discover_official_vrs_sequence_dirs(self) -> list[Path]:
        sequence_dirs: list[Path] = []
        for metadata_path in self.root_dir.rglob("metadata.json"):
            sequence_dir = metadata_path.parent
            has_vrs = (sequence_dir / "recording.vrs").exists()
            has_pose_files = (sequence_dir / "dynamic_objects.csv").exists() or (
                sequence_dir / "mano_hand_pose_trajectory.jsonl"
            ).exists()
            if has_vrs or has_pose_files:
                sequence_dirs.append(sequence_dir)
        return sorted(set(sequence_dirs))

    def _summarize_official_vrs_sequence(self, sequence_dir: Path) -> dict[str, Any]:
        metadata = self._load_json_if_available(sequence_dir / "metadata.json")
        headset = metadata.get("headset", "unknown") if isinstance(metadata, dict) else "unknown"
        required_files = list(OFFICIAL_VRS_COMMON_FILES)
        if headset == "Quest3":
            required_files.extend(OFFICIAL_VRS_QUEST_FILES)

        missing_required = [
            filename for filename in required_files if not (sequence_dir / filename).exists()
        ]
        optional_present = [
            filename for filename in OFFICIAL_VRS_OPTIONAL_FILES if (sequence_dir / filename).exists()
        ]
        mask_dir = sequence_dir / "masks"
        mask_files = sorted(path.name for path in mask_dir.glob("mask_*.csv")) if mask_dir.exists() else []
        has_aria_mps = any((sequence_dir / hint).exists() for hint in OFFICIAL_VRS_ARIA_HINTS)

        return {
            "sequence_id": sequence_dir.name,
            "headset": headset,
            "participant_id": metadata.get("participant_id") if isinstance(metadata, dict) else None,
            "gt_available_status": metadata.get("gt_available_status", {}) if isinstance(metadata, dict) else {},
            "missing_required_files": missing_required,
            "optional_files_present": optional_present,
            "mask_files": mask_files,
            "has_aria_mps": has_aria_mps,
        }

    def _discover_sequence_dirs(self) -> list[Path]:
        """Detect sequence/session directories by locating image-containing folders."""
        dirs: set[Path] = set()
        for path in self.root_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in self.frame_extensions:
                dirs.add(path.parent)
        return sorted(dirs)

    def _list_frame_paths(self, sequence_dir: Path) -> list[Path]:
        frame_paths = [
            path
            for path in sequence_dir.iterdir()
            if path.is_file() and path.suffix.lower() in self.frame_extensions
        ]
        return sorted(frame_paths, key=lambda path: (self._frame_number_from_path(path, 0), path.name))

    def _load_sequence_annotation(self, sequence_dir: Path) -> tuple[Path | None, dict[str, Any] | None]:
        candidates: list[Path] = []
        candidates.extend(sequence_dir / name for name in self.annotation_candidates)
        if self.annotation_dir.exists():
            candidates.append(self.annotation_dir / f"{sequence_dir.name}.json")
            candidates.extend(self.annotation_dir / sequence_dir.name / name for name in self.annotation_candidates)

        for path in candidates:
            if path.exists() and path.is_file():
                with path.open("r", encoding="utf-8") as handle:
                    payload = json.load(handle)
                if not isinstance(payload, dict):
                    raise ValueError(f"Annotation JSON must contain an object at top level: {path}")
                return path, payload
        return None, None

    def _extract_events(self, annotation: dict[str, Any], frame_numbers: list[int]) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []

        for key in ("contact_frame", "event_frame", "interaction_frame"):
            value = self._coerce_int(annotation.get(key))
            if value is not None:
                events.append({"event_frame": value})

        for key in ("contact_frames", "event_frames", "interaction_frames"):
            values = annotation.get(key)
            if isinstance(values, list):
                for item in values:
                    if isinstance(item, dict):
                        frame_value = self._event_frame_from_record(item)
                        if frame_value is not None:
                            event = dict(item)
                            event["event_frame"] = frame_value
                            events.append(event)
                    else:
                        frame_value = self._coerce_int(item)
                        if frame_value is not None:
                            events.append({"event_frame": frame_value})

        for key in ("events", "interactions"):
            values = annotation.get(key)
            if isinstance(values, list):
                for item in values:
                    if not isinstance(item, dict):
                        continue
                    frame_value = self._event_frame_from_record(item)
                    if frame_value is not None:
                        event = dict(item)
                        event["event_frame"] = frame_value
                        events.append(event)

        for frame_number in frame_numbers:
            record = self._frame_record(annotation, frame_number)
            if not record:
                continue
            if record.get("is_contact") or record.get("contact") or record.get("interaction_event"):
                events.append({"event_frame": frame_number, **record})

        unique: dict[int, dict[str, Any]] = {}
        for event in events:
            frame_value = self._coerce_int(event.get("event_frame"))
            if frame_value is not None:
                event["event_frame"] = frame_value
                unique.setdefault(frame_value, event)
        return list(unique.values())

    def _event_frame_from_record(self, record: dict[str, Any]) -> int | None:
        for key in ("contact_frame", "event_frame", "interaction_frame", "frame_index", "frame_id"):
            value = self._coerce_int(record.get(key))
            if value is not None:
                return value
        return None

    def _frame_record(self, annotation: dict[str, Any], frame_number: int) -> dict[str, Any]:
        frames = annotation.get("frames")
        if isinstance(frames, dict):
            record = frames.get(str(frame_number))
            return record if isinstance(record, dict) else {}
        if isinstance(frames, list):
            for record in frames:
                if not isinstance(record, dict):
                    continue
                record_frame = self._coerce_int(
                    record.get("frame_index", record.get("frame_id", record.get("frame")))
                )
                if record_frame == frame_number:
                    return record
        return {}

    def _extract_pose_sequence(
        self,
        annotation: dict[str, Any],
        frame_numbers: list[int],
        frame_positions: list[int],
    ) -> torch.Tensor | None:
        poses: list[torch.Tensor] = []
        for frame_number, frame_position in zip(frame_numbers, frame_positions):
            pose_value = self._pose_for_frame(annotation, frame_number, frame_position)
            pose = self._normalize_pose(pose_value)
            if pose is None:
                return None
            poses.append(pose)
        return torch.stack(poses, dim=0)

    def _has_pose_sequence(
        self,
        annotation: dict[str, Any],
        frame_numbers: list[int],
        frame_positions: list[int],
    ) -> bool:
        return self._extract_pose_sequence(annotation, frame_numbers, frame_positions) is not None

    def _pose_for_frame(
        self,
        annotation: dict[str, Any],
        frame_number: int,
        frame_position: int,
    ) -> Any:
        record = self._frame_record(annotation, frame_number)
        for key in POSE_KEYS:
            if key in record:
                return record[key]

        for key in POSE_KEYS:
            value = annotation.get(key)
            if isinstance(value, dict):
                if str(frame_number) in value:
                    return value[str(frame_number)]
                if str(frame_position) in value:
                    return value[str(frame_position)]
            if isinstance(value, list) and 0 <= frame_position < len(value):
                return value[frame_position]
        return None

    def _normalize_pose(self, value: Any) -> torch.Tensor | None:
        if value is None:
            return None
        tensor = torch.as_tensor(value, dtype=torch.float32)
        if tensor.numel() != self.num_hand_joints * 3:
            return None
        return tensor.reshape(self.num_hand_joints, 3)

    def _features_from_hand_pose(self, hand_pose_3d: torch.Tensor) -> torch.Tensor | None:
        if hand_pose_3d.ndim != 3 or hand_pose_3d.shape[-1] != 3:
            return None
        features = hand_pose_3d.flatten(start_dim=1)
        if features.shape[-1] < self.feature_dim:
            features = F.pad(features, (0, self.feature_dim - features.shape[-1]))
        elif features.shape[-1] > self.feature_dim:
            features = features[:, : self.feature_dim]
        return features

    def _load_frame_tensor(self, frame_paths: list[str]) -> torch.Tensor:
        try:
            import cv2
        except ImportError as exc:  # pragma: no cover - covered by environment setup.
            raise ImportError("opencv-python is required when load_frames: true.") from exc

        frames: list[torch.Tensor] = []
        for path_value in frame_paths:
            image = cv2.imread(path_value, cv2.IMREAD_COLOR)
            if image is None:
                raise FileNotFoundError(f"Could not read frame: {path_value}")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = cv2.resize(image, (self.image_size, self.image_size))
            tensor = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
            frames.append(tensor)
        return torch.stack(frames, dim=0)

    def _first_available(self, *records: dict[str, Any], keys: tuple[str, ...]) -> Any:
        for record in records:
            if not isinstance(record, dict):
                continue
            for key in keys:
                if key in record and record[key] is not None:
                    return record[key]
        return None

    def _normalize_object_pose(self, value: Any) -> list[list[float]] | None:
        if value is None:
            return None
        tensor = torch.as_tensor(value, dtype=torch.float32)
        if tensor.numel() != 16:
            return None
        return tensor.reshape(4, 4).tolist()

    def _coerce_action_label(self, value: Any) -> int | None:
        direct = self._coerce_int(value)
        if direct is not None:
            return direct
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in self.action_taxonomy:
                return self.action_taxonomy.index(normalized)
        return None

    def _coerce_int(self, value: Any) -> int | None:
        if value is None or isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.isdigit() or (stripped.startswith("-") and stripped[1:].isdigit()):
                return int(stripped)
        return None

    def _frame_number_from_path(self, path: Path, fallback: int) -> int:
        matches = re.findall(r"\d+", path.stem)
        if not matches:
            return fallback
        return int(matches[-1])

    def _resolve_path(self, value: str | Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else Path.cwd() / path

    def _load_json_if_available(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return payload if isinstance(payload, dict) else {}
