# Highlights

- PreHOI-Rank frames pre-contact hand-object forecasting as candidate-level ranking over visible objects.
- Derived affordance-grounded proxy labels are constructed from forecast-frame hand-object proximity while forecast-frame features are excluded from model inputs.
- The evaluation protocol uses clip-level splits, stable candidate ordering, and position baselines to reduce temporal and candidate-order leakage.
- The 50-clip HOT3D-Clips local subset is used as the primary controlled result, with a 75-clip expansion reported as a robustness/scalability check.
- Pose metrics are reported as MANO/UmeTrack pose-parameter vector MAE/MSE; MPJPE is not reported.
