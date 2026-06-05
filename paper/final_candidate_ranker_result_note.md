# Final-Protocol Candidate Ranker Result Note

Date: 2026-06-06

## Status

This note records the first 5-seed final-protocol candidate-ranker run for
PreHOI-Rank on the 50-clip local HOT3D-Clips subset.

These are paper-candidate diagnostics, not unconditional final paper claims.
Target-object labels are derived proxy labels, not direct HOT3D ground truth.
The result should be reported with the limitations below.

## Dataset and Split

- Dataset subset: 50 local HOT3D-Clips shards.
- Proxy samples before optimized filtering: 6500.
- Candidate order: `stable_uid`.
- Input safety: `input_uses_forecast_frame=false`.
- Model: `candidate_ranker_non_vl`.
- Seeds: 42, 123, 2026, 7, 99.

Optimized split:

| Split | Clips | Samples | Forecast-Input Count |
| --- | ---: | ---: | ---: |
| Train | 35 | 4175 | 0 |
| Validation | 8 | 1040 | 0 |
| Test | 7 | 910 | 0 |

## Candidate-Order and Position Baselines

Test split, `stable_uid` order:

| Baseline | Value |
| --- | ---: |
| Candidate-0 top-1 | 0.1857 |
| First-3 top-3 | 0.5681 |
| Position-only MRR | 0.4377 |
| Expected random top-1 | 0.2025 |
| Expected random top-3 | 0.5947 |

The candidate ranker is evaluated against these order/position baselines. Runs
using raw/as-is candidate order remain excluded.

## Five-Seed Result

Summary file:
`results/tables/final_candidate_ranker_summary.csv`

| Metric | Mean +/- Std |
| --- | ---: |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 |
| MRR | 0.8605 +/- 0.0221 |
| Pose MSE | 0.4301 +/- 0.0116 |
| Pose MAE | 0.4102 +/- 0.0051 |

Per-seed results:

| Seed | Top-1 | Top-3 | MRR | Pose MSE | Pose MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.8198 | 0.9484 | 0.8934 | 0.4372 | 0.4128 |
| 123 | 0.7297 | 0.9802 | 0.8522 | 0.4170 | 0.4087 |
| 2026 | 0.7637 | 0.9626 | 0.8683 | 0.4463 | 0.4178 |
| 7 | 0.7352 | 0.9901 | 0.8548 | 0.4246 | 0.4056 |
| 99 | 0.7011 | 0.9681 | 0.8339 | 0.4252 | 0.4061 |

## Comparison to Earlier 25-Clip Pilot

| Setting | Top-1 | MRR | Pose MAE |
| --- | ---: | ---: | ---: |
| 25-clip, 3-seed pilot | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| 50-clip, 5-seed protocol | 0.7499 +/- 0.0450 | 0.8605 +/- 0.0221 | 0.4102 +/- 0.0051 |

The expanded 50-clip protocol improves the candidate-ranker diagnostics over
the earlier 25-clip pilot while using the same order-safe candidate-ranking
formulation.

## Limitations

- Target-object labels are derived proxy labels, not direct HOT3D ground truth.
- The experiment uses a 50-clip local subset, not the full HOT3D-Clips dataset.
- Class imbalance remains:
  - test is missing `food_waffles`, `potato_masher`, and `spatula_red`,
  - train has low counts for `bottle_ranch=16`, `cellphone=6`, and
    `mug_white=4`.
- Pose is evaluated as MANO/UmeTrack pose-vector MAE/MSE, not MPJPE.
- Final manuscript claims should include these limitations and should compare
  against all required baselines under the final protocol.

## Interpretation

This result supports the current PreHOI-Rank framing: leakage-safe,
affordance-grounded candidate ranking is the strongest evidence-backed
formulation in the project so far. It should be treated as a paper-candidate
result that still requires manuscript-level limitations and, ideally, stronger
split coverage or a larger local subset before submission.
