# Export Instructions

Date: 2026-06-09

Status: draft export workflow. Do not submit exported files until author metadata, journal formatting, APC/waiver, and HOT3D-Clips license/access checks are complete.

## Converter Status

- Pandoc detected: no
- DOCX created by this run: no
- PDF created by this run: no

## Manual Conversion

The combined Markdown draft is ready at:

- `paper/exported_drafts/prehoi_rank_combined_draft.md`

If Pandoc is installed, run:

```powershell
pandoc paper/exported_drafts/prehoi_rank_combined_draft.md -o paper/exported_drafts/prehoi_rank_manuscript_draft.docx --resource-path=paper/formatted_submission_draft;paper/formatted_submission_draft/figures
pandoc paper/exported_drafts/prehoi_rank_combined_draft.md -o paper/exported_drafts/prehoi_rank_manuscript_draft.pdf --resource-path=paper/formatted_submission_draft;paper/formatted_submission_draft/figures
```

If Pandoc PDF export fails because a LaTeX engine is missing, open the DOCX in Word or LibreOffice and export to PDF manually.

If using Word manually:

1. Open `paper/exported_drafts/prehoi_rank_combined_draft.md` or copy its content into Word.
2. Preserve author placeholders until final metadata is confirmed.
3. Insert figures from `paper/formatted_submission_draft/figures/` if needed.
4. Insert tables from `paper/formatted_submission_draft/tables/` if needed.
5. Export DOCX/PDF only after final author and journal checks.
