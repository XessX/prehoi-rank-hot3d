# Zenodo Release Plan

Status: prepared for a future GitHub/Zenodo software archive. No DOI has been
created or inserted yet.

Target repository:
`https://github.com/XessX/prehoi-rank-hot3d`

Planned release tag:
`v0.1.0`

Current citation/release metadata files:

- `CITATION.cff`
- `.zenodo.json`
- `paper/release_v0_1_0_notes.md`

## Human Release Steps

1. Log in to Zenodo with the GitHub account that has access to
   `XessX/prehoi-rank-hot3d`.
2. Open Zenodo GitHub settings.
3. Sync repositories if the new repository does not appear.
4. Enable Zenodo archiving for `XessX/prehoi-rank-hot3d`.
5. Confirm the repository contains no raw HOT3D-Clips data, processed outputs,
   logs, checkpoints, caches, or model weights.
6. Confirm the repository contains `CITATION.cff` and `.zenodo.json`.
7. Create a GitHub release, recommended tag `v0.1.0`.
8. Use the release notes from `paper/release_v0_1_0_notes.md`.
9. Wait for Zenodo to archive the GitHub release.
10. Copy the generated Zenodo DOI.
11. Update `README.md`, manuscript data/code availability, submission package,
    exported draft, `CITATION.cff` if needed, and repository checklist with the
    generated DOI.
12. Commit and push the DOI update.

## Release Safety Requirements

- Do not use the old Scientific Reports sparse 3D Gaussian Splatting GitHub
  repository link.
- Do not use the old Scientific Reports Zenodo DOI.
- Do not include raw HOT3D-Clips data.
- Do not include generated processed HOT3D data, logs, caches, checkpoints, or
  weights.
- Keep target-object labels described as derived proxy labels.
- Keep MPJPE as not reported.
- Keep the 50-clip result primary and the 75-clip result as
  robustness/scalability analysis.

## After Zenodo DOI Creation

Update these files with the generated DOI:

- `README.md`
- `paper/formatted_submission_draft/data_code_availability.md`
- `paper/formatted_submission_draft/manuscript_formatted.md`
- `paper/submission_package/data_code_availability.md`
- `paper/submission_package/manuscript_main.md`
- `paper/exported_drafts/prehoi_rank_combined_draft.md`
- `paper/repository_release_checklist.md`
- `paper/submission_readiness_checklist.md`

Do not invent a DOI before Zenodo creates it.
