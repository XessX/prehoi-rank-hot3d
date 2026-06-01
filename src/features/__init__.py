"""Feature extraction utilities.

The MVP consumes synthetic feature tensors. Real feature extraction modules are
kept separate so HOT3D integration can add visual, hand, object, affordance,
and language features without changing the training loop.
"""

