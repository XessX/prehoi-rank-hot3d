# Final Experiment Protocol

Working title:

**PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D
Hand-Object Interaction Forecasting**

This protocol defines the requirements for moving from pilot/debug experiments
to paper-ready experiments. Current numbers remain pilot diagnostics until this
protocol is satisfied and reviewed.

## Dataset Scope and Limitations

- Dataset base: local HOT3D-Clips subset.
- Current subset: 50 clips, 6500 derived target-object proxy samples before
  optimized filtering.
- Current optimized split: 4175 train samples, 1040 validation samples, and 910
  test samples.
- Current eligible proxy classes: 23.
- Current shared train/validation/test classes: 20.
- Split policy: clip-level split only.
- Input policy: observation-window inputs only.
- Label policy: target-object labels are derived proxy labels, not direct HOT3D
  ground truth.

The 50-clip subset is the primary experimental base, but it is still a local
subset. A 75-clip local expansion has also been completed and should be reported
as robustness/scalability analysis rather than as a replacement for the cleaner
50-clip primary result.

## Derived Target-Object Proxy Definition

HOT3D-Clips does not directly provide the final paper target labels used by the
current candidate-ranking task. The current target-object proxy is derived from
the forecast frame:

1. Read visible hands and visible object candidates at the forecast frame.
2. Compute the union of visible hand bounding boxes.
3. Score each visible object candidate by hand-object box overlap and normalized
   center distance.
4. Select the highest-scoring object as the derived target-object proxy.
5. Store proxy score, proxy confidence, candidate scores, selected object ID,
   selected object name, and label-status metadata.

This proxy is a supervised target only. It must not be called ground truth, and
forecast-frame object/hand proximity features must not be used as model input.

## Leakage Prevention Rules

Every valid experiment must satisfy:

- `input_uses_forecast_frame=false`.
- Observation windows may use frames up to the last observation frame only.
- Target-object proxy labels may be computed at the forecast frame.
- Model inputs must not include forecast-frame object boxes, hand boxes, proxy
  scores, candidate scores, visual features, or metadata.
- Visual features, if used, must be cached from observation frames only.
- Splits must be clip-level, never random sample-level.

Any run violating these rules is excluded from paper claims.

## Candidate-Order Safety Rules

Candidate-ranking experiments must use:

- `candidate_order: stable_uid`
- `candidate_order_seed` fixed in config, even if unused by stable UID ordering
- candidate-0, first-3, random-candidate, and position-only MRR baselines
- target-position distribution reporting for train, validation, and test

Allowed for final protocol:

- `stable_uid`

Excluded from paper claims:

- `as_is`
- proxy-score sorted order
- target-aware order
- any order derived from forecast-frame quantities

## Train/Validation/Test Split Requirements

Required:

- Clip-level split.
- Train covers every validation/test class.
- Report classes missing from each split.
- Report classes with low train sample count.
- Report shared train/validation/test class count.
- Report per-class sample distributions.

Current 50-clip warnings to resolve or explicitly discuss:

- Test missing: `food_waffles`, `potato_masher`, `spatula_red`
- Low train count: `bottle_ranch=16`, `cellphone=6`, `mug_white=4`

## Final Model Candidates

Primary current candidate:

- `candidate_ranker_non_vl`

Potential improved method:

- PreHOI-Rank improved version with the same leakage/order safety rules

Optional ablations:

- Vision-language candidate ranker
- PreHOI-Former variants
- Frozen visual feature variants

Vision-language or PreHOI-Former variants should be framed as ablations or
future extensions unless they beat the primary candidate ranker under the same
final split and repeated-seed protocol.

## Required Baselines

Position/order baselines:

- Candidate-0 position baseline.
- First-3 position baseline.
- Random candidate baseline.
- Position-only MRR.

Model baselines:

- Metadata-only baseline.
- Object-aware global classifier.
- Non-VL candidate ranker.
- Any proposed PreHOI-Rank improved version.
- Optional vision-language ablation.

## Required Metrics

Ranking:

- Top-1 candidate accuracy.
- Top-3 candidate accuracy.
- Mean reciprocal rank.
- Candidate-position baselines.

Pose:

- Pose MSE.
- Pose MAE.
- MPJPE-style metric if MANO/UmeTrack-to-3D-joint conversion is implemented.

Data/proxy diagnostics:

- Proxy confidence mean and distribution.
- Low-confidence proxy count.
- Rankable candidate coverage.
- Per-class distribution.
- Split-quality warnings.

Stability:

- Mean and standard deviation across seeds.

## Required Repeated Seeds

- Pilot: at least 3 seeds.
- Final: preferably 5 seeds.

Default final-protocol seeds:

```text
42, 123, 2026, 7, 99
```

## Exclusion Rules

Exclude any run that uses:

- Forecast-frame input features.
- `as_is`, proxy-sorted, or target-aware candidate ordering.
- Random sample-level splitting.
- Derived proxy labels described as ground truth.
- Missing candidate-order baseline report.
- Missing seed-stability report for the main claim.

## Next-Step Checklist Before Manuscript Claims

- Run the repeatable 50-clip final protocol with 5 seeds.
- Report the completed 75-clip protocol as robustness/scalability analysis.
- Resolve or document remaining split warnings.
- Add MANO/UmeTrack-to-3D-joint conversion if feasible.
- Rerun all required baselines on the locked split.
- Update Methods and Experiments sections with exact config paths, seeds, and
  exclusion rules.
- Preserve all current pilot/debug caveats until the final protocol has been
  reviewed.
