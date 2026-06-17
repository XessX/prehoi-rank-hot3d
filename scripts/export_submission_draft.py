"""Export the formatted PreHOI-Rank submission draft.

This script is intentionally conservative. It always creates a combined
Markdown draft from the formatted submission package. If Pandoc is available on
PATH, it also attempts DOCX and PDF exports. If Pandoc or a PDF backend is not
available, the script writes manual export instructions instead of failing.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMATTED_DIR = ROOT / "paper" / "formatted_submission_draft"
EXPORT_DIR = ROOT / "paper" / "exported_drafts"


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Required source file is missing: {path}")
    return path.read_text(encoding="utf-8").strip()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def run_command(command: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        return False, str(exc)

    output = "\n".join(part for part in [result.stdout, result.stderr] if part)
    return result.returncode == 0, output.strip()


def build_combined_markdown(include_captions: bool = True) -> str:
    title_page = read_text(FORMATTED_DIR / "title_page.md")
    manuscript = read_text(FORMATTED_DIR / "manuscript_formatted.md")

    parts = [
        "<!-- DRAFT EXPORT: five-author metadata, repository URL, and Zenodo DOI are filled; student co-author consent responses/contribution roles have been received; fifth-author spelling, journal formatting, APC/waiver, and HOT3D license/access checks remain pending. -->",
        "# PreHOI-Rank Manuscript Draft Export",
        "",
        "**Status:** DRAFT. Not submission-ready until the fifth-author spelling check, journal formatting, APC/waiver, and HOT3D license/access checks are complete.",
        "",
        "## Title Page",
        "",
        title_page,
        "",
        "\\newpage",
        "",
        "## Main Manuscript",
        "",
        manuscript,
    ]

    if include_captions:
        figure_captions = read_text(FORMATTED_DIR / "figure_caption_list.md")
        table_captions = read_text(FORMATTED_DIR / "table_caption_list.md")
        parts.extend(
            [
                "",
                "\\newpage",
                "",
                "## Figure Captions",
                "",
                figure_captions,
                "",
                "## Table Captions",
                "",
                table_captions,
            ]
        )

    return "\n".join(parts)


def write_export_instructions(pandoc_path: str | None, docx_created: bool, pdf_created: bool) -> Path:
    docx_cmd = (
        'pandoc paper/exported_drafts/prehoi_rank_combined_draft.md '
        '-o paper/exported_drafts/prehoi_rank_manuscript_draft.docx '
        '--resource-path=paper/formatted_submission_draft;paper/formatted_submission_draft/figures'
    )
    pdf_cmd = (
        'pandoc paper/exported_drafts/prehoi_rank_combined_draft.md '
        '-o paper/exported_drafts/prehoi_rank_manuscript_draft.pdf '
        '--resource-path=paper/formatted_submission_draft;paper/formatted_submission_draft/figures'
    )

    lines = [
        "# Export Instructions",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "Status: draft export workflow. Do not submit exported files until the fifth-author spelling check, journal formatting, APC/waiver, and HOT3D-Clips license/access checks are complete.",
        "",
        "## Converter Status",
        "",
        f"- Pandoc detected: {'yes' if pandoc_path else 'no'}",
        f"- DOCX created by this run: {'yes' if docx_created else 'no'}",
        f"- PDF created by this run: {'yes' if pdf_created else 'no'}",
        "",
        "## Manual Conversion",
        "",
        "The combined Markdown draft is ready at:",
        "",
        "- `paper/exported_drafts/prehoi_rank_combined_draft.md`",
        "",
        "If Pandoc is installed, run:",
        "",
        "```powershell",
        docx_cmd,
        pdf_cmd,
        "```",
        "",
        "If Pandoc PDF export fails because a LaTeX engine is missing, open the DOCX in Word or LibreOffice and export to PDF manually.",
        "",
        "If using Word manually:",
        "",
        "1. Open `paper/exported_drafts/prehoi_rank_combined_draft.md` or copy its content into Word.",
        "2. Preserve pending fifth-author spelling, APC/waiver, HOT3D license/access, and journal-system fields until they are confirmed.",
        "3. Insert figures from `paper/formatted_submission_draft/figures/` if needed.",
        "4. Insert tables from `paper/formatted_submission_draft/tables/` if needed.",
        "5. Export DOCX/PDF only after the final fifth-author spelling, journal, APC/waiver, and HOT3D license/access checks.",
    ]

    path = EXPORT_DIR / "export_instructions.md"
    write_text(path, "\n".join(lines))
    return path


def write_export_audit(
    combined_path: Path,
    pandoc_path: str | None,
    docx_path: Path,
    pdf_path: Path,
    docx_created: bool,
    pdf_created: bool,
    docx_log: str,
    pdf_log: str,
    instructions_path: Path,
) -> Path:
    lines = [
        "# Export Audit",
        "",
        f"Date: {date.today().isoformat()}",
        "",
        "Status: draft export audit. Exported artifacts are not submission-ready until the fifth-author spelling check, journal formatting, APC/waiver, and HOT3D license/access checks are complete.",
        "",
        "## Output Files",
        "",
        f"- Combined Markdown created: yes, `{combined_path.as_posix()}`",
        f"- DOCX created: {'yes' if docx_created else 'no'}, `{docx_path.as_posix()}`",
        f"- PDF created: {'yes' if pdf_created else 'no'}, `{pdf_path.as_posix()}`",
        f"- Export instructions: `{instructions_path.as_posix()}`",
        "",
        "## Converter Availability",
        "",
        f"- Pandoc path: `{pandoc_path}`" if pandoc_path else "- Pandoc path: not found on PATH",
        "",
        "## Remaining Pending Fields",
        "",
        "- final fifth-author spelling check;",
        "- final decision on derived index/log/checkpoint sharing;",
        "- final MLWA APC/tax/waiver/Research4Life checks;",
        "- final HOT3D-Clips license/access wording.",
        "",
        "## Export Logs",
        "",
        "### DOCX",
        "",
        "```text",
        docx_log or "No DOCX conversion attempted or no converter output.",
        "```",
        "",
        "### PDF",
        "",
        "```text",
        pdf_log or "No PDF conversion attempted or no converter output.",
        "```",
        "",
        "## Final Warning",
        "",
        "These files are draft exports only. They must not be submitted until the final fifth-author spelling check, journal formatting, APC/waiver route, and HOT3D-Clips license/access wording are confirmed.",
    ]

    path = EXPORT_DIR / "export_audit.md"
    write_text(path, "\n".join(lines))
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--no-captions",
        action="store_true",
        help="Do not append figure and table caption lists to the combined Markdown.",
    )
    args = parser.parse_args()

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    combined_path = EXPORT_DIR / "prehoi_rank_combined_draft.md"
    docx_path = EXPORT_DIR / "prehoi_rank_manuscript_draft.docx"
    pdf_path = EXPORT_DIR / "prehoi_rank_manuscript_draft.pdf"

    combined_markdown = build_combined_markdown(include_captions=not args.no_captions)
    write_text(combined_path, combined_markdown)

    pandoc_path = shutil.which("pandoc")
    docx_created = False
    pdf_created = False
    docx_log = ""
    pdf_log = ""

    if pandoc_path:
        docx_ok, docx_log = run_command(
            [
                pandoc_path,
                str(combined_path),
                "-o",
                str(docx_path),
                "--resource-path=paper/formatted_submission_draft;paper/formatted_submission_draft/figures",
            ]
        )
        docx_created = docx_ok and docx_path.exists()

        pdf_ok, pdf_log = run_command(
            [
                pandoc_path,
                str(combined_path),
                "-o",
                str(pdf_path),
                "--resource-path=paper/formatted_submission_draft;paper/formatted_submission_draft/figures",
            ]
        )
        pdf_created = pdf_ok and pdf_path.exists()

    instructions_path = write_export_instructions(pandoc_path, docx_created, pdf_created)
    audit_path = write_export_audit(
        combined_path=combined_path,
        pandoc_path=pandoc_path,
        docx_path=docx_path,
        pdf_path=pdf_path,
        docx_created=docx_created,
        pdf_created=pdf_created,
        docx_log=docx_log,
        pdf_log=pdf_log,
        instructions_path=instructions_path,
    )

    print("DRAFT EXPORT -- NOT SUBMISSION READY")
    print(f"Combined Markdown: {combined_path}")
    print(f"Pandoc available: {bool(pandoc_path)}")
    print(f"DOCX created: {docx_created}")
    print(f"PDF created: {pdf_created}")
    print(f"Export instructions: {instructions_path}")
    print(f"Export audit: {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
