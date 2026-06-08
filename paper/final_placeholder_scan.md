# Final Placeholder and Official-Source Scan

Date checked: 2026-06-09

Status: completed for the current pre-submission package. The package is still
not submission-ready because final author details, author confirmations, final
journal formatting, APC/Research4Life eligibility, and final HOT3D-Clips
license/access wording must be confirmed by the authors before upload.

## Scan Commands

The following local scans were run:

```powershell
rg -n -i "TODO|FIXME|TBD|citation needed|placeholder|verify|APC|Research4Life|license|author confirmation|affiliation|corresponding author" paper
rg -n -i "TODO|FIXME|TBD|citation needed|\[REF-|placeholder" paper\submission_package\manuscript_main.md paper\manuscript_prehoi_rank_draft.md paper\related_work_expanded_draft.md
rg -n -i "TODO|FIXME|TBD|citation needed|placeholder|verify|APC|Research4Life|license|author confirmation|affiliation|corresponding author" paper\submission_package
```

## Submission Package Integrity

| Item | Status |
| --- | --- |
| `paper/submission_package/manuscript_main.md` | present |
| `paper/submission_package/references.bib` | present |
| `paper/submission_package/highlights.md` | present |
| `paper/submission_package/package_audit.md` | present |
| Cover letter, data/code, checklist, contribution, COI, funding, ethics statements | present |
| Figure files | 10 files present: PNG and PDF for Figures 1-5 |
| Table files | 2 files present |

## Current Manuscript Placeholder Status

- No `TODO`, `FIXME`, `TBD`, `citation needed`, `[REF-*]`, or generic
  placeholder markers were found in `paper/submission_package/manuscript_main.md`
  or `paper/manuscript_prehoi_rank_draft.md`.
- `paper/related_work_expanded_draft.md` still contains a planning note that the
  draft originally used placeholders while bibliographic details were being
  verified. This is outside the submission package manuscript.
- `paper/manuscript.md` is an older scaffold with TODO markers. It should not be
  used as the submission manuscript.

## Submission Package Placeholders and Warnings

The following items remain intentionally unresolved and must be completed before
submission:

- `paper/submission_package/cover_letter.md` contains bracketed placeholders for
  corresponding author name and affiliation.
- `paper/submission_package/conflict_of_interest_statement.md` and
  `paper/submission_package/funding_statement.md` are drafts that require author
  confirmation.
- `paper/submission_package/data_code_availability.md` asks for final
  HOT3D-Clips license/access verification before submission.
- `paper/submission_package/references.bib` contains commented optional TODO
  blocks for active-object ranking and OpenCLIP citations. These are not cited
  in the current manuscript and should either remain commented or be removed
  during final cleanup.

## Official-Source Verification Snapshot

This check used official or authoritative pages only.

### Machine Learning with Applications

- The official ScienceDirect journal page identifies Machine Learning with
  Applications as a peer-reviewed open-access journal focused on machine
  learning research and applications, including computer vision and related
  applied ML topics.
- The same page states that MLWA accepts regular papers and technical notes.
- The journal page lists the article publishing charge as USD 2,460 excluding
  taxes on 2026-06-09.
- The MLWA Guide for Authors states that one corresponding author must be
  designated, uploaded files must include figures/tables/captions as relevant,
  references must be mutually consistent, permissions must be obtained for
  copyrighted material, and authors are responsible for the APC if an open
  access article is accepted unless covered by an institution or funder.
- The Guide for Authors lists APA 7th as the reference style.

Final author-side verification is still required because article charges,
taxes, submission-file expectations, and editorial policies can change.

### APC and Research4Life

- Elsevier's open-access information says institutional/funder agreements may
  pay or discount APCs.
- Elsevier's Research4Life waiver language is based on author-group countries:
  all Group A author groups may receive a full waiver, all Group B or mixed
  Group A/B author groups may receive a discount, and inclusion of a
  non-Research4Life author group can prevent that Research4Life waiver/discount.
- Elsevier's waiver support page says individual waiver requests may be
  considered case-by-case for genuine need, with priority for authors from
  Research4Life-eligible countries.

Final Research4Life/APC eligibility cannot be concluded until the exact author
list, author affiliations, corresponding author, institutional agreements, and
tax context are known.

### HOT3D and HOT3D-Clips

- The official HOT3D Toolkit repository describes HOT3D as an egocentric 3D
  hand/object tracking dataset and states that HOT3D-Clips is a curated HOT3D
  subset in WebDataset format.
- The official HOT3D-Clips README states that HOT3D-Clips is distributed under
  the same license as the full HOT3D dataset.
- The HOT3D Dataset License Agreement states that sequence data and annotations
  excluding hand annotations are CC BY-SA, hand annotations are CC BY-NC-SA, and
  3D object model data are CC BY-SA with an added no-sale/product-incorporation
  restriction.

Final official HOT3D-Clips access/license confirmation is required before
submission, especially for exact data-use wording, derived-output sharing, and
any redistribution boundary.

## Risky Wording Check

- Numerical results were not changed.
- The current manuscript keeps 50 clips as the primary result and 75 clips as a
  robustness/scalability check.
- Proxy labels are described as derived labels, not direct ground truth.
- MPJPE is not reported; pose metrics remain MANO/UmeTrack pose-parameter vector
  MAE/MSE.
- Vision-language and PreHOI-Former variants remain exploratory rather than the
  main claim.

## Sources Checked

- Machine Learning with Applications journal page:
  https://www.sciencedirect.com/journal/machine-learning-with-applications
- Machine Learning with Applications Guide for Authors:
  https://www.sciencedirect.com/journal/machine-learning-with-applications/publish/guide-for-authors
- Elsevier open-access publishing options:
  https://www.elsevier.com/researcher/author/open-access/choice
- Elsevier waiver policy:
  https://www.elsevier.support/publishing/answer/what-is-elseviers-waiver-policy-for-open-access-fees
- HOT3D Toolkit:
  https://github.com/facebookresearch/hot3d
- HOT3D-Clips README:
  https://github.com/facebookresearch/hot3d/blob/main/hot3d/clips/README.md
- HOT3D Dataset License Agreement:
  https://huggingface.co/datasets/bop-benchmark/hot3d/resolve/main/hot3d_dataset_license_agreement.pdf?download=true
