# PreHOI-Rank Pre-Submission Package

Status: pre-submission assembly draft, not submission-ready.

Target journal: Machine Learning with Applications.

Backup journal: PLOS ONE.

## Contents

- `manuscript_main.md`: current manuscript draft.
- `references.bib`: BibTeX scaffold and verified core references.
- `cover_letter.md`: draft cover letter.
- `data_code_availability.md`: draft data/code availability statement.
- `submission_checklist.md`: submission file checklist.
- `contribution_statement.md`: contribution statement.
- `conflict_of_interest_statement.md`: draft conflict of interest statement.
- `funding_statement.md`: draft funding statement.
- `ethics_data_use_statement.md`: draft ethics/data-use statement.
- `highlights.md`: draft journal-style highlights.
- `figures/`: PNG and PDF exports for Figures 1-5.
- `tables/`: manuscript table Markdown files.
- `package_audit.md`: package completeness and remaining follow-up audit.

## Result Framing

- 50-clip protocol: primary controlled paper-candidate result.
- 75-clip protocol: robustness/scalability check on a broader but harder local subset.
- Target-object labels: derived proxy labels, not direct HOT3D annotations.
- Pose metrics: MANO/UmeTrack pose-parameter vector MAE/MSE; MPJPE is not reported.
- Vision-language and PreHOI-Former variants: exploratory only.

## Official Verification Snapshot

Checked on 2026-06-09 from official/authoritative pages:

- Machine Learning with Applications is an Elsevier open-access journal focused
  on machine learning research and applications.
- The ScienceDirect journal page listed an APC of USD 2,460 excluding taxes at
  the time of checking.
- Elsevier Research4Life/waiver handling depends on the final author-group
  countries, institutional agreements, and exact author affiliations.
- HOT3D-Clips is documented by the official HOT3D Toolkit as a curated HOT3D
  WebDataset subset.
- The HOT3D-Clips README points to the complete HOT3D license. The license agreement
  identifies sequence/non-hand annotations as CC BY-SA, hand annotations as
  CC BY-NC-SA, and object model data as CC BY-SA with an added no-sale/product
  incorporation restriction.

These checks do not replace final author-side verification immediately before
submission.

## Not Submission-Ready Until

- Author names, affiliations, and contributions are finalized.
- `paper/author_information_template.md` is completed and confirmed by all
  authors.
- `paper/submission_metadata_template.md` is completed against the live
  submission form.
- Conflict of interest and funding statements are confirmed by all authors.
- HOT3D-Clips license/access wording is rechecked against official sources for
  the exact submitted manuscript and release artifacts.
- Machine Learning with Applications formatting, APC/tax status, institutional
  agreement coverage, and Research4Life route are verified using the final
  author list.
- Citation placeholders and optional unresolved citations are reviewed one final
  time after formatting and author details are inserted.

## Metadata Templates

Author information and submission metadata templates now live outside the
package root:

- `paper/author_information_template.md`
- `paper/submission_metadata_template.md`
- `paper/author_metadata_remaining_items.md`

These files are intentionally not final. They collect the human-provided
metadata needed before DOCX/PDF formatting or online submission.
