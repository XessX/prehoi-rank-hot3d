# PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting

## Abstract

Anticipating which object a person is about to interact with is an important
step toward pre-contact hand-object interaction forecasting in egocentric
video. We present PreHOI-Rank, a leakage-safe candidate-ranking formulation for
forecasting likely future hand-object targets before contact. Rather than
training a closed-set classifier over all object classes, the method ranks
visible object candidates from the observation window using hand-object geometry
and temporal metadata. We construct derived affordance-grounded proxy labels
from HOT3D-Clips by selecting the forecast-frame object most aligned with hand
proximity, while strictly preventing forecast-frame features from entering the
model input. Candidate order is fixed with stable object identifiers, and
position-biased candidate orders are excluded. On a 50-clip local HOT3D-Clips
subset with clip-level splits, the order-safe non-vision-language candidate
ranker achieves 5-seed paper-candidate diagnostics of 0.7499 +/- 0.0450 top-1
candidate accuracy, 0.9699 +/- 0.0161 top-3 accuracy, 0.8605 +/- 0.0221 MRR,
and 0.4102 +/- 0.0051 future pose-vector MAE. These results support candidate
ranking as a practical and reproducible formulation for pre-contact target
forecasting, while remaining limited by derived proxy labels, local-subset
evaluation, residual class imbalance, and pose-vector rather than MPJPE-style
pose evaluation.

## Keywords

Egocentric video; hand-object interaction; pre-contact forecasting; candidate
ranking; HOT3D-Clips; affordance proxy labels; leakage prevention; 3D hand pose.

## 1. Introduction

Pre-contact hand-object interaction forecasting asks whether a system can infer
an upcoming interaction before physical contact occurs. This problem is useful
for assistive augmented reality, robotic anticipation, and wearable systems
that need to reason about a user's likely next object target. In egocentric
video, the challenge is not only to recognize what is visible, but also to
anticipate which visible object is likely to become the target of a future hand
interaction.

An intuitive approach is to train a global object classifier. However, this can
be brittle when the relevant target is one of several visible candidates and
when class coverage is limited by the available local subset. We therefore
frame pre-contact target forecasting as candidate ranking: given an observation
window and a set of visible object candidates, the model scores each candidate
as the likely future hand-object target.

The central contribution of this draft is not a claim of state-of-the-art
performance. Instead, we present a reproducible, leakage-safe protocol for
building and evaluating an affordance-grounded candidate-ranking task from
HOT3D-Clips. The current evidence supports the following narrower claim: with
careful proxy-label construction, clip-level splitting, stable candidate
ordering, and explicit position baselines, hand-object geometry provides a
strong signal for pre-contact target-object candidate ranking.

Vision-language and transformer variants explored during development are kept
as ablations and future extensions. The current strongest model is the simpler
non-vision-language candidate ranker, which is more stable under repeated seeds
on the 50-clip local subset.

## 2. Related Work Placeholder

This section will later review:

- egocentric action anticipation and hand-object interaction forecasting,
- hand-object pose estimation and affordance reasoning,
- target-object prediction and object-centric interaction modeling,
- candidate ranking versus closed-set classification,
- leakage and split design in video forecasting benchmarks,
- vision-language models for object and interaction reasoning.

The current draft does not yet include full citations. This section should be
completed before submission.

## 3. Dataset and Preprocessing

We use HOT3D-Clips as the current source for egocentric hand-object interaction
data. The present experiments use a 50-clip local subset rather than the full
dataset. Each clip is stored as a tar shard containing image streams and
per-frame annotations including hands, objects, cameras, and metadata.

Samples are built as fixed pre-contact forecasting windows. Each sample contains
16 observation frames and a forecast frame 5 frames after the observation
window. Observation frames provide all model inputs. The forecast frame provides
the derived target-object proxy and future hand-pose vector.

The current 50-clip index contains 6500 derived proxy samples before optimized
class filtering. The optimized clip-level split contains 4175 train samples,
1040 validation samples, and 910 test samples. Clip-level splitting is required
to avoid leakage from temporally adjacent samples appearing across different
splits.

The split is improved over earlier 25-clip pilots, but it remains imperfect.
The test split is missing `food_waffles`, `potato_masher`, and `spatula_red`,
and the train split has low counts for `bottle_ranch`, `cellphone`, and
`mug_white`. These limitations must be retained in any paper-facing
interpretation.

## 4. Derived Target-Object Proxy Label

The current task uses a derived target-object proxy rather than direct HOT3D
ground truth. For each forecast frame, visible hand boxes are combined into a
hand union box. Visible object candidates are scored according to overlap with
the hand union box and normalized center distance. The object with the highest
score is selected as the target-object proxy.

This proxy is intended to approximate the object most aligned with future hand
contact or affordance use. It is not a human action label, contact label, or
official target-object annotation. The proxy is used only as the supervised
target. The model is not allowed to use forecast-frame hand boxes, object boxes,
proxy scores, candidate scores, images, or metadata as input.

Each sample stores:

- observation frame IDs,
- forecast frame ID,
- observation-frame object candidates,
- forecast-frame derived target-object proxy,
- future MANO/UmeTrack pose vector,
- metadata and safety flags.

