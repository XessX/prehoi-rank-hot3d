# Related Work Plan: PreHOI-Rank

This file structures the related-work section without inventing citations.
Replace placeholders such as `[REF-HOI-1]` with real references after literature
review.

## 3D Hand-Object Interaction Understanding

Goal:

Position PreHOI-Rank relative to work that estimates hands, objects, and their
3D relationships in egocentric or interaction scenes.

Topics to cover:

- 3D hand pose estimation from images or video `[REF-HAND-POSE-1]`.
- Hand-object pose estimation and interaction reconstruction `[REF-HOI-3D-1]`.
- Object pose and modeled-object interaction datasets `[REF-OBJECT-POSE-1]`.
- HOT3D and related egocentric 3D interaction datasets `[REF-HOT3D-1]`.

Connection to this paper:

PreHOI-Rank does not claim to solve full 3D reconstruction. It uses available
HOT3D-Clips hand/object annotations to study pre-contact target candidate
ranking and future pose-vector prediction.

## Egocentric Hand-Object Forecasting

Goal:

Relate the task to action anticipation, future hand trajectory forecasting, and
egocentric interaction prediction.

Topics to cover:

- Egocentric action anticipation `[REF-EGO-ACTION-1]`.
- Future hand trajectory or contact anticipation `[REF-HAND-FORECAST-1]`.
- Target-object or active-object prediction in egocentric video
  `[REF-ACTIVE-OBJECT-1]`.
- Pre-contact forecasting as a stricter temporal setting than post-contact
  recognition `[REF-PRECONTACT-1]`.

Connection to this paper:

PreHOI-Rank focuses on ranking currently visible object candidates before
contact, using observation-window cues only.

## Hand-Object Contact and Affordance Reasoning

Goal:

Ground the derived proxy in prior work on contact, affordance, and hand-object
spatial relationships.

Topics to cover:

- Contact prediction and hand-object contact maps `[REF-CONTACT-1]`.
- Object affordance recognition from human interaction `[REF-AFFORDANCE-1]`.
- Spatial hand-object proximity as a cue for likely interaction
  `[REF-SPATIAL-HOI-1]`.

Connection to this paper:

The target-object proxy is affordance-grounded through forecast-frame
hand-object proximity. It is a derived label and should be described as a
practical proxy, not direct semantic intent or human-annotated contact.

## Candidate Ranking and Object Interaction Prediction

Goal:

Justify the choice of candidate ranking over global object classification.

Topics to cover:

- Candidate ranking or proposal scoring in object-centric tasks
  `[REF-RANKING-1]`.
- Active-object selection among visible candidates `[REF-ACTIVE-OBJECT-2]`.
- Ranking losses and masked candidate prediction `[REF-RANKING-LOSS-1]`.
- Cases where closed-set classification is less natural than candidate scoring
  `[REF-CANDIDATE-1]`.

Connection to this paper:

PreHOI-Rank treats target forecasting as choosing among observed candidates,
which makes candidate-order safety and position baselines central to the
evaluation protocol.

## Leakage-Safe Evaluation in Temporal Forecasting

Goal:

Frame the paper's protocol contribution around avoiding common temporal
forecasting pitfalls.

Topics to cover:

- Temporal leakage in video splits `[REF-LEAKAGE-1]`.
- Subject/sequence/clip-level split requirements `[REF-SPLIT-1]`.
- Candidate-order or annotation-order bias in ranking tasks `[REF-BIAS-1]`.
- Repeated-seed reporting and uncertainty estimates `[REF-SEED-1]`.

Connection to this paper:

The manuscript should emphasize that forecast-frame features are excluded from
input, candidate order is stable UID based, and position-only baselines are
reported to prevent misleading ranking metrics.

## Vision-Language Models as Exploratory Extensions

Goal:

Mention vision-language approaches without making them the paper's main claim.

Topics to cover:

- Frozen visual or text embeddings for object recognition `[REF-VL-1]`.
- Vision-language grounding in egocentric interaction tasks `[REF-VL-EGO-1]`.
- Limitations of adding text/CLIP features without stable repeated-seed gains
  `[REF-VL-ROBUSTNESS-1]`.

Connection to this paper:

Vision-language and PreHOI-Former variants are exploratory ablations in this
project. The current evidence supports the non-VL candidate ranker as the main
method.
