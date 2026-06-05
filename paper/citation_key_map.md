# Citation Key Map

This map connects manuscript placeholders to proposed BibTeX keys. Only replace
placeholders with citation-style keys where the mapping is clear. Entries marked
TODO/UNVERIFIED must be checked before submission.

| Placeholder | Proposed BibTeX key | Verified status | Source URL / note | Used in |
| --- | --- | --- | --- | --- |
| `[HOT3D]` | `@hot3d2025` | verified | https://openaccess.thecvf.com/content/CVPR2025/papers/Banerjee_HOT3D_Hand_and_Object_Tracking_in_3D_from_Egocentric_Multi-View_CVPR_2025_paper.pdf | Abstract, Dataset, Proxy label, Related Work |
| `[HOT3D-Clips]` | `@hot3dclips2026` | verified as official docs; formal citation needs recheck | https://github.com/facebookresearch/hot3d/blob/main/hot3d/clips/README.md | Abstract, Dataset, Limitations |
| `[HOT3DToolkit]` | `@hot3dtoolkit2026` | verified as official repo; formal citation needs recheck | https://github.com/facebookresearch/hot3d | Dataset/tooling notes |
| `[BOP]` / `[BOP2024]` | `@bop2024` | verified | https://arxiv.org/abs/2504.02812 | HOT3D-Clips/BOP context only |
| `[MANO]` | `@mano2017` | verified | https://arxiv.org/abs/2201.02610 | Pose representation, Dataset/Method |
| `[UmeTrack]` | `@umetrack2022` | verified | https://arxiv.org/abs/2211.00099 | Pose representation |
| `[DexYCB]` | `@dexycb2021` | verified | https://dex-ycb.github.io/ | Related Work |
| `[HO3D]` | `@ho3d2020` | verified | https://arxiv.org/abs/1907.01481 | Related Work |
| `[HO3Dv3]` | `@ho3dv32021` | verified | https://arxiv.org/abs/2107.00887 | Optional annotation/contact discussion |
| `[FPHA]` | `@fpha2018` | verified | https://kcvl-kaist.github.io/FPHA/ | Related Work |
| `[AssemblyHands]` | `@assemblyhands2023` | partial/TODO | https://assemblyhands.github.io/ | Related Work |
| `[EPIC-KITCHENS]` | `@epickitchens2020` | partial/TODO | https://arxiv.org/abs/2005.00343 | Egocentric forecasting related work |
| `[CLIP]` | `@clip2021` | verified | https://arxiv.org/abs/2103.00020 | Vision-language ablation discussion |
| `[Affordance reasoning]` | `@contactposeTODO` or another verified affordance/contact paper | TODO/UNVERIFIED | Need exact source | Proxy motivation, Related Work |
| `[ActiveObjectRanking]` | `@activeObjectRankingTODO` | TODO/UNVERIFIED | Need active-object/candidate-ranking source | Candidate-ranking related work and method framing |
| `[CandidateRankingLoss]` | `@candidateRankingLossTODO` | TODO/UNVERIFIED | Need learning-to-rank or masked candidate-scoring source | Candidate-ranking method discussion |
| `[Temporal leakage]` | `@temporalLeakageTODO` | TODO/UNVERIFIED | Need temporal leakage/split-design source | Experimental protocol and evaluation safety |
| `[MLWA]` | `@mlwa2026` | verified as journal info | https://www.sciencedirect.com/journal/machine-learning-with-applications | Internal target-journal notes only |

## Replacement Policy

- Replace verified placeholders in manuscript prose with citation-style keys,
  e.g. `[HOT3D]` to `[@hot3d2025]`.
- Keep TODO placeholders in square brackets until a real source is selected.
- Do not cite MLWA in the manuscript body unless the submission plan requires
  discussion of target journal scope or article type.
- Do not cite BOP unless the text explicitly discusses HOT3D-Clips challenge
  usage or the BOP benchmark context.
