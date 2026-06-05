# Citation Verification Checklist

Use this checklist before converting citation placeholders into BibTeX.

## Per-Reference Verification

- [ ] Verify each paper title from the official paper page, publisher page, or
      arXiv page.
- [ ] Verify author list and author order.
- [ ] Verify year and venue.
- [ ] Verify DOI if available.
- [ ] Verify project-page URL and dataset URL.
- [ ] Verify whether a newer version supersedes the cited version.
- [ ] Add BibTeX entries only after verification.

## Dataset and Tooling Verification

- [ ] Verify HOT3D paper citation recommendation.
- [ ] Verify HOT3D toolkit citation recommendation.
- [ ] Verify HOT3D-Clips citation recommendation.
- [ ] Verify HOT3D-Clips license/access terms.
- [ ] Verify whether the BOP Challenge 2024 paper should be cited for
      HOT3D-Clips/WebDataset usage.
- [ ] Verify MANO/SMPL-X license requirements if hand-model conversion is used.
- [ ] Verify UmeTrack citation and relation to HOT3D annotations.
- [ ] Verify OpenCLIP or `open-clip-torch` software citation if CLIP ablations
      remain in the manuscript.

## Related-Work Gap Checks

- [ ] Add at least one verified citation for 3D hand-object interaction
      datasets.
- [ ] Add at least one verified citation for egocentric action anticipation.
- [ ] Add at least one verified citation for affordance/contact reasoning.
- [ ] Add at least one verified citation for active-object prediction or
      candidate ranking.
- [ ] Add at least one verified citation for temporal leakage or split design.
- [ ] Add at least one verified citation for repeated-seed/reproducibility
      reporting if the journal expects methodological justification.

## Journal Formatting

- [ ] Verify Machine Learning with Applications reference style.
- [ ] Verify whether numbered or author-year citations are required.
- [ ] Verify whether dataset/tool citations belong in references, footnotes, or
      data availability sections.
- [ ] Verify article type, word limits, figure limits, and supplementary
      material policy.
- [ ] Verify APC, waiver, or Research4Life route before submission.

## Current Placeholder Keys to Resolve

- [ ] `[HOT3D]`
- [ ] `[HOT3D-Clips]`
- [ ] `[MANO]`
- [ ] `[UmeTrack]`
- [ ] `[DexYCB]`
- [ ] `[HO3D]`
- [ ] `[AssemblyHands]`
- [ ] `[FPHA]`
- [ ] `[EPIC-KITCHENS]`
- [ ] `[CLIP]`
- [ ] `[Temporal leakage]`
- [ ] `[Affordance reasoning]`
- [ ] `[ActiveObjectRanking]`
- [ ] `[CandidateRankingLoss]`

## Current Citation Key Verification Table

| Citation Key | Verified | Source Checked | Remaining Action |
| --- | --- | --- | --- |
| `@hot3d2025` | yes | CVF Open Access HOT3D paper | Recheck final BibTeX formatting before submission. |
| `@hot3dtoolkit2026` | partial | Official GitHub toolkit | Verify formal software citation recommendation. |
| `@hot3dclips2026` | partial | Official HOT3D-Clips README | Verify formal standalone citation recommendation. |
| `@bop2024` | yes | arXiv page | Cite only if BOP/HOT3D-Clips challenge context remains. |
| `@dexycb2021` | yes | Official DexYCB project page | Recheck final BibTeX formatting. |
| `@ho3d2020` | yes | arXiv page and HO-3D repository citation | Recheck final BibTeX formatting. |
| `@ho3dv32021` | yes | arXiv page | Use only if discussing HO-3D v3/contact-region accuracy. |
| `@fpha2018` | yes | Official FPHA project page | Recheck final BibTeX formatting. |
| `@assemblyhands2023` | no | Project page title checked | Verify authors, venue, and BibTeX. |
| `@mano2017` | yes | arXiv metadata with journal DOI | Recheck final journal formatting. |
| `@umetrack2022` | yes | arXiv and citation page | Recheck exact author capitalization. |
| `@epickitchens2020` | partial | arXiv page | Verify complete author list and final venue. |
| `@clip2021` | yes | arXiv/Hugging Face paper metadata | Recheck ICML proceedings formatting. |
| `@mlwa2026` | yes | ScienceDirect journal page | Internal note only; not likely a manuscript citation. |
| `@activeObjectRankingTODO` | no | none | Find verified active-object/candidate-ranking paper. |
| `@candidateRankingLossTODO` | no | none | Find verified ranking/loss reference if needed. |
| `@temporalLeakageTODO` | no | none | Find verified temporal leakage or split-design reference. |
| `@contactposeTODO` | no | none | Verify ContactPose or another affordance/contact source. |
| `@openclipTODO` | no | none | Verify software citation if OpenCLIP remains in paper. |
