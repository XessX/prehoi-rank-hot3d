# Full Consistency Audit

Date: 2026-06-08

## Scope

This audit checks consistency across the PreHOI-Rank manuscript package after
adding the 75-clip robustness protocol. It does not change numerical results.

Reviewed core files:

- `paper/manuscript_prehoi_rank_draft.md`
- `paper/tables/results_table_prehoi_rank.md`
- `paper/final_candidate_ranker_result_note.md`
- `paper/final_candidate_ranker_result_note_75clip.md`
- `paper/compare_50clip_vs_75clip_results.md`
- `paper/submission_readiness_decision_audit.md`
- `paper/next_action_recommendation.md`
- `paper/submission_readiness_checklist.md`
- `paper/figure_plan_prehoi_rank.md`
- `paper/figures/README.md`
- `paper/methods_draft_prehoi_rank.md`
- `paper/research_decision_note.md`

Additional support files checked and adjusted where stale wording was found:

- `paper/contribution_statement_prehoi_rank.md`
- `paper/data_code_availability_draft.md`
- `paper/figure_quality_review.md`
- `paper/final_experiment_protocol.md`
- `paper/hand_pose_conversion_feasibility.md`
- `paper/submission_file_checklist.md`

## Consistency Findings

### 50-Clip and 75-Clip Roles

Status: consistent after edits.

- The 50-clip protocol is consistently described as the primary controlled
  paper-candidate result.
- The 75-clip protocol is consistently described as a robustness/scalability
  analysis on a broader but harder local subset.
- Stale wording that described the 75-clip expansion as pending was removed or
  updated.

### Metrics

Status: consistent.

Primary 50-clip result:

- Top-1: `0.7499 +/- 0.0450`
- Top-3: `0.9699 +/- 0.0161`
- MRR: `0.8605 +/- 0.0221`
- Pose MSE: `0.4301 +/- 0.0116`
- Pose MAE: `0.4102 +/- 0.0051`

75-clip robustness result:

- Top-1: `0.7115 +/- 0.0571`
- Top-3: `0.9789 +/- 0.0009`
- MRR: `0.8340 +/- 0.0343`
- Pose MSE: `0.5854 +/- 0.0296`
- Pose MAE: `0.4676 +/- 0.0096`

25-clip pilot:

- Top-1: `0.5624 +/- 0.0693`
- MRR: `0.7502 +/- 0.0312`
- Pose MAE: `0.4412 +/- 0.0042`
- Top-3 is marked as not reported in the comparison table.

### Pose Metric Wording

Status: consistent.

- Current pose metrics are described as MANO/UmeTrack or MANO pose-parameter
  vector MAE/MSE.
- MPJPE is not reported.
- MPJPE-style 3D-joint evaluation remains future work or pending validated
  official conversion dependencies/assets.

### Proxy Label Wording

Status: consistent.

- Target-object labels are consistently described as derived proxy labels.
- They are not described as direct HOT3D ground truth, human action labels, or
  official contact labels.

### Leakage and Candidate-Order Safety

Status: consistent.

- Valid runs use observation-frame inputs only.
- `input_uses_forecast_frame=false` remains the required safety condition.
- `candidate_order: stable_uid` remains the required candidate-order policy.
- Raw/as-is, proxy-sorted, or target-aware candidate orderings remain excluded.

### Figure and Table References

Status: consistent after edits.

- Figure 5 now reflects the 25/50/75-clip comparison.
- Figure documentation, figure plan, and submission file checklist now refer to
  the 75-clip robustness comparison.
- Result tables distinguish the 50-clip primary result from the 75-clip
  robustness check.

### Limitations and Recommendations

Status: consistent after edits.

- Limitations consistently include derived proxy labels, local subsets,
  residual class imbalance, and pose-vector rather than MPJPE evaluation.
- Recommendations now emphasize manuscript polishing, final formatting,
  journal/APC verification, optional MPJPE if validated, and optional fair
  baseline work.
- Further data expansion beyond 75 clips is not recommended unless reviewers
  request it or a new split strategy improves shared class coverage.

## Wording Fixes Applied

- Replaced stale "75-clip expansion pending" language with completed
  robustness/scalability wording.
- Updated the methods draft to describe both the 50-clip primary protocol and
  the 75-clip robustness protocol.
- Updated the research decision note to use the final 50-clip five-seed metrics
  instead of earlier pilot-only 50-clip metrics.
- Updated Figure 5 documentation from "25 vs 50" to "25/50/75".
- Updated data/code availability wording to mention both the 50-clip primary
  split and 75-clip robustness split.
- Updated contribution and feasibility notes to avoid stale "unless more data
  is added" or "switch to 75 clips" wording.

## Remaining Pending Items

- Final journal formatting.
- Final Machine Learning with Applications route/APC/Research4Life verification.
- Final HOT3D-Clips license/access wording.
- Citation placeholder cleanup if any remain in the final manuscript.
- MPJPE-style pose evaluation only if the official conversion path can be
  validated.
- Optional stronger fair baseline under the same leakage/order-safety protocol.
