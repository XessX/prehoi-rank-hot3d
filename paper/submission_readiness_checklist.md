# Submission Readiness Checklist

This checklist tracks what remains before the PreHOI-Rank manuscript should be
treated as submission-ready. Current results are paper-candidate diagnostics,
not a completed journal submission.

## Data and Experimental Scope

- [ ] Decide whether the 50-clip local HOT3D-Clips subset remains the primary
      result or whether to report both 50-clip and 75-clip protocols.
- [x] Expanded to 75 clips and reran proxy indexing, split optimization,
      split-quality checks, candidate-order diagnostics, image-stat feature
      refresh, and final-protocol candidate-ranker training.
- [ ] Final 50-vs-75 manuscript decision pending.
- [ ] Resolve or explicitly discuss remaining class-coverage warnings.
- [ ] Verify HOT3D-Clips license/access terms and add a dataset access note.
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
- [ ] Complete related-work citations.
- [ ] Replace all `[Citation needed]` and `[REF-*]` placeholders.
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
- [ ] Add author contribution statement.
- [x] Add data/code availability statement.

## Journal and Submission Logistics

- [ ] Verify target journal formatting requirements.
- [ ] Verify Machine Learning with Applications article type and scope fit.
- [ ] Verify APC, waiver, or Research4Life route.
- [x] Create submission-readiness decision audit:
      `paper/submission_readiness_decision_audit.md`.
- [ ] Decide whether to strengthen first with 75-clip expansion, MPJPE-style
      pose evaluation, or a stronger fair baseline.
- [ ] Journal route verification pending; see
      `paper/journal_route_verification.md`.
- [ ] Research4Life verification pending for final corresponding-author and
      co-author affiliations.
- [x] Prepare cover letter draft:
      `paper/cover_letter_draft_prehoi_rank.md`.
- [x] Prepare data/code availability draft:
      `paper/data_code_availability_draft.md`.
- [ ] Prepare highlights if required.
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
- Submission decision audit: completed; current recommendation is to strengthen
  before submission, preferably with MPJPE if feasible or 75-clip expansion.
- Hand pose conversion feasibility: checked. MPJPE is feasible with official
  dependencies/assets but blocked locally until that path is validated.
- Journal route verification: started; APC/Research4Life status not final.
- Cover letter and data/code availability drafts: started.
- Final formatting: pending.
- Submission-ready status: not yet.
