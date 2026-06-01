"""Extract cached visual features from observation frames only."""

from __future__ import annotations

import argparse
import json
import sys
import tarfile
from collections import Counter
from pathlib import Path
from typing import Any

import cv2
import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import load_index_payload
from src.datasets.hot3d_stream_selection import choose_image_stream

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover
    tqdm = None


IMAGE_STATS_FEATURE_NAMES = (
    "mean_r",
    "mean_g",
    "mean_b",
    "std_r",
    "std_g",
    "std_b",
    "min_r",
    "min_g",
    "min_b",
    "max_r",
    "max_g",
    "max_b",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract cached HOT3D-Clips visual features.")
    parser.add_argument("--index", type=Path, required=True, help="Split/index JSON file.")
    parser.add_argument("--output", type=Path, required=True, help="Output .npz feature cache.")
    parser.add_argument("--feature-type", choices=("image_stats", "clip"), default="image_stats")
    parser.add_argument("--clips-root", type=Path, default=None, help="Override HOT3D-Clips root.")
    parser.add_argument("--stream", default="auto", help="Image stream name or auto.")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--max-samples", type=int, default=0, help="Optional debug sample limit.")
    return parser.parse_args()


class TarImageStatsReader:
    """Read images from tar shards and cache per-frame statistics."""

    def __init__(self, image_size: int) -> None:
        self.image_size = int(image_size)
        self._tar_handles: dict[Path, tarfile.TarFile] = {}
        self._feature_cache: dict[tuple[Path, str], np.ndarray] = {}

    def close(self) -> None:
        for handle in self._tar_handles.values():
            handle.close()
        self._tar_handles.clear()

    def read_feature(self, shard_path: Path, member_name: str) -> np.ndarray:
        key = (shard_path, member_name)
        if key in self._feature_cache:
            return self._feature_cache[key]

        tar = self._tar_handles.get(shard_path)
        if tar is None:
            tar = tarfile.open(shard_path, mode="r")
            self._tar_handles[shard_path] = tar

        file_obj = tar.extractfile(member_name)
        if file_obj is None:
            raise FileNotFoundError(f"Tar member not found: {member_name}")
        encoded = np.frombuffer(file_obj.read(), dtype=np.uint8)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_UNCHANGED)
        if decoded is None:
            raise ValueError(f"Could not decode image member: {member_name}")

        feature = image_stats_feature(decoded, image_size=self.image_size)
        self._feature_cache[key] = feature
        return feature


def image_stats_feature(image: np.ndarray, *, image_size: int) -> np.ndarray:
    """Return mean/std/min/max RGB-like features after resizing."""
    if image.ndim == 2:
        image = np.repeat(image[:, :, None], repeats=3, axis=2)
    elif image.shape[2] == 1:
        image = np.repeat(image, repeats=3, axis=2)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    resized = cv2.resize(image, (image_size, image_size), interpolation=cv2.INTER_AREA)
    normalized = resized.astype(np.float32) / 255.0
    return np.concatenate(
        [
            normalized.mean(axis=(0, 1)),
            normalized.std(axis=(0, 1)),
            normalized.min(axis=(0, 1)),
            normalized.max(axis=(0, 1)),
        ]
    ).astype(np.float32)


def resolve_clips_root(payload: dict[str, Any], override: Path | None) -> Path:
    if override is not None:
        return override
    metadata = payload.get("metadata", {})
    if isinstance(metadata, dict) and metadata.get("root"):
        return Path(str(metadata["root"]))
    return Path("data/raw/hot3d_clips")


def shard_path_for_sample(root: Path, sample: dict[str, Any]) -> Path:
    shard = str(sample.get("shard", "")).replace("\\", "/")
    path = root / Path(shard)
    if not path.exists():
        raise FileNotFoundError(f"Shard not found for sample {sample.get('sample_id')}: {path}")
    return path


def extract_image_stats_features(args: argparse.Namespace) -> dict[str, Any]:
    payload = load_index_payload(args.index)
    samples = [sample for sample in payload["samples"] if isinstance(sample, dict)]
    if args.max_samples > 0:
        samples = samples[: args.max_samples]
    if not samples:
        raise RuntimeError(f"No samples found in index: {args.index}")

    root = resolve_clips_root(payload, args.clips_root)
    observation_length = len(samples[0].get("observation_frame_ids", []))
    feature_dim = len(IMAGE_STATS_FEATURE_NAMES)
    features = np.zeros((len(samples), observation_length, feature_dim), dtype=np.float32)
    sample_ids = np.empty((len(samples),), dtype=object)
    selected_streams = np.empty((len(samples),), dtype=object)
    missing_images_per_sample = np.zeros((len(samples),), dtype=np.int32)
    stream_counts: Counter[str] = Counter()
    missing_image_count = 0

    reader = TarImageStatsReader(image_size=args.image_size)
    iterator = enumerate(samples)
    if tqdm is not None:
        iterator = tqdm(iterator, total=len(samples), desc=f"extract {args.feature_type}")  # type: ignore[assignment]

    try:
        for sample_index, sample in iterator:
            sample_id = str(sample.get("sample_id"))
            sample_ids[sample_index] = sample_id
            selection = choose_image_stream(sample, requested_stream=args.stream)
            stream = str(selection["stream"])
            selected_streams[sample_index] = stream
            stream_counts[stream] += 1
            member_names = list(selection["member_names"])
            shard_path = shard_path_for_sample(root, sample)

            if len(member_names) != observation_length:
                missing = abs(observation_length - len(member_names))
                missing_image_count += missing
                missing_images_per_sample[sample_index] += missing

            for frame_index, member_name in enumerate(member_names[:observation_length]):
                try:
                    features[sample_index, frame_index] = reader.read_feature(shard_path, str(member_name))
                except (FileNotFoundError, ValueError) as exc:
                    missing_image_count += 1
                    missing_images_per_sample[sample_index] += 1
                    print(f"warning: {exc}", file=sys.stderr)
    finally:
        reader.close()

    metadata = {
        "feature_type": args.feature_type,
        "index": str(args.index),
        "clips_root": str(root),
        "num_samples": len(samples),
        "feature_shape": list(features.shape),
        "feature_names": list(IMAGE_STATS_FEATURE_NAMES),
        "image_size": args.image_size,
        "stream_request": args.stream,
        "selected_stream_distribution": dict(stream_counts.most_common()),
        "missing_image_count": int(missing_image_count),
        "note": "Features are extracted from observation-frame images only. No forecast-frame images are used.",
    }
    return {
        "features": features,
        "sample_ids": sample_ids,
        "selected_streams": selected_streams,
        "missing_images_per_sample": missing_images_per_sample,
        "metadata": metadata,
    }


def main() -> None:
    args = parse_args()
    if args.feature_type != "image_stats":
        raise NotImplementedError("Only image_stats extraction is implemented for the CPU-safe MVP path.")
    if args.image_size <= 0:
        raise ValueError("--image-size must be positive.")

    payload = extract_image_stats_features(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        features=payload["features"],
        sample_ids=payload["sample_ids"],
        selected_streams=payload["selected_streams"],
        missing_images_per_sample=payload["missing_images_per_sample"],
        metadata_json=json.dumps(payload["metadata"], sort_keys=True),
    )
    print(json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()
