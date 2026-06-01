"""Observation-frame image stream selection for HOT3D-Clips."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


PREFERRED_STREAM = "image_214-1"
STREAM_SPECS = {
    "image_214-1": {"width": 1408, "height": 1408, "channels": 3, "priority": 0},
    "image_1201-1": {"width": 640, "height": 480, "channels": 1, "priority": 10},
    "image_1201-2": {"width": 640, "height": 480, "channels": 1, "priority": 11},
}
FRAME_MEMBER_RE = re.compile(r"^(?P<frame_id>\d{1,8})\.(?P<key>.+)$")


def available_image_streams(sample: dict[str, Any]) -> dict[str, list[str]]:
    """Return image streams that contain observation-frame member names."""
    streams = sample.get("image_streams", {})
    if not isinstance(streams, dict):
        return {}

    available: dict[str, list[str]] = {}
    observation_ids = {_normalize_frame_id(frame_id) for frame_id in sample.get("observation_frame_ids", [])}
    forecast_id = _normalize_frame_id(sample.get("forecast_frame_id"))
    for stream_name, members in streams.items():
        if not str(stream_name).startswith("image_") or not isinstance(members, list):
            continue
        member_names = [str(member) for member in members if isinstance(member, str)]
        if not member_names:
            continue
        member_frame_ids = {_frame_id_from_member(member) for member in member_names}
        member_frame_ids.discard(None)
        if forecast_id and forecast_id in member_frame_ids:
            raise ValueError(
                f"Image stream {stream_name} includes forecast frame {forecast_id}; "
                f"sample_id={sample.get('sample_id')}"
            )
        if observation_ids and not member_frame_ids.issubset(observation_ids):
            raise ValueError(
                f"Image stream {stream_name} includes non-observation frames; "
                f"sample_id={sample.get('sample_id')}"
            )
        available[str(stream_name)] = member_names
    return available


def choose_image_stream(sample: dict[str, Any], requested_stream: str = "auto") -> dict[str, Any]:
    """Choose a leakage-safe observation image stream for one sample."""
    streams = available_image_streams(sample)
    if not streams:
        raise ValueError(f"No observation image streams found for sample {sample.get('sample_id')}")

    if requested_stream != "auto":
        if requested_stream not in streams:
            raise ValueError(
                f"Requested stream {requested_stream} not available for sample {sample.get('sample_id')}. "
                f"Available streams: {sorted(streams)}"
            )
        return {
            "stream": requested_stream,
            "member_names": streams[requested_stream],
            "reason": "requested_stream",
        }

    if PREFERRED_STREAM in streams:
        return {
            "stream": PREFERRED_STREAM,
            "member_names": streams[PREFERRED_STREAM],
            "reason": "preferred_rgb_aria_stream",
        }

    ranked = sorted(
        streams,
        key=lambda stream: (
            -_stream_area(stream),
            -_stream_channels(stream),
            _stream_priority(stream),
            stream,
        ),
    )
    selected = ranked[0]
    return {
        "stream": selected,
        "member_names": streams[selected],
        "reason": "largest_consistent_observation_stream",
    }


def selected_stream_name(sample: dict[str, Any], requested_stream: str = "auto") -> str:
    return str(choose_image_stream(sample, requested_stream=requested_stream)["stream"])


def _stream_area(stream: str) -> int:
    spec = STREAM_SPECS.get(stream, {})
    return int(spec.get("width", 1)) * int(spec.get("height", 1))


def _stream_channels(stream: str) -> int:
    spec = STREAM_SPECS.get(stream, {})
    if "channels" in spec:
        return int(spec["channels"])
    return 3 if any(token in stream.lower() for token in ("rgb", "214")) else 1


def _stream_priority(stream: str) -> int:
    spec = STREAM_SPECS.get(stream, {})
    return int(spec.get("priority", 100))


def _frame_id_from_member(member_name: str) -> str | None:
    match = FRAME_MEMBER_RE.match(Path(member_name).name)
    if not match:
        return None
    return _normalize_frame_id(match.group("frame_id"))


def _normalize_frame_id(frame_id: Any) -> str:
    if frame_id is None:
        return ""
    try:
        return str(frame_id).zfill(6)
    except (TypeError, ValueError):
        return str(frame_id)
