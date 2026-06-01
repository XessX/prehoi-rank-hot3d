"""Check HOT3D-Clips clip-level split quality before any training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_dataset import class_distribution, load_index_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check HOT3D-Clips train/val/test split quality.")
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--val", type=Path, required=True)
    parser.add_argument("--test", type=Path, required=True)
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--min-train-samples", type=int, default=20)
    return parser.parse_args()


def load_label_map(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Label map not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected label map JSON object: {path}")
    return payload


def split_info(path: Path) -> dict[str, Any]:
    payload = load_index_payload(path)
    samples = [sample for sample in payload["samples"] if isinstance(sample, dict)]
    metadata = payload.get("metadata", {})
    clip_ids = metadata.get("clip_ids", []) if isinstance(metadata, dict) else []
    if not isinstance(clip_ids, list):
        clip_ids = sorted({str(sample.get("clip_id")) for sample in samples})
    distribution = class_distribution(samples)
    return {
        "path": str(path),
        "sample_count": len(samples),
        "clip_count": len(set(str(clip_id) for clip_id in clip_ids)),
        "clip_ids": [str(clip_id) for clip_id in clip_ids],
        "class_distribution": distribution,
        "classes": set(distribution),
    }


def missing_classes(all_classes: set[str], present: set[str]) -> list[str]:
    return sorted(all_classes - present)


def underrepresented_train_classes(distribution: dict[str, int], min_samples: int) -> dict[str, int]:
    return {label: count for label, count in sorted(distribution.items()) if count < min_samples}


def build_quality_report(args: argparse.Namespace) -> dict[str, Any]:
    label_map = load_label_map(args.label_map)
    label_classes = label_map.get("classes", [])
    if not isinstance(label_classes, list):
        label_classes = list(label_map.get("class_to_idx", {}).keys())
    all_classes = {str(label) for label in label_classes}

    splits = {
        "train": split_info(args.train),
        "val": split_info(args.val),
        "test": split_info(args.test),
    }
    if not all_classes:
        all_classes = set().union(*(info["classes"] for info in splits.values()))

    train_classes = splits["train"]["classes"]
    val_classes = splits["val"]["classes"]
    test_classes = splits["test"]["classes"]

    warnings: list[str] = []
    val_absent_from_train = sorted(val_classes - train_classes)
    test_absent_from_train = sorted(test_classes - train_classes)
    if val_absent_from_train:
        warnings.append(
            "Validation contains classes absent from train: " + ", ".join(val_absent_from_train)
        )
    if test_absent_from_train:
        warnings.append("Test contains classes absent from train: " + ", ".join(test_absent_from_train))

    low_train = underrepresented_train_classes(
        splits["train"]["class_distribution"],
        min_samples=args.min_train_samples,
    )
    if low_train:
        warnings.append(
            f"Train has classes below {args.min_train_samples} samples: "
            + ", ".join(f"{label}={count}" for label, count in low_train.items())
        )

    if missing_classes(all_classes, train_classes):
        warnings.append("Train is missing classes: " + ", ".join(missing_classes(all_classes, train_classes)))
    if missing_classes(all_classes, val_classes):
        warnings.append("Val is missing classes: " + ", ".join(missing_classes(all_classes, val_classes)))
    if missing_classes(all_classes, test_classes):
        warnings.append("Test is missing classes: " + ", ".join(missing_classes(all_classes, test_classes)))

    if val_absent_from_train or test_absent_from_train or missing_classes(all_classes, train_classes):
        recommendation = (
            "Do not train target-object prediction yet. Download more clips or filter to classes "
            "represented in train/val/test."
        )
    elif low_train or missing_classes(all_classes, val_classes) or missing_classes(all_classes, test_classes):
        recommendation = (
            "Usable only for a debug/pilot run. For scientifically safer evaluation, download more clips "
            "or filter to classes with enough train samples and validation/test coverage."
        )
    else:
        recommendation = (
            "Split looks usable for a debug/pilot run; proxy labels remain derived labels, not direct ground truth."
        )

    return {
        "label_map_path": str(args.label_map),
        "num_classes": len(all_classes),
        "classes": sorted(all_classes),
        "sample_count_per_split": {name: info["sample_count"] for name, info in splits.items()},
        "clip_count_per_split": {name: info["clip_count"] for name, info in splits.items()},
        "clip_ids_per_split": {name: info["clip_ids"] for name, info in splits.items()},
        "object_class_distribution_per_split": {
            name: info["class_distribution"] for name, info in splits.items()
        },
        "classes_missing_from_train": missing_classes(all_classes, train_classes),
        "classes_missing_from_val": missing_classes(all_classes, val_classes),
        "classes_missing_from_test": missing_classes(all_classes, test_classes),
        "classes_with_fewer_than_min_train_samples": low_train,
        "min_train_samples": args.min_train_samples,
        "warnings": warnings,
        "recommendation": recommendation,
        "label_status": "target-object labels are derived proxies, not direct HOT3D ground truth",
        "note": "Quality check only. No training was run.",
    }


def main() -> None:
    args = parse_args()
    report = build_quality_report(args)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
