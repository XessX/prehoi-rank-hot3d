# 75-Clip Final-Protocol Candidate Ranker Result Note

Date: 2026-06-08

## Status

This note records the 5-seed final-protocol candidate-ranker run for
PreHOI-Rank on the 75-clip local HOT3D-Clips subset.

This is a paper-candidate protocol result, but it should not replace the
50-clip result until the two settings are compared carefully. Target-object
labels are derived proxy labels, not direct HOT3D ground truth.

## Dataset and Split

- Dataset subset: 75 local HOT3D-Clips shards.
- Proxy samples before optimized filtering: 9,750.
- Raw target-object proxy classes: 32.
- Optimized eligible target-object proxy classes: 30.
- Candidate order: `stable_uid`.
- Input safety: `input_uses_forecast_frame=false`.
- Model: `candidate_ranker_non_vl`.
- Seeds: 42, 123, 2026, 7, 99.
- Logs: `results/logs/final_protocol_75clip/`.
- Summary table: `results/tables/final_candidate_ranker_summary_75clip.csv`.

Optimized split:

| Split | Clips | Samples | Forecast-Input Count |
| --- | ---: | ---: | ---: |
| Train | 52 | 6,714 | 0 |
| Validation | 11 | 1,430 | 0 |
| Test | 11 | 1,430 | 0 |

## Candidate-Order and Position Baselines

Candidate-order diagnostics used `candidate_order=stable_uid`. All samples were
rankable and included the derived target-object proxy among the candidates.

| Split | Candidate-0 Top-1 | First-3 Top-3 | Position-Only MRR | Expected Random Top-1 |
| --- | ---: | ---: | ---: | ---: |
| Train | 0.1833 | 0.5329 | 0.4227 | 0.1818 |
| Validation | 0.1140 | 0.6140 | 0.4011 | 0.2014 |
| Test | 0.0280 | 0.4420 | 0.2945 | 0.1817 |

The test candidate-0 baseline is low, so the 75-clip result is not explained by
a trivial candidate-position shortcut.

## Five-Seed Result

| Metric | Mean +/- Std |
| --- | ---: |
| Top-1 candidate accuracy | 0.7115 +/- 0.0571 |
| Top-3 candidate accuracy | 0.9789 +/- 0.0009 |
| MRR | 0.8340 +/- 0.0343 |
| Pose MSE | 0.5854 +/- 0.0296 |
| Pose MAE | 0.4676 +/- 0.0096 |

Per-seed results:

| Seed | Top-1 | Top-3 | MRR | Pose MSE | Pose MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.7168 | 0.9797 | 0.8423 | 0.6139 | 0.4819 |
| 123 | 0.6650 | 0.9790 | 0.8142 | 0.5938 | 0.4683 |
| 2026 | 0.6993 | 0.9783 | 0.8260 | 0.5559 | 0.4574 |
| 7 | 0.6699 | 0.9797 | 0.7990 | 0.6111 | 0.4702 |
| 99 | 0.8063 | 0.9776 | 0.8885 | 0.5523 | 0.4603 |

## Limitations

- Target-object labels are derived proxy labels, not direct HOT3D ground truth.
- The experiment uses a 75-clip local subset, not the full HOT3D-Clips dataset.
- Class imbalance remains despite the larger subset.
- Validation is missing five eligible classes.
- Test is missing ten eligible classes.
- Train has low counts for `can_soup=1` and `whiteboard_marker=13`.
- Pose is evaluated as MANO pose-parameter vector MAE/MSE, not MPJPE.
- Results should be compared with the 50-clip protocol before manuscript claims
  are updated.

## Interpretation

The 75-clip run is leakage-safe and order-safe, but it does not clearly improve
over the 50-clip protocol. Top-3 remains very high and stable, but Top-1 and MRR
are lower than the 50-clip result, and pose-parameter MAE is worse. This suggests
that the expanded subset is harder and still class-imbalanced. The result is
useful for robustness analysis, but the manuscript should not simply replace the
50-clip headline result with the 75-clip result.
