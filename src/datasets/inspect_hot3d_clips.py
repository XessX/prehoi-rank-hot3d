"""Inspect HOT3D-Clips/WebDataset shards without training."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.datasets.hot3d_clips_loader import HOT3DClipsAdapter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect HOT3D-Clips tar shards safely.")
    parser.add_argument(
        "clips_root",
        type=Path,
        help="Path to a HOT3D-Clips root containing split folders or tar shards.",
    )
    parser.add_argument(
        "--max-shards",
        type=int,
        default=2,
        help="Maximum tar shards to inspect.",
    )
    parser.add_argument(
        "--max-samples",
        type=int,
        default=5,
        help="Maximum frame/sample keys to show per inspected shard.",
    )
    parser.add_argument(
        "--use-webdataset",
        action="store_true",
        help="Optionally try WebDataset iteration if webdataset is installed.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    adapter = HOT3DClipsAdapter(
        clips_root=args.clips_root.resolve(),
        max_shards_for_inspection=args.max_shards,
        max_samples_for_inspection=args.max_samples,
    )
    print(json.dumps(adapter.inspect(use_webdataset=args.use_webdataset), indent=2))


if __name__ == "__main__":
    main()

