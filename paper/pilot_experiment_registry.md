# Pilot Experiment Registry

This registry tracks model-development runs only. Nothing here is a final paper
result, and target-object labels are derived proxy labels rather than direct
HOT3D ground truth.

## Dataset Scope

- Dataset: HOT3D-Clips local subset.
- Initial local subset: 25 shards, 3250 proxy samples before optimized
  filtering.
- Expanded local subset: 50 shards, 6500 proxy samples before optimized
  filtering.
- Current expanded optimized split: 6125 filtered samples, 23 eligible proxy
  classes.
- Split rule: clip-level split only, never random sample-level split.
- Input rule: model inputs must use observation frames only.
- Candidate rule: candidate ranking uses `candidate_order: stable_uid` unless a
  run is explicitly marked as excluded debug.

## Status Key

- `valid_pilot`: acceptable for internal model-development comparison only.
- `invalid_excluded`: known leakage/order-bias risk or superseded unsafe debug
  attempt; exclude from any paper claim.
- `missing_log`: expected artifact was not available when the registry was
  generated.

## Experiment Status

| Experiment | Status | Safety | Current Use |
| --- | --- | --- | --- |
| Metadata-only baseline | valid_pilot | Observation metadata only | Pipeline sanity check; weak target-object input. |
| Object-aware metadata baseline | valid_pilot | Leakage-safe observation-frame object candidates | Global proxy-classification pilot. |
| Image-stats visual-object baseline | valid_pilot | Observation-frame cached image statistics | Visual cache pipeline check, not deep visual modeling. |
| Frozen CLIP visual-object baseline | valid_pilot | Observation-frame frozen CLIP image features | Stronger visual-feature pipeline check; CLIP is frozen. |
| Non-VL candidate ranker | valid_pilot | `stable_uid` candidate order | Candidate-ranking baseline. |
| VL candidate ranker | valid_pilot | `stable_uid`, frozen text features | Tests object-name text features. |
| PreHOI-Former v1 | valid_pilot | `stable_uid`, observation-frame inputs | First model-development architecture. |
| PreHOI-Former v1 ablations | valid_pilot | Same split and order-safe candidate protocol | Controlled checks for text, attention, and loss balance. |
| PreHOI-Former v2 | valid_pilot | Dual branch, validation-MRR checkpointing | Infrastructure model; did not beat best v1 ablation in current pilot. |
| Object-aware metadata pre-leakage-audit | invalid_excluded | Forecast-frame input risk | Exclude; superseded by leakage-safe run. |
| Candidate ranker raw/as-is order debug | invalid_excluded | Candidate-position leakage risk | Exclude; use `stable_uid` runs and position baselines. |

## Current Interpretation

The seed-stability check changes the model-development interpretation. Although
PreHOI-Former v1 had the best single pilot run, the non-VL candidate ranker is
currently the strongest stable pilot across seeds. PreHOI-Former v2 remains
useful infrastructure because it adds dual-branch separation, early stopping,
and validation-MRR checkpointing, but its first geometry-only pilot did not
improve over the stable candidate-ranker baseline.

Pose regression and candidate ranking still appear to compete. Future model
work should focus on cleaner loss balancing, better pose targets/features, and
better validated labels before any paper-facing claims.

## Seed Stability Update

Three-seed pilot stability was run for the current best candidates using seeds
42, 123, and 2026.

| Model | Top-1 | MRR | Pose MAE |
| --- | --- | --- | --- |
| Non-VL candidate ranker | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| PreHOI-Former v1 | 0.4131 +/- 0.0283 | 0.6603 +/- 0.0143 | 0.4933 +/- 0.0382 |
| PreHOI-Former v1 geometry-only/no-attention | 0.5164 +/- 0.0180 | 0.7306 +/- 0.0092 | 0.4941 +/- 0.0370 |

The non-VL candidate ranker is currently the best stable pilot. The strong
single-run PreHOI-Former v1 result should not be used as the main claim. All
current results remain pilot/debug evidence only, based on derived proxy labels
rather than direct HOT3D ground truth.

## 50-Clip Expansion Update

The 50-clip expanded subset is now the strongest pilot signal. It improves the
order-safe non-VL candidate ranker over the earlier 25-clip pilot and supports
the current PreHOI-Rank manuscript direction.

Expanded split summary:

| Split | Clips | Samples |
| --- | ---: | ---: |
| Train | 35 | 4175 |
| Validation | 8 | 1040 |
| Test | 7 | 910 |

Current 50-clip seed stability for `candidate_ranker_non_vl`:

| Model | Top-1 | MRR | Pose MAE | Status |
| --- | --- | --- | --- | --- |
| Non-VL candidate ranker, 50 clips | 0.7711 +/- 0.0455 | 0.8713 +/- 0.0208 | 0.4131 +/- 0.0045 | current_best_pilot |

Comparison against the earlier 25-clip pilot:

| Subset | Top-1 | MRR | Pose MAE |
| --- | --- | --- | --- |
| 25 clips | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| 50 clips | 0.7711 +/- 0.0455 | 0.8713 +/- 0.0208 | 0.4131 +/- 0.0045 |

Remaining split warnings: test is missing `food_waffles`, `potato_masher`, and
`spatula_red`; train has low sample counts for `bottle_ranch`, `cellphone`, and
`mug_white`. These warnings keep the result in pilot/debug status.

Vision-language and PreHOI-Former runs are retained as exploratory ablations.
They are not the current main claim because the order-safe non-VL candidate
ranker is more stable under repeated seeds.

## 50-Clip 5-Seed Candidate-Ranker Protocol

The first 5-seed final-protocol run was completed for the order-safe non-VL
candidate ranker on the 50-clip local subset.

Protocol settings:

- model: `candidate_ranker_non_vl`
- candidate order: `stable_uid`
- seeds: 42, 123, 2026, 7, 99
- train/validation/test sample counts: 4175 / 1040 / 910
- forecast-frame input count: 0 for all splits
- summary: `results/tables/final_candidate_ranker_summary.csv`

Mean and standard deviation:

| Metric | Mean +/- Std |
| --- | ---: |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 |
| MRR | 0.8605 +/- 0.0221 |
| Pose MSE | 0.4301 +/- 0.0116 |
| Pose MAE | 0.4102 +/- 0.0051 |

This is the current strongest paper-candidate diagnostic for PreHOI-Rank, but
it remains limited by derived proxy labels, the 50-clip local subset, residual
class imbalance, and MANO/UmeTrack pose-vector evaluation rather than MPJPE.

Generate the metric summary with:

```powershell
python src/training/collect_pilot_results.py
python src/training/print_best_pilot_models.py --summary results/tables/pilot_experiment_summary.csv
```
