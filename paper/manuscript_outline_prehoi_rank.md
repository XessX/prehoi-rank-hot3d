# PreHOI-Rank Manuscript Outline

## Title

PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D
Hand-Object Interaction Forecasting

## Abstract Placeholder

This paper will study pre-contact forecasting of hand-object interaction in
egocentric video by framing target-object anticipation as candidate ranking
over observed object proposals. The current pilot evidence suggests that
observation-frame hand-object geometry is a strong and stable signal for
derived HOT3D-Clips target-object proxy labels. Final claims require a locked
dataset split, more robust class coverage, repeated-seed evaluation, and
validated pose metrics.

## Contributions

- Formulate pre-contact target-object anticipation as an order-safe candidate
  ranking problem rather than only global object classification.
- Define a derived target-object proxy from forecast-frame hand-object
  proximity while keeping all model inputs restricted to observation frames.
- Introduce candidate-order safety checks using stable UID ordering, candidate-0
  baselines, first-3 baselines, and position-only MRR.
- Provide a pilot HOT3D-Clips pipeline from shard inspection through proxy
  indexing, optimized clip-level splitting, candidate ranking, and seed
  stability.
- Retain vision-language and PreHOI-Former variants as controlled ablations and
  future extensions rather than unsupported main claims.

## Dataset and Proxy-Label Definition

- Dataset: HOT3D-Clips local subset.
- Current expanded pilot subset: 50 clips, 6500 derived proxy samples before
  optimized filtering.
- Split policy: clip-level split only to reduce leakage between adjacent samples.
- Target proxy: selected object at the forecast frame based on hand-object box
  proximity.
- Input policy: observation-frame hand metadata, object candidates, and optional
  cached visual/text features only.
- Label status: derived proxy labels, not direct HOT3D ground truth.

Needed before submission:

- More clips or stricter class filtering for train/validation/test coverage.
- Clear statement that proxy labels approximate target-object intent but do not
  replace official action/contact annotations.
- MANO/UmeTrack conversion to 3D joints for MPJPE-style pose metrics.

## Candidate-Order Leakage Prevention

- Default candidate order: `stable_uid`.
- Unsafe order modes such as raw/as-is proxy order are excluded from paper
  claims.
- Required diagnostics:
  - target candidate position distribution,
  - candidate-0 top-1 baseline,
  - first-3 top-3 baseline,
  - position-only MRR,
  - random-candidate expectation.
- Current 50-clip test position baselines:
  - candidate-0 top-1: 0.1857,
  - first-3 top-3: 0.5681,
  - position-only MRR: 0.4377.

## Model Formulation

Primary pilot model: order-safe non-VL candidate ranker.

Inputs:

- Observation metadata sequence, currently `[T, 9]`.
- Observation-frame object candidate tensor with candidate geometry, visibility,
  hand-object proximity features, and candidate mask.
- Stable candidate ordering by object UID/name.

Outputs:

- Candidate ranking scores over observed candidates.
- Future MANO-pose regression vector.

Loss:

- Candidate ranking cross-entropy over the target candidate.
- Future hand-pose regression loss.
- Weighted combined loss for pilot optimization.

Exploratory extensions:

- Frozen object-name text features.
- PreHOI-Former v1 attention fusion.
- PreHOI-Former v2 dual-branch architecture.
- Cached image-stat or frozen CLIP visual features.

These extensions remain ablations until they beat the stable non-VL ranker under
the same split and repeated-seed protocol.

## Experimental Setup

Current pilot setup:

- Expanded HOT3D-Clips subset: 50 local shards.
- Optimized split:
  - train: 35 clips, 4175 samples,
  - validation: 8 clips, 1040 samples,
  - test: 7 clips, 910 samples.
- Eligible proxy classes: 23.
- Shared train/validation/test classes: 20.
- Seeds for stability: 42, 123, 2026.
- Candidate order: `stable_uid`.
- Input safety: `input_uses_forecast_frame=false`.

Metrics:

- Candidate top-1.
- Candidate top-3.
- Mean reciprocal rank.
- Pose MSE.
- Pose MAE.
- Position-only baselines.

## Pilot Results

Current best pilot: non-VL candidate ranker on the 50-clip expanded subset.

| Subset | Top-1 | MRR | Pose MAE |
| --- | --- | --- | --- |
| 25 clips | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| 50 clips | 0.7711 +/- 0.0455 | 0.8713 +/- 0.0208 | 0.4131 +/- 0.0045 |

Interpretation:

- Candidate-level ranking is currently the strongest stable formulation.
- Expanded data improves the pilot diagnostics.
- Vision-language and PreHOI-Former variants are useful but not yet stable
  enough to be the main claim.

These are pilot/debug diagnostics only, not final paper results.

## Limitations

- Target-object labels are derived proxies, not direct HOT3D ground truth.
- The expanded split still has class-coverage warnings:
  - test is missing `food_waffles`, `potato_masher`, and `spatula_red`,
  - train has low counts for `bottle_ranch`, `cellphone`, and `mug_white`.
- Future hand pose is currently evaluated on MANO/UmeTrack parameters, not
  converted 3D joints.
- No final action/contact labels are available yet.
- Vision-language fusion has not yet improved over the stable non-VL ranker.
- Current results are from a local subset, not the full HOT3D-Clips dataset.

## Next Steps Before Submission

- Expand or filter the dataset until train/validation/test class coverage is
  defensible.
- Lock the final split and rerun all valid baselines over repeated seeds.
- Add MANO/UmeTrack-to-3D-joint conversion for MPJPE or similar pose metrics.
- Decide whether the paper's main task is target candidate ranking, future pose
  forecasting, or a joint multi-task formulation.
- Reassess vision-language features only after the candidate-ranking baseline is
  locked.
- Write a clear proxy-label limitations section for the manuscript.
