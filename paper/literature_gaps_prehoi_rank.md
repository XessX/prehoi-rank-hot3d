# Literature Gaps for PreHOI-Rank

This note summarizes the research gap that the PreHOI-Rank manuscript should
argue for after citation verification.

- Most 3D hand-object interaction work emphasizes estimating hand pose, object
  pose, contact, or reconstruction during/after interaction rather than ranking
  likely future target objects before contact.

- Egocentric action anticipation datasets motivate future interaction reasoning,
  but they often frame the problem as action/verb/noun prediction rather than
  leakage-safe candidate ranking among visible object proposals.

- Contact and action labels are not always directly available in annotation
  formats such as HOT3D-Clips, so transparent derived proxy-label protocols are
  needed when constructing pre-contact forecasting tasks.

- Evaluation can be inflated by temporal leakage if future-frame annotations,
  adjacent samples, or random sample-level splits allow future information to
  enter the model or the split.

- Candidate-ranking evaluation can also be inflated by candidate-order leakage
  if raw annotation order, proxy-score order, or target-aware ordering places
  the correct object in an easy position.

- Candidate-level ranking is more appropriate than global object classification
  when the task is to select the likely future target from a visible set of
  object candidates in each observation window.

- Reporting position-only baselines, random-candidate expectations, clip-level
  splits, and repeated-seed mean/std should be part of a defensible protocol for
  pre-contact candidate-ranking experiments.
