"""Derived HOT3D-Clips proxy labels.

The utilities in this module create explicit proxy labels from annotation
geometry. They do not create direct action/contact ground truth.
"""

from __future__ import annotations

import math
from typing import Any


TARGET_OBJECT_PROXY_V1_RULE = "target_object_proxy_v1_hand_object_box_proximity"
FALLBACK_IMAGE_SIZES = {
    "214-1": (1408, 1408),
    "1201-1": (640, 480),
    "1201-2": (640, 480),
}


Box = tuple[float, float, float, float]


def _as_box(box: Any) -> Box | None:
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


def compute_iou(box_a: Any, box_b: Any) -> float:
    """Compute intersection-over-union for two xyxy boxes."""
    parsed_a = _as_box(box_a)
    parsed_b = _as_box(box_b)
    if parsed_a is None or parsed_b is None:
        return 0.0

    ax1, ay1, ax2, ay2 = parsed_a
    bx1, by1, bx2, by2 = parsed_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_width = max(0.0, inter_x2 - inter_x1)
    inter_height = max(0.0, inter_y2 - inter_y1)
    intersection = inter_width * inter_height
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - intersection
    if union <= 0.0:
        return 0.0
    return intersection / union


def box_center(box: Any) -> tuple[float, float] | None:
    """Return the center of an xyxy box."""
    parsed = _as_box(box)
    if parsed is None:
        return None
    x1, y1, x2, y2 = parsed
    return ((x1 + x2) / 2.0, (y1 + y2) / 2.0)


def normalized_center_distance(
    box_a: Any,
    box_b: Any,
    image_width: int | float,
    image_height: int | float,
) -> float:
    """Compute center distance normalized by image diagonal."""
    center_a = box_center(box_a)
    center_b = box_center(box_b)
    if center_a is None or center_b is None:
        return float("inf")

    diagonal = math.hypot(float(image_width), float(image_height))
    if diagonal <= 0.0:
        return float("inf")

    return math.hypot(center_a[0] - center_b[0], center_a[1] - center_b[1]) / diagonal


def union_boxes(boxes: list[Any]) -> list[float] | None:
    """Return the xyxy union of all valid boxes."""
    parsed = [_as_box(box) for box in boxes]
    valid_boxes = [box for box in parsed if box is not None]
    if not valid_boxes:
        return None
    x1 = min(box[0] for box in valid_boxes)
    y1 = min(box[1] for box in valid_boxes)
    x2 = max(box[2] for box in valid_boxes)
    y2 = max(box[3] for box in valid_boxes)
    return [x1, y1, x2, y2]


def score_object_candidates(
    hand_boxes: dict[str, list[Any]],
    object_boxes: dict[str, Any],
    image_size: dict[str, tuple[int, int]],
) -> dict[str, Any] | None:
    """Score one object against union hand boxes in all shared streams."""
    stream_scores: list[dict[str, Any]] = []

    for stream_id, boxes_for_stream in sorted(hand_boxes.items()):
        if stream_id not in object_boxes:
            continue
        hand_union = union_boxes(boxes_for_stream)
        object_box = _as_box(object_boxes[stream_id])
        if hand_union is None or object_box is None:
            continue

        width, height = image_size.get(stream_id, FALLBACK_IMAGE_SIZES.get(stream_id, (1, 1)))
        iou = compute_iou(hand_union, object_box)
        distance = normalized_center_distance(hand_union, object_box, width, height)
        if not math.isfinite(distance):
            continue

        distance_clipped = max(0.0, min(1.0, distance))
        stream_score = iou - distance_clipped
        stream_confidence = max(iou, 1.0 - distance_clipped)
        stream_scores.append(
            {
                "stream_id": stream_id,
                "hand_box_union": hand_union,
                "object_box": list(object_box),
                "iou": iou,
                "normalized_center_distance": distance,
                "proxy_score": stream_score,
                "proxy_confidence": max(0.0, min(1.0, stream_confidence)),
            }
        )

    if not stream_scores:
        return None

    best_stream = max(stream_scores, key=lambda item: item["proxy_score"])
    return {
        "proxy_score": best_stream["proxy_score"],
        "proxy_confidence": best_stream["proxy_confidence"],
        "best_stream_id": best_stream["stream_id"],
        "best_iou": best_stream["iou"],
        "best_normalized_center_distance": best_stream["normalized_center_distance"],
        "stream_scores": stream_scores,
    }


