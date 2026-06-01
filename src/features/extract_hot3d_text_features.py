"""Extract frozen CLIP text features for HOT3D object candidate names."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


DEFAULT_PROMPT_TEMPLATES = (
    "a photo of a {object}",
    "a person is about to interact with a {object}",
    "a hand is reaching toward a {object}",
    "an object used in a hand-object interaction: {object}",
)
DEFAULT_CANDIDATE_INDEXES = (
    Path("data/processed/hot3d_clips_sample_index_proxy_v1_multi.json"),
    Path("data/processed/hot3d_clips_train_optimized.json"),
    Path("data/processed/hot3d_clips_val_optimized.json"),
    Path("data/processed/hot3d_clips_test_optimized.json"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract HOT3D object-name CLIP text features.")
    parser.add_argument("--label-map", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--clip-model", default="ViT-B-32")
    parser.add_argument("--clip-pretrained", default="laion2b_s34b_b79k")
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument(
        "--candidate-index",
        action="append",
        type=Path,
        default=None,
        help="Optional sample index to scan for visible candidate object names.",
    )
    parser.add_argument(
        "--label-map-only",
        action="store_true",
        help="Only embed label-map classes; do not auto-include candidate names from local indexes.",
    )
    return parser.parse_args()


def load_object_names(label_map_path: Path) -> list[str]:
    if not label_map_path.exists():
        raise FileNotFoundError(f"Label map not found: {label_map_path}")
    with label_map_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    classes = payload.get("classes")
    if isinstance(classes, list) and classes:
        return [str(item) for item in classes]
    class_to_idx = payload.get("class_to_idx", {})
    if isinstance(class_to_idx, dict) and class_to_idx:
        return sorted((str(name) for name in class_to_idx), key=lambda name: int(class_to_idx[name]))
    raise ValueError(f"Could not find object classes in label map: {label_map_path}")


def candidate_index_paths(args: argparse.Namespace) -> list[Path]:
    if args.label_map_only:
        return []
    if args.candidate_index:
        return [Path(path) for path in args.candidate_index]
    return [path for path in DEFAULT_CANDIDATE_INDEXES if path.exists()]


def load_candidate_object_names(index_paths: list[Path]) -> dict[str, list[str]]:
    names_by_path: dict[str, list[str]] = {}
    for index_path in index_paths:
        if not index_path.exists():
            continue
        with index_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        samples = payload.get("samples", [])
        if not isinstance(samples, list):
            continue
        names: set[str] = set()
        for sample in samples:
            if not isinstance(sample, dict):
                continue
            for field in ("target_object_candidates", "observation_object_candidates", "observation_object_candidate_scores"):
                candidates = sample.get(field)
                if not isinstance(candidates, list):
                    continue
                for candidate in candidates:
                    if not isinstance(candidate, dict):
                        continue
                    name = candidate.get("object_name")
                    if name:
                        names.add(str(name))
            proxy = sample.get("target_object_proxy", {})
            if isinstance(proxy, dict) and proxy.get("selected_object_name"):
                names.add(str(proxy["selected_object_name"]))
        if names:
            names_by_path[str(index_path)] = sorted(names)
    return names_by_path


def object_display_name(name: str) -> str:
    return name.replace("_", " ")


def build_prompts(object_names: list[str]) -> list[list[str]]:
    return [
        [template.format(object=object_display_name(name)) for template in DEFAULT_PROMPT_TEMPLATES]
        for name in object_names
    ]


def extract_text_features(args: argparse.Namespace) -> dict[str, Any]:
    try:
        import torch
        import open_clip
    except ImportError as exc:
        raise RuntimeError(
            "Text feature extraction requires torch and open_clip_torch. "
            "Install project requirements before running this script."
        ) from exc

    label_map_names = load_object_names(args.label_map)
    candidate_names_by_path = load_candidate_object_names(candidate_index_paths(args))
    all_names = set(label_map_names)
    for names in candidate_names_by_path.values():
        all_names.update(names)
    object_names = sorted(all_names)
    prompts_by_object = build_prompts(object_names)
    flat_prompts = [prompt for prompts in prompts_by_object for prompt in prompts]

    device = torch.device("cuda" if args.device == "cuda" and torch.cuda.is_available() else "cpu")
    model, _, _ = open_clip.create_model_and_transforms(
        args.clip_model,
        pretrained=args.clip_pretrained,
        device=device,
    )
    tokenizer = open_clip.get_tokenizer(args.clip_model)
    model.eval()

    encoded_batches: list[np.ndarray] = []
    with torch.no_grad():
        for start in range(0, len(flat_prompts), args.batch_size):
            batch_prompts = flat_prompts[start : start + args.batch_size]
            tokens = tokenizer(batch_prompts).to(device)
            text_features = model.encode_text(tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True).clamp_min(1.0e-8)
            encoded_batches.append(text_features.detach().cpu().numpy().astype(np.float32))

    prompt_features = np.concatenate(encoded_batches, axis=0)
    prompt_count = len(DEFAULT_PROMPT_TEMPLATES)
    prompt_features = prompt_features.reshape(len(object_names), prompt_count, -1)
    object_features = prompt_features.mean(axis=1)
    norms = np.linalg.norm(object_features, axis=1, keepdims=True)
    object_features = object_features / np.maximum(norms, 1.0e-8)
    object_features = object_features.astype(np.float32)

    metadata = {
        "feature_type": "clip_text",
        "label_map": str(args.label_map),
        "label_map_object_count": len(label_map_names),
        "candidate_name_sources": {
            path: len(names)
            for path, names in candidate_names_by_path.items()
        },
        "model_name": args.clip_model,
        "pretrained": args.clip_pretrained,
        "num_object_classes": len(object_names),
        "prompt_templates": list(DEFAULT_PROMPT_TEMPLATES),
        "feature_dim": int(object_features.shape[-1]),
        "note": "Frozen CLIP text embeddings for object names. No HOT3D labels or model results are produced.",
    }
    return {
        "object_names": np.array(object_names, dtype=object),
        "prompts": np.array(prompts_by_object, dtype=object),
        "text_features": object_features,
        "prompt_text_features": prompt_features.astype(np.float32),
        "metadata": metadata,
    }


def main() -> None:
    args = parse_args()
    payload = extract_text_features(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        object_names=payload["object_names"],
        prompts=payload["prompts"],
        text_features=payload["text_features"],
        prompt_text_features=payload["prompt_text_features"],
        model_name=np.array(payload["metadata"]["model_name"], dtype=object),
        pretrained=np.array(payload["metadata"]["pretrained"], dtype=object),
        feature_dim=np.array(payload["metadata"]["feature_dim"], dtype=np.int32),
        metadata_json=np.array(json.dumps(payload["metadata"]), dtype=object),
    )
    print(json.dumps({"output": str(args.output), **payload["metadata"]}, indent=2))


if __name__ == "__main__":
    main()
