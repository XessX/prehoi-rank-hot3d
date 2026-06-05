# PreHOI-Rank Result Tables

## Main 50-Clip Five-Seed Candidate-Ranker Result

Model: `candidate_ranker_non_vl`

Dataset: 50-clip local HOT3D-Clips subset

Candidate order: `stable_uid`

Target labels: derived proxy labels, not direct HOT3D ground truth

| Metric | Mean +/- Std |
| --- | ---: |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 |
| MRR | 0.8605 +/- 0.0221 |
| Pose MSE | 0.4301 +/- 0.0116 |
| Pose MAE | 0.4102 +/- 0.0051 |

## Per-Seed Results

| Seed | Top-1 | Top-3 | MRR | Pose MSE | Pose MAE |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 42 | 0.8198 | 0.9484 | 0.8934 | 0.4372 | 0.4128 |
| 123 | 0.7297 | 0.9802 | 0.8522 | 0.4170 | 0.4087 |
| 2026 | 0.7637 | 0.9626 | 0.8683 | 0.4463 | 0.4178 |
| 7 | 0.7352 | 0.9901 | 0.8548 | 0.4246 | 0.4056 |
| 99 | 0.7011 | 0.9681 | 0.8339 | 0.4252 | 0.4061 |

## 25-Clip Versus 50-Clip Comparison

| Setting | Top-1 | MRR | Pose MAE |
| --- | ---: | ---: | ---: |
| 25-clip, 3-seed pilot | 0.5624 | 0.7502 | 0.4412 |
| 50-clip, 5-seed protocol | 0.7499 | 0.8605 | 0.4102 |

## Test Split Position Baselines

| Baseline | Value |
| --- | ---: |
| Candidate-0 top-1 | 0.1857 |
| First-3 top-3 | 0.5681 |
| Position-only MRR | 0.4377 |
| Expected random top-1 | 0.2025 |
| Expected random top-3 | 0.5947 |

These values are paper-candidate diagnostics only. The manuscript must state
that the labels are derived proxies and that the experiment uses a 50-clip local
subset.
