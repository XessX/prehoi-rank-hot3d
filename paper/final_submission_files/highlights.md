# Highlights

- PreHOI-Rank formulates pre-contact hand-object forecasting as candidate-level ranking over visible objects.
- Derived affordance-grounded proxy labels use forecast-frame hand-object proximity, while forecast-frame features are excluded from model inputs.
- Clip-level splits, stable candidate ordering, and position baselines reduce temporal and candidate-order leakage risks.
- A 50-clip HOT3D-Clips local subset provides the primary controlled result; a 75-clip expansion is reported as robustness/scalability analysis.
- Pose metrics are MANO/UmeTrack pose-parameter vector MAE/MSE; MPJPE is not reported.
