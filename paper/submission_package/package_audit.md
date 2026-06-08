# Submission Package Audit

Date: 2026-06-09

Status: assembled pre-submission package. This package is not submission-ready until final author, journal, formatting, license/access, and APC checks are completed.

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

## Remaining TODOs

- Final journal formatting.
- Final author information and author contribution details.
- Author confirmation of conflict of interest and funding statements.
- Final Machine Learning with Applications APC/Research4Life route verification.
- Final HOT3D-Clips license/access wording.
- Final citation placeholder scan before submission.
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
