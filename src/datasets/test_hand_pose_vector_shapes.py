"""Audit current HOT3D-Clips future hand-pose vector targets."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_OUTPUT = Path("paper/hand_pose_vector_target_report.md")
HAND_ORDER = ("left", "right")
MANO_THETA_DIM = 15
MANO_WRIST_DIM = 6


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit future hand-pose vector target shapes.")
    parser.add_argument("--index", type=Path, required=True, help="HOT3D-Clips sample index JSON.")
    parser.add_argument("--max-samples", type=int, default=20)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def load_samples(index_path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with index_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    samples = [sample for sample in payload.get("samples", []) if isinstance(sample, dict)]
    return payload, samples


def numeric_list(value: Any, max_len: int) -> list[float]:
    if not isinstance(value, list):
        return []
    numbers: list[float] = []
    for item in value[:max_len]:
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            numbers.append(float(item))
    return numbers


def pad_or_trim(values: list[float], length: int) -> list[float]:
    if len(values) >= length:
        return values[:length]
    return values + [0.0] * (length - len(values))


def mano_vector_for_hand(sample: dict[str, Any], hand: str) -> tuple[list[float], dict[str, Any]]:
    hand_record = sample.get("future_hand_pose", {}).get(hand)
    detail: dict[str, Any] = {
        "hand": hand,
        "present": isinstance(hand_record, dict),
        "source": None,
        "theta_len": 0,
        "wrist_xform_len": 0,
        "used_dim": MANO_THETA_DIM + MANO_WRIST_DIM,
        "missing_or_padded": False,
    }
    if not isinstance(hand_record, dict):
        detail["missing_or_padded"] = True
        return [0.0] * (MANO_THETA_DIM + MANO_WRIST_DIM), detail

    detail["source"] = hand_record.get("source")
    payload = hand_record.get("payload", {})
    if not isinstance(payload, dict):
        detail["missing_or_padded"] = True
        return [0.0] * (MANO_THETA_DIM + MANO_WRIST_DIM), detail

    theta_raw = payload.get("thetas")
    wrist_raw = payload.get("wrist_xform")
    detail["theta_len"] = len(theta_raw) if isinstance(theta_raw, list) else 0
    detail["wrist_xform_len"] = len(wrist_raw) if isinstance(wrist_raw, list) else 0
    thetas = numeric_list(theta_raw, MANO_THETA_DIM)
    wrist = numeric_list(wrist_raw, MANO_WRIST_DIM)
    detail["missing_or_padded"] = len(thetas) < MANO_THETA_DIM or len(wrist) < MANO_WRIST_DIM
    return pad_or_trim(thetas, MANO_THETA_DIM) + pad_or_trim(wrist, MANO_WRIST_DIM), detail


def vector_for_sample(sample: dict[str, Any]) -> tuple[list[float], list[dict[str, Any]]]:
    vector: list[float] = []
    details: list[dict[str, Any]] = []
    for hand in HAND_ORDER:
        hand_vector, detail = mano_vector_for_hand(sample, hand)
        vector.extend(hand_vector)
        details.append(detail)
    return vector, details


def build_report(
    *,
    index_path: Path,
    output_path: Path,
    payload: dict[str, Any],
    samples: list[dict[str, Any]],
    inspected_details: list[dict[str, Any]],
    counters: Counter[str],
    dims: Counter[int],
) -> str:
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    lines = [
        "# Hand Pose Vector Target Report",
        "",
        "Status: current target-vector audit.",
        "",
        "This report documents the current future hand-pose target used by the",
        "HOT3D-Clips dataset class. It does not claim MPJPE and does not convert",
        "MANO/UmeTrack parameters to 3D joints.",
        "",
        "## Source",
        "",
        f"- Index: `{index_path}`",
        f"- Samples in index: {len(samples)}",
        f"- Observation frames: {metadata.get('observation_frames', 'unknown')}",
        f"- Forecast horizon: {metadata.get('forecast_horizon', 'unknown')}",
        f"- Requested hand source: {metadata.get('hand_source_requested', 'unknown')}",
        "",
        "## Current 42-D Target Interpretation",
        "",
        f"- Hand order: `{', '.join(HAND_ORDER)}`",
        f"- Per hand: first {MANO_THETA_DIM} MANO `thetas` values + first {MANO_WRIST_DIM} `wrist_xform` values.",
        f"- Per-hand dimension: {MANO_THETA_DIM + MANO_WRIST_DIM}",
        f"- Both-hands dimension: {(MANO_THETA_DIM + MANO_WRIST_DIM) * len(HAND_ORDER)}",
        "- Missing hands are zero-padded by the dataset class.",
        "- This is a pose-parameter vector target, not a 3D joint target.",
        "",
        "## Inspected Dimension Counts",
        "",
    ]
    for dim, count in sorted(dims.items()):
        lines.append(f"- Vector dimension {dim}: {count} inspected samples")

    lines.extend(["", "## Availability Counts", ""])
    for key, count in counters.most_common():
        lines.append(f"- {key}: {count}")

    lines.extend(["", "## First Inspected Samples", ""])
    for detail in inspected_details[:5]:
        lines.append(f"### `{detail['sample_id']}`")
        lines.append("")
        lines.append(f"- Vector dimension: {detail['vector_dim']}")
        lines.append(f"- Available hands in index: {detail['available_hands']}")
        for hand_detail in detail["hands"]:
            lines.append(
                "- {hand}: present={present}, source={source}, theta_len={theta_len}, "
                "wrist_xform_len={wrist_xform_len}, padded={missing_or_padded}".format(**hand_detail)
            )
        lines.append("")

    lines.extend(
        [
            "## MPJPE Status",
            "",
            "MPJPE is not available from this vector directly. A valid MPJPE pipeline",
            "requires verified MANO or UmeTrack model conversion to 3D joints and",
            "matching predicted/target joint arrays in the same coordinate frame.",
        ]
    )

    report = "\n".join(lines) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    args = parse_args()
    payload, samples = load_samples(args.index)
    inspected = samples[: max(0, args.max_samples)]
    counters: Counter[str] = Counter()
    dims: Counter[int] = Counter()
    inspected_details: list[dict[str, Any]] = []

    for sample in inspected:
        vector, hand_details = vector_for_sample(sample)
        dims[len(vector)] += 1
        for hand_detail in hand_details:
            hand = hand_detail["hand"]
            counters[f"{hand}.present={hand_detail['present']}"] += 1
            counters[f"{hand}.source={hand_detail['source']}"] += 1
            counters[f"{hand}.theta_len={hand_detail['theta_len']}"] += 1
            counters[f"{hand}.wrist_xform_len={hand_detail['wrist_xform_len']}"] += 1
            if hand_detail["missing_or_padded"]:
                counters[f"{hand}.padded"] += 1

        inspected_details.append(
            {
                "sample_id": str(sample.get("sample_id")),
                "available_hands": sample.get("available_hands", []),
                "vector_dim": len(vector),
                "hands": hand_details,
            }
        )

    build_report(
        index_path=args.index,
        output_path=args.output,
        payload=payload,
        samples=samples,
        inspected_details=inspected_details,
        counters=counters,
        dims=dims,
    )

    print(
        json.dumps(
            {
                "index": str(args.index),
                "samples_in_index": len(samples),
                "samples_inspected": len(inspected),
                "vector_dims": dict(dims),
                "counts": dict(counters),
                "report": str(args.output),
                "interpretation": (
                    "Current target is [left MANO thetas(15)+wrist_xform(6), "
                    "right MANO thetas(15)+wrist_xform(6)] = 42 values, with zero padding for missing hands."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
