# Expanded 75-Clip HOT3D-Clips Dataset Note

This note documents the local HOT3D-Clips expansion from 50 shards to 75 shards for PreHOI-Rank. It is a dataset-preparation checkpoint only. No model training was run in this step, and target-object labels remain derived proxy labels rather than HOT3D ground-truth contact or action labels.

## Expansion Summary

- Local shard count: 75 `.tar` shards
- Total local shard size: 7,773,685,760 bytes, approximately 7.24 GiB
- Proxy sample count: 9,750
- Proxy assignments: 9,750
- Average proxy confidence: 0.9200
- Low-confidence proxy count: 0
- Raw target-object proxy classes: 32
- Optimized eligible classes: 30
- Classes appearing in at least 3 clips: 26

The two raw classes filtered out during optimized splitting were `birdhouse_toy` and `mouse`, because they did not satisfy the configured class-coverage criteria.

## Classes Appearing In At Least 3 Clips

`aria_small`, `bottle_ranch`, `bowl`, `can_parmesan`, `can_soup`, `can_tomato_sauce`, `carton_milk`, `carton_oj`, `cellphone`, `coffee_pot`, `dumbbell_5lb`, `dvd_remote`, `flask`, `food_vegetables`, `holder_black`, `holder_gray`, `keyboard`, `mug_patterned`, `mug_white`, `plate_bamboo`, `potato_masher`, `puzzle_toy`, `spatula_red`, `spoon_wooden`, `vase`, `whiteboard_eraser`.

## Optimized Split Summary

The optimized split was generated with clip-level splitting and the same leakage-safe configuration used in earlier protocol work.

| Split | Clips | Samples |
| --- | ---: | ---: |
| Train | 52 | 6,714 |
| Validation | 11 | 1,430 |
| Test | 11 | 1,430 |

Shared target-object proxy classes across train/validation/test:

`bottle_ranch`, `bowl`, `can_soup`, `can_tomato_sauce`, `carton_milk`, `carton_oj`, `coffee_pot`, `dumbbell_5lb`, `flask`, `food_vegetables`, `keyboard`, `mug_white`, `plate_bamboo`, `potato_masher`, `spatula_red`, `spoon_wooden`, `vase`.

The split contains 17 classes shared across all three splits. Train covers every validation/test class, but validation and test do not cover all eligible classes.

## Remaining Split-Quality Warnings

- Train has classes below 20 samples: `can_soup=1`, `whiteboard_marker=13`.
- Validation is missing: `bottle_mustard`, `can_parmesan`, `dino_toy`, `dvd_remote`, `food_waffles`.
- Test is missing: `aria_small`, `bottle_mustard`, `cellphone`, `food_waffles`, `holder_black`, `holder_gray`, `mug_patterned`, `puzzle_toy`, `whiteboard_eraser`, `whiteboard_marker`.

These warnings do not indicate leakage, but they mean the 75-clip split is still not a fully class-balanced benchmark. Any 75-clip result should report these limitations explicitly.

## Candidate-Order Bias Check

Candidate order was checked using `candidate_order=stable_uid`. All rankable samples contained the target candidate.

| Split | Rankable Samples | Candidate-0 Top-1 | First-3 Top-3 | Position-Only MRR | Expected Random Top-1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Train | 6,714 | 0.1833 | 0.5329 | 0.4227 | 0.1818 |
| Validation | 1,430 | 0.1140 | 0.6140 | 0.4011 | 0.2014 |
| Test | 1,430 | 0.0280 | 0.4420 | 0.2945 | 0.1817 |

The test candidate-0 baseline is very low, which suggests the stable UID ordering is not leaking the target through candidate position.

## Image-Stats Feature Cache Refresh

Because the optimized split changed after the 75-clip expansion, lightweight observation-frame image statistics were re-extracted. Frozen CLIP features were not re-extracted.

| Split | Feature Shape | Missing Images |
| --- | ---: | ---: |
| Train | `[6714, 16, 12]` | 0 |
| Validation | `[1430, 16, 12]` | 0 |
| Test | `[1430, 16, 12]` | 0 |

These features are extracted only from observation-frame images. No forecast-frame images or features are used as input.

## Readiness Decision

The 75-clip subset is ready for a leakage-safe 5-seed candidate-ranker protocol run, but it should be treated as a cautious next experiment rather than an automatic replacement for the 50-clip result. The expansion increases the sample count and eligible class count, and the candidate-order baseline is safer on the test split. However, class imbalance and missing validation/test classes remain.

Recommended next step: run the same stable non-VL candidate-ranker protocol on this 75-clip split, then compare against the completed 50-clip 5-seed result before updating the manuscript claims.
