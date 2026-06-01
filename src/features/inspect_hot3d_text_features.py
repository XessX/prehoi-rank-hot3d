"""Inspect cached HOT3D object text feature files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect a HOT3D object text feature .npz file.")
    parser.add_argument("feature_file", type=Path)
    parser.add_argument("--max-objects", type=int, default=5)
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
        raise FileNotFoundError(f"Text feature file not found: {args.feature_file}")

    with np.load(args.feature_file, allow_pickle=True) as npz:
        object_names = [str(item) for item in npz["object_names"].tolist()]
        prompts = npz["prompts"]
        text_features = npz["text_features"]
        metadata = load_metadata(npz)

        preview_prompts = []
        for index, object_name in enumerate(object_names[: args.max_objects]):
            prompt_values = prompts[index].tolist() if prompts.ndim >= 2 else []
            preview_prompts.append(
                {
                    "object_name": object_name,
                    "prompts": [str(prompt) for prompt in prompt_values],
                }
            )

        summary = {
            "feature_file": str(args.feature_file),
            "num_object_classes": len(object_names),
            "text_feature_shape": list(text_features.shape),
            "feature_dim": int(text_features.shape[-1]) if text_features.ndim >= 1 else 0,
            "feature_mean": float(np.mean(text_features)) if text_features.size else 0.0,
            "feature_std": float(np.std(text_features)) if text_features.size else 0.0,
            "nan_count": int(np.isnan(text_features).sum()) if text_features.size else 0,
            "object_names_preview": object_names[: args.max_objects],
            "prompt_preview": preview_prompts,
            "metadata": metadata,
        }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
