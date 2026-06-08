# Submission Package Audit

Date: 2026-06-09

Status: assembled pre-submission package. This package is not submission-ready
until final author, journal, formatting, license/access, and APC checks are
completed.

## Expected Files

| File | Status |
| --- | --- |
| `manuscript_main.md` | present |
| `references.bib` | present |
| `cover_letter.md` | present |
| `data_code_availability.md` | present |
| `submission_checklist.md` | present |
| `contribution_statement.md` | present |
| `conflict_of_interest_statement.md` | present, author confirmation needed |
| `funding_statement.md` | present, author confirmation needed |
| `ethics_data_use_statement.md` | present |
| `highlights.md` | present |
| `README_submission_package.md` | present |

## Figures

Figures are copied under `paper/submission_package/figures/`.

Expected figure exports:

- `fig1_problem_overview.png`
- `fig1_problem_overview.pdf`
- `fig2_proxy_label_generation.png`
- `fig2_proxy_label_generation.pdf`
- `fig3_prehoi_rank_architecture.png`
- `fig3_prehoi_rank_architecture.pdf`
- `fig4_protocol_safety.png`
- `fig4_protocol_safety.pdf`
- `fig5_25clip_vs_50clip_results.png`
- `fig5_25clip_vs_50clip_results.pdf`

Status: all expected figure files are present.

## Tables

Tables are copied under `paper/submission_package/tables/`.

- `results_table_prehoi_rank.md`
- `protocol_safety_table.md`

Status: all expected table files are present.

## References and Citation Checks

- `references.bib` is present in the package.
- The unresolved citation tracker remains outside the package at `paper/unresolved_citations.md`.
- Current unresolved items are optional or partially verified documentation/tooling references, not required manuscript placeholders.

## Placeholder Scan

The final placeholder scan on 2026-06-09 found no `TODO`, `FIXME`, `TBD`,
`citation needed`, `[REF-*]`, or generic placeholder markers in
`manuscript_main.md`.

Expected pre-submission placeholders remain:

- cover-letter corresponding author name and affiliation;
- author confirmation for conflict of interest and funding statements;
- final HOT3D-Clips license/access wording in the data/code statement;
- optional commented citation TODOs in `references.bib` that are not cited in
  the current manuscript.

Planning files outside the submission package still contain TODO/checklist
language. These are not part of the current submission manuscript.

## Official-Source Verification Snapshot

Checked on 2026-06-09:

- Machine Learning with Applications is listed by ScienceDirect as a
  peer-reviewed open-access journal focused on machine learning research and
  applications. The page lists regular papers and technical notes among accepted
  article types and lists the APC as USD 2,460 excluding taxes.
- The MLWA Guide for Authors requires a designated corresponding author,
  complete uploaded manuscript files including figure/table material as
  relevant, mutually consistent in-text citations and references, permission for
  copyrighted third-party material, and author responsibility for APC payment if
  accepted unless covered by an institution or funder. The guide lists APA 7th
  as the reference style.
- Elsevier's Research4Life/open-access pages indicate that APC waiver/discount
  handling depends on author-group countries and that final eligibility cannot
  be concluded without the exact author affiliations.
- The HOT3D Toolkit identifies HOT3D-Clips as a curated HOT3D subset in
  WebDataset format. The HOT3D-Clips README says the clips use the same license
  as the full HOT3D dataset. The HOT3D license agreement separates sequence data
  and non-hand annotations under CC BY-SA, hand annotations under CC BY-NC-SA,
  and object model data under CC BY-SA with an added no-sale/product-use
  restriction.

Final author-side checks remain required because APC/tax status, Research4Life
eligibility, submission-file requirements, and dataset license wording can
depend on the exact author list, institution, and submitted artifact.

## Remaining TODOs

- Final journal formatting.
- Final author information and author contribution details.
- Author confirmation of conflict of interest and funding statements.
- Final author-side Machine Learning with Applications APC/tax/institutional
  agreement/Research4Life route verification.
- Final HOT3D-Clips license/access wording for the exact manuscript and release
  artifacts.
- Final citation placeholder scan after author details and formatting are
  inserted.
- Optional MPJPE-style 3D-joint evaluation only if official conversion dependencies/assets are validated.
- Optional stronger fair baseline if feasible under the same leakage/order-safety protocol.

## Safety Framing Check

- 50-clip result remains the primary controlled result.
- 75-clip result is described as a robustness/scalability check.
- Target-object labels are derived proxy labels, not direct HOT3D ground truth.
- MPJPE is not reported.
- Candidate order remains `stable_uid`.
- Valid runs require `input_uses_forecast_frame=false`.
- Vision-language and PreHOI-Former variants remain exploratory.
