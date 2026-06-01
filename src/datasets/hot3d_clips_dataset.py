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

from src.datasets.hot3d_clips_parser import get_frame_member_names, read_image_member, read_json_member
from src.datasets.hot3d_proxy_labels import FALLBACK_IMAGE_SIZES, select_target_object_proxy


DEFAULT_INDEX_PATH = Path("data/processed/hot3d_clips_sample_index_proxy_v1_multi.json")
DEFAULT_LABEL_MAP_PATH = Path("data/processed/hot3d_target_object_label_map.json")
STREAM_ORDER = ("image_1201-1", "image_1201-2", "image_214-1")
HAND_ORDER = ("left", "right")
MANO_THETA_DIM = 15
MANO_WRIST_DIM = 6
MANO_DIM_PER_HAND = MANO_THETA_DIM + MANO_WRIST_DIM
CANDIDATE_NUMERIC_FEATURE_NAMES = (
    "known_class",
    "class_index_normalized",
    "object_bop_id_normalized",
    "visibility",
    "has_pose",
    "proxy_score",
    "proxy_confidence",
    "best_iou",
    "best_normalized_center_distance",
    "object_box_cx",
    "object_box_cy",
    "object_box_w",
    "object_box_h",
    "hand_box_cx",
    "hand_box_cy",
    "hand_box_w",
    "hand_box_h",
)


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
    - object_metadata: adds padded object-candidate geometry/proxy features.
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
        max_candidates: int = 8,
        allow_forecast_object_input: bool = False,
    ) -> None:
        if mode not in {"metadata_only", "object_metadata", "image"}:
            raise ValueError("mode must be 'metadata_only', 'object_metadata', or 'image'.")
        if hand_selection not in {"left", "right", "both"}:
            raise ValueError("hand_selection must be 'left', 'right', or 'both'.")
        if int(max_candidates) <= 0:
            raise ValueError("max_candidates must be positive.")

        self.index_path = Path(index_path)
        self.mode = mode
        self.hand_selection = hand_selection
        self.image_stream = image_stream
        self.image_size = int(image_size)
        self.max_candidates = int(max_candidates)
        self.allow_forecast_object_input = bool(allow_forecast_object_input)

        payload = load_index_payload(self.index_path)
        self.index_metadata = payload.get("metadata", {})
        root_value = clips_root or self.index_metadata.get("root") or "data/raw/hot3d_clips"
        self.clips_root = Path(root_value)
        self.min_visibility = float(self.index_metadata.get("min_visibility", 0.0))

        raw_samples = [sample for sample in payload["samples"] if isinstance(sample, dict)]
        self.label_map = load_or_create_label_map(raw_samples, label_map_path)
        self.class_to_idx = {str(key): int(value) for key, value in self.label_map["class_to_idx"].items()}

        self.skipped_counts: Counter[str] = Counter()
        self.missing_counts: Counter[str] = Counter()
        self._observation_candidate_cache: dict[
            tuple[str, str],
            tuple[list[dict[str, Any]], list[dict[str, Any]]],
        ] = {}
        self.samples = self._filter_usable_samples(raw_samples)
        if not self.samples:
            raise RuntimeError("No usable HOT3D-Clips samples after proxy-label filtering.")

        self.frame_feature_dim = self._metadata_frame_features(self.samples[0]).shape[-1]
        self.future_hand_pose_dim = self._future_hand_pose_vector(self.samples[0]).numel()
        self.object_candidate_feature_names = [
            *(f"class_one_hot:{name}" for name in self.label_map["classes"]),
            *CANDIDATE_NUMERIC_FEATURE_NAMES,
        ]
        self.object_candidate_feature_dim = len(self.object_candidate_feature_names)

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
        object_input_frame = self._object_input_frame_id(sample)
        target_proxy_frame = self._target_proxy_frame_id(sample)
        input_uses_forecast_frame = object_input_frame == target_proxy_frame
        item: dict[str, Any] = {
            "features": frame_features,
            "frame_features": frame_features,
            "future_hand_pose": future_hand_pose,
            "target_object_label": torch.tensor(self.class_to_idx[object_name], dtype=torch.long),
            "target_object_proxy_label": torch.tensor(self.class_to_idx[object_name], dtype=torch.long),
            "target_object_name": object_name,
            "proxy_confidence": torch.tensor(float(proxy.get("proxy_confidence", 0.0)), dtype=torch.float32),
            "proxy_label_status": proxy.get("label_status", "derived_proxy_not_direct_ground_truth"),
            "clip_id": str(sample.get("clip_id")),
            "sample_id": str(sample.get("sample_id")),
            "object_input_frame": object_input_frame,
            "target_object_proxy_frame": target_proxy_frame,
            "input_uses_forecast_frame": input_uses_forecast_frame,
            "metadata": sample.get("metadata", {}),
        }

        if self.mode == "image":
            item["frames"] = self._load_image_frames(sample)
        if self.mode == "object_metadata":
            candidate_features, candidate_mask, candidate_names = self._object_candidate_features(sample)
            item["observation_object_candidates"] = candidate_features
            item["object_candidates"] = candidate_features
            item["candidate_mask"] = candidate_mask
            item["candidate_object_names"] = candidate_names

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
            "max_candidates": self.max_candidates,
            "object_candidate_feature_dim": self.object_candidate_feature_dim,
            "object_candidate_feature_names": self.object_candidate_feature_names,
            "object_input_source": "last_observation_frame",
            "input_uses_forecast_frame": False,
            "allow_forecast_object_input": self.allow_forecast_object_input,
            "hand_selection": self.hand_selection,
            "image_stream": self.image_stream,
            "image_size": self.image_size,
            "class_distribution": class_distribution(self.samples),
            "candidate_coverage": self.candidate_coverage_stats(),
            "missing_counts": dict(self.missing_counts),
            "skipped_counts": dict(self.skipped_counts),
            "label_status": "target object labels are derived proxies, not direct HOT3D ground truth",
        }

    def candidate_coverage_stats(self) -> dict[str, Any]:
        total_candidates = 0
        capped_candidates = 0
        samples_with_candidates = 0
        selected_in_top_k = 0
        missing_candidate_scores = 0
        input_uses_forecast_frame = 0

        for sample in self.samples:
            candidates, _ = self._observation_candidate_payload(sample)
            if not candidates:
                missing_candidate_scores += 1
                continue
            if self._object_input_frame_id(sample) == self._target_proxy_frame_id(sample):
                input_uses_forecast_frame += 1
            samples_with_candidates += 1
            total_candidates += len(candidates)
            capped_candidates += min(len(candidates), self.max_candidates)
            if self._selected_object_in_top_k(sample, candidates[: self.max_candidates]):
                selected_in_top_k += 1

        sample_count = max(1, len(self.samples))
        candidates_sample_count = max(1, samples_with_candidates)
        return {
            "max_candidates": self.max_candidates,
            "samples": len(self.samples),
            "samples_with_candidates": samples_with_candidates,
            "samples_missing_candidate_scores": missing_candidate_scores,
            "samples_using_forecast_frame_as_input": input_uses_forecast_frame,
            "mean_candidates_per_sample": total_candidates / sample_count,
            "mean_capped_candidates_per_sample": capped_candidates / sample_count,
            "selected_object_in_top_k_fraction": selected_in_top_k / candidates_sample_count,
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
        max_frame_id = max([_safe_int(frame_id) for frame_id in frame_ids])
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

    def _object_candidate_features(self, sample: dict[str, Any]) -> tuple[torch.Tensor, torch.Tensor, list[str]]:
        self._validate_object_input_frame(sample)
        features = torch.zeros(
            (self.max_candidates, self.object_candidate_feature_dim),
            dtype=torch.float32,
        )
        mask = torch.zeros((self.max_candidates,), dtype=torch.float32)
        candidate_names: list[str] = []
        candidate_scores, raw_candidates_list = self._observation_candidate_payload(sample)
        raw_candidates = self._raw_candidate_lookup(raw_candidates_list)

        for row_index, candidate in enumerate(candidate_scores[: self.max_candidates]):
            raw_candidate = raw_candidates.get(_candidate_identity_key(candidate), {})
            vector = self._candidate_feature_vector(candidate, raw_candidate)
            features[row_index] = torch.tensor(vector, dtype=torch.float32)
            mask[row_index] = 1.0
            candidate_names.append(str(candidate.get("object_name") or "unknown"))

        return features, mask, candidate_names

    def _candidate_feature_vector(self, candidate: dict[str, Any], raw_candidate: dict[str, Any]) -> list[float]:
        class_count = max(1, len(self.class_to_idx))
        object_name = str(candidate.get("object_name") or "")
        class_index = self.class_to_idx.get(object_name)
        one_hot = [0.0] * len(self.class_to_idx)
        if class_index is not None:
            one_hot[class_index] = 1.0

        best_stream = _best_stream_score(candidate)
        stream_id = str(best_stream.get("stream_id") or candidate.get("best_stream_id") or "")
        object_box_features = _normalized_box_features(best_stream.get("object_box"), stream_id)
        hand_box_features = _normalized_box_features(best_stream.get("hand_box_union"), stream_id)

        class_index_normalized = (
            float(class_index) / max(1, class_count - 1)
            if class_index is not None
            else -1.0
        )
        numeric = [
            1.0 if class_index is not None else 0.0,
            class_index_normalized,
            _safe_float(candidate.get("object_bop_id"), default=0.0) / 100.0,
            _safe_float(candidate.get("visibility"), default=0.0),
            1.0 if raw_candidate.get("has_pose") is True else 0.0,
            _safe_float(candidate.get("proxy_score"), default=0.0),
            _safe_float(candidate.get("proxy_confidence"), default=0.0),
            _safe_float(candidate.get("best_iou"), default=0.0),
            _safe_float(candidate.get("best_normalized_center_distance"), default=1.0),
            *object_box_features,
            *hand_box_features,
        ]
        return one_hot + numeric

    def _observation_candidate_payload(
        self,
        sample: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        self._validate_object_input_frame(sample)
        object_input_frame = self._object_input_frame_id(sample)

        indexed_scores = sample.get("observation_object_candidate_scores")
        indexed_candidates = sample.get("observation_object_candidates")
        if isinstance(indexed_scores, list) and isinstance(indexed_candidates, list):
            return (
                self._sort_candidate_scores(indexed_scores),
                [candidate for candidate in indexed_candidates if isinstance(candidate, dict)],
            )

        return self._load_observation_candidates_from_tar(sample, object_input_frame)

    def _load_observation_candidates_from_tar(
        self,
        sample: dict[str, Any],
        frame_id: str,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        shard_path = self._shard_path(sample)
        cache_key = (str(shard_path), frame_id)
        if cache_key in self._observation_candidate_cache:
            return self._observation_candidate_cache[cache_key]

        members = get_frame_member_names(frame_id)
        try:
            hands_json = read_json_member(shard_path, members["hands"])
            objects_json = read_json_member(shard_path, members["objects"])
            cameras_json = read_json_member(shard_path, members["cameras"])
        except (FileNotFoundError, json.JSONDecodeError) as exc:
            self.missing_counts[f"observation_object_input_read_error:{type(exc).__name__}"] += 1
            payload = ([], [])
            self._observation_candidate_cache[cache_key] = payload
            return payload

        raw_candidates = _extract_visible_object_candidates(objects_json, self.min_visibility)
        if not raw_candidates:
            self.missing_counts["observation_object_candidates"] += 1
            payload = ([], [])
            self._observation_candidate_cache[cache_key] = payload
            return payload

        observation_proxy = select_target_object_proxy(
            {
                "hands_json": hands_json,
                "cameras_json": cameras_json,
                "target_object_candidates": raw_candidates,
                "min_visibility": self.min_visibility,
            }
        )
        candidate_scores = observation_proxy.get("candidate_scores", [])
        if not isinstance(candidate_scores, list):
            candidate_scores = []
        payload = (self._sort_candidate_scores(candidate_scores), raw_candidates)
        self._observation_candidate_cache[cache_key] = payload
        return payload

    def _sort_candidate_scores(self, candidates: list[Any]) -> list[dict[str, Any]]:
        typed_candidates = [candidate for candidate in candidates if isinstance(candidate, dict)]
        return sorted(
            typed_candidates,
            key=lambda candidate: _safe_float(candidate.get("proxy_score"), default=float("-inf")),
            reverse=True,
        )

    def _raw_candidate_lookup(
        self,
        raw_candidates: list[dict[str, Any]],
    ) -> dict[tuple[str, str, str, str, int], dict[str, Any]]:
        lookup: dict[tuple[str, str, str, str, int], dict[str, Any]] = {}
        for candidate in raw_candidates:
            if isinstance(candidate, dict):
                lookup[_candidate_identity_key(candidate)] = candidate
        return lookup

    def _object_input_frame_id(self, sample: dict[str, Any]) -> str:
        explicit = sample.get("object_input_frame")
        if explicit is not None:
            return str(explicit)
        frame_ids = sample.get("observation_frame_ids", [])
        if isinstance(frame_ids, list) and frame_ids:
            return str(frame_ids[-1])
        metadata = sample.get("metadata", {})
        if isinstance(metadata, dict) and metadata.get("end_frame") is not None:
            return str(metadata["end_frame"])
        return str(sample.get("forecast_frame_id", ""))

    def _target_proxy_frame_id(self, sample: dict[str, Any]) -> str:
        explicit = sample.get("target_object_proxy_frame")
        if explicit is not None:
            return str(explicit)
        return str(sample.get("forecast_frame_id", ""))

    def _validate_object_input_frame(self, sample: dict[str, Any]) -> None:
        object_input_frame = self._object_input_frame_id(sample)
        target_proxy_frame = self._target_proxy_frame_id(sample)
        if object_input_frame == target_proxy_frame and not self.allow_forecast_object_input:
            raise RuntimeError(
                "Object-aware input would use the forecast frame. "
                f"sample_id={sample.get('sample_id')} frame={object_input_frame}. "
                "Set allow_forecast_object_input=True only for explicit leakage-debug experiments."
            )
        if sample.get("input_uses_forecast_frame") is True and not self.allow_forecast_object_input:
            raise RuntimeError(
                "Sample declares input_uses_forecast_frame=true. "
                f"sample_id={sample.get('sample_id')}. "
                "Default object_metadata mode refuses forecast-frame input features."
            )

    def _selected_object_in_top_k(self, sample: dict[str, Any], top_candidates: list[dict[str, Any]]) -> bool:
        proxy = sample.get("target_object_proxy", {})
        if not isinstance(proxy, dict):
            return False
        selected = {
            "object_uid": proxy.get("selected_object_uid"),
            "object_bop_id": proxy.get("selected_object_bop_id"),
            "object_name": proxy.get("selected_object_name"),
            "object_group_key": proxy.get("selected_object_group_key"),
            "instance_index": proxy.get("selected_instance_index"),
        }
        selected_key = _candidate_identity_key(selected)
        return any(_candidate_identity_key(candidate) == selected_key for candidate in top_candidates)


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _extract_visible_object_candidates(
    objects_json: dict[str, Any],
    min_visibility: float,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    if not isinstance(objects_json, dict):
        return candidates

    for object_group_key, instances in objects_json.items():
        if not isinstance(instances, list):
            continue
        for instance_index, instance in enumerate(instances):
            if not isinstance(instance, dict):
                continue
            visibility = _max_visibility(instance)
            if visibility <= min_visibility:
                continue
            candidates.append(
                {
                    "object_group_key": str(object_group_key),
                    "instance_index": instance_index,
                    "object_uid": instance.get("object_uid"),
                    "object_bop_id": instance.get("object_bop_id"),
                    "object_name": instance.get("object_name"),
                    "visibility": visibility,
                    "visibilities_modeled": instance.get("visibilities_modeled", {}),
                    "boxes_amodal": instance.get("boxes_amodal", {}),
                    "has_pose": "T_world_from_object" in instance,
                    "T_world_from_object": instance.get("T_world_from_object"),
                }
            )
    return candidates


def _max_visibility(record: dict[str, Any]) -> float:
    values = record.get("visibilities_modeled", {})
    if isinstance(values, dict) and values:
        numeric = [_safe_float(value, default=0.0) for value in values.values()]
        return max(numeric) if numeric else 0.0
    return 0.0


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return number


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


def _candidate_identity_key(candidate: dict[str, Any]) -> tuple[str, str, str, str, int]:
    return (
        str(candidate.get("object_uid") or ""),
        str(candidate.get("object_bop_id") or ""),
        str(candidate.get("object_name") or ""),
        str(candidate.get("object_group_key") or ""),
        _safe_int(candidate.get("instance_index")),
    )


def _best_stream_score(candidate: dict[str, Any]) -> dict[str, Any]:
    stream_scores = candidate.get("stream_scores", [])
    if not isinstance(stream_scores, list) or not stream_scores:
        return {}
    dict_scores = [score for score in stream_scores if isinstance(score, dict)]
    if not dict_scores:
        return {}
    best_stream_id = str(candidate.get("best_stream_id") or "")
    for score in dict_scores:
        if str(score.get("stream_id") or "") == best_stream_id:
            return score
    return max(dict_scores, key=lambda score: _safe_float(score.get("proxy_score"), default=float("-inf")))


def _normalized_box_features(box: Any, stream_id: str) -> list[float]:
    parsed = _as_box(box)
    if parsed is None:
        return [0.0, 0.0, 0.0, 0.0]

    width, height = FALLBACK_IMAGE_SIZES.get(stream_id, (1, 1))
    x1, y1, x2, y2 = parsed
    box_width = max(0.0, x2 - x1)
    box_height = max(0.0, y2 - y1)
    center_x = x1 + box_width / 2.0
    center_y = y1 + box_height / 2.0
    return [
        center_x / max(1.0, float(width)),
        center_y / max(1.0, float(height)),
        box_width / max(1.0, float(width)),
        box_height / max(1.0, float(height)),
    ]


def _as_box(box: Any) -> tuple[float, float, float, float] | None:
    if isinstance(box, (list, tuple)) and len(box) == 4:
        try:
            x1, y1, x2, y2 = (float(value) for value in box)
        except (TypeError, ValueError):
            return None
        return (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

    if isinstance(box, dict):
        if all(key in box for key in ("x1", "y1", "x2", "y2")):
            return _as_box([box["x1"], box["y1"], box["x2"], box["y2"]])
        if all(key in box for key in ("xmin", "ymin", "xmax", "ymax")):
            return _as_box([box["xmin"], box["ymin"], box["xmax"], box["ymax"]])
        if all(key in box for key in ("x", "y", "width", "height")):
            return _as_box([box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"]])

    return None


def _image_to_tensor(image: np.ndarray, *, image_size: int) -> torch.Tensor:
    if image.ndim == 2:
        image = np.repeat(image[:, :, None], repeats=3, axis=2)
    elif image.shape[2] == 1:
        image = np.repeat(image, repeats=3, axis=2)
    resized = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
    tensor = torch.from_numpy(resized.copy()).permute(2, 0, 1).float() / 255.0
    return tensor
