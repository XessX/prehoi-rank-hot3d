# Unresolved Citations

Status: citation-cleanup checkpoint.
Date: 2026-06-08.

The core dataset/model references used in the current manuscript have been
verified or partially verified. This file now tracks only optional or unresolved
items that still need manual source selection before submission if the
associated claims remain in the manuscript.

## Resolved in This Pass

| Former Placeholder | Resolved Key | Source |
| --- | --- | --- |
| `[contactposeTODO]` | `@contactpose2020` | Official ContactPose project page / ECCV 2020 metadata |
| `[candidateRankingLossTODO]` | `@burges2005ranknet` | ACM DOI page / Microsoft Research page |
| `[temporalLeakageTODO]` | `@kaufman2012leakage` | ACM DOI metadata / Tel Aviv University publication page |

## Still Needed

| Placeholder | Proposed Key | Need | Current Action |
| --- | --- | --- | --- |
| `[activeObjectRankingTODO]` | `@activeObjectRankingTODO` | A domain-specific active-object prediction or egocentric object-candidate scoring reference. | Optional. Add only if the related-work section expands beyond the current general learning-to-rank framing. |
| `@openclipTODO` | `@openclipTODO` | OpenCLIP/open-clip-torch software citation. | Optional. Not needed in the current manuscript, methods draft, or data/code availability draft; verify only if OpenCLIP implementation details appear in supplement/code-citation notes. |

## Partially Verified Dataset/Tooling Items

- `@hot3dtoolkit2026`: official GitHub toolkit verified, but no formal
  software citation was found in the checked documentation.
- `@hot3dclips2026`: official HOT3D-Clips README and Hugging Face dataset page
  verified, but no formal standalone citation was found. Current plan: cite the
  HOT3D paper for the dataset and HOT3D-Clips docs for format details.
- HOT3D-Clips license/access wording still needs a final official check before
  the data availability statement is submission-ready.

## Manuscript Placeholders Still Present

No required unresolved citation placeholders should remain in the current
manuscript or expanded related-work draft after this pass. Re-run `rg` before
submission to confirm.
