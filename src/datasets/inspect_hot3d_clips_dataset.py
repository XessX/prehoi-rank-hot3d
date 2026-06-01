"""Inspect HOT3D-Clips PyTorch dataset outputs without training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import torch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import DEFAULT_LABEL_MAP_PATH, HOT3DClipsDataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HOT3D-Clips Dataset v1.")
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--mode", choices=("metadata_only", "image"), default="metadata_only")
    parser.add_argument("--clips-root", type=Path, default=None)
    parser.add_argument("--label-map", type=Path, default=DEFAULT_LABEL_MAP_PATH)
    parser.add_argument("--hand-selection", choices=("left", "right", "both"), default="both")
    parser.add_argument("--image-stream", default="auto")
    parser.add_argument("--image-size", type=int, default=224)
    parser.add_argument("--batch-size", type=int, default=2)
    return parser.parse_args()


def tensor_shape(value: Any) -> list[int] | None:
    if isinstance(value, torch.Tensor):
        return list(value.shape)
    return None


def preview_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": item["sample_id"],
        "clip_id": item["clip_id"],
        "target_object_label": int(item["target_object_label"].item()),
        "target_object_name": item["target_object_name"],
        "proxy_confidence": round(float(item["proxy_confidence"].item()), 6),
        "features_shape": tensor_shape(item["features"]),
        "frame_features_shape": tensor_shape(item["frame_features"]),
        "frames_shape": tensor_shape(item.get("frames")),
        "future_hand_pose_shape": tensor_shape(item["future_hand_pose"]),
        "metadata": item["metadata"],
        "proxy_label_status": item["proxy_label_status"],
    }


def collate_preview(items: list[dict[str, Any]]) -> dict[str, Any]:
    tensor_keys = ("features", "frame_features", "future_hand_pose", "target_object_label", "proxy_confidence")
    if "frames" in items[0]:
        tensor_keys = (*tensor_keys, "frames")
    batch_shapes: dict[str, list[int]] = {}
    for key in tensor_keys:
        try:
            batch_shapes[key] = list(torch.stack([item[key] for item in items], dim=0).shape)
        except RuntimeError:
            batch_shapes[key] = ["variable"]  # type: ignore[list-item]
    return {
        "batch_size": len(items),
        "batch_tensor_shapes": batch_shapes,
        "sample_ids": [item["sample_id"] for item in items],
        "clip_ids": [item["clip_id"] for item in items],
        "target_object_names": [item["target_object_name"] for item in items],
        "proxy_confidences": [round(float(item["proxy_confidence"].item()), 6) for item in items],
    }


def main() -> None:
    args = parse_args()
    dataset = HOT3DClipsDataset(
        args.index,
        mode=args.mode,
        clips_root=args.clips_root,
        label_map_path=args.label_map,
        hand_selection=args.hand_selection,
        image_stream=args.image_stream,
        image_size=args.image_size,
    )
    preview_count = min(args.batch_size, len(dataset))
    preview_items = [dataset[index] for index in range(preview_count)]

    summary = {
        "dataset_summary": dataset.summary(),
        "label_map": dataset.label_map,
        "first_item_previews": [preview_item(item) for item in preview_items],
        "first_batch_preview": collate_preview(preview_items) if preview_items else {},
        "note": "Dataset inspection only. No training was run and proxy labels are not direct ground truth.",
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
