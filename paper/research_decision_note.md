# Research Decision Note

Project title: PreHOI-Rank: Affordance-Grounded Candidate Ranking for
Pre-Contact 3D Hand-Object Interaction Forecasting.

This note records the current research direction after HOT3D-Clips pilot
experiments and seed-stability checks. It is not a results section and should
not be treated as final paper evidence.

## Dataset State

- Dataset: HOT3D-Clips local subset.
- Local data: 75 downloaded shards available locally.
- Primary controlled protocol: 50 clips, 6500 derived target-object proxy
  samples before optimized filtering.
- Robustness/scalability protocol: 75 clips, 9750 derived target-object proxy
  samples before optimized filtering.
- Split policy: clip-level split only.
- Input policy: observation frames only.
- Label policy: target-object labels are derived proxy labels, not direct HOT3D
  ground truth.

## Valid Pilot Models

- Metadata-only baseline.
- Leakage-safe object-aware metadata baseline.
- Image-stats visual-object baseline.
- Frozen CLIP visual-object baseline.
- Non-VL candidate ranker.
- VL candidate ranker.
- PreHOI-Former v1.
- PreHOI-Former v1 controlled ablations.
- PreHOI-Former v2 dual-branch pilot.

## Invalid Or Excluded Runs

- Object-aware metadata attempt before the leakage audit.
- Candidate ranker using raw/as-is candidate order.

These runs are excluded because forecast-frame leakage or candidate-position
order bias would make any metric scientifically unsafe.

## Seed-Stability Result

Three-seed pilot stability was run with seeds 42, 123, and 2026.

| Model | Top-1 | MRR | Pose MAE |
| --- | --- | --- | --- |
| Non-VL candidate ranker | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| PreHOI-Former v1 | 0.4131 +/- 0.0283 | 0.6603 +/- 0.0143 | 0.4933 +/- 0.0382 |
| PreHOI-Former v1 geometry-only/no-attention | 0.5164 +/- 0.0180 | 0.7306 +/- 0.0092 | 0.4941 +/- 0.0370 |

The simpler non-VL candidate ranker is currently the strongest stable pilot
model across ranking and pose metrics. PreHOI-Former v1 had a strong single run,
but that single-run result is not stable enough to use as the main model claim.

## 50-Clip Final-Protocol Update

The local HOT3D-Clips subset was expanded from 25 clips to 50 clips. The
expanded subset contains 6500 derived proxy samples before optimized class
filtering. The optimized split contains 4175 train samples, 1040 validation
samples, and 910 test samples across 23 eligible proxy classes.

The order-safe non-VL candidate ranker was rerun on the expanded split with
`candidate_order: stable_uid` and observation-frame inputs only.

| Subset | Top-1 | MRR | Pose MAE |
| --- | --- | --- | --- |
| 25 clips | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| 50 clips | 0.7499 +/- 0.0450 | 0.8605 +/- 0.0221 | 0.4102 +/- 0.0051 |

This update strengthens the evidence that affordance-grounded candidate ranking
is the current best stable formulation. The result is a paper-candidate
diagnostic, not an unconditional final benchmark claim: target-object labels are
derived proxies, not direct HOT3D ground truth, and the 50-clip split still has
class-coverage warnings.

## 75-Clip Robustness Update

The local subset was later expanded to 75 clips. This increased the proxy sample
count to 9750, but the optimized split became broader and less balanced. The
75-clip run is therefore treated as robustness/scalability analysis, not as a
replacement for the 50-clip primary result.

| Subset | Role | Top-1 | MRR | Pose MAE |
| --- | --- | ---: | ---: | ---: |
| 50 clips | Primary result | 0.7499 +/- 0.0450 | 0.8605 +/- 0.0221 | 0.4102 +/- 0.0051 |
| 75 clips | Robustness check | 0.7115 +/- 0.0571 | 0.8340 +/- 0.0343 | 0.4676 +/- 0.0096 |

## Decisions

- Do not claim PreHOI-Former v1 as the final model yet.
- Treat candidate-level ranking as the main stable formulation.
- Use the order-safe non-VL candidate ranker as the current best stable pilot
  baseline.
- Treat PreHOI-Former variants as architecture-development experiments until a
  redesigned version improves under repeated seeds.
- Treat vision-language components as exploratory ablations and future
  extensions unless they beat the stable candidate-ranking baseline under the
  same split and repeated-seed protocol.
- Use **PreHOI-Rank** as the recommended manuscript direction.
- Keep current numbers labeled as paper-candidate diagnostics tied to local
  subsets and derived proxy labels.

## Next Research Needs

- Do not pursue further data expansion unless reviewers request it or a new
  split strategy improves shared class coverage.
- Redesign PreHOI-Former around the stable candidate-ranking formulation instead
  of forcing the current v1 attention design.
- Add MANO/UmeTrack-to-3D-joint conversion for MPJPE-style pose evaluation.
- Improve text and vision-language fusion with stronger controls against
  overfitting and order bias.
- Keep final evaluations repeated over multiple seeds under the locked
  leakage-safe protocol.

## Current Paper Direction

The honest current paper direction is not "vision-language guided PreHOI-Former
already wins." The defensible direction is:

Candidate-level pre-contact object ranking is a promising and stable framing for
HOT3D-Clips proxy targets. The recommended working title is:

**PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D
Hand-Object Interaction Forecasting**

The current PreHOI-Former and vision-language family remains an active model
development path, but it needs redesign and stronger validation before becoming
the main claimed method.
