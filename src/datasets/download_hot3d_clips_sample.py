"""Safely acquire a tiny HOT3D-Clips sample from Hugging Face.

The default mode is a dry run. Add --confirm-download to actually download the
selected files. This script is intentionally conservative and refuses broad or
large downloads unless the user supplies explicit flags.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_REPO_ID = "bop-benchmark/hot3d"
DEFAULT_OUTPUT_DIR = Path("data/raw/hot3d_clips")
DEFAULT_PATTERNS = ("clip_splits.json",)
LARGE_FILE_SUFFIXES = (".tar", ".vrs", ".zip", ".z01", ".mp4", ".mps")


@dataclass(frozen=True)
class CandidateFile:
    path: str
    size: int | None = None

    @property
    def size_mb(self) -> float | None:
        return None if self.size is None else self.size / (1024 * 1024)

    @property
    def is_large_type(self) -> bool:
        return self.path.lower().endswith(LARGE_FILE_SUFFIXES)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dry-run or download a tiny HOT3D-Clips subset from Hugging Face."
    )
    parser.add_argument("--repo-id", default=DEFAULT_REPO_ID, help="Hugging Face dataset repo ID.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Local output directory for downloaded files.",
    )
    parser.add_argument(
        "--pattern",
        action="append",
        default=None,
        help=(
            "Glob pattern inside the dataset repo. Can be repeated. "
            "Example: train_aria/*.tar"
        ),
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=1,
        help="Maximum matching files to select.",
    )
    parser.add_argument(
        "--max-total-gb",
        type=float,
        default=2.0,
        help="Refuse downloads whose known selected size exceeds this limit.",
    )
    parser.add_argument(
        "--confirm-download",
        action="store_true",
        help="Actually download selected files. Omit for dry-run listing only.",
    )
    parser.add_argument(
        "--allow-large-files",
        action="store_true",
        help="Allow large file types such as .tar after --confirm-download is supplied.",
    )
    parser.add_argument(
        "--allow-unknown-size",
        action="store_true",
        help="Allow download when Hugging Face does not report file sizes.",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Optional Hugging Face token. Prefer `huggingface-cli login` for normal use.",
    )
    return parser.parse_args()


def import_huggingface_hub() -> dict[str, Any]:
    try:
        from huggingface_hub import HfApi, hf_hub_download
        from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError
    except ImportError:
        print(
            json.dumps(
                {
                    "ok": False,
                    "error": "huggingface_hub is not installed.",
                    "next_steps": [
                        "Activate .venv.",
                        "Run: pip install -r requirements.txt",
                        "Or install directly: pip install huggingface_hub",
                    ],
                },
                indent=2,
            )
        )
        raise SystemExit(2)

    return {
        "HfApi": HfApi,
        "hf_hub_download": hf_hub_download,
        "GatedRepoError": GatedRepoError,
        "HfHubHTTPError": HfHubHTTPError,
        "RepositoryNotFoundError": RepositoryNotFoundError,
    }


def list_repo_candidates(repo_id: str, token: str | None) -> list[CandidateFile]:
    hub = import_huggingface_hub()
    api = hub["HfApi"]()

    try:
        files = list(api.list_repo_tree(repo_id=repo_id, repo_type="dataset", recursive=True, token=token))
    except (hub["GatedRepoError"], hub["RepositoryNotFoundError"], hub["HfHubHTTPError"]) as exc:
        print_access_error(repo_id, exc)
        raise SystemExit(3)

    candidates: list[CandidateFile] = []
    for item in files:
        item_type = getattr(item, "type", None)
        path = getattr(item, "path", None)
        if item_type not in (None, "file") or not path:
            continue
        candidates.append(CandidateFile(path=path, size=getattr(item, "size", None)))
    return candidates


def select_candidates(
    candidates: list[CandidateFile],
    patterns: tuple[str, ...],
    max_files: int,
) -> list[CandidateFile]:
    selected: list[CandidateFile] = []
    seen: set[str] = set()
    for pattern in patterns:
        for candidate in candidates:
            if candidate.path in seen:
                continue
            if fnmatch.fnmatch(candidate.path, pattern):
                selected.append(candidate)
                seen.add(candidate.path)
                if len(selected) >= max_files:
                    return selected
    return selected


def validate_selection(
    selected: list[CandidateFile],
    args: argparse.Namespace,
) -> tuple[bool, list[str]]:
    problems: list[str] = []
    if not selected:
        problems.append("No files matched the requested pattern(s).")
        return False, problems

    if args.max_files <= 0:
        problems.append("--max-files must be positive.")

    unknown_size = [item.path for item in selected if item.size is None]
    if unknown_size and not args.allow_unknown_size:
        problems.append(
            "Selected files have unknown sizes. Re-run with --allow-unknown-size "
            "only after confirming the file list is small."
        )

    total_size = sum(item.size or 0 for item in selected)
    total_gb = total_size / (1024**3)
    if total_size and total_gb > args.max_total_gb:
        problems.append(
            f"Selected files total {total_gb:.2f} GB, above --max-total-gb={args.max_total_gb}."
        )

    large_files = [item.path for item in selected if item.is_large_type]
    if large_files and not args.allow_large_files:
        problems.append(
            "Selected files include large dataset artifact types. Add --allow-large-files "
            "after reviewing the dry-run output."
        )

    if not args.confirm_download:
        problems.append("Dry run only. Add --confirm-download to download the selected files.")

    return not problems, problems


def download_files(selected: list[CandidateFile], args: argparse.Namespace) -> list[dict[str, str]]:
    hub = import_huggingface_hub()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[dict[str, str]] = []
    for item in selected:
        try:
            local_path = hub["hf_hub_download"](
                repo_id=args.repo_id,
                repo_type="dataset",
                filename=item.path,
                local_dir=args.output_dir,
                local_dir_use_symlinks=False,
                token=args.token,
            )
        except (hub["GatedRepoError"], hub["RepositoryNotFoundError"], hub["HfHubHTTPError"]) as exc:
            print_access_error(args.repo_id, exc)
            raise SystemExit(3)
        downloaded.append({"repo_path": item.path, "local_path": str(local_path)})
    return downloaded


def print_access_error(repo_id: str, exc: Exception) -> None:
    print(
        json.dumps(
            {
                "ok": False,
                "repo_id": repo_id,
                "error": str(exc),
                "next_steps": [
                    "Open the Hugging Face dataset page and review/accept any license terms.",
                    "Run: huggingface-cli login",
                    "Then retry this script, or pass --token if you use a scoped token.",
                    "Do not bypass dataset license or access restrictions.",
                ],
            },
            indent=2,
        )
    )


def main() -> None:
    args = parse_args()
    patterns = tuple(args.pattern or DEFAULT_PATTERNS)
    candidates = list_repo_candidates(args.repo_id, args.token)
    selected = select_candidates(candidates, patterns, args.max_files)
    can_download, problems = validate_selection(selected, args)

    payload = {
        "ok": can_download,
        "repo_id": args.repo_id,
        "output_dir": str(args.output_dir),
        "patterns": patterns,
        "max_files": args.max_files,
        "selected_files": [
            {
                "path": item.path,
                "size_bytes": item.size,
                "size_mb": None if item.size_mb is None else round(item.size_mb, 2),
                "large_type": item.is_large_type,
            }
            for item in selected
        ],
        "known_total_gb": round(sum(item.size or 0 for item in selected) / (1024**3), 4),
        "messages": problems,
    }

    if not can_download:
        payload["downloaded_files"] = []
        payload["next_steps"] = [
            "Review selected_files and messages.",
            "Use a narrow --pattern and --max-files 1 for the first local inspection.",
            "Add --confirm-download and --allow-large-files only after approving the exact selection.",
        ]
        print(json.dumps(payload, indent=2))
        return

    payload["downloaded_files"] = download_files(selected, args)
    payload["next_steps"] = [
        f"Inspect downloaded data: python src/datasets/inspect_hot3d_clips.py {args.output_dir}",
        "Keep downloaded data out of Git.",
    ]
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()

