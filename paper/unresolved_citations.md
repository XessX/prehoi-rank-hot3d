# Unresolved Citations

Status: citation-cleanup checkpoint.
Date: 2026-06-08.

The core dataset/model references used in the current manuscript have been
verified or partially verified. The items below still need manual source
selection before submission if the associated claims remain in the manuscript.

## Still Needed

| Placeholder | Proposed Key | Need | Current Action |
| --- | --- | --- | --- |
| `[contactposeTODO]` | `@contactposeTODO` | A verified contact/affordance reasoning reference. | Select ContactPose or another better-matched hand-object contact/affordance source. |
| `[activeObjectRankingTODO]` | `@activeObjectRankingTODO` | A verified active-object prediction or candidate-ranking reference. | Search egocentric active-object prediction and object-candidate scoring literature. |
| `[candidateRankingLossTODO]` | `@candidateRankingLossTODO` | A verified learning-to-rank or candidate-scoring methodological reference. | Add only if the method section needs a ranking-method citation beyond masked cross-entropy. |
| `[temporalLeakageTODO]` | `@temporalLeakageTODO` | A verified citation for temporal leakage, subject/clip-level splits, or temporal evaluation leakage. | Search video forecasting/evaluation protocol literature. |
| `@openclipTODO` | `@openclipTODO` | OpenCLIP/open-clip-torch software citation. | Needed only if CLIP/OpenCLIP implementation details stay in the final manuscript or supplement. |

## Partially Verified Dataset/Tooling Items

- `@hot3dtoolkit2026`: official GitHub toolkit verified, but no formal
  software citation was found in the checked documentation.
- `@hot3dclips2026`: official HOT3D-Clips README and Hugging Face dataset page
  verified, but no formal standalone citation was found. Current plan: cite the
  HOT3D paper for the dataset and HOT3D-Clips docs for format details.
- HOT3D-Clips license/access wording still needs a final official check before
  the data availability statement is submission-ready.

## Manuscript Placeholders Still Present

The following placeholders intentionally remain in the manuscript or expanded
related-work draft until source selection is complete:

- `[contactposeTODO]`
- `[activeObjectRankingTODO]`
- `[candidateRankingLossTODO]`
- `[temporalLeakageTODO]`

Do not replace these with real citation keys until the exact source is chosen
and verified.
