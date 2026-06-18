# Final Formatting Plan

Date: 2026-06-18

Status: final DOCX/PDF formatting workflow prepared for the PreHOI-Rank
pre-submission draft. This plan does not change numerical results or scientific
claims.

## Converter Availability

- Pandoc: not available on PATH.
- LibreOffice/soffice: not available on PATH.
- Microsoft Word COM automation: available locally, but PDF export timed out in
  this run and was not selected for the final draft export.
- Bundled Python `python-docx`: available.
- Bundled Python PDF libraries: available for structural checks.

## Selected Conversion Method

The selected local workflow is:

1. Read the combined Markdown draft:
   `paper/exported_drafts/prehoi_rank_combined_draft.md`.
2. Generate a draft DOCX using bundled Python and `python-docx`.
3. Generate a draft PDF from the same combined Markdown using bundled Python
   and ReportLab.
4. Run structural checks for file existence, non-empty output, page count, final
   DOI, final author spelling, and absence of public-facing restricted strings.

This is a draft formatting workflow, not a final journal typesetting pass.
The DOCX and PDF are parallel draft exports from the same Markdown source, not
a visually verified Word-to-PDF conversion.

## Source Manuscript File

Primary source:

- `paper/exported_drafts/prehoi_rank_combined_draft.md`

Supporting files copied into the final submission folder:

- `paper/formatted_submission_draft/title_page.md`
- `paper/formatted_submission_draft/cover_letter_formatted.md`
- `paper/formatted_submission_draft/highlights.md`
- `paper/formatted_submission_draft/figure_caption_list.md`
- `paper/formatted_submission_draft/table_caption_list.md`
- `paper/formatted_submission_draft/references.bib`
- `paper/final_pre_formatting_audit.md`

## Target Output Files

Target folder:

- `paper/final_submission_files/`

Target manuscript exports:

- `paper/final_submission_files/PreHOI_Rank_Manuscript_DRAFT.docx`
- `paper/final_submission_files/PreHOI_Rank_Manuscript_DRAFT.pdf`

## Figures and Tables Inclusion Plan

The draft DOCX/PDF includes figure and table caption lists from the combined
Markdown. Figure image files and table Markdown files remain available in the
submission package and formatted draft folders. Before final journal upload,
confirm whether MLWA expects figures/tables embedded in the manuscript file or
uploaded separately.

## References Handling Plan

The draft DOCX/PDF includes the manuscript references note and copies
`references.bib` into the final submission folder. Before final journal upload,
check whether the journal submission system expects BibTeX, a formatted
reference list in the manuscript, or both.

## Final Checks Before Submission

- Confirm final GitHub URL: `https://github.com/XessX/prehoi-rank-hot3d`.
- Confirm final Zenodo DOI: `10.5281/zenodo.20736962`.
- Confirm final author spelling: Seyam Rahman Nayem.
- Confirm no student IDs appear in public-facing files.
- Confirm old PreHOI v0.1.0/v0.1.1 DOIs do not appear in public-facing files.
- Confirm old Scientific Reports sparse 3D repository/DOI strings are absent.
- Confirm HOT3D-Clips access/license wording against official sources.
- Confirm MLWA formatting, APC, waiver, and Research4Life details in the live
  submission context.
- Run a final post-formatting scan before upload.
