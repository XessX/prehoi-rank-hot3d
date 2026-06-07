# Figure Plan: PreHOI-Rank

This plan lists figures needed for the PreHOI-Rank manuscript. Figures should
support the honest paper framing: leakage-safe, affordance-grounded candidate
ranking on a 50-clip local HOT3D-Clips subset with derived proxy labels.

## Fig. 1: Pre-Contact Forecasting Problem Overview

Status: reviewed draft generated at
`paper/figures/fig1_problem_overview.png` and
`paper/figures/fig1_problem_overview.pdf`.

Purpose:

Show the task setup: an observation window precedes a forecast frame, and the
model must rank visible object candidates before contact.

Inputs:

- Egocentric observation frames.
- Last observation frame with visible hand/object candidates.
- Forecast frame used only for target proxy creation.

Visual elements:

- Timeline with frames `t0 ... t15` as observation and `t20` as forecast.
- Hand trajectory or hand boxes in observation frames.
- Multiple visible object candidates in the scene.
- Arrow from observation window to ranked candidate list.
- Clear lock icon or boundary showing forecast-frame features are not input.

Caption draft:

**Figure 1. Pre-contact candidate-ranking setup.** Given an observation window,
PreHOI-Rank ranks visible object candidates as likely future hand-object
targets. The forecast frame is used only to define a derived proxy target and is
not used as model input.

## Fig. 2: Proxy-Label Generation from Forecast-Frame Hand-Object Proximity

Status: reviewed draft generated at
`paper/figures/fig2_proxy_label_generation.png` and
`paper/figures/fig2_proxy_label_generation.pdf`.

Purpose:

Explain the derived affordance-grounded target-object proxy without calling it
ground truth.

Inputs:

- Forecast-frame hands annotation.
- Forecast-frame object candidates.
- Hand union box.
- Object boxes and visibility metadata.

Visual elements:

- Forecast frame schematic.
- Hand union box.
- Object boxes with overlap and center-distance arrows.
- Scoring table for candidate objects.
- Selected proxy target highlighted.
- Warning note: derived target only, not model input.

Caption draft:

**Figure 2. Derived target-object proxy construction.** The proxy target is
selected at the forecast frame using hand-object box overlap and normalized
center distance. These forecast-frame quantities define the supervised target
only and are excluded from model inputs.

## Fig. 3: PreHOI-Rank Candidate-Ranking Architecture

Status: reviewed draft generated at
`paper/figures/fig3_prehoi_rank_architecture.png` and
`paper/figures/fig3_prehoi_rank_architecture.pdf`.

Purpose:

Show the current strongest model: non-VL candidate ranker with temporal context,
candidate features, ranking scores, and pose regression.

Inputs:

- Observation metadata sequence `[T, 9]`.
- Observation-frame object candidate tensor.
- Candidate mask.

Visual elements:

- Temporal encoder for observation sequence.
- Candidate encoder for object candidates.
- Fusion block.
- Candidate score head.
- Future pose-vector head.
- Masked candidate ranking loss and pose loss.

Caption draft:

**Figure 3. PreHOI-Rank model overview.** The model encodes observation-window
metadata and object candidates, ranks visible candidates with a masked scoring
head, and regresses a future hand-pose vector. The current strongest model does
not require vision-language features.

## Fig. 4: Leakage and Candidate-Order Bias Prevention Protocol

Status: reviewed draft generated at
`paper/figures/fig4_protocol_safety.png` and
`paper/figures/fig4_protocol_safety.pdf`.

Purpose:

Make the evaluation protocol visually explicit so readers understand why the
reported candidate ranking is not caused by future-frame leakage or raw
candidate order.

Inputs:

- Split policy.
- Candidate-order policy.
- Exclusion rules.
- Position baselines.

Visual elements:

- Checklist diagram:
  - clip-level split,
  - `input_uses_forecast_frame=false`,
  - `candidate_order: stable_uid`,
  - candidate-0 baseline,
  - first-3 baseline,
  - random baseline,
  - position-only MRR.
- Red crossed-out items for `as_is`, proxy-sorted order, and forecast-frame
  inputs.

Caption draft:

**Figure 4. Evaluation safety protocol.** Valid runs use clip-level splits,
observation-frame inputs, stable UID candidate ordering, and position baselines.
Runs with forecast-frame inputs or target-aware candidate ordering are excluded.

## Fig. 5: Results Summary and 25-Clip Versus 50-Clip Comparison

Status: reviewed draft generated at
`paper/figures/fig5_25clip_vs_50clip_results.png` and
`paper/figures/fig5_25clip_vs_50clip_results.pdf`.

Purpose:

Summarize the key empirical finding: the 50-clip 5-seed protocol improves the
candidate-ranker diagnostics compared with the earlier 25-clip pilot.

Inputs:

- 25-clip pilot metrics.
- 50-clip protocol metrics.
- Candidate-order baseline metrics.

Visual elements:

- Bar plot or grouped table for top-1, MRR, and pose MAE.
- Seed-standard-deviation error bars for repeated-seed runs.
- Separate small table for 50-clip final-protocol top-1, top-3, MRR, pose MSE,
  and pose MAE.
- Note that values are paper-candidate diagnostics on derived proxy labels.

Caption draft:

**Figure 5. Candidate-ranker protocol diagnostics.** Expanding from 25 to 50
local HOT3D-Clips shards improves top-1 candidate accuracy, MRR, and pose-vector
MAE under the same order-safe candidate-ranking formulation. Results remain
limited by derived proxy labels and local-subset evaluation.
