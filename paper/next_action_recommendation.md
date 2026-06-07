# Next Action Recommendation

Status: recommendation draft.
Date: 2026-06-08.

## Short Answer

Do **not** submit immediately. The current 50-clip five-seed result is strong
enough to support the PreHOI-Rank direction, but the paper should be
strengthened before submission to Machine Learning with Applications.

## Minimum Next Action

Complete a final manuscript hygiene pass:

- verify HOT3D-Clips license/access wording,
- confirm all citation placeholders are resolved or intentionally removed,
- ensure every figure/table is referenced,
- keep proxy labels described as derived proxy labels,
- keep all results tied to the 50-clip local subset,
- update the checklist after the decision audit.

This minimum path is enough to keep the project defensible, but it does not
fully reduce the major reviewer risks.

## Best Next Action

Attempt MANO/UmeTrack-to-3D-joint conversion and report MPJPE-style metrics.

Reason:

- MPJPE is more recognizable than MANO/UmeTrack pose-vector MAE.
- It strengthens the pose-forecasting side of the paper.
- It addresses one of the clearest technical weaknesses without changing the
  main candidate-ranking claim.

If MPJPE conversion becomes too slow or blocked by tooling/license details,
switch to the 75-clip expansion path.

## Strong Practical Alternative

Expand from 50 to about 75 HOT3D-Clips shards and rerun the final candidate
ranker protocol.

Reason:

- It directly addresses local-subset concerns.
- It improves class/split coverage.
- It uses infrastructure that already works.

## Optional Later Action

Add one stronger comparative baseline under the exact same safety protocol:

- observation-window inputs only,
- `candidate_order: stable_uid`,
- clip-level split,
- no forecast-frame input,
- derived proxy labels only.

This is valuable, but it should not be rushed if the baseline would be unfair,
weakly implemented, or leakage-prone.

## What Not To Do

- Do not claim state-of-the-art.
- Do not call derived proxy labels ground truth.
- Do not make PreHOI-Former or vision-language models the main claim unless
  repeated-seed results improve.
- Do not add an external baseline that violates the same leakage/order-safety
  protocol.
- Do not expand figures or prose into claims that the current 50-clip subset
  cannot support.

## Recommendation

Best route:

1. Try MPJPE conversion.
2. If feasible, report MPJPE and update Methods/Results.
3. If blocked, expand to 75 clips and rerun the final protocol.
4. After one of those strengthening steps, perform final formatting and journal
   route verification.

Fallback route:

1. Submit with the 50-clip result only if time is constrained.
2. Make the local-subset/proxy-label limitations explicit in the abstract,
   results, discussion, and cover letter.
