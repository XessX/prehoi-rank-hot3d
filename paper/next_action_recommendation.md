# Next Action Recommendation

Status: recommendation draft.
Date: 2026-06-08.

## Short Answer

Do **not** submit immediately. The current 50-clip five-seed result remains the
primary controlled result, and the completed 75-clip run should be reported as a
robustness/scalability check. The paper now needs manuscript polishing, final
formatting, and final citation/license verification more than another round of
data expansion.

## Minimum Next Action

Complete a final manuscript hygiene pass:

- verify HOT3D-Clips license/access wording,
- confirm all citation placeholders are resolved or intentionally removed,
- ensure every figure/table is referenced,
- keep proxy labels described as derived proxy labels,
- keep the primary result tied to the 50-clip local subset,
- report the 75-clip result only as robustness/scalability analysis,
- update the checklist after the decision audit.

This minimum path is enough to keep the project defensible, but MPJPE and a
stronger fair baseline remain possible reviewer asks.

## Best Next Action

Polish the manuscript and final submission package around the current evidence,
while attempting MANO/UmeTrack-to-3D-joint conversion only if the official
dependency/assets path can be solved cleanly.

Reason:

- The 75-clip expansion is already complete and did not replace the 50-clip
  primary result.
- MPJPE would strengthen the pose-forecasting side, but it should not be faked
  or rushed.
- The biggest practical need is now to present the 50-clip primary and 75-clip
  robustness results clearly and conservatively.

If MPJPE conversion remains blocked by tooling/license details, keep pose
evaluation as MANO pose-parameter vector MAE/MSE and document that limitation.

## Strong Practical Alternative

Add one stronger comparative baseline under the exact same safety protocol.

Reason:

- It would reduce concern that the method only beats position baselines and
  internal pilots.
- It must use observation-window inputs only, `candidate_order: stable_uid`,
  clip-level splits, and derived proxy labels.

## Optional Later Action

Further data expansion beyond 75 clips:

- should not be pursued now unless reviewers request it,
- should only be done with a split strategy that improves shared class coverage,
- should not distract from final manuscript quality.

## What Not To Do

- Do not claim state-of-the-art.
- Do not call derived proxy labels ground truth.
- Do not make PreHOI-Former or vision-language models the main claim unless
  repeated-seed results improve.
- Do not add an external baseline that violates the same leakage/order-safety
  protocol.
- Do not claim the 75-clip run improves the main metric; it is a harder
  robustness check.

## Recommendation

Best route:

1. Use the 50-clip result as the primary controlled result.
2. Include the 75-clip result as robustness/scalability analysis.
3. Try MPJPE conversion only if the official dependency path is clean.
4. Perform final manuscript polishing, formatting, and journal route
   verification.

Fallback route:

1. Submit with 50-clip primary plus 75-clip robustness if time is constrained.
2. Make the local-subset/proxy-label/class-imbalance limitations explicit in
   the abstract, results, discussion, and cover letter.
