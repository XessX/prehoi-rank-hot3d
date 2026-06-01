"""Inspect cached HOT3D-Clips visual feature files."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a HOT3D-Clips visual feature .npz file.")
    parser.add_argument("feature_file", type=Path)
    parser.add_argument("--max-samples", type=int, default=5)
    return parser.parse_args()


def load_metadata(npz: Any) -> dict[str, Any]:
    raw = npz.get("metadata_json")
    if raw is None:
        return {}
    value = raw.item() if hasattr(raw, "item") else raw
    try:
        return json.loads(str(value))
    except json.JSONDecodeError:
        return {"metadata_json": str(value)}


def main() -> None:
    args = parse_args()
    if not args.feature_file.exists():
        raise FileNotFoundError(f"Feature file not found: {args.feature_file}")

    with np.load(args.feature_file, allow_pickle=True) as npz:
        features = npz["features"]
        sample_ids = npz["sample_ids"]
        selected_streams = npz["selected_streams"]
        missing_images = npz.get("missing_images_per_sample")
        metadata = load_metadata(npz)

        missing_image_count = (
            int(np.sum(missing_images))
            if missing_images is not None
            else int(metadata.get("missing_image_count", 0))
        )
        stream_distribution = Counter(str(stream) for stream in selected_streams.tolist())
        feature_min = float(np.min(features)) if features.size else 0.0
        feature_max = float(np.max(features)) if features.size else 0.0

        summary = {
            "feature_file": str(args.feature_file),
            "num_samples": int(features.shape[0]),
            "feature_tensor_shape": list(features.shape),
            "sample_ids": [str(item) for item in sample_ids[: args.max_samples].tolist()],
            "selected_stream_distribution": dict(stream_distribution.most_common()),
            "missing_image_count": missing_image_count,
            "feature_min": feature_min,
            "feature_max": feature_max,
            "metadata": metadata,
        }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
