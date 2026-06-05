# Expanded Related Work Draft

This is a draft scaffold for the manuscript related-work section. Citation keys
are placeholders until bibliographic details and BibTeX entries are verified.
Do not treat this as a final literature review.

## 3D Hand-Object Interaction Understanding

Research on 3D hand-object interaction has increasingly moved from isolated hand
pose estimation toward joint reasoning about hands, objects, and their spatial
relationships. Early and widely used datasets such as HO-3D introduced real
hand-object image sequences with 3D hand and object pose annotations, making it
possible to evaluate joint hand-object pose estimation under occlusion
[HO3D]. DexYCB expanded the benchmark setting with multi-view RGB-D capture of
hand grasping over YCB objects and tasks including 6D object pose and 3D hand
pose estimation [DexYCB]. HOT3D extends this line toward egocentric multi-view
recordings from head-mounted devices, with synchronized camera streams,
hand/object pose annotations, object models, and multimodal data [HOT3D].

PreHOI-Rank differs from full hand-object reconstruction benchmarks. It does not
claim to recover full interaction geometry from raw video. Instead, it uses
HOT3D-Clips annotations to define and evaluate a pre-contact target-object
candidate-ranking task. This makes the method closer to forecasting and
target-selection than to pure reconstruction.

## 3D Hand Pose, MANO, and UmeTrack

Many recent hand-object datasets and models rely on parametric hand
representations. MANO provides a compact articulated hand model that is widely
used for hand pose and shape modeling [MANO]. HOT3D also provides hand
annotations in MANO and UmeTrack formats, which makes these representations
directly relevant to the current pose targets [HOT3D], [UmeTrack].

In the present project, future hand pose is evaluated as a MANO/UmeTrack
pose-vector regression target. This is a practical first step for pipeline
validation, but it is not yet equivalent to MPJPE-style evaluation over 3D hand
joints. A future version should convert MANO/UmeTrack parameters to 3D joints
before making stronger pose-estimation claims.

## Egocentric Hand-Object Forecasting

Egocentric video datasets such as FPHA and EPIC-KITCHENS have helped frame hand
action recognition and action anticipation from first-person observations
[FPHA], [EPIC-KITCHENS]. AssemblyHands focuses on egocentric 3D hand pose for
activity understanding, showing the value of accurate hand pose annotations in
challenging hand-object settings [AssemblyHands]. These works motivate
pre-contact forecasting, where the system must reason about what the wearer is
likely to do before the action is fully observed.

PreHOI-Rank focuses on a narrower but concrete version of this problem:
forecasting the likely future target among visible object candidates. The task
uses observation-window cues only and evaluates whether candidate-level
hand-object geometry is predictive of the derived future target-object proxy.

## Hand-Object Contact and Affordance Reasoning

Hand-object interaction is strongly shaped by contact, reachability, and object
affordances. Datasets and methods that study contact or affordance reasoning
provide useful context for interpreting hand-object proximity as a signal
[Affordance reasoning]. However, the current PreHOI-Rank labels are not
human-annotated contact labels. They are derived proxy labels based on
forecast-frame hand-object proximity.

This distinction is important. The proxy is useful because it provides a
reproducible supervision signal for pre-contact target ranking, but it may not
always match semantic intent, action labels, or physical contact. The manuscript
should therefore present the proxy as an affordance-grounded approximation, not
as direct ground truth.

## Candidate Ranking and Object Interaction Prediction

Many interaction settings are naturally candidate-based: the question is not
which object class exists in the scene, but which visible object is most likely
to become relevant next. PreHOI-Rank adopts this candidate-ranking formulation
for pre-contact target-object anticipation. The model receives a set of visible
object candidates from the observation window and predicts a masked score for
each candidate.

This framing contrasts with closed-set global classification. Candidate ranking
allows the target space to be sample-specific and requires explicit candidate
ordering controls. In this project, ranking is trained with a candidate-index
target derived from the forecast-frame proxy, while all candidate features come
from the observation window. Additional citations are still needed for active
object prediction, proposal ranking, and object-interaction candidate scoring
[ActiveObjectRanking], [CandidateRankingLoss].

## Leakage-Safe Evaluation in Temporal Forecasting

Temporal forecasting can be vulnerable to leakage if future frames, adjacent
clips, or annotation order encode the target. PreHOI-Rank explicitly separates
forecast-frame target construction from observation-frame inputs. The target
object proxy is computed at the forecast frame, but no forecast-frame hand
boxes, object boxes, proxy scores, candidate scores, images, or metadata are
used as model input.

The evaluation also uses clip-level train/validation/test splits rather than
random sample-level splits. Candidate order is fixed by stable object
identifiers with `candidate_order: stable_uid`. Unsafe candidate orders such as
raw/as-is order, proxy-score order, or target-aware order are excluded. The
paper reports candidate-0, first-3, random-candidate, and position-only MRR
baselines to distinguish model performance from candidate-position bias.
Dedicated citations are still needed for temporal leakage and split design in
video forecasting [Temporal leakage].

## Vision-Language Models and Exploratory Ablations

Vision-language models such as CLIP provide transferable image-text
representations and are natural candidates for object-centric interaction
reasoning [CLIP]. The project includes frozen CLIP and vision-language
experiments as exploratory ablations. However, these components are not the
current main claim because repeated-seed evidence favors the non-vision-language
candidate ranker on the 50-clip local subset.

The manuscript should therefore discuss vision-language features as a future
extension or ablation rather than as the core contribution. This keeps the paper
aligned with the evidence: leakage-safe candidate ranking with observation-frame
hand-object geometry is currently the strongest and most stable formulation.
