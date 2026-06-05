# Contribution Statement: PreHOI-Rank

Working title:

**PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D
Hand-Object Interaction Forecasting**

This document states the current manuscript contributions without overclaiming.
The paper should not claim state-of-the-art performance, should not call derived
proxy labels ground truth, and should keep all results tied to the 50-clip local
HOT3D-Clips subset unless more data is added.

## Contributions

1. **Pre-contact candidate-ranking formulation**

   We formulate pre-contact target-object forecasting as ranking visible object
   candidates from the observation window. This avoids forcing the task into a
   closed-set global object classifier and better matches scenarios where the
   relevant future target is one object among several visible candidates.

2. **Derived affordance-grounded target-object proxy protocol**

   We define a reproducible target-object proxy from forecast-frame
   hand-object proximity. The proxy selects the visible forecast-frame object
   most aligned with hand overlap and normalized center distance. The proxy is
   explicitly treated as a derived label, not direct HOT3D ground truth.

3. **Leakage- and order-bias-safe evaluation protocol**

   We enforce observation-frame-only inputs, clip-level splits, and
   `candidate_order: stable_uid`. We exclude forecast-frame inputs,
   target-aware candidate ordering, `as_is` ordering, and proxy-sorted ordering.
   We also report candidate-position baselines so candidate-ranker performance
   is not confused with order bias.

4. **Empirical 5-seed validation on 50 HOT3D-Clips shards**

   On a 50-clip local HOT3D-Clips subset, the order-safe non-VL candidate
   ranker achieves 5-seed paper-candidate diagnostics of top-1
   `0.7499 +/- 0.0450`, top-3 `0.9699 +/- 0.0161`, MRR
   `0.8605 +/- 0.0221`, pose MSE `0.4301 +/- 0.0116`, and pose MAE
   `0.4102 +/- 0.0051`. These results support candidate ranking as the main
   evidence-backed formulation, with limitations around proxy labels,
   local-subset evaluation, class imbalance, and pose-vector metrics.
