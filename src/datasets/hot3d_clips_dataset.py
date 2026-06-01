"""PyTorch dataset for verified HOT3D-Clips sample indexes.

This is the first real-data dataset surface. It consumes derived proxy labels
from the sample index, but it does not treat them as direct HOT3D ground truth.
"""

from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset

from src.datasets.hot3d_clips_parser import read_image_member


DEFAULT_INDEX_PATH = Path("data/processed/hot3d_clips_sample_index_proxy_v1_multi.json")
DEFAULT_LABEL_MAP_PATH = Path("data/processed/hot3d_target_object_label_map.json")
STREAM_ORDER = ("image_1201-1", "image_1201-2", "image_214-1")
HAND_ORDER = ("left", "right")
MANO_THETA_DIM = 15
MANO_WRIST_DIM = 6
MANO_DIM_PER_HAND = MANO_THETA_DIM + MANO_WRIST_DIM


def load_index_payload(index_path: str | Path) -> dict[str, Any]:
    path = Path(index_path)
    if not path.exists():
        raise FileNotFoundError(f"HOT3D-Clips sample index not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict) or not isinstance(payload.get("samples"), list):
        raise ValueError(f"Expected sample-index JSON with a samples list: {path}")
    return payload


def selected_object_name(sample: dict[str, Any]) -> str | None:
    proxy = sample.get("target_object_proxy", {})
    if not isinstance(proxy, dict) or proxy.get("assigned") is not True:
        return None
    name = proxy.get("selected_object_name")
    return str(name) if name else None


def build_label_map(samples: list[dict[str, Any]]) -> dict[str, Any]:
    classes = sorted({name for sample in samples if (name := selected_object_name(sample))})
    return {
        "label_status": "derived_proxy_not_direct_ground_truth",
        "classes": classes,
        "class_to_idx": {name: index for index, name in enumerate(classes)},
        "idx_to_class": {str(index): name for index, name in enumerate(classes)},
    }


def save_label_map(label_map: dict[str, Any], label_map_path: str | Path) -> None:
    path = Path(label_map_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(label_map, handle, indent=2)


def load_or_create_label_map(
    samples: list[dict[str, Any]],
    label_map_path: str | Path = DEFAULT_LABEL_MAP_PATH,
) -> dict[str, Any]:
    path = Path(label_map_path)
    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            label_map = json.load(handle)
        if isinstance(label_map, dict) and isinstance(label_map.get("class_to_idx"), dict):
            return label_map

    label_map = build_label_map(samples)
    save_label_map(label_map, path)
    return label_map


def class_distribution(samples: list[dict[str, Any]]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for sample in samples:
        name = selected_object_name(sample)
        if name:
            counts[name] += 1
    return dict(counts.most_common())


class HOT3DClipsDataset(Dataset):
    """Dataset backed by a verified HOT3D-Clips sample-index JSON.

    Modes:
    - metadata_only: returns lightweight per-frame metadata features.
    - image: loads one image stream from each tar shard and resizes to 224x224
      by default.
    """

    def __init__(
        self,
        index_path: str | Path = DEFAULT_INDEX_PATH,
        *,
        mode: str = "metadata_only",
        clips_root: str | Path | None = None,
        label_map_path: str | Path = DEFAULT_LABEL_MAP_PATH,
        hand_selection: str = "both",
        image_stream: str = "auto",
        image_size: int = 224,
    ) -> None:
        if mode not in {"metadata_only", "image"}:
            raise ValueError("mode must be 'metadata_only' or 'image'.")
        if hand_selection not in {"left", "right", "both"}:
            raise ValueError("hand_selection must be 'left', 'right', or 'both'.")

        self.index_path = Path(index_path)
        self.mode = mode
        self.hand_selection = hand_selection
        self.image_stream = image_stream
        self.image_size = int(image_size)

        payload = load_index_payload(self.index_path)
        self.index_metadata = payload.get("metadata", {})
        root_value = clips_root or self.index_metadata.get("root") or "data/raw/hot3d_clips"
        self.clips_root = Path(root_value)

        raw_samples = [sample for sample in payload["samples"] if isinstance(sample, dict)]
        self.label_map = load_or_create_label_map(raw_samples, label_map_path)
        self.class_to_idx = {str(key): int(value) for key, value in self.label_map["class_to_idx"].items()}

        self.skipped_counts: Counter[str] = Counter()
        self.missing_counts: Counter[str] = Counter()
        self.samples = self._filter_usable_samples(raw_samples)
        if not self.samples:
            raise RuntimeError("No usable HOT3D-Clips samples after proxy-label filtering.")

        self.frame_feature_dim = self._metadata_frame_features(self.samples[0]).shape[-1]
        self.future_hand_pose_dim = self._future_hand_pose_vector(self.samples[0]).numel()

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        sample = self.samples[index]
        frame_features = self._metadata_frame_features(sample)
        future_hand_pose = self._future_hand_pose_vector(sample)
        object_name = selected_object_name(sample)
        if object_name is None or object_name not in self.class_to_idx:
            raise RuntimeError(f"Sample lost usable proxy label after filtering: {sample.get('sample_id')}")

        proxy = sample["target_object_proxy"]
        item: dict[str, Any] = {
            "features": frame_features,
            "frame_features": frame_features,
            "future_hand_pose": future_hand_pose,
            "target_object_label": torch.tensor(self.class_to_idx[object_name], dtype=torch.long),
            "target_object_name": object_name,
            "proxy_confidence": torch.tensor(float(proxy.get("proxy_confidence", 0.0)), dtype=torch.float32),
            "proxy_label_status": proxy.get("label_status", "derived_proxy_not_direct_ground_truth"),
            "clip_id": str(sample.get("clip_id")),
            "sample_id": str(sample.get("sample_id")),
            "metadata": sample.get("metadata", {}),
        }

        if self.mode == "image":
            item["frames"] = self._load_image_frames(sample)

        return item

    def summary(self) -> dict[str, Any]:
        return {
            "index_path": str(self.index_path),
            "clips_root": str(self.clips_root),
            "mode": self.mode,
            "num_samples": len(self),
            "num_object_classes": len(self.class_to_idx),
            "frame_feature_dim": self.frame_feature_dim,
            "future_hand_pose_dim": self.future_hand_pose_dim,
            "hand_selection": self.hand_selection,
            "image_stream": self.image_stream,
            "image_size": self.image_size,
            "class_distribution": class_distribution(self.samples),
            "missing_counts": dict(self.missing_counts),
            "skipped_counts": dict(self.skipped_counts),
            "label_status": "target object labels are derived proxies, not direct HOT3D ground truth",
        }

    def _filter_usable_samples(self, raw_samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
        usable: list[dict[str, Any]] = []
        for sample in raw_samples:
            object_name = selected_object_name(sample)
            if object_name is None:
                self.skipped_counts["missing_target_object_proxy"] += 1
                continue
            if object_name not in self.class_to_idx:
                self.skipped_counts["target_object_not_in_label_map"] += 1
                continue
            if not isinstance(sample.get("future_hand_pose"), dict):
                self.skipped_counts["missing_future_hand_pose"] += 1
                continue
            usable.append(sample)
        return usable

    def _metadata_frame_features(self, sample: dict[str, Any]) -> torch.Tensor:
        frame_ids = sample.get("observation_frame_ids", [])
        if not isinstance(frame_ids, list) or not frame_ids:
            self.missing_counts["observation_frame_ids"] += 1
            frame_ids = ["0"]

        image_streams = sample.get("image_streams", {})
        stream_keys = set(image_streams.keys()) if isinstance(image_streams, dict) else set()
        metadata = sample.get("metadata", {})
        device = str(metadata.get("device", "")).lower() if isinstance(metadata, dict) else ""
        max_frame_id = max([_safe_int(frame_id) for frame_id in frame_ids] + [_safe_int(sample.get("forecast_frame_id"))])
        denom = max(1, max_frame_id)
        seq_denom = max(1, len(frame_ids) - 1)

        rows: list[list[float]] = []
        for index, frame_id in enumerate(frame_ids):
            position = index / seq_denom
            rows.append(
                [
                    _safe_int(frame_id) / denom,
                    position,
                    math.sin(2.0 * math.pi * position),
                    math.cos(2.0 * math.pi * position),
                    1.0 if STREAM_ORDER[0] in stream_keys else 0.0,
                    1.0 if STREAM_ORDER[1] in stream_keys else 0.0,
                    1.0 if STREAM_ORDER[2] in stream_keys else 0.0,
                    1.0 if device == "aria" else 0.0,
                    1.0 if device == "quest3" else 0.0,
                ]
            )
        return torch.tensor(rows, dtype=torch.float32)

    def _future_hand_pose_vector(self, sample: dict[str, Any]) -> torch.Tensor:
        hands = ("left", "right") if self.hand_selection == "both" else (self.hand_selection,)
        values: list[float] = []
        for hand in hands:
            values.extend(self._mano_vector_for_hand(sample, hand))
        return torch.tensor(values, dtype=torch.float32)

    def _mano_vector_for_hand(self, sample: dict[str, Any], hand: str) -> list[float]:
        hand_record = sample.get("future_hand_pose", {}).get(hand)
        if not isinstance(hand_record, dict):
            self.missing_counts[f"future_hand_pose.{hand}"] += 1
            return [0.0] * MANO_DIM_PER_HAND

        payload = hand_record.get("payload", {})
        if not isinstance(payload, dict):
            self.missing_counts[f"future_hand_pose.{hand}.payload"] += 1
            return [0.0] * MANO_DIM_PER_HAND

        thetas = _numeric_list(payload.get("thetas"), MANO_THETA_DIM)
        wrist = _numeric_list(payload.get("wrist_xform"), MANO_WRIST_DIM)
        if len(thetas) < MANO_THETA_DIM:
            self.missing_counts[f"future_hand_pose.{hand}.thetas"] += 1
        if len(wrist) < MANO_WRIST_DIM:
            self.missing_counts[f"future_hand_pose.{hand}.wrist_xform"] += 1
        return _pad_or_trim(thetas, MANO_THETA_DIM) + _pad_or_trim(wrist, MANO_WRIST_DIM)

    def _load_image_frames(self, sample: dict[str, Any]) -> torch.Tensor:
        image_streams = sample.get("image_streams", {})
        if not isinstance(image_streams, dict) or not image_streams:
            raise RuntimeError(f"Sample has no image streams: {sample.get('sample_id')}")

        stream = self._resolve_image_stream(image_streams)
        shard_path = self._shard_path(sample)
        frames: list[torch.Tensor] = []
        for member_name in image_streams[stream]:
            image = read_image_member(shard_path, member_name)
            frames.append(_image_to_tensor(image, image_size=self.image_size))
        return torch.stack(frames, dim=0)

    def _resolve_image_stream(self, image_streams: dict[str, Any]) -> str:
        if self.image_stream != "auto" and self.image_stream in image_streams:
            return self.image_stream
        for stream in ("image_214-1", "image_1201-1", "image_1201-2"):
            if stream in image_streams:
                return stream
        return sorted(image_streams.keys())[0]

    def _shard_path(self, sample: dict[str, Any]) -> Path:
        shard = str(sample.get("shard", "")).replace("\\", "/")
        path = self.clips_root / Path(shard)
        if not path.exists():
            raise FileNotFoundError(f"Shard not found for sample {sample.get('sample_id')}: {path}")
        return path


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _numeric_list(value: Any, max_len: int) -> list[float]:
    if not isinstance(value, list):
        return []
    numbers: list[float] = []
    for item in value[:max_len]:
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            numbers.append(float(item))
    return numbers


def _pad_or_trim(values: list[float], length: int) -> list[float]:
    if len(values) >= length:
        return values[:length]
    return values + [0.0] * (length - len(values))


def _image_to_tensor(image: np.ndarray, *, image_size: int) -> torch.Tensor:
    if image.ndim == 2:
        image = np.repeat(image[:, :, None], repeats=3, axis=2)
    elif image.shape[2] == 1:
        image = np.repeat(image, repeats=3, axis=2)
    resized = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
    tensor = torch.from_numpy(resized.copy()).permute(2, 0, 1).float() / 255.0
    return tensor
