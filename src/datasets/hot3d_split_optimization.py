"""Shared helpers for HOT3D-Clips clip/class split optimization."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from src.datasets.hot3d_clips_dataset import selected_object_name


def samples_by_clip(samples: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for sample in samples:
        grouped[str(sample.get("clip_id"))].append(sample)
    return dict(grouped)


def clip_class_matrix(samples: list[dict[str, Any]]) -> dict[str, Counter[str]]:
    matrix: dict[str, Counter[str]] = {}
    for clip_id, clip_samples in samples_by_clip(samples).items():
        counts: Counter[str] = Counter()
        for sample in clip_samples:
            name = selected_object_name(sample)
            if name:
                counts[name] += 1
        matrix[clip_id] = counts
    return matrix


def class_totals(matrix: dict[str, Counter[str]]) -> Counter[str]:
    totals: Counter[str] = Counter()
    for counts in matrix.values():
        totals.update(counts)
    return totals


def class_clip_coverage(matrix: dict[str, Counter[str]]) -> dict[str, list[str]]:
    coverage: dict[str, list[str]] = defaultdict(list)
    for clip_id, counts in matrix.items():
        for label, count in counts.items():
            if count > 0:
                coverage[label].append(clip_id)
    return {label: sorted(clip_ids, key=_clip_sort_key) for label, clip_ids in coverage.items()}


def sample_count_for_clips(grouped: dict[str, list[dict[str, Any]]], clip_ids: list[str]) -> int:
    return sum(len(grouped[clip_id]) for clip_id in clip_ids)


def class_distribution_for_clips(matrix: dict[str, Counter[str]], clip_ids: list[str]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for clip_id in clip_ids:
        counts.update(matrix[clip_id])
    return dict(counts.most_common())


def filter_samples_to_classes(samples: list[dict[str, Any]], allowed_classes: set[str]) -> list[dict[str, Any]]:
    return [sample for sample in samples if (selected_object_name(sample) in allowed_classes)]


def eligible_classes(
    matrix: dict[str, Counter[str]],
    *,
    min_class_samples: int,
    min_class_clips: int,
) -> set[str]:
    totals = class_totals(matrix)
    coverage = class_clip_coverage(matrix)
    return {
        label
        for label, total in totals.items()
        if total >= min_class_samples and len(coverage.get(label, [])) >= min_class_clips
    }


def _clip_sort_key(clip_id: str) -> tuple[int, str]:
    try:
        return (int(clip_id), clip_id)
    except ValueError:
        return (10**12, clip_id)
