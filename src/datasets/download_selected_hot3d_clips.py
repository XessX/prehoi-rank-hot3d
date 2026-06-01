"""Download selected HOT3D-Clips shards from a reviewed selection JSON.

This wrapper delegates one shard at a time to download_hot3d_clips_sample.py so
the existing access checks, size limits, and license/login errors stay in one
place. Dry run is the default.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SELECTION = Path("data/processed/hot3d_diverse_clip_selection.json")
DEFAULT_OUTPUT_DIR = Path("data/raw/hot3d_clips")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download reviewed HOT3D-Clips shard selections.")
    parser.add_argument("--selection", type=Path, default=DEFAULT_SELECTION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--repo-id", default="bop-benchmark/hot3d")
    parser.add_argument("--max-clips", type=int, default=8)
    parser.add_argument("--max-total-gb", type=float, default=2.0)
    parser.add_argument("--confirm-download", action="store_true")
    parser.add_argument("--token", default=None)
    parser.add_argument(
        "--python-executable",
        default=sys.executable,
        help="Python executable used to call the existing downloader.",
    )
    return parser.parse_args()


def load_selection(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Selection file not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Selection file must contain a JSON object: {path}")
    return payload


def selected_shards(payload: dict[str, Any], max_clips: int) -> list[dict[str, Any]]:
    selected = payload.get("selected_clips", [])
    if not isinstance(selected, list):
        raise ValueError("Selection JSON must contain a list at selected_clips.")
    records: list[dict[str, Any]] = []
    for item in selected:
        if not isinstance(item, dict):
            continue
        shard_path = item.get("expected_shard_path")
        if not isinstance(shard_path, str) or not shard_path:
            continue
        records.append(item)
        if len(records) >= max_clips:
            break
    return records


def local_shard_path(output_dir: Path, shard_path: str) -> Path:
    return output_dir / Path(shard_path)


def file_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)


def build_downloader_command(args: argparse.Namespace, shard_path: str) -> list[str]:
    command = [
        args.python_executable,
        str(PROJECT_ROOT / "src" / "datasets" / "download_hot3d_clips_sample.py"),
        "--repo-id",
        args.repo_id,
        "--pattern",
        shard_path,
        "--max-files",
        "1",
        "--output-dir",
        str(args.output_dir),
        "--max-total-gb",
        str(args.max_total_gb),
        "--allow-large-files",
    ]
    if args.confirm_download:
        command.append("--confirm-download")
    if args.token:
        command.extend(["--token", args.token])
    return command


def dry_run_downloader_command(args: argparse.Namespace, shard_path: str) -> list[str]:
    command = build_downloader_command(args, shard_path)
    return [part for part in command if part != "--confirm-download"]


def run_downloader(command: list[str]) -> tuple[int, str, str]:
    completed = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    return completed.returncode, completed.stdout, completed.stderr


def parse_json_stdout(stdout: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def parse_downloaded_files(stdout: str) -> list[dict[str, Any]]:
    payload = parse_json_stdout(stdout)
    if payload is None:
        return []
    downloaded = payload.get("downloaded_files", [])
    return downloaded if isinstance(downloaded, list) else []


def selected_size_bytes_from_stdout(stdout: str) -> int:
    payload = parse_json_stdout(stdout)
    if payload is None:
        return 0
    selected_files = payload.get("selected_files", [])
    if not isinstance(selected_files, list):
        return 0
    size = 0
    for item in selected_files:
        if isinstance(item, dict) and isinstance(item.get("size_bytes"), int):
            size += item["size_bytes"]
    return size


def preflight_missing_records(
    args: argparse.Namespace,
    missing_records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    preflight: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    total_size = 0
    for record in missing_records:
        shard_path = record["expected_shard_path"]
        command = dry_run_downloader_command(args, shard_path)
        returncode, stdout, stderr = run_downloader(command)
        size_bytes = selected_size_bytes_from_stdout(stdout)
        total_size += size_bytes
        entry = {
            "clip_id": record.get("clip_id"),
            "shard_path": shard_path,
            "command": command,
            "returncode": returncode,
            "known_size_mb": round(size_bytes / (1024 * 1024), 2) if size_bytes else None,
        }
        if returncode != 0:
            entry["stdout"] = stdout
            entry["stderr"] = stderr
            failed.append(entry)
        else:
            preflight.append(entry)

    return preflight, failed, total_size


def main() -> None:
    args = parse_args()
    if args.max_clips <= 0:
        raise ValueError("--max-clips must be positive.")

    payload = load_selection(args.selection)
    records = selected_shards(payload, args.max_clips)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    skipped: list[dict[str, Any]] = []
    downloaded: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    dry_run: list[dict[str, Any]] = []
    preflight: list[dict[str, Any]] = []
    missing_records: list[dict[str, Any]] = []

    for record in records:
        shard_path = record["expected_shard_path"]
        local_path = local_shard_path(args.output_dir, shard_path)
        if local_path.exists():
            skipped.append(
                {
                    "clip_id": record.get("clip_id"),
                    "shard_path": shard_path,
                    "local_path": str(local_path),
                    "size_mb": round(file_size_mb(local_path), 2),
                    "reason": "already_downloaded",
                }
            )
            continue
        missing_records.append(record)

    if args.confirm_download and missing_records:
        preflight, preflight_failed, selected_total_size = preflight_missing_records(args, missing_records)
        failed.extend(preflight_failed)
        selected_total_gb = selected_total_size / (1024**3)
        if selected_total_size and selected_total_gb > args.max_total_gb:
            failed.append(
                {
                    "reason": "selected_total_exceeds_max_total_gb",
                    "selected_total_gb": round(selected_total_gb, 4),
                    "max_total_gb": args.max_total_gb,
                }
            )
        if failed:
            summary = {
                "selection": str(args.selection),
                "output_dir": str(args.output_dir),
                "repo_id": args.repo_id,
                "max_clips": args.max_clips,
                "confirm_download": args.confirm_download,
                "selected_count": len(records),
                "downloaded_count": 0,
                "skipped_count": len(skipped),
                "failed_count": len(failed),
                "dry_run_count": 0,
                "preflight": preflight,
                "downloaded": [],
                "skipped": skipped,
                "failed": failed,
                "note": "Download was stopped before transfer. No training was run.",
            }
            print(json.dumps(summary, indent=2))
            raise SystemExit(3)

    for record in missing_records:
        shard_path = record["expected_shard_path"]
        local_path = local_shard_path(args.output_dir, shard_path)
        command = build_downloader_command(args, shard_path)
        returncode, stdout, stderr = run_downloader(command)
        entry = {
            "clip_id": record.get("clip_id"),
            "shard_path": shard_path,
            "command": command,
            "returncode": returncode,
        }
        if returncode != 0:
            entry["stdout"] = stdout
            entry["stderr"] = stderr
            failed.append(entry)
            continue

        downloaded_files = parse_downloaded_files(stdout)
        if args.confirm_download:
            entry["downloaded_files"] = downloaded_files
            if local_path.exists():
                entry["local_path"] = str(local_path)
                entry["size_mb"] = round(file_size_mb(local_path), 2)
            downloaded.append(entry)
        else:
            entry["dry_run_output"] = stdout
            dry_run.append(entry)

    total_downloaded_mb = sum(item.get("size_mb", 0.0) for item in downloaded if isinstance(item.get("size_mb"), float))
    total_existing_mb = sum(item.get("size_mb", 0.0) for item in skipped if isinstance(item.get("size_mb"), float))
    summary = {
        "selection": str(args.selection),
        "output_dir": str(args.output_dir),
        "repo_id": args.repo_id,
        "max_clips": args.max_clips,
        "confirm_download": args.confirm_download,
        "selected_count": len(records),
        "downloaded_count": len(downloaded),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "dry_run_count": len(dry_run),
        "total_downloaded_mb_this_run": round(total_downloaded_mb, 2),
        "total_existing_selected_mb": round(total_existing_mb, 2),
        "preflight": preflight,
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "dry_run": dry_run,
        "note": "No training was run. Only selected shard acquisition was attempted.",
    }
    print(json.dumps(summary, indent=2))

    if failed:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
