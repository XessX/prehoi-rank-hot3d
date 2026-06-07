# 50-Clip vs 75-Clip Candidate-Ranker Protocol Comparison

This note compares the completed 50-clip and 75-clip final-protocol
candidate-ranker runs for PreHOI-Rank. Both use derived target-object proxy
labels, `candidate_order=stable_uid`, clip-level splitting, and
`input_uses_forecast_frame=false`.

## Dataset and Split Comparison

| Property | 50-Clip Protocol | 75-Clip Protocol |
| --- | ---: | ---: |
| Local shards | 50 | 75 |
| Proxy samples | 6,500 | 9,750 |
| Raw proxy classes | 25 | 32 |
| Optimized eligible classes | 23 | 30 |
| Classes appearing in 3+ clips | 22 | 26 |
| Train samples | 4,175 | 6,714 |
| Validation samples | 1,040 | 1,430 |
| Test samples | 910 | 1,430 |
| Shared train/val/test classes | 20 | 17 |

The 75-clip subset is larger and covers more classes overall, but the optimized
split has fewer classes shared across train, validation, and test. This is the
main reason the larger subset should be treated as a harder robustness check
rather than an automatic improvement.

## Result Comparison

| Metric | 50-Clip 5-Seed Result | 75-Clip 5-Seed Result | Direction |
| --- | ---: | ---: | --- |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 | 0.7115 +/- 0.0571 | 50-clip higher |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 | 0.9789 +/- 0.0009 | 75-clip higher |
| MRR | 0.8605 +/- 0.0221 | 0.8340 +/- 0.0343 | 50-clip higher |
| Pose MSE | 0.4301 +/- 0.0116 | 0.5854 +/- 0.0296 | 50-clip lower |
| Pose MAE | 0.4102 +/- 0.0051 | 0.4676 +/- 0.0096 | 50-clip lower |

## Candidate-Order Baseline Comparison

| Test Baseline | 50-Clip | 75-Clip |
| --- | ---: | ---: |
| Candidate-0 top-1 | 0.1857 | 0.0280 |
| First-3 top-3 | 0.5681 | 0.4420 |
| Position-only MRR | 0.4377 | 0.2945 |
| Expected random top-1 | 0.2025 | 0.1817 |

The 75-clip test split has a much lower candidate-position baseline, making it
less vulnerable to candidate-order shortcuts. This is scientifically useful even
though the learned Top-1/MRR metrics are lower.

## Split-Warning Comparison

50-clip warnings:

- Test missing: `food_waffles`, `potato_masher`, `spatula_red`.
- Low train count: `bottle_ranch=16`, `cellphone=6`, `mug_white=4`.

75-clip warnings:

- Train has classes below 20 samples: `can_soup=1`, `whiteboard_marker=13`.
- Validation missing: `bottle_mustard`, `can_parmesan`, `dino_toy`,
  `dvd_remote`, `food_waffles`.
- Test missing: `aria_small`, `bottle_mustard`, `cellphone`, `food_waffles`,
  `holder_black`, `holder_gray`, `mug_patterned`, `puzzle_toy`,
  `whiteboard_eraser`, `whiteboard_marker`.

## Recommendation

Report both results if space allows:

- Use the 50-clip result as the current primary paper-candidate result because
  it has higher Top-1, higher MRR, better pose-parameter error, and more shared
  train/validation/test classes.
- Use the 75-clip result as a robustness and scalability check showing that the
  protocol remains leakage-safe and order-safe on a larger, harder local subset.

Do not claim that 75 clips improves the main metric. The honest conclusion is
that expanding to 75 clips increases data and class coverage, but the optimized
split becomes harder and less balanced across validation/test, reducing Top-1,
MRR, and pose-vector accuracy.
