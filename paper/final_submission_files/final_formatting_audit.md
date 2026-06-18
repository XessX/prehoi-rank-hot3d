# Final Formatting Audit

Date: 2026-06-18

Status: draft DOCX/PDF formatting workflow completed. The generated files are
draft submission artifacts and still require final journal-formatting review
before upload.

## Generated Files

- DOCX created: yes,
  `paper/final_submission_files/PreHOI_Rank_Manuscript_DRAFT.docx`
- PDF created: yes,
  `paper/final_submission_files/PreHOI_Rank_Manuscript_DRAFT.pdf`
- Source Markdown:
  `paper/exported_drafts/prehoi_rank_combined_draft.md`

## Conversion Method

- Pandoc: not available on PATH.
- LibreOffice/soffice: not available on PATH.
- Microsoft Word COM automation: available, but PDF export timed out locally.
- DOCX method used: bundled Python with `python-docx`.
- PDF method used: bundled Python with ReportLab from the same combined
  Markdown source.

Because LibreOffice is not available, page-image render QA via the Documents
skill renderer was not completed. The generated files passed structural checks
but still need visual review in Word/PDF viewer before journal upload.

## Structural Checks

- DOCX size: non-empty.
- DOCX paragraph count: 249.
- DOCX table count: 6.
- PDF size: non-empty.
- PDF page count: 14.
- Figure captions file copied: yes.
- Table captions file copied: yes.
- `references.bib` copied: yes.
- Final pre-formatting audit copied: yes.

## Metadata Checks

- Final GitHub URL: `https://github.com/XessX/prehoi-rank-hot3d`
- Final Zenodo DOI: `10.5281/zenodo.20736962`
- Final author spelling: Seyam Rahman Nayem
- Old Scientific Reports sparse 3D repository/DOI strings: absent from
  public-facing final submission files.
- Student IDs: absent from public-facing final submission files.
- Old PreHOI v0.1.0/v0.1.1 DOI strings: absent from public-facing final
  submission files.
- Unresolved editing markers and missing-citation markers: absent from
  public-facing final submission files.
- Unsupported superlative/proof/guarantee claim wording: absent from the
  generated DOCX/PDF under word-boundary scan.
- Final file QA checklist created:
  `paper/final_submission_files/final_file_qa_checklist.md`.

## Remaining Manual Tasks

- Visually inspect the DOCX in Word or equivalent.
- Visually inspect the PDF.
- Confirm whether MLWA requires figures/tables embedded, uploaded separately,
  or both.
- Confirm whether a graphical abstract is required or optional.
- Replace bracket placeholders such as the cover-letter date before submission.
- Confirm final HOT3D-Clips license/access wording against official sources.
- Confirm final APC/waiver/Research4Life details in the live submission system.
