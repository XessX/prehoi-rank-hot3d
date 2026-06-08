# Methods Draft: PreHOI-Rank

## Dataset Preprocessing

We use HOT3D-Clips as the current experimental source for egocentric
hand-object interaction forecasting. The primary controlled protocol uses a
50-clip local subset stored as HOT3D-Clips tar shards. A 75-clip local expansion
is reported separately as a robustness/scalability analysis. Each clip contains
synchronized image streams and per-frame JSON annotations for hands, objects,
cameras, and metadata.

For each clip, we construct fixed-length pre-contact forecasting windows. A
sample contains an observation window of 16 frames and a forecast frame 5 frames
after the end of the observation window. The observation window provides model
inputs. The forecast frame provides the supervised derived target and future
hand-pose target.

The primary 50-clip index contains 6500 derived proxy samples before optimized
class filtering. The optimized clip-level split contains 4175 train samples,
1040 validation samples, and 910 test samples. The 75-clip robustness index
contains 9750 derived proxy samples before optimized filtering and uses 6714
train samples, 1430 validation samples, and 1430 test samples. The 75-clip split
is broader but harder and less balanced, so it does not replace the 50-clip
primary result.

## Proxy Target-Object Definition

HOT3D-Clips does not provide direct labels for the specific target-object
forecasting task used in the current experiments. We therefore define a derived
target-object proxy from forecast-frame hand-object proximity.

For each forecast frame, visible hand boxes are combined into a hand union box.
Visible object candidates are scored using overlap with the hand union box and
normalized center distance. The object with the strongest score is selected as
the target-object proxy. The proxy record stores the selected object ID, object
name, proxy score, proxy confidence, and all candidate scores.

This label is a derived proxy target, not direct HOT3D ground truth. The proxy
is used only as a supervised target. The model input never includes
forecast-frame object boxes, hand boxes, proxy scores, or candidate scores.

## Candidate Ranking Formulation

PreHOI-Rank formulates pre-contact target-object anticipation as candidate
ranking. Instead of predicting a global object class from a fixed label set, the
model ranks the visible object candidates observed before contact.

For each sample, the model receives:

- an observation-frame temporal metadata sequence,
- observation-frame object candidate features,
- a candidate mask,
- stable candidate identifiers and metadata.

The model predicts a score for each candidate. Training uses cross-entropy over
the candidate index corresponding to the derived target-object proxy, when that
target is present in the observation-frame candidate set. The same model also
regresses a future MANO-pose vector for the forecast frame.

This formulation is useful because it avoids assuming that every target object
must be predicted from a closed global class list. It also forces evaluation to
compare the model against explicit position-only and random-candidate baselines.

## Leakage and Order-Bias Prevention

All valid experiments use observation-frame inputs only:

- `input_uses_forecast_frame=false`
- target proxy from forecast frame only as a supervised target
- object candidate features from the last observation frame or observation
  window only
- no forecast-frame image, object, hand, proxy-score, or candidate-score input

Candidate order is fixed with `candidate_order: stable_uid`. Raw/as-is ordering
is excluded because it can encode unsafe target-position bias. Every
candidate-ranking run must report:

- target candidate position distribution,
- candidate-0 top-1 baseline,
- first-3 top-3 baseline,
- random-candidate expectation,
- position-only MRR.

Experiments that use forecast-frame inputs, target-aware ordering, proxy-score
ordering, or random sample-level splits are excluded from paper claims.

## Model Overview

The current strongest pilot model is the non-vision-language candidate ranker.
It encodes the observation metadata sequence with a temporal encoder and encodes
each object candidate with an object-feature encoder. Candidate scores are
computed from fused temporal context and candidate features. A separate pose
head regresses the future hand-pose vector.

The main current model uses:

- temporal observation features,
- object candidate geometry,
- visibility and proximity features computed from observation frames,
- candidate masks,
- stable UID candidate ordering.

Vision-language and PreHOI-Former variants are retained as exploratory
ablations. They are not the main method claim unless they beat the non-VL
candidate ranker under the same split, safety checks, and repeated-seed
protocol.

## Evaluation Metrics

Candidate-ranking metrics:

- top-1 candidate accuracy,
- top-3 candidate accuracy,
- mean reciprocal rank.

Pose metrics:

- pose MSE,
- pose MAE,
- MPJPE-style 3D-joint error is not reported in the current results because the
  MANO/UmeTrack-to-joint conversion path has not yet been validated.

Data and safety diagnostics:

- proxy confidence statistics,
- rankable candidate coverage,
- candidate-position baseline metrics,
- split class distributions,
- classes missing from train/validation/test,
- seed mean and standard deviation.

The current 50-clip and 75-clip numbers are paper-candidate diagnostics, not
unqualified final benchmark claims. Final manuscript reporting must preserve the
locked splits, repeated-seed protocol, safety audits, and limitations for
derived proxy labels.
