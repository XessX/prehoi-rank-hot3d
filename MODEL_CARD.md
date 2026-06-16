# Model Card: PreHOI-Rank Candidate Ranker

## Model and Task

PreHOI-Rank is a candidate-ranking model for pre-contact 3D hand-object
interaction forecasting in egocentric video. Given an observation window and a
set of visible object candidates, the model ranks the candidate objects and
predicts a future MANO/UmeTrack pose-parameter vector.

## Inputs

- Observation-window hand/object metadata.
- Observation-window object candidate features.
- Candidate mask for padded candidates.

Forecast-frame images, hand boxes, object boxes, metadata, proxy scores, or
candidate ordering are not valid inputs.

## Outputs

- Candidate ranking scores.
- Future pose-parameter vector.

## Training and Evaluation Data Scope

The current manuscript reports:

- a 50-clip HOT3D-Clips local subset as the primary controlled evaluation;
- a 75-clip HOT3D-Clips local subset as a robustness/scalability check.

The target-object labels are derived proxy labels generated from forecast-frame
hand-object proximity. They are not direct HOT3D ground truth.

## Metrics

- Top-1 candidate accuracy.
- Top-3 candidate accuracy.
- Mean reciprocal rank.
- MANO/UmeTrack pose-parameter vector MSE/MAE.

MPJPE is not reported.

## Limitations

- Evaluation is not on the full HOT3D-Clips release.
- Proxy labels may be noisy or incorrect when proximity does not match intent.
- Residual class imbalance remains.
- Pose metrics are parameter-vector errors, not 3D joint errors.
- The method assumes the future target appears in the visible candidate set.
- Not validated for safety-critical decision making.

## Intended Use

Research on pre-contact hand-object interaction forecasting and leakage-safe
candidate-ranking protocols.

## Not Suitable For

- Safety-critical assistive systems without additional validation.
- Claims about direct human intent or contact labels.
- Full-dataset HOT3D benchmark claims without additional evaluation.