The key safety flag is `input_uses_forecast_frame=false`, which must hold for
all valid experiments.

## 5. PreHOI-Rank Method

PreHOI-Rank formulates target anticipation as candidate ranking over visible
object candidates. The model receives an observation-window metadata sequence
and a padded set of object candidates. Candidate features include object
geometry, visibility, hand-object proximity features computed from observation
frames, and candidate masks.

The current strongest model is the non-vision-language candidate ranker. It
uses a temporal encoder for observation metadata and an object-candidate encoder
for candidate features. The model outputs one ranking score per candidate and a
future pose-vector regression output. Training combines candidate-ranking
cross-entropy with pose regression loss.

Candidate order is fixed using `stable_uid`, which sorts by stable object
identifier or name rather than by proxy score or target-aware information.
Raw/as-is and proxy-sorted orderings are excluded because they can produce
candidate-position leakage. The model must outperform position-only baselines,
including candidate-0 top-1, first-3 top-3, random-candidate expectation, and
position-only MRR.

Vision-language and PreHOI-Former models are retained as exploratory ablations.
They are not treated as the primary method because the present repeated-seed
evidence favors the non-vision-language candidate ranker.

## 6. Experimental Protocol

The protocol uses the 50-clip local HOT3D-Clips subset with optimized clip-level
train/validation/test splits. The final-protocol candidate-ranker run uses five
seeds: 42, 123, 2026, 7, and 99.

Required safety rules:

- forecast-frame proxy labels may be used only as targets,
- no forecast-frame features may be used as input,
- candidate order must be `stable_uid`,
- raw/as-is and proxy-sorted candidate orderings are excluded,
- train/validation/test splitting must be clip-level,
- proxy labels must be described as derived labels, not ground truth.

Metrics include top-1 candidate accuracy, top-3 candidate accuracy, mean
reciprocal rank, pose MSE, and pose MAE. Pose metrics currently operate on
MANO/UmeTrack pose vectors. MPJPE-style 3D joint evaluation is future work.

## 7. Results

The primary paper-candidate result is the 5-seed final-protocol run of the
order-safe non-vision-language candidate ranker on the 50-clip local subset.

| Metric | Mean +/- Std |
| --- | ---: |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 |
| MRR | 0.8605 +/- 0.0221 |
| Pose MSE | 0.4301 +/- 0.0116 |
| Pose MAE | 0.4102 +/- 0.0051 |

The 50-clip protocol improves over the earlier 25-clip pilot:

| Setting | Top-1 | MRR | Pose MAE |
| --- | ---: | ---: | ---: |
| 25-clip, 3-seed pilot | 0.5624 | 0.7502 | 0.4412 |
| 50-clip, 5-seed protocol | 0.7499 | 0.8605 | 0.4102 |

The test split position baselines under `stable_uid` order are:

| Baseline | Value |
| --- | ---: |
| Candidate-0 top-1 | 0.1857 |
| First-3 top-3 | 0.5681 |
| Position-only MRR | 0.4377 |
| Expected random top-1 | 0.2025 |
| Expected random top-3 | 0.5947 |

The candidate ranker substantially exceeds candidate-0 and position-only MRR
baselines. Top-3 accuracy is high, but it should be interpreted alongside the
first-3 and random top-3 baselines because many samples contain a small number
of candidates.

## 8. Discussion

The current evidence suggests that candidate-level ranking is a better fit for
this local HOT3D-Clips proxy task than global target-object classification.
The formulation asks the model to choose among observed candidates, which
matches the pre-contact setting more directly than predicting one class from a
fixed global vocabulary.

The improvement from the 25-clip pilot to the 50-clip protocol suggests that
data expansion and split quality matter strongly. The current result should be
read as evidence that the PreHOI-Rank formulation is promising, not as a final
benchmark claim.

The fact that the non-vision-language ranker is strongest is also important.
It indicates that observation-window hand-object geometry is a strong signal
and that vision-language components should remain ablations until they improve
under the same leakage-safe, order-safe repeated-seed protocol.

## 9. Limitations

- The experiment uses a 50-clip local HOT3D-Clips subset, not the full dataset.
- Target-object labels are derived proxy labels, not direct HOT3D ground truth.
- The proxy is based on forecast-frame hand-object proximity and may not always
  match semantic intent, action labels, or contact labels.
- Some class imbalance remains in the optimized split.
- Pose metrics are MANO/UmeTrack pose-vector MAE/MSE, not MPJPE.
- Vision-language and PreHOI-Former variants are not yet the strongest
  components.
- The related-work section and citation grounding are not yet complete.

## 10. Conclusion

PreHOI-Rank presents a focused and evidence-supported formulation for
pre-contact hand-object target forecasting: rank the visible object candidates
using observation-window cues while preventing forecast-frame leakage and
candidate-order bias. On the current 50-clip HOT3D-Clips local subset, the
order-safe non-vision-language candidate ranker produces stable 5-seed
paper-candidate diagnostics. The result supports candidate ranking as the main
research direction, while future work should expand the dataset subset,
strengthen class coverage, add 3D joint pose metrics, and revisit
vision-language fusion as a controlled ablation.
