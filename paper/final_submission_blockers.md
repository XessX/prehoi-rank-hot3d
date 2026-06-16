# Final Submission Blockers

Status: remaining blockers before real submission. This list intentionally
excludes optional research improvements and focuses only on what blocks a real
journal upload.

## Blockers

1. **Final multi-author consent and contribution confirmation pending**

   Five-author metadata has been added. Before submission, all authors must
   confirm author order, consent to submission, and CRediT roles. Student
   co-author roles are currently proposed and must be confirmed by the authors.

2. **Final archive citation check before submission**

   The PreHOI-Rank repository is available at
   `https://github.com/XessX/prehoi-rank-hot3d`, and the corrected `v0.1.1`
   Zenodo archive DOI is `10.5281/zenodo.20722666`. Before submission, confirm
   that the DOI resolves to the intended repository release. Do not reuse the
   Scientific Reports sparse 3D Gaussian Splatting GitHub or Zenodo links for
   this paper.

3. **Final journal/APC/Research4Life verification depends on live submission context**

   The official-source route has been checked, but the final APC, taxes,
   institutional agreement coverage, waiver route, and Research4Life eligibility
   must be verified using the filled AIUB/Bangladesh affiliation and the live
   submission system.

4. **Final HOT3D-Clips license/access wording**

   The current wording is cautious, but the final manuscript and any public code
   release need one last official HOT3D-Clips license/access check, especially
   for derived sample indexes, logs, checkpoints, and clip-selection metadata.

5. **DOCX/PDF conversion pending**

   The combined Markdown draft is available, but DOCX/PDF export was not
   produced because Pandoc is not available locally. Install/enable a converter
   or convert manually after metadata is finalized.

6. **Final post-fill placeholder scan pending**

   After repository, APC, license, journal metadata, or author confirmations are
   filled, rerun the placeholder scan over the formatted submission draft and
   exported files before upload.

## Not Current Blockers

- No additional experiments are required before final submission metadata is
  filled.
- MPJPE remains optional unless the validated MANO/UmeTrack conversion path is
  solved.
- Further data expansion beyond 75 clips is not needed unless reviewers request
  it.
- Vision-language and PreHOI-Former variants should remain exploratory.
