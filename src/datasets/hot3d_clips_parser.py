"""Low-level HOT3D-Clips tar parsing helpers.

These functions are intentionally small and side-effect free so they can be
used by inspectors, reports, and later dataset adapters. They do not create
labels or training samples.
"""

from __future__ import annotations

import io
import json
import re
import tarfile
from pathlib import Path
from typing import Any

import cv2
import numpy as np


FRAME_MEMBER_RE = re.compile(r"^(?P<frame_id>\d{1,8})\.(?P<key>.+)$")
OFFICIAL_SPLIT_DIRS = ("train_aria", "train_quest3", "test_aria", "test_quest3")


def list_shards(root: str | Path) -> list[Path]:
    """List HOT3D-Clips tar shards under a root, preferring official split folders."""
    root = Path(root)
    shards: list[Path] = []
    for split_dir in OFFICIAL_SPLIT_DIRS:
        split_path = root / split_dir
        if split_path.exists():
            shards.extend(sorted(split_path.glob("*.tar")))
    return shards if shards else sorted(root.rglob("*.tar")) if root.exists() else []


def list_frame_ids_from_tar(tar_path: str | Path) -> list[str]:
    """Return sorted frame IDs found in a HOT3D-Clips tar."""
    frame_ids: set[str] = set()
    with tarfile.open(tar_path, mode="r") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            match = FRAME_MEMBER_RE.match(Path(member.name).name)
            if match:
                frame_ids.add(match.group("frame_id"))
    return sorted(frame_ids)


def get_frame_member_names(frame_id: str) -> dict[str, str]:
    """Return official member names for a frame ID."""
    frame_id = str(frame_id).zfill(6)
    return {
        "cameras": f"{frame_id}.cameras.json",
        "hands": f"{frame_id}.hands.json",
        "hand_crops": f"{frame_id}.hand_crops.json",
        "objects": f"{frame_id}.objects.json",
        "info": f"{frame_id}.info.json",
        "image_214-1": f"{frame_id}.image_214-1.jpg",
        "image_1201-1": f"{frame_id}.image_1201-1.jpg",
        "image_1201-2": f"{frame_id}.image_1201-2.jpg",
    }


def list_frame_keys_from_tar(tar_path: str | Path, frame_id: str) -> list[str]:
    """List available keys/extensions for one frame ID."""
    frame_id = str(frame_id).zfill(6)
    keys: list[str] = []
    with tarfile.open(tar_path, mode="r") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            match = FRAME_MEMBER_RE.match(Path(member.name).name)
            if match and match.group("frame_id") == frame_id:
                keys.append(match.group("key"))
    return sorted(keys)


def read_json_member(tar_path: str | Path, member_name: str) -> Any:
    """Read a JSON member from a tar file."""
    with tarfile.open(tar_path, mode="r") as tar:
        file_obj = tar.extractfile(member_name)
        if file_obj is None:
            raise FileNotFoundError(f"Tar member not found or not a file: {member_name}")
        return json.load(file_obj)


def read_image_member(tar_path: str | Path, member_name: str) -> np.ndarray:
    """Read an image member from a tar file as an RGB numpy array."""
    with tarfile.open(tar_path, mode="r") as tar:
        file_obj = tar.extractfile(member_name)
        if file_obj is None:
            raise FileNotFoundError(f"Tar member not found or not a file: {member_name}")
        data = np.frombuffer(file_obj.read(), dtype=np.uint8)
    image_bgr = cv2.imdecode(data, cv2.IMREAD_UNCHANGED)
    if image_bgr is None:
        raise ValueError(f"Could not decode image member: {member_name}")
    if image_bgr.ndim == 2:
        return image_bgr
    return cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)


def get_member_sizes(tar_path: str | Path, member_names: list[str]) -> dict[str, int | None]:
    """Return sizes in bytes for selected tar members."""
    with tarfile.open(tar_path, mode="r") as tar:
        info_by_name = {member.name: member for member in tar.getmembers() if member.isfile()}
    return {
        member_name: info_by_name[member_name].size if member_name in info_by_name else None
        for member_name in member_names
    }


def count_tar_members(tar_path: str | Path) -> int:
    """Count file members in a tar file."""
    with tarfile.open(tar_path, mode="r") as tar:
        return sum(1 for member in tar.getmembers() if member.isfile())


def summarize_json_structure(
    obj: Any,
    *,
    max_depth: int = 5,
    max_items: int = 4,
    max_string: int = 120,
) -> Any:
    """Summarize JSON structure with types and short examples.

    Arrays and long strings are deliberately truncated so reports do not dump
    masks, model weights, or long pose arrays.
    """
    return _summarize_json_structure(
        obj=obj,
        depth=0,
        max_depth=max_depth,
        max_items=max_items,
        max_string=max_string,
    )


def _summarize_json_structure(
    obj: Any,
    *,
    depth: int,
    max_depth: int,
    max_items: int,
    max_string: int,
) -> Any:
    if depth >= max_depth:
        return {"type": type(obj).__name__, "summary": "max_depth_reached"}

    if isinstance(obj, dict):
        keys = list(obj.keys())
        shown_keys = keys[:max_items]
        return {
            "type": "dict",
            "num_keys": len(keys),
            "keys": {
                str(key): _summarize_json_structure(
                    obj=obj[key],
                    depth=depth + 1,
                    max_depth=max_depth,
                    max_items=max_items,
                    max_string=max_string,
                )
                for key in shown_keys
            },
            "truncated_keys": max(0, len(keys) - len(shown_keys)),
        }

    if isinstance(obj, list):
        shown_items = obj[:max_items]
        numeric = all(isinstance(item, (int, float)) and not isinstance(item, bool) for item in obj)
        payload: dict[str, Any] = {
            "type": "list",
            "length": len(obj),
            "items": [
                _summarize_json_structure(
                    obj=item,
                    depth=depth + 1,
                    max_depth=max_depth,
                    max_items=max_items,
                    max_string=max_string,
                )
                for item in shown_items
            ],
            "truncated_items": max(0, len(obj) - len(shown_items)),
        }
        if numeric and obj:
            payload["numeric_min"] = min(obj)
            payload["numeric_max"] = max(obj)
        return payload

    if isinstance(obj, str):
        value = obj if len(obj) <= max_string else obj[:max_string] + "..."
        return {"type": "str", "example": value}

    if isinstance(obj, bool):
        return {"type": "bool", "example": obj}

    if obj is None:
        return {"type": "null", "example": None}

    if isinstance(obj, (int, float)):
        return {"type": type(obj).__name__, "example": obj}

    return {"type": type(obj).__name__, "example": repr(obj)[:max_string]}


def image_shape_summary(image: np.ndarray) -> dict[str, Any]:
    """Return JSON-friendly image shape metadata."""
    return {
        "height": int(image.shape[0]),
        "width": int(image.shape[1]),
        "channels": 1 if image.ndim == 2 else int(image.shape[2]),
        "dtype": str(image.dtype),
    }

