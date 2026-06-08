# Paraphrase and Author-Voice Audit

Date: 2026-06-09

Status: academic voice polish completed for the formatted draft package. This
was a readability and author-voice pass, not a scientific or numerical revision.

## Files Polished

- `paper/formatted_submission_draft/manuscript_formatted.md`
- `paper/formatted_submission_draft/cover_letter_formatted.md`
- `paper/formatted_submission_draft/highlights.md`
- `paper/formatted_submission_draft/data_code_availability.md`
- `paper/formatted_submission_draft/ethics_data_use_statement.md`

## Wording Types Improved

- Replaced generic phrasing with more direct academic prose, especially in the
  abstract, introduction, discussion, and conclusion.
- Reduced repeated sentence openings around "This work", "The model", and "The
  manuscript".
- Improved transitions between problem motivation, candidate-ranking
  formulation, leakage controls, and limitations.
- Tightened cautious claims so that the paper reads as a method/protocol
  contribution rather than a benchmark-superiority claim.
- Replaced potentially ambiguous direct-label negations with clearer wording
  such as "human-annotated" and "official annotation" where proxy labels were
  discussed.
- Corrected section-numbering artifacts in the formatted manuscript, including
  duplicated method subsection numbering and result subsection labels.

## Preservation Checks

- Numerical results were preserved.
- Citations were preserved.
- Figure and table references were preserved.
- The 50-clip protocol remains the primary result.
- The 75-clip protocol remains a robustness/scalability analysis.
- Proxy labels remain described as derived labels, not direct annotations.
- MPJPE remains not reported.
- Pose metrics remain described as MANO/UmeTrack pose-parameter vector MSE/MAE.
- Vision-language and PreHOI-Former variants remain exploratory only.
- Limitations around proxy labels, local subsets, split imbalance, and pose
  metrics were preserved.

## Manual Author Checks Still Needed

- Confirm that the abstract tone matches the authors' preferred level of
  caution.
- Confirm whether the cover letter should say "research article" or a different
  article type after checking the live MLWA submission system.
- Confirm the final data/code availability wording after HOT3D-Clips
  license/access review.
- Fill author names, affiliations, corresponding author details, funding,
  acknowledgments, and CRediT roles before final DOCX/PDF conversion.

## Risky Wording Scan Summary

The polished files were scanned for:

`ground truth`, `state-of-the-art`, `proves`, `guarantees`, `full HOT3D`,
`MPJPE`, `citation needed`, `TODO`, `TBD`, and `FIXME`.

Results:

- No remaining hits for `ground truth`, `state-of-the-art`, `proves`,
  `guarantees`, `full HOT3D`, `citation needed`, `TODO`, `TBD`, or `FIXME` in
  the polished target files.
- `MPJPE` remains intentionally where the manuscript states that MPJPE is not
  reported or is future work pending validated conversion.