def select_target_object_proxy(sample_or_frame_data: dict[str, Any]) -> dict[str, Any]:
    """Select a derived object proxy from one frame's hand-object box proximity.

    The caller decides whether that frame is a forecast target frame or an
    observation input frame. Do not feed scores from a forecast frame into a
    pre-contact forecasting model.
    """
    hands_json = sample_or_frame_data.get("hands_json") or sample_or_frame_data.get("hands") or {}
    candidates = sample_or_frame_data.get("target_object_candidates") or []
    cameras_json = sample_or_frame_data.get("cameras_json") or sample_or_frame_data.get("cameras") or {}
    min_visibility = float(sample_or_frame_data.get("min_visibility", 0.0))

    hand_boxes = _collect_visible_hand_boxes(hands_json, min_visibility=min_visibility)
    if not hand_boxes:
        return {
            "rule": TARGET_OBJECT_PROXY_V1_RULE,
            "assigned": False,
            "reason": "missing_visible_hand_boxes",
            "candidate_scores": [],
        }

    image_sizes = _extract_image_sizes(cameras_json)
    scored_candidates: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        object_boxes = candidate.get("boxes_amodal", {})
        if not isinstance(object_boxes, dict) or not object_boxes:
            continue
        score = score_object_candidates(hand_boxes, object_boxes, image_sizes)
        if score is None:
            continue
        scored_candidates.append(
            {
                "object_uid": candidate.get("object_uid"),
                "object_bop_id": candidate.get("object_bop_id"),
                "object_name": candidate.get("object_name"),
                "object_group_key": candidate.get("object_group_key"),
                "instance_index": candidate.get("instance_index"),
                "visibility": candidate.get("visibility"),
                **score,
            }
        )

    if not scored_candidates:
        return {
            "rule": TARGET_OBJECT_PROXY_V1_RULE,
            "assigned": False,
            "reason": "missing_shared_hand_object_boxes",
            "candidate_scores": [],
        }

    scored_candidates.sort(key=lambda item: item["proxy_score"], reverse=True)
    selected = scored_candidates[0]
    return {
        "rule": TARGET_OBJECT_PROXY_V1_RULE,
        "assigned": True,
        "selected_object_uid": selected.get("object_uid"),
        "selected_object_bop_id": selected.get("object_bop_id"),
        "selected_object_name": selected.get("object_name"),
        "selected_object_group_key": selected.get("object_group_key"),
        "selected_instance_index": selected.get("instance_index"),
        "proxy_score": selected["proxy_score"],
        "proxy_confidence": selected["proxy_confidence"],
        "best_stream_id": selected["best_stream_id"],
        "candidate_scores": scored_candidates,
        "label_status": "derived_proxy_not_direct_ground_truth",
    }


def _collect_visible_hand_boxes(hands_json: dict[str, Any], *, min_visibility: float) -> dict[str, list[Any]]:
    hand_boxes: dict[str, list[Any]] = {}
    if not isinstance(hands_json, dict):
        return hand_boxes

    for hand_record in hands_json.values():
        if not isinstance(hand_record, dict):
            continue
        boxes = hand_record.get("boxes_amodal", {})
        if not isinstance(boxes, dict):
            continue
        stream_visibilities = hand_record.get("visibilities_modeled", {})
        for stream_id, box in boxes.items():
            if isinstance(stream_visibilities, dict) and stream_id in stream_visibilities:
                visibility = stream_visibilities.get(stream_id)
                if isinstance(visibility, (int, float)) and float(visibility) <= min_visibility:
                    continue
            if _as_box(box) is None:
                continue
            hand_boxes.setdefault(str(stream_id), []).append(box)

    return hand_boxes


def _extract_image_sizes(cameras_json: dict[str, Any]) -> dict[str, tuple[int, int]]:
    sizes = dict(FALLBACK_IMAGE_SIZES)
    if not isinstance(cameras_json, dict):
        return sizes

    for stream_id, camera_record in cameras_json.items():
        if not isinstance(camera_record, dict):
            continue
        calibration = camera_record.get("calibration", {})
        if not isinstance(calibration, dict):
            continue
        width = calibration.get("image_width")
        height = calibration.get("image_height")
        if isinstance(width, (int, float)) and isinstance(height, (int, float)):
            sizes[str(stream_id)] = (int(width), int(height))

    return sizes
