# PreHOI-Rank Figure Set

Source script:

```text
src/visualization/create_prehoi_rank_figures.py
```

Regenerate all reviewed draft figures with:

```powershell
python src/visualization/create_prehoi_rank_figures.py
```

These are schematic diagrams. They do not use copyrighted HOT3D images or
dataset frames. The script exports both 300-DPI PNG files and PDF versions.

## Figure 1

- PNG: `paper/figures/fig1_problem_overview.png`
- PDF: `paper/figures/fig1_problem_overview.pdf`
- Purpose: Explain the pre-contact forecasting setup.
- Caption draft: **Figure 1. Pre-contact candidate-ranking setup.** Given an
  observation window, PreHOI-Rank ranks visible object candidates as likely
  future hand-object targets. The forecast frame is used only to define a
  derived proxy target and is not used as model input.

## Figure 2

- PNG: `paper/figures/fig2_proxy_label_generation.png`
- PDF: `paper/figures/fig2_proxy_label_generation.pdf`
- Purpose: Show derived proxy-label generation from forecast-frame hand-object
  proximity.
- Caption draft: **Figure 2. Derived target-object proxy construction.** The
  proxy target is selected at the forecast frame using hand-object box overlap
  and normalized center distance. These forecast-frame quantities define the
  supervised target only and are excluded from model inputs.

## Figure 3

- PNG: `paper/figures/fig3_prehoi_rank_architecture.png`
- PDF: `paper/figures/fig3_prehoi_rank_architecture.pdf`
- Purpose: Show the current candidate-ranker architecture.
- Caption draft: **Figure 3. PreHOI-Rank model overview.** The model encodes
  observation-window metadata and object candidates, ranks visible candidates
  with a masked scoring head, and regresses a future hand-pose vector. The
  current strongest model does not require vision-language features.

## Figure 4

- PNG: `paper/figures/fig4_protocol_safety.png`
- PDF: `paper/figures/fig4_protocol_safety.pdf`
- Purpose: Summarize leakage and candidate-order safety rules.
- Caption draft: **Figure 4. Evaluation safety protocol.** Valid runs use
  clip-level splits, observation-frame inputs, stable UID candidate ordering,
  and position baselines. Runs with forecast-frame inputs or target-aware
  candidate ordering are excluded.

## Figure 5

- PNG: `paper/figures/fig5_25clip_vs_50clip_results.png`
- PDF: `paper/figures/fig5_25clip_vs_50clip_results.pdf`
- Purpose: Compare the earlier 25-clip pilot, the 50-clip primary protocol, and
  the 75-clip robustness protocol.
- Caption draft: **Figure 5. Candidate-ranker protocol diagnostics.** Expanding
  from 25 to 50 local HOT3D-Clips shards improves top-1 candidate accuracy, MRR,
  and pose-vector MAE under the same order-safe candidate-ranking formulation.
  The 75-clip robustness split increases data scale and class diversity but is
  harder and less balanced; it maintains high top-3 performance while top-1,
  MRR, and pose-vector MAE are weaker than the 50-clip primary protocol. Bars
  show mean values with seed-standard-deviation error bars. Results remain
  limited by derived proxy labels and local-subset evaluation.
