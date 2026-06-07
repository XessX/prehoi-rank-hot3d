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

- [x] `[HOT3D]`
- [ ] `[HOT3D-Clips]` formal standalone citation, if one exists.
- [x] `[MANO]`
- [x] `[UmeTrack]`
- [x] `[DexYCB]`
- [x] `[HO3D]`
- [x] `[AssemblyHands]`
- [x] `[FPHA]`
- [x] `[EPIC-KITCHENS]`
- [x] `[CLIP]`
- [ ] `[Temporal leakage]`
- [ ] `[Affordance reasoning]`
- [ ] `[ActiveObjectRanking]`
- [ ] `[CandidateRankingLoss]`

## Current Citation Key Verification Table

| Citation Key | Verified | Source Checked | Remaining Action |
| --- | --- | --- | --- |
| `@hot3d2025` | verified | CVF Open Access HOT3D paper | Complete; recheck journal style before submission. |
| `@hot3dtoolkit2026` | partially verified | Official GitHub toolkit | No formal software citation found; cite with HOT3D paper unless toolkit citation is later provided. |
| `@hot3dclips2026` | partially verified | Official HOT3D-Clips README and Hugging Face dataset README | No formal standalone citation found; cite with HOT3D paper unless standalone citation is later provided. |
| `@bop2024` | verified | arXiv page | Cite only if BOP/HOT3D-Clips challenge context remains. |
| `@dexycb2021` | verified | CVF Open Access paper page | Complete; recheck journal style before submission. |
| `@ho3d2020` | verified | CVF Open Access paper page | Complete; recheck journal style before submission. |
| `@ho3dv32021` | verified | arXiv page | Use only if discussing HO-3D v3/contact-region accuracy. |
| `@fpha2018` | verified | CVF Open Access paper page and author project page | Complete; recheck journal style before submission. |
| `@assemblyhands2023` | verified | Official AssemblyHands project page and arXiv | Complete; recheck journal style before submission. |
| `@mano2017` | verified | MPI/MANO publication page with DOI and BibTeX | Complete; recheck journal style before submission. |
| `@umetrack2022` | verified | arXiv and DOI metadata | Complete; recheck journal style before submission. |
| `@epickitchens2020` | verified | Official EPIC-KITCHENS citation page and PubMed DOI record | Complete; recheck journal style before submission. |
| `@clip2021` | verified | PMLR ICML paper page | Complete; recheck journal style before submission. |
| `@mlwa2026` | verified | ScienceDirect journal page | Internal note only; not likely a manuscript citation. |
| `@activeObjectRankingTODO` | unresolved | none selected | Find verified active-object/candidate-ranking paper or remove placeholder. |
| `@candidateRankingLossTODO` | unresolved | none selected | Find verified ranking/loss reference if needed. |
| `@temporalLeakageTODO` | unresolved | none selected | Find verified temporal leakage or split-design reference. |
| `@contactposeTODO` | unresolved | none selected | Verify ContactPose or another affordance/contact source. |
| `@openclipTODO` | unresolved | none selected | Verify software citation if OpenCLIP remains in paper or supplement. |
