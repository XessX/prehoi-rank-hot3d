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

- [ ] Complete related-work citations.
- [ ] Replace all `[Citation needed]` and `[REF-*]` placeholders.
- [ ] Generate Fig. 1 problem overview.
- [ ] Generate Fig. 2 proxy-label construction diagram.
- [ ] Generate Fig. 3 model architecture diagram.
- [ ] Generate Fig. 4 leakage/order-bias protocol diagram.
- [ ] Generate Fig. 5 results summary figure.
- [ ] Add dataset license/access note.
- [ ] Add ethics and data-use note.
- [ ] Add threats-to-validity section or expand limitations.
- [ ] Add author contribution statement.
- [ ] Add data/code availability statement.

## Journal and Submission Logistics

- [ ] Verify target journal formatting requirements.
- [ ] Verify Machine Learning with Applications article type and scope fit.
- [ ] Verify APC, waiver, or Research4Life route.
- [ ] Prepare cover letter.
- [ ] Prepare highlights if required.
- [ ] Prepare graphical abstract if required.
- [ ] Confirm all tables and figures are cited in text.
- [ ] Confirm generated logs/checkpoints are not committed.
- [ ] Create a clean release tag or archive after final review.

## Current Readiness Summary

- Working title: done.
- Candidate-ranking method framing: done.
- 50-clip final-protocol candidate-ranker run: done.
- First manuscript draft: started.
- Related work: planned, citations incomplete.
- Figures: planned, not generated.
- Submission-ready status: not yet.
