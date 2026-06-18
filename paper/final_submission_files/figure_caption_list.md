# Figure Caption List

Status: draft captions for the formatted submission package.

## Figure 1

**Figure 1. Pre-contact candidate-ranking setup.** Given an observation window,
PreHOI-Rank ranks visible object candidates as likely future hand-object
targets. The forecast frame is used only to define a derived proxy target and
is not used as model input.

Files:

- `fig1_problem_overview.png`
- `fig1_problem_overview.pdf`

## Figure 2

**Figure 2. Derived target-object proxy construction.** The proxy target is
selected at the forecast frame using hand-object box overlap and normalized
center distance. These forecast-frame quantities define the supervised target
only and are excluded from model inputs.

Files:

- `fig2_proxy_label_generation.png`
- `fig2_proxy_label_generation.pdf`

## Figure 3

**Figure 3. PreHOI-Rank model overview.** The model encodes observation-window
metadata and object candidates, ranks visible candidates with a masked scoring
head, and regresses a future hand-pose vector. The current strongest model does
not require vision-language features.

Files:

- `fig3_prehoi_rank_architecture.png`
- `fig3_prehoi_rank_architecture.pdf`

## Figure 4

**Figure 4. Evaluation safety protocol.** Valid runs use clip-level splits,
observation-frame inputs, stable UID candidate ordering, and position
baselines. Runs with forecast-frame inputs or target-aware candidate ordering
are excluded.

Files:

- `fig4_protocol_safety.png`
- `fig4_protocol_safety.pdf`

## Figure 5

**Figure 5. Candidate-ranker protocol diagnostics across 25, 50, and 75 local
HOT3D-Clips subsets.** Expanding from 25 to 50 local shards improves Top-1
candidate accuracy, MRR, and pose-vector MAE under the same order-safe
candidate-ranking formulation. The 75-clip robustness split increases data
scale and class diversity but is harder and less balanced; it maintains high
Top-3 performance while Top-1, MRR, and pose-vector MAE are weaker than the
50-clip primary protocol. Bars show mean values with seed-standard-deviation
error bars where available. Lower is better for pose-vector MAE.

Files:

- `fig5_25clip_vs_50clip_results.png`
- `fig5_25clip_vs_50clip_results.pdf`
