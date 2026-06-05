# Research Decision Note

Project title: PreHOI-Rank: Affordance-Grounded Candidate Ranking for
Pre-Contact 3D Hand-Object Interaction Forecasting.

This note records the current research direction after HOT3D-Clips pilot
experiments and seed-stability checks. It is not a results section and should
not be treated as final paper evidence.

## Dataset State

- Dataset: HOT3D-Clips local subset.
- Local data: 25 shards.
- Proxy index: 3250 derived target-object proxy samples before optimized
  filtering.
- Optimized filtered split: 2673 samples across 16 eligible proxy classes.
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

## 50-Clip Expansion Update

The local HOT3D-Clips subset was expanded from 25 clips to 50 clips. The
expanded subset contains 6500 derived proxy samples before optimized class
filtering. The optimized split contains 4175 train samples, 1040 validation
samples, and 910 test samples across 23 eligible proxy classes.

The order-safe non-VL candidate ranker was rerun on the expanded split with
`candidate_order: stable_uid` and observation-frame inputs only.

| Subset | Top-1 | MRR | Pose MAE |
| --- | --- | --- | --- |
| 25 clips | 0.5624 +/- 0.0693 | 0.7502 +/- 0.0312 | 0.4412 +/- 0.0042 |
| 50 clips | 0.7711 +/- 0.0455 | 0.8713 +/- 0.0208 | 0.4131 +/- 0.0045 |

This update strengthens the evidence that affordance-grounded candidate ranking
is the current best stable formulation. The result is still pilot/debug only:
target-object labels are derived proxies, not direct HOT3D ground truth, and
the 50-clip split still has class-coverage warnings.

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
- Keep all current numbers labeled as pilot/debug only.

## Next Research Needs

- Download or select more HOT3D-Clips shards to improve split diversity and
  reduce proxy-class fragility.
- Redesign PreHOI-Former around the stable candidate-ranking formulation instead
  of forcing the current v1 attention design.
- Add MANO/UmeTrack-to-3D-joint conversion for MPJPE-style pose evaluation.
- Improve text and vision-language fusion with stronger controls against
  overfitting and order bias.
- Repeat final evaluation over multiple seeds after data expansion and model
  redesign.

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
