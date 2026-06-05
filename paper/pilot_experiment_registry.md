# Pilot Experiment Registry

This registry tracks model-development runs only. Nothing here is a final paper
result, and target-object labels are derived proxy labels rather than direct
HOT3D ground truth.

## Dataset Scope

- Dataset: HOT3D-Clips local subset.
- Local shards: 25.
- Proxy sample index: 3250 samples before optimized filtering.
- Optimized filtered split: 2673 samples, 16 eligible proxy classes.
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

Generate the metric summary with:

```powershell
python src/training/collect_pilot_results.py
python src/training/print_best_pilot_models.py --summary results/tables/pilot_experiment_summary.csv
```
