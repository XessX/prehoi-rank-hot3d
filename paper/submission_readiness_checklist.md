# Submission Readiness Checklist

This checklist tracks what remains before the PreHOI-Rank manuscript should be
treated as submission-ready. Current results are paper-candidate diagnostics,
not a completed journal submission.

## Data and Experimental Scope

- [ ] Decide whether the 50-clip local HOT3D-Clips subset is acceptable for the
      first submission or whether to expand to 75 clips.
- [ ] If expanding, rerun proxy indexing, split optimization, split-quality
      checks, candidate-order diagnostics, and final-protocol training.
- [ ] Resolve or explicitly discuss remaining class-coverage warnings.
- [ ] Verify HOT3D-Clips license/access terms and add a dataset access note.
- [ ] Confirm downloaded data remains ignored by Git.

## Labels and Metrics

- [ ] Keep target-object labels described as derived proxy labels, not ground
      truth.
- [ ] Decide whether to convert MANO/UmeTrack pose parameters to 3D joints.
- [ ] Add MPJPE-style pose metrics if conversion is feasible.
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
- [ ] Complete related-work citations.
- [ ] Replace all `[Citation needed]` and `[REF-*]` placeholders.
- [x] Generate Fig. 1 problem overview.
- [x] Generate Fig. 2 proxy-label construction diagram.
- [x] Generate Fig. 3 model architecture diagram.
- [x] Generate Fig. 4 leakage/order-bias protocol diagram.
- [x] Generate Fig. 5 results summary figure.
- [ ] Review generated figure quality, resolution, fonts, and journal-style
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
- First manuscript draft: expanded journal-style draft created.
- Related work: expanded draft started, citations incomplete.
- Figures: first versions generated; quality review pending.
- Journal route verification: started; APC/Research4Life status not final.
- Cover letter and data/code availability drafts: started.
- Final formatting: pending.
- Submission-ready status: not yet.
