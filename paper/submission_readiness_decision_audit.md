# Submission-Readiness Decision Audit

Status: decision audit draft.
Date: 2026-06-08.

This audit asks whether the PreHOI-Rank manuscript should be submitted with the
current 50-clip result or strengthened first. It does not change the manuscript
claims. Target-object labels remain derived proxy labels, not ground truth.

## Current Manuscript Status

- Working title: **PreHOI-Rank: Affordance-Grounded Candidate Ranking for
  Pre-Contact 3D Hand-Object Interaction Forecasting**.
- Dataset scope: local 50-shard HOT3D-Clips subset, not full HOT3D-Clips or
  full HOT3D.
- Main formulation: leakage-safe candidate-level ranking over visible object
  candidates.
- Main safety controls:
  - `candidate_order: stable_uid`,
  - `input_uses_forecast_frame=false`,
  - clip-level train/validation/test split,
  - as-is/proxy-sorted candidate orders excluded.
- Manuscript state: expanded draft, figures, citation scaffold, result note,
  cover letter draft, and data/code availability draft exist.
- Submission-ready status: **not yet**.

## Current Strongest Result

Current paper-candidate result on the 50-clip local HOT3D-Clips subset:

| Metric | Five-seed result |
| --- | ---: |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 |
| MRR | 0.8605 +/- 0.0221 |
| Pose MSE | 0.4301 +/- 0.0116 |
| Pose MAE | 0.4102 +/- 0.0051 |

This result is promising and reproducible within the current local subset, but
it should remain tied to the limitations of derived proxy labels and local
subset evaluation.

## Current Strengths

- Clear and evidence-supported paper direction: candidate-level pre-contact
  object ranking is stronger than the exploratory PreHOI-Former/VL variants.
- Leakage controls are explicit and implemented.
- Candidate-order bias was audited, and unsafe candidate orders are excluded.
- Five-seed protocol result is available for the current main method.
- Position baselines are recorded for candidate-order safety.
- Figures and tables now support the manuscript narrative.
- Citations for the core dataset, pose representation, contact reasoning,
  learning-to-rank, and data leakage have been verified or partially verified.

## Current Weaknesses

- The dataset remains a local 50-clip subset, not the full HOT3D-Clips release.
- Labels are derived proxy labels rather than human action/contact labels.
- Class imbalance remains in the optimized split.
- Pose evaluation is still MANO/UmeTrack pose-vector MAE/MSE, not MPJPE.
- No stronger external baseline has been added beyond internal baselines and
  candidate-position controls.
- HOT3D-Clips license/access wording still needs final pre-submission checking.
- Final journal formatting, highlights, graphical abstract decision, and author
  statements are incomplete.

## Journal Risk Assessment

### Machine Learning with Applications

Risk level: **medium to high** if submitted immediately.

Rationale:

- The method and protocol are technically coherent and aligned with applied
  machine-learning evaluation concerns.
- The leakage/order-bias prevention angle is a real strength.
- The main empirical result is repeatable over five seeds.
- However, reviewers may view a 50-clip local subset and proxy-label target as
  insufficient without either more data, a stronger comparative baseline, or a
  more standard 3D pose metric such as MPJPE.

Likely reviewer pressure:

- Justify why 50 clips are enough.
- Explain whether proxy labels correlate with actual contact/intent.
- Add MPJPE or 3D joint metrics.
- Compare against a stronger baseline or simpler heuristic more thoroughly.

### PLOS ONE Backup

Risk level: **medium** if framed as a transparent reproducible protocol paper.

Rationale:

- PLOS ONE may be more receptive to a carefully scoped, reproducible method with
  transparent limitations.
- The paper must still be methodologically sound and complete.
- The derived proxy-label limitation and local subset scope must be front and
  center.

Likely reviewer pressure:

- Tighten reproducibility and data-access details.
- Avoid overclaiming model novelty.
- Provide full limitations around proxy labels and subset selection.

## Option Comparison

### Option A: Submit With Current 50-Clip Result and Transparent Limitations

- Benefit: Fastest route to submission; current pipeline, manuscript, figures,
  and five-seed result are already coherent.
- Time/complexity: Low.
- Risk reduction: Low.
- Recommendation: **Not preferred for Machine Learning with Applications**. It
  may be viable only if the manuscript is framed very conservatively and the
  target journal accepts the local-subset/proxy-label scope.

### Option B: Expand to 75 Clips Before Submission

- Benefit: Improves dataset coverage, class diversity, and reviewer confidence
  that the 50-clip result is not subset-specific.
- Time/complexity: Medium. Requires selecting/downloading additional shards,
  rebuilding proxy indexes, optimizing split, checking candidate-order bias, and
  rerunning the final protocol.
- Risk reduction: Medium to high.
- Recommendation: **Recommended if download/storage/time budget allows**. This
  is the best data-strengthening step and directly addresses the local-subset
  weakness.

### Option C: Add MANO/UmeTrack to 3D-Joint Conversion and Report MPJPE

- Benefit: Converts pose evaluation into a more standard hand-pose metric,
  making the pose branch easier for reviewers to interpret.
- Time/complexity: Medium to high, depending on official HOT3D/MANO/UmeTrack
  tooling availability and license constraints.
- Risk reduction: High for pose-evaluation credibility.
- Recommendation: **Best scientific strengthening step** if feasible. If not
  feasible quickly, document why pose-vector MAE is used and treat pose as an
  auxiliary diagnostic.

### Option D: Add Stronger External/Comparative Baseline

- Benefit: Reduces concern that the method only beats weak internal baselines.
- Time/complexity: Medium to high. Requires selecting a fair baseline that uses
  the same observation-only inputs, stable candidate order, and clip-level split.
- Risk reduction: Medium to high.
- Recommendation: **Recommended after Option B or C**, unless a simple fair
  baseline can be implemented quickly. Avoid adding an unfair or leakage-prone
  baseline just to pad the table.

## Decision

The manuscript should **not** be treated as submission-ready today.

Minimum acceptable path:

- Complete final citation/license/formatting checks.
- Keep the 50-clip result framed as local-subset evidence.
- Strengthen the limitations and proxy-label discussion.

Preferred path before Machine Learning with Applications submission:

1. Add either 75-clip expansion or MPJPE-style pose evaluation.
2. Rerun the final candidate-ranker protocol after the chosen strengthening
   step.
3. Update the manuscript result table and limitations.

Best path if time allows:

1. Expand to 75 clips.
2. Add MPJPE if official conversion is feasible.
3. Add one fair external/simple comparative baseline under the same safety
   protocol.

## Current Decision State

Recommendation: **strengthen before submission**.

Priority order:

1. MANO/UmeTrack-to-3D-joint conversion and MPJPE, if feasible.
2. 75-clip expansion and final protocol rerun.
3. Stronger fair baseline.

If time is constrained, Option B is likely the most straightforward next
experiment. If technical feasibility is good, Option C is the most valuable for
pose-metric credibility.
