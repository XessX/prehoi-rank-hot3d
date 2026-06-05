# PreHOI-Rank Figure Set

Source script:

```text
src/visualization/create_prehoi_rank_figures.py
```

Regenerate all first-version figures with:

```powershell
python src/visualization/create_prehoi_rank_figures.py
```

These are schematic diagrams. They do not use copyrighted HOT3D images or
dataset frames.

## Figure 1

- Path: `paper/figures/fig1_problem_overview.png`
- Purpose: Explain the pre-contact forecasting setup.
- Caption draft: **Figure 1. Pre-contact candidate-ranking setup.** Given an
  observation window, PreHOI-Rank ranks visible object candidates as likely
  future hand-object targets. The forecast frame is used only to define a
  derived proxy target and is not used as model input.

## Figure 2

- Path: `paper/figures/fig2_proxy_label_generation.png`
- Purpose: Show derived proxy-label generation from forecast-frame hand-object
  proximity.
- Caption draft: **Figure 2. Derived target-object proxy construction.** The
  proxy target is selected at the forecast frame using hand-object box overlap
  and normalized center distance. These forecast-frame quantities define the
  supervised target only and are excluded from model inputs.

## Figure 3

- Path: `paper/figures/fig3_prehoi_rank_architecture.png`
- Purpose: Show the current candidate-ranker architecture.
- Caption draft: **Figure 3. PreHOI-Rank model overview.** The model encodes
  observation-window metadata and object candidates, ranks visible candidates
  with a masked scoring head, and regresses a future hand-pose vector. The
  current strongest model does not require vision-language features.

## Figure 4

- Path: `paper/figures/fig4_protocol_safety.png`
- Purpose: Summarize leakage and candidate-order safety rules.
- Caption draft: **Figure 4. Evaluation safety protocol.** Valid runs use
  clip-level splits, observation-frame inputs, stable UID candidate ordering,
  and position baselines. Runs with forecast-frame inputs or target-aware
  candidate ordering are excluded.

## Figure 5

- Path: `paper/figures/fig5_25clip_vs_50clip_results.png`
- Purpose: Compare the earlier 25-clip pilot with the 50-clip 5-seed protocol.
- Caption draft: **Figure 5. Candidate-ranker protocol diagnostics.** Expanding
  from 25 to 50 local HOT3D-Clips shards improves top-1 candidate accuracy, MRR,
  and pose-vector MAE under the same order-safe candidate-ranking formulation.
  Results remain limited by derived proxy labels and local-subset evaluation.
