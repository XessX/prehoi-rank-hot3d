# Expanded 50-Clip HOT3D-Clips Pilot Note

Date: 2026-06-05

## Status

This note records a pilot/debug rerun after expanding the local HOT3D-Clips subset from 25 clips to 50 clips.

These are not final paper results. Target-object labels are derived proxy labels, not direct HOT3D ground truth. The candidate ranker uses `candidate_order: stable_uid` and observation-frame inputs only.

## Expanded Dataset Summary

- Local HOT3D-Clips shards: 50
- Total local shard size: 4.786 GB
- Proxy samples: 6500
- Proxy assignments: 6500
- Average proxy confidence: 0.9182
- Low-confidence proxies: 0
- Eligible classes after optimized filtering: 23
- Classes appearing in 3+ clips: 22
- Shared train/validation/test classes after optimized split: 20

## Optimized Split Summary

| Split | Clips | Samples |
| --- | ---: | ---: |
| Train | 35 | 4175 |
| Validation | 8 | 1040 |
| Test | 7 | 910 |

Remaining split-quality warnings:

- Test is missing: `food_waffles`, `potato_masher`, `spatula_red`
- Train has low sample counts for: `bottle_ranch=16`, `cellphone=6`, `mug_white=4`

This split is stronger than the 25-clip split but is still pilot-grade. A final evaluation should either add more clips or use a stricter class filter.

## Candidate-Order Baseline

Candidate order: `stable_uid`

| Split | Candidate-0 Top-1 | First-3 Top-3 | Position-Only MRR | Rankable Samples |
| --- | ---: | ---: | ---: | ---: |
| Train | 0.2196 | 0.4989 | 0.4284 | 4175 / 4175 |
| Validation | 0.0067 | 0.4971 | 0.3163 | 1040 / 1040 |
| Test | 0.1857 | 0.5681 | 0.4377 | 910 / 910 |

The `stable_uid` ordering substantially reduces the earlier candidate-0 leakage concern. The model must still be compared against these position-only baselines in any pilot table.

## Single-Run Candidate Ranker Metrics

Model: non-VL HOT3D candidate ranker

| Metric | Value |
| --- | ---: |
| Candidate top-1 | 0.7462 |
| Candidate top-3 | 0.9560 |
| MRR | 0.8586 |
| Pose MSE | 0.4062 |
| Pose MAE | 0.4076 |

This run is a pilot/debug diagnostic only.

## Three-Seed Stability

Seeds: 42, 123, 2026

| Model | Top-1 Mean +/- Std | MRR Mean +/- Std | Pose MAE Mean +/- Std |
| --- | ---: | ---: | ---: |
| candidate_ranker_non_vl | 0.7711 +/- 0.0455 | 0.8713 +/- 0.0208 | 0.4131 +/- 0.0045 |

Per-seed results:

| Seed | Top-1 | Top-3 | MRR | Pose MSE | Pose MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.8198 | 0.9484 | 0.8934 | 0.4372 | 0.4128 |
| 123 | 0.7297 | 0.9802 | 0.8522 | 0.4170 | 0.4087 |
| 2026 | 0.7637 | 0.9626 | 0.8683 | 0.4463 | 0.4178 |

## Comparison Against 25-Clip Pilot Stability

| Dataset Subset | Model | Top-1 Mean +/- Std | MRR Mean +/- Std | Pose MAE Mean +/- Std |
| --- | --- | ---: | ---: | ---: |
| 25 clips | candidate_ranker_non_vl | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| 50 clips | candidate_ranker_non_vl | 0.7711 +/- 0.0455 | 0.8713 +/- 0.0208 | 0.4131 +/- 0.0045 |

The expanded subset improves the pilot candidate-ranking diagnostics and slightly improves pose MAE. This supports the current research decision that candidate-level ranking is the strongest stable formulation so far. It does not establish final paper performance because the labels are derived proxies and the split still has class-coverage limitations.

## Next Steps

- Add more clips or filter to classes with train/validation/test coverage before final evaluation.
- Rerun baselines after the final split is locked.
- Keep candidate-order and observation-only input audits in every training script.
- Add MANO/UmeTrack-to-3D-joint conversion for MPJPE-style pose evaluation.
- Treat vision-language and PreHOI-Former variants as model-development experiments until they are stable over repeated seeds.
