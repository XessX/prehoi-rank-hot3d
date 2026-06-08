# Pre-Submission Remaining Tasks

Status: remaining tasks after the final placeholder scan and official-source
verification pass on 2026-06-09.

## Must Complete Before Submission

- Replace cover-letter placeholders with final corresponding author name,
  affiliation, and contact details.
- Prepare the title page with final author names, affiliations, ORCID details if
  used, and corresponding author details.
- Confirm author contributions with all authors.
- Confirm the conflict of interest statement with all authors.
- Confirm the funding statement with all authors.
- Complete final Machine Learning with Applications formatting checks against
  the current Guide for Authors, including reference style, figure/table
  requirements, and submission-file expectations.
- Confirm current APC, taxes, institutional agreement coverage, and any waiver
  or Research4Life route using the exact final author list and affiliations.
- Confirm HOT3D-Clips access/license wording from official sources immediately
  before submission, including any limits on derived index/log/checkpoint
  sharing.
- Ensure no raw HOT3D-Clips data, tar shards, downloaded assets, or restricted
  model files are included in a public release.
- Run a final placeholder scan over the submission package after author details
  and formatting are inserted.
- Confirm every figure and table is cited in the manuscript and every cited
  figure/table file exists in the submission package.
- Confirm every in-text citation appears in `references.bib` and every required
  bibliography entry is cited.

## Recommended But Optional

- Add MPJPE-style joint metrics only if official MANO/UmeTrack conversion
  dependencies and required model assets are installed and validated.
- Add another fair baseline only if it can be run under the same clip-level
  split, `stable_uid` candidate order, and no-forecast-input protocol.
- Prepare a graphical abstract if Machine Learning with Applications requests
  or encourages one.
- Create a public code-release tag or archived artifact after removing local
  dataset paths and confirming license constraints.
- Add a short supplementary note that documents exact local shard IDs if allowed
  by the dataset license and useful for reproducibility.

## Not Needed Now

- Do not expand beyond 75 HOT3D-Clips shards unless reviewers request it or the
  split strategy changes.
- Do not make the vision-language or PreHOI-Former variants the main claim based
  on current evidence.
- Do not report MPJPE or 3D-joint errors until conversion is validated.
- Do not claim state-of-the-art performance.
- Do not describe derived proxy labels as ground truth.
- Do not redistribute HOT3D-Clips raw data with the code package.
