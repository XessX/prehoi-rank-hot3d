# Final Pre-Formatting Submission Audit

Date: 2026-06-18

Status: completed before DOCX/PDF formatting. This audit checks the final
GitHub/Zenodo release metadata, author metadata, data-use wording, journal-route
wording, and remaining formatting risks. It does not change numerical results or
scientific claims.

## GitHub and DOI Final Status

- Final GitHub repository: `https://github.com/XessX/prehoi-rank-hot3d`
- Final release: `v0.1.2`
- Final Zenodo DOI: `10.5281/zenodo.20736962`
- `README.md`, `CITATION.cff`, `.zenodo.json`, formatted manuscript files,
  submission-package files, and the exported combined draft use the final DOI.
- The old PreHOI `v0.1.0` DOI is not used for public citation.
- The `v0.1.1` DOI is superseded because final co-author spelling was corrected
  after that release.
- Old DOI strings remain only in internal notes where they are explicitly marked
  as not used or superseded.

## Author Consent Final Status

Final author list:

1. Al Jubair Hossain
2. ASIF SHAHRIAR SIAM
3. MD. ABUBOKOR SIDDIK ROJAN
4. Maria Sultana Alif
5. Seyam Rahman Nayem

Author metadata status:

- Student co-author consent: complete.
- Student CRediT confirmations: complete.
- Final co-author spelling: complete.
- Student IDs: retained only in internal author metadata files, not in
  public-facing manuscript/package files.
- Student ORCIDs: not provided unless later supplied by the authors.

## HOT3D/HOT3D-Clips Wording Status

Local official notes and saved package documentation support the current cautious
wording:

- raw HOT3D-Clips data is not redistributed;
- users must obtain HOT3D-Clips from official HOT3D/HOT3D-Clips sources;
- users must follow official access, license, and citation terms;
- derived proxy labels are generated locally from downloaded data;
- processed outputs, logs, checkpoints, and derived indexes should be shared
  only if allowed by the dataset terms.

The current manuscript/package wording is therefore acceptable for a
pre-formatting draft. A final author-side check against the official
HOT3D/HOT3D-Clips access and license pages is still required immediately before
submission or public artifact sharing.

## MLWA/APC/Research4Life Status

The existing journal-route notes identify Machine Learning with Applications as
the target journal and record an earlier official-source check of scope, article
type basics, APC route, and Research4Life/waiver uncertainty.

Current status:

- target journal remains Machine Learning with Applications;
- PLOS ONE remains a backup route only;
- final APC, taxes, institutional agreement coverage, waiver eligibility, and
  Research4Life route cannot be concluded from local notes alone;
- final author-side verification is required using the live Elsevier submission
  system, current Elsevier policy, and the final AIUB/Bangladesh affiliation.

## Result and Claim Consistency

- 50-clip protocol remains the primary result.
- 75-clip protocol remains a robustness/scalability analysis.
- Target-object labels are described as derived proxy labels, not ground truth.
- MPJPE is not reported.
- Pose metrics remain MANO/UmeTrack pose-parameter vector MAE/MSE.
- Vision-language and PreHOI-Former variants remain exploratory.
- No numerical results were changed during this audit.

## Remaining Formatting Tasks

- Convert the formatted Markdown draft to DOCX/PDF after the target-journal
  formatting requirements are checked.
- Confirm whether figures and tables should be embedded or uploaded separately.
- Confirm whether a graphical abstract is required or optional.
- Replace cover-letter bracket placeholders such as the final date.
- Run a final post-formatting placeholder and public-facing scan before upload.

## Final Risks

- HOT3D-Clips access/license wording must be checked against official sources
  immediately before submission.
- MLWA APC/Research4Life/waiver status must be checked in the live submission
  context.
- DOCX/PDF conversion has not been completed locally because Pandoc is not
  available on PATH.
- Optional unresolved research improvements, such as MPJPE-style evaluation,
  remain future work unless official conversion dependencies/assets are
  validated.
