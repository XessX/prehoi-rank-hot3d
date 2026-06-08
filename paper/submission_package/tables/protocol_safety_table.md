# Protocol Safety Table

## Required Safety Conditions

| Safety Condition | Requirement | Current Status |
| --- | --- | --- |
| Forecast-frame input exclusion | Model inputs must use observation frames only | Satisfied; train/val/test forecast-input count is 0 |
| Target proxy usage | Forecast-frame proxy may be used only as supervised target | Satisfied |
| Candidate order | Must use `stable_uid` | Satisfied |
| Unsafe candidate order | `as_is`, proxy-sorted, or target-aware order excluded | Satisfied |
| Split policy | Clip-level train/validation/test split | Satisfied |
| Label wording | Derived proxy labels, not direct HOT3D annotations | Required in all paper text |
| Generated artifacts | Logs/checkpoints/results ignored by Git | Satisfied |

## Current Split Summary

| Split | Clips | Samples | Forecast-Input Count |
| --- | ---: | ---: | ---: |
| Train | 35 | 4175 | 0 |
| Validation | 8 | 1040 | 0 |
| Test | 7 | 910 | 0 |

## Candidate-Order Bias Diagnostics

Test split with `stable_uid` candidate order:

| Diagnostic | Value |
| --- | ---: |
| Rankable samples | 910 / 910 |
| Candidate-0 top-1 baseline | 0.1857 |
| First-3 top-3 baseline | 0.5681 |
| Position-only MRR | 0.4377 |
| Expected random top-1 | 0.2025 |
| Expected random top-3 | 0.5947 |

## Remaining Split Warnings

| Warning Type | Details |
| --- | --- |
| Test missing classes | `food_waffles`, `potato_masher`, `spatula_red` |
| Low train counts | `bottle_ranch=16`, `cellphone=6`, `mug_white=4` |

These warnings do not invalidate the current paper-candidate diagnostic, but
they must be included as limitations unless the dataset is expanded or filtered
again before submission.
