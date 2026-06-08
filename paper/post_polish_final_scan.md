# Post-Polish Final Scan

Date: 2026-06-09

Status: completed after the author-voice polish pass. No numerical results,
citations, method claims, or limitations were changed during this scan.

## Files Scanned

- `paper/formatted_submission_draft/manuscript_formatted.md`
- `paper/formatted_submission_draft/cover_letter_formatted.md`
- `paper/formatted_submission_draft/highlights.md`
- `paper/formatted_submission_draft/data_code_availability.md`
- `paper/formatted_submission_draft/ethics_data_use_statement.md`
- `paper/exported_drafts/prehoi_rank_combined_draft.md`
- `paper/submission_package/`
- `paper/submission_readiness_checklist.md`

## Export Refresh

The combined draft was regenerated with:

```powershell
python scripts/export_submission_draft.py
```

Pandoc is still unavailable on PATH, so DOCX/PDF files were not created. The
combined Markdown draft remains current.

## Risky Wording Found and Fixed

The scan checked for:

- unresolved editing markers;
- missing-citation markers;
- unresolved reference-key placeholders;
- direct-label wording around proxy labels;
- benchmark-superiority phrasing;
- unsupported certainty language;
- complete-dataset wording that could imply full HOT3D evaluation.

Fixes applied:

- Synchronized `paper/submission_package/` manuscript, cover letter, highlights,
  data/code statement, ethics statement, and references with the polished
  formatted draft.
- Replaced stale package wording that described proxy labels as direct
  ground-truth-like labels with safer "direct HOT3D annotations" wording.
- Replaced package-facing benchmark-superiority language with cautious
  method/protocol wording.
- Removed optional commented citation placeholders from the submission-package
  references file by syncing it to the formatted draft references file.
- Reworded package audit text so it no longer contains literal checklist marker
  terms that are not part of the submission manuscript.

No remaining target-file hits were found for:

- direct ground-truth wording for proxy labels;
- benchmark-superiority phrasing;
- `proves`;
- `guarantees`;
- complete-HOT3D result claims;
- missing-citation markers;
- unresolved reference-key placeholders;
- unresolved editing markers.

## Intentional Placeholders Remaining

The following placeholders remain intentionally because they require human
author input:

- author placeholder block;
- corresponding author placeholder;
- affiliation fields;
- ORCID fields;
- CRediT contribution roles;
- conflict of interest confirmation;
- funding confirmation;
- acknowledgments;
- final repository/archive URL;
- final MLWA APC/Research4Life responsibility confirmation;
- final HOT3D-Clips license/access confirmation.

These placeholders are expected and should not be removed until the author
fill-in form is completed.

## Result Consistency

The formatted manuscript, exported combined draft, submission package, and
result tables consistently preserve the primary 50-clip result:

- Top-1: `0.7499 +/- 0.0450`
- Top-3: `0.9699 +/- 0.0161`
- MRR: `0.8605 +/- 0.0221`
- Pose MSE: `0.4301 +/- 0.0116`
- Pose MAE: `0.4102 +/- 0.0051`

They also preserve the 75-clip robustness framing in the concise comparison
table:

- Top-1: `0.7115 +/- 0.0571`
- Top-3: `0.9789 +/- 0.0009`
- MRR: `0.8340 +/- 0.0343`
- Pose MAE: `0.4676 +/- 0.0096`

The 50-clip protocol remains the primary controlled result. The 75-clip
protocol remains a robustness/scalability analysis on a broader but harder
split.

## Proxy and MPJPE Wording

- Proxy labels remain described as derived labels, not direct HOT3D
  annotations.
- MPJPE remains explicitly not reported.
- Pose metrics remain described as MANO/UmeTrack pose-parameter vector
  MAE/MSE.
- MPJPE mentions remain intentionally only where they explain a limitation or
  future work.

## Remaining Submission Blockers

- Human author metadata still needs to be filled.
- DOCX/PDF conversion remains pending because Pandoc is unavailable locally.
- Final MLWA APC/Research4Life verification must use final affiliations.
- Final HOT3D-Clips license/access wording must be confirmed before submission.
