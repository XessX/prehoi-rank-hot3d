# Citation Key Map

This map connects manuscript placeholders to proposed BibTeX keys. Only replace
placeholders with citation-style keys where the mapping is clear. Entries marked
TODO/UNRESOLVED must be checked before submission.

| Placeholder | Proposed BibTeX key | Verified status | Source URL / note | Used in |
| --- | --- | --- | --- | --- |
| `[HOT3D]` | `@hot3d2025` | verified | https://openaccess.thecvf.com/content/CVPR2025/html/Banerjee_HOT3D_Hand_and_Object_Tracking_in_3D_from_Egocentric_Multi-View_CVPR_2025_paper.html | Abstract, Dataset, Proxy label, Related Work |
| `[HOT3D-Clips]` | `@hot3dclips2026` | partially verified | https://github.com/facebookresearch/hot3d/blob/main/hot3d/clips/README.md | Abstract, Dataset, Limitations |
| `[HOT3DToolkit]` | `@hot3dtoolkit2026` | partially verified | https://github.com/facebookresearch/hot3d | Dataset/tooling notes |
| `[BOP]` / `[BOP2024]` | `@bop2024` | verified | https://arxiv.org/abs/2504.02812 | HOT3D-Clips/BOP context only |
| `[MANO]` | `@mano2017` | verified | https://is.mpg.de/ps/publications/embodiedhands | Pose representation, Dataset/Method |
| `[UmeTrack]` | `@umetrack2022` | verified | https://arxiv.org/abs/2211.00099 and DOI 10.1145/3550469.3555378 | Pose representation |
| `[DexYCB]` | `@dexycb2021` | verified | https://openaccess.thecvf.com/content/CVPR2021/html/Chao_DexYCB_A_Benchmark_for_Capturing_Hand_Grasping_of_Objects_CVPR_2021_paper.html | Related Work |
| `[HO3D]` | `@ho3d2020` | verified | https://openaccess.thecvf.com/content_CVPR_2020/html/Hampali_HOnnotate_A_Method_for_3D_Annotation_of_Hand_and_Object_CVPR_2020_paper.html | Related Work |
| `[HO3Dv3]` | `@ho3dv32021` | verified | https://arxiv.org/abs/2107.00887 | Optional annotation/contact discussion |
| `[FPHA]` | `@fpha2018` | verified | https://openaccess.thecvf.com/content_cvpr_2018/html/Garcia-Hernando_First-Person_Hand_Action_CVPR_2018_paper.html | Related Work |
| `[AssemblyHands]` | `@assemblyhands2023` | verified | https://assemblyhands.github.io/ | Related Work |
| `[EPIC-KITCHENS]` | `@epickitchens2020` | verified | https://epic-kitchens.github.io/2022.html | Egocentric forecasting related work |
| `[CLIP]` | `@clip2021` | verified | https://proceedings.mlr.press/v139/radford21a.html | Vision-language ablation discussion |
| `[Affordance reasoning]` / `[contactposeTODO]` | `@contactposeTODO` or another verified affordance/contact paper | TODO/UNRESOLVED | Need exact source | Proxy motivation, Related Work |
| `[ActiveObjectRanking]` / `[activeObjectRankingTODO]` | `@activeObjectRankingTODO` | TODO/UNRESOLVED | Need active-object/candidate-ranking source | Candidate-ranking related work and method framing |
| `[CandidateRankingLoss]` / `[candidateRankingLossTODO]` | `@candidateRankingLossTODO` | TODO/UNRESOLVED | Need learning-to-rank or masked candidate-scoring source | Candidate-ranking method discussion |
| `[Temporal leakage]` / `[temporalLeakageTODO]` | `@temporalLeakageTODO` | TODO/UNRESOLVED | Need temporal leakage/split-design source | Experimental protocol and evaluation safety |
| `[MLWA]` | `@mlwa2026` | verified as journal info | https://www.sciencedirect.com/journal/machine-learning-with-applications | Internal target-journal notes only |

## Replacement Policy

- Replace verified placeholders in manuscript prose with citation-style keys,
  e.g. `[HOT3D]` to `[@hot3d2025]`.
- Keep TODO placeholders in square brackets until a real source is selected.
- Do not cite MLWA in the manuscript body unless the submission plan requires
  discussion of target journal scope or article type.
- Do not cite BOP unless the text explicitly discusses HOT3D-Clips challenge
  usage or the BOP benchmark context.
