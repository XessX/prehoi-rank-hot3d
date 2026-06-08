# Submission Readiness Checklist

This checklist tracks what remains before the PreHOI-Rank manuscript should be
treated as submission-ready. Current results are paper-candidate diagnostics,
not a completed journal submission.

## Data and Experimental Scope

- [x] Decide result framing: use the 50-clip protocol as the primary controlled
      result and report the 75-clip protocol as robustness/scalability analysis.
- [x] Expanded to 75 clips and reran proxy indexing, split optimization,
      split-quality checks, candidate-order diagnostics, image-stat feature
      refresh, and final-protocol candidate-ranker training.
- [x] Final 50-vs-75 manuscript decision completed.
- [ ] Resolve or explicitly discuss remaining class-coverage warnings.
- [x] Check official HOT3D-Clips license/access sources and record the current
      license wording in the package audit and placeholder scan.
- [ ] Finalize HOT3D-Clips access/license wording for the exact manuscript and
      any public release artifacts.
- [ ] Confirm downloaded data remains ignored by Git.

## Labels and Metrics

- [ ] Keep target-object labels described as derived proxy labels, not ground
      truth.
- [x] Check MANO/UmeTrack-to-3D-joint conversion feasibility:
      `paper/hand_pose_conversion_feasibility.md`.
- [ ] Decide whether to install official hand-conversion dependencies and
      licensed MANO/UmeTrack assets.
- [ ] Add MPJPE-style pose metrics if conversion is validated.
- [ ] Report proxy confidence statistics in the manuscript.
- [ ] Include candidate-position baselines next to ranking metrics.

## Models and Baselines

- [ ] Decide whether to add a stronger external baseline.
- [ ] Rerun required baselines on the locked final split.
- [ ] Keep vision-language and PreHOI-Former variants as exploratory ablations
      unless they outperform the candidate ranker under the same protocol.
- [ ] Confirm all final runs use `candidate_order: stable_uid`.
- [ ] Confirm all final runs have `input_uses_forecast_frame=false`.

## Writing and Figures

- [x] Create expanded journal-style manuscript draft.
- [x] Complete manuscript quality audit.
- [x] Complete full consistency audit after the 75-clip robustness update.
- [x] Assemble pre-submission package:
      `paper/submission_package/`.
- [x] Complete core related-work citation verification.
- [x] Confirm no `[Citation needed]` or `[REF-*]` placeholders remain in the
      current submission manuscript.
- [ ] Remove or keep out of the submission package optional commented citation
      TODOs that are not cited in the manuscript.
- [x] Generate Fig. 1 problem overview.
- [x] Generate Fig. 2 proxy-label construction diagram.
- [x] Generate Fig. 3 model architecture diagram.
- [x] Generate Fig. 4 leakage/order-bias protocol diagram.
- [x] Generate Fig. 5 results summary figure.
- [x] Review generated figure quality, resolution, fonts, and journal-style
      readability.
- [ ] Add dataset license/access note.
- [x] Add ethics and data-use note.
- [x] Add threats-to-validity section or expand limitations.
- [x] Add author contribution statement.
- [x] Add data/code availability statement.

## Journal and Submission Logistics

- [ ] Verify target journal formatting requirements.
- [x] Check Machine Learning with Applications scope fit, article type language,
      APC listing, Guide for Authors basics, and Elsevier Research4Life/waiver
      route from official sources on 2026-06-09.
- [ ] Finalize Machine Learning with Applications formatting requirements
      against the live Guide for Authors before upload.
- [ ] Verify final APC, taxes, institutional agreement coverage, waiver, or
      Research4Life route using the exact author list and affiliations.
- [x] Create submission-readiness decision audit:
      `paper/submission_readiness_decision_audit.md`.
- [x] Complete 75-clip expansion and decide it is a robustness/scalability
      analysis, not the primary result.
- [ ] Decide whether to strengthen further with MPJPE-style pose evaluation or
      a stronger fair baseline.
- [x] Complete official-source journal route verification pass; see
      `paper/final_placeholder_scan.md` and
      `paper/journal_route_verification.md`.
- [ ] Research4Life verification pending for final corresponding-author and
      co-author affiliations.
- [x] Prepare cover letter draft:
      `paper/cover_letter_draft_prehoi_rank.md`.
- [x] Prepare data/code availability draft:
      `paper/data_code_availability_draft.md`.
- [x] Prepare highlights draft:
      `paper/submission_package/highlights.md`.
- [x] Prepare conflict of interest, funding, and ethics/data-use statement
      drafts in `paper/submission_package/`.
- [ ] Confirm author names, affiliations, author contributions, conflict of
      interest statement, and funding statement.
- [x] Run final placeholder scan for the current paper folder and submission
      package:
      `paper/final_placeholder_scan.md`.
- [ ] Replace cover-letter bracket placeholders after author details are final.
- [ ] Prepare graphical abstract if required.
- [ ] Confirm all tables and figures are cited in text.
- [ ] Confirm generated logs/checkpoints are not committed.
- [ ] Create a clean release tag or archive after final review.

## Current Readiness Summary

- Working title: done.
- Candidate-ranking method framing: done.
- 50-clip final-protocol candidate-ranker run: done.
- 75-clip final-protocol candidate-ranker run: completed; comparison note
  created, with recommendation to treat it as a harder robustness check rather
  than an automatic replacement for the 50-clip result.
- First manuscript draft: expanded journal-style draft created.
- Manuscript quality audit: completed; revision log created.
- Related work: expanded draft started, citations incomplete.
- Figures: reviewed draft versions generated with PNG and PDF exports.
- Pre-submission package: assembled under `paper/submission_package/`; not yet
  submission-ready.
- Submission decision audit: completed; current recommendation is to keep the
  50-clip result primary, report the 75-clip result as robustness analysis, and
  strengthen further only with validated MPJPE or a fair baseline if feasible.
- Hand pose conversion feasibility: checked. MPJPE is feasible with official
  dependencies/assets but blocked locally until that path is validated.
- Journal route verification: official-source pass completed on 2026-06-09;
  APC/Research4Life status still depends on final author-side details.
- Final placeholder scan: completed for the current submission package.
- Cover letter, highlights, contribution, ethics/data-use, conflict of
  interest, funding, and data/code availability drafts: started.
- Author information and author confirmations: pending.
- Final formatting: pending.
- Submission-ready status: not yet.
