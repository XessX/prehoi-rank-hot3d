<!-- DRAFT EXPORT: author metadata, journal formatting, APC/waiver, and HOT3D license/access checks remain pending. -->
# PreHOI-Rank Manuscript Draft Export

**Status:** DRAFT. Not submission-ready until author metadata and final journal checks are complete.

## Title Page

# Title Page Draft

Status: draft. Human author details are required before submission.

## Full Title

PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting

## Short Title

PreHOI-Rank for Pre-Contact Hand-Object Forecasting

## Author Placeholder Table

| Order | Full author name | Affiliation number(s) | Email | ORCID |
| --- | --- | --- | --- | --- |
| 1 | [Author 1 full name] | [1] | [email] | [ORCID if used] |
| 2 | [Author 2 full name] | [2] | [email] | [ORCID if used] |
| 3 | [Author 3 full name] | [3] | [email] | [ORCID if used] |

Add or remove rows after the final author list is confirmed.

## Affiliations Placeholder

| Number | Institution | Department/unit | City | Country |
| --- | --- | --- | --- | --- |
| 1 | [Institution] | [Department/unit] | [City] | [Country] |
| 2 | [Institution] | [Department/unit] | [City] | [Country] |
| 3 | [Institution] | [Department/unit] | [City] | [Country] |

## Corresponding Author Placeholder

- Name: [Corresponding author full name]
- Email: [Corresponding author email]
- Affiliation: [Affiliation number and institution]
- Postal address: [Postal address if required]
- Phone number: [Phone number if required]

## CRediT Author Contribution Placeholder

Confirm roles with all authors before submission.

| Author | Conceptualization | Methodology | Software | Validation | Formal analysis | Investigation | Data curation | Writing - original draft | Writing - review and editing | Visualization | Supervision | Funding acquisition |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [Author 1] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] |
| [Author 2] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] | [yes/no] |

## Declarations Checklist

- [ ] Conflict of interest statement confirmed by all authors.
- [ ] Funding statement confirmed by all authors.
- [ ] Acknowledgments confirmed by all authors.
- [ ] Data/code availability statement confirmed.
- [ ] HOT3D-Clips license/access wording confirmed.
- [ ] Machine Learning with Applications APC/waiver/Research4Life route checked
      using final author affiliations.
- [ ] Corresponding author details match the submission system.

\newpage

## Main Manuscript

# PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting

## Author Placeholder Block

Author names, affiliations, emails, ORCID IDs, and contribution roles require
human confirmation before submission.

| Order | Author | Affiliation(s) | Email | ORCID |
| --- | --- | --- | --- | --- |
| 1 | [Author 1 full name] | [Affiliation number(s)] | [Email] | [ORCID if used] |
| 2 | [Author 2 full name] | [Affiliation number(s)] | [Email] | [ORCID if used] |
| 3 | [Author 3 full name] | [Affiliation number(s)] | [Email] | [ORCID if used] |

Affiliations:

- [1] [Department/unit, institution, city, country]
- [2] [Department/unit, institution, city, country]
- [3] [Department/unit, institution, city, country]

## Corresponding Author Placeholder

- Name: [Corresponding author full name]
- Email: [Corresponding author email]
- Affiliation: [Affiliation number and institution]

## Abstract

Pre-contact hand-object forecasting asks whether an egocentric perception
system can infer the likely object of a future hand interaction before contact
occurs. The problem is relevant to assistive augmented reality, wearable
interfaces, and robotic systems that must reason from partial observations of
human intent. We present PreHOI-Rank, a leakage-safe candidate-ranking
formulation for pre-contact 3D hand-object interaction forecasting. Rather than
predicting a target from a global closed-set vocabulary, PreHOI-Rank scores the
visible object candidates in an observation window and jointly predicts a
future hand-pose representation. We construct derived affordance-grounded
target-object proxy labels from HOT3D-Clips [@hot3d2025], [@hot3dclips2026]
using forecast-frame hand-object proximity, while preventing forecast-frame
images, annotations, candidate scores, and metadata from entering the model
input. Stable candidate ordering is enforced to avoid candidate-position
leakage. On a local 50-clip HOT3D-Clips subset with clip-level splits, the
order-safe non-vision-language candidate ranker achieves five-seed
paper-candidate diagnostics of 0.7499 +/- 0.0450 Top-1 candidate accuracy,
0.9699 +/- 0.0161 Top-3 candidate accuracy, 0.8605 +/- 0.0221 MRR, and 0.4102
+/- 0.0051 future pose-vector MAE. These results support candidate ranking as
a practical formulation for pre-contact target forecasting under derived
labels, while leaving important limitations around the local 50-clip subset,
residual class imbalance, proxy-label assumptions, and pose-vector rather than
MPJPE-style evaluation.

## Keywords

Egocentric video; hand-object interaction; pre-contact forecasting; candidate
ranking; HOT3D-Clips; affordance proxy labels; leakage prevention; 3D hand pose.

## Highlights

- PreHOI-Rank frames pre-contact hand-object forecasting as candidate-level ranking over visible objects.
- Derived affordance-grounded proxy labels are constructed from forecast-frame hand-object proximity while forecast-frame features are excluded from model inputs.
- The evaluation protocol uses clip-level splits, stable candidate ordering, and position baselines to reduce temporal and candidate-order leakage.
- The 50-clip HOT3D-Clips local subset is used as the primary controlled result, with a 75-clip expansion reported as a robustness/scalability check.
- Pose metrics are reported as MANO/UmeTrack pose-parameter vector MAE/MSE; MPJPE is not reported.

## 1. Introduction

Before contact occurs, human object interactions are often foreshadowed by hand
motion, the body-centered viewpoint, and the changing spatial relation between
hands and nearby objects. Anticipating this interaction can help egocentric
systems act earlier: an assistive AR interface may prepare object-specific
guidance, a robot may infer a user's likely target, and a wearable perception
system may forecast hand-object contact before it is visually obvious.

This paper focuses on pre-contact target-object forecasting in egocentric
video. The goal is to use an observation window before contact to infer which
visible object candidate is most likely to become the future hand-object target,
while also predicting a future hand-pose representation. Figure 1 summarizes
this problem setting.

[Figure 1 here: `paper/figures/fig1_problem_overview.png`; PDF version:
`paper/figures/fig1_problem_overview.pdf`.]

A direct approach would cast the task as global object classification. Although
convenient, that framing is not always well matched to egocentric interaction.
In many frames, the practical question is not "which object class in the
dataset is present?" but "which currently visible object will the hand
approach?" Global classification can also make evaluation sensitive to local
class coverage and can hide candidate-order or temporal leakage effects.

We therefore propose PreHOI-Rank: a candidate-level formulation that ranks the
visible object candidates in each observation window. The current strongest
model is intentionally simple. It uses observation-window hand/object metadata
and object candidate features, excludes forecast-frame inputs, sorts candidates
with stable identifiers, and trains with a candidate-ranking objective plus
future pose-vector regression. More complex vision-language and transformer
variants are retained as exploratory ablations, but they are not the main
claim because they have not yet outperformed the order-safe non-vision-language
ranker under repeated-seed evaluation.

This paper makes four contributions:

1. We formulate pre-contact target-object forecasting as ranking visible object
   candidates rather than closed-set global classification.
2. We define a reproducible derived target-object proxy from forecast-frame
   hand-object proximity and clearly distinguish it from human contact or
   action annotations.
3. We introduce a leakage- and order-bias-safe evaluation protocol with
   observation-frame-only inputs, clip-level splitting, stable candidate
   ordering, and position-only baselines.
4. We provide five-seed paper-candidate diagnostics on a 50-clip local
   HOT3D-Clips subset, showing that the order-safe candidate ranker is stronger
   than candidate-position baselines and improves over the earlier 25-clip
   pilot.

The manuscript is therefore framed as a reproducible method and evaluation
protocol for pre-contact candidate ranking with derived affordance-grounded
proxy labels, not as a benchmark-superiority claim.

## 2. Related Work

Research on 3D hand-object interaction has produced increasingly rich datasets
for hand pose, object pose, and hand-object state estimation. HO-3D and
HOnnotate support 3D hand-object pose estimation in object-interaction scenes
[@ho3d2020], while DexYCB provides multi-view RGB-D data for hand-object
grasping and pose estimation [@dexycb2021]. HOT3D extends this line of work to
egocentric multi-view video with 3D hand/object tracking, object models, and
multiple annotation streams [@hot3d2025]. The present work builds on
HOT3D-Clips [@hot3dclips2026], while using only a local 50-clip subset and
without redistributing the dataset.

Hand-pose representations are also central to this work. MANO provides a
widely used parametric hand model [@mano2017], and HOT3D includes hand
annotations compatible with MANO/UmeTrack-style representations
[@umetrack2022]. The current experiments regress future pose vectors directly.
They do not yet convert the pose representation to 3D joints for MPJPE-style
evaluation, which remains an important future improvement.

Egocentric interaction datasets and action-anticipation benchmarks motivate the
pre-contact setting. First-person action and hand-action datasets such as FPHA
[@fpha2018], EPIC-KITCHENS [@epickitchens2020], and AssemblyHands
[@assemblyhands2023] show the value of modeling hands, objects, and temporal
context in first-person video. Our focus is narrower: we rank visible object
candidates before contact, using derived proxy labels when direct
target-object/contact annotations are unavailable.

Affordance and contact reasoning are closely related because the target proxy
uses hand-object proximity at a future frame. However, the proxy should not be
interpreted as an official semantic affordance annotation or human contact
annotation.
ContactPose provides a related contact-focused reference for hand-object
grasp/contact modeling [@contactpose2020].

The candidate-ranking formulation is related to learning-to-rank and
object-centric interaction prediction, where the model scores a set of
candidates rather than predicting a single global class. This design is related
to learning-to-rank methods such as RankNet [@burges2005ranknet]. In this
paper, that formulation is also a safety choice: ranking visible candidates
makes candidate-order leakage measurable and allows position-only baselines.

Temporal leakage is a central concern in forecasting. A method that uses
forecast-frame features as input can appear effective while violating the
pre-contact premise. We therefore enforce observation-frame-only inputs and
clip-level train/validation/test splitting, following the broader
machine-learning principle that target information must not be available
through features or evaluation design at prediction time
[@kaufman2012leakage].

## 3. Methods

### 3.1 HOT3D-Clips Local Subset

We use HOT3D-Clips as the current data source [@hot3d2025],
[@hot3dclips2026]. HOT3D-Clips provides curated HOT3D subsequences in
WebDataset shard format, with image streams and per-frame annotations for
hands, objects, cameras, and metadata. The primary controlled experiment uses a
local subset of 50 downloaded shards, not the complete HOT3D or HOT3D-Clips
release. A later 75-clip expansion is reported as a robustness/scalability
analysis rather than as the main result.

The local subset contains 6500 proxy-labeled samples before optimized
class-based filtering. After filtering and optimized clip-level splitting, the
final protocol uses 4175 training samples, 1040 validation samples, and 910 test
samples. The split uses 35 training clips, 8 validation clips, and 7 test clips.
Clip-level splitting is required because neighboring samples from the same clip
can be highly correlated.

### 3.2 Sample Construction

Each sample is a pre-contact forecasting window with 16 observation frames and
a forecast frame 5 frames after the observation window. If the observation
frames are indexed from `t` to `t + 15`, the forecast target is defined at
`t + 20`. Model inputs may use only the observation frames. The forecast frame
is used only to derive the target-object proxy and the future hand-pose vector.

Each sample stores:

- observation frame identifiers;
- the forecast frame identifier;
- observation-frame hand/object metadata;
- observation-frame object candidates;
- the forecast-frame derived target-object proxy label;
- the future MANO/UmeTrack pose vector;
- metadata including clip ID and safety flags.

The key safety flag is `input_uses_forecast_frame=false`. Any run that violates
this flag should be excluded.

### 3.3 Ethics and Data Use

This study uses an existing third-party dataset. The authors did not collect
new human-subject data. HOT3D-Clips data, image streams, raw annotations,
WebDataset shards, object models, and other restricted dataset files are not
redistributed by this project. Users must obtain HOT3D-Clips from the official
provider and follow the dataset license, access conditions, and citation
requirements.

The current manuscript should include a final dataset license/access note after
the official HOT3D-Clips terms are rechecked. The repository should contain
code and regeneration scripts, not downloaded dataset files.

### 3.4 Derived Target-Object Proxy Label

The current target-object labels are derived proxy labels, not direct HOT3D
official annotations. This distinction is central to the paper.

For each forecast frame, the proxy generator collects visible hand boxes and
visible object boxes. It forms a hand union box and scores each candidate object
using overlap with the hand union box and normalized center distance. The
highest-scoring forecast-frame object is selected as the target-object proxy.
Figure 2 illustrates this proxy-label construction.

[Figure 2 here: `paper/figures/fig2_proxy_label_generation.png`; PDF version:
`paper/figures/fig2_proxy_label_generation.pdf`.]

The proxy is intended to approximate the object most aligned with future hand
contact or affordance use. It is not a human action label, not an official
contact annotation, and not a semantic intention label. It can be wrong when
the nearest future object is not the intended object, when bounding boxes are
noisy, when multiple objects are close to the hand, or when the action depends
on context that is not captured by proximity.

The proxy is allowed only as a supervised target. The following forecast-frame
signals are not allowed as model inputs:

- forecast-frame images;
- forecast-frame object boxes;
- forecast-frame hand boxes;
- forecast-frame proxy scores;
- forecast-frame candidate ordering;
- forecast-frame metadata.

This separation preserves the pre-contact forecasting setting: the model sees
only the past observation window and predicts a future target proxy.

### 3.5 Candidate-Ranking Formulation

Given an observation window and a set of visible object candidates, PreHOI-Rank
predicts a score for each candidate. The target is the candidate matching the
derived forecast-frame target-object proxy. Candidates are padded to a fixed
maximum count and accompanied by a candidate mask so invalid padded candidates
do not contribute to the ranking loss.

This formulation differs from global object classification. The model is not
asked to choose among every object class in the dataset. Instead, it chooses
among the objects visible in the current observation context. This better
matches egocentric interaction forecasting, where the target is constrained by
what is present around the hand.

### 3.6 Input Features

The current strongest model uses observation-window metadata and object
candidate features. Temporal metadata summarizes hand/object context over the
16 observation frames. Candidate features describe each visible object from the
observation window, including geometry, visibility, hand-object proximity
computed from observation frames, and object identity features. No image,
CLIP, or forecast-frame features are used in the final candidate-ranker
protocol.

The model also predicts a future MANO/UmeTrack pose vector. This auxiliary
target keeps the formulation connected to 3D hand-object forecasting, although
future work should convert pose parameters to 3D joints for MPJPE-style
evaluation.

### 3.7 Model Architecture

The non-vision-language candidate ranker contains:

- a temporal encoder for observation-window metadata;
- an object-candidate encoder for padded candidate features;
- a fusion module that combines temporal context with candidate features;
- a candidate score head producing one score per candidate;
- a future pose-vector regression head.

The training objective combines candidate-ranking cross-entropy with pose
regression loss. Figure 3 shows the current architecture at a high level.

[Figure 3 here: `paper/figures/fig3_prehoi_rank_architecture.png`; PDF
version: `paper/figures/fig3_prehoi_rank_architecture.pdf`.]

### 3.8 Candidate-Order Safety

Candidate order can create a hidden leakage path. Earlier pilot checks showed
that unsafe ordering could place the target candidate near position 0 too
often, inflating candidate-ranking metrics. PreHOI-Rank therefore uses
`candidate_order: stable_uid`, which sorts candidates by stable object
identifier or object name. The model is not evaluated with raw/as-is ordering,
proxy-score ordering, target-aware ordering, or any order based on
forecast-frame information.

The evaluation also reports position-only baselines, including candidate-0
Top-1, first-3 Top-3, and position-only MRR. A valid ranker must be interpreted
relative to these baselines.

## 4. Experimental Setup

The final-protocol candidate-ranker experiment uses the 50-clip local
HOT3D-Clips subset and optimized clip-level splits. The protocol is summarized
in Table 2 and Figure 4.

[Figure 4 here: `paper/figures/fig4_protocol_safety.png`; PDF version:
`paper/figures/fig4_protocol_safety.pdf`.]

[Table 2 here: `paper/tables/protocol_safety_table.md`.]

The required safety rules are:

- use only observation-frame inputs;
- keep `input_uses_forecast_frame=false`;
- use forecast-frame proxy labels only as supervised targets;
- use `candidate_order: stable_uid`;
- exclude raw/as-is, proxy-sorted, and target-aware candidate orderings;
- split train/validation/test by clip ID, not random sample ID;
- call labels derived proxy labels, not official annotations.

The final candidate-ranker protocol uses five seeds: 42, 123, 2026, 7, and 99.
Metrics are reported as mean +/- standard deviation over seeds.

The ranking metrics are:

- Top-1 candidate accuracy;
- Top-3 candidate accuracy;
- mean reciprocal rank (MRR).

The pose metrics are:

- future pose-vector mean squared error (MSE);
- future pose-vector mean absolute error (MAE).

These pose metrics are computed on the current pose-vector representation, not
on reconstructed 3D joints.

## 5. Results

### 5.1 Main 50-Clip Five-Seed Result

Table 1 reports the main paper-candidate result for the order-safe
non-vision-language candidate ranker on the 50-clip local HOT3D-Clips subset.

[Table 1 here: `paper/tables/results_table_prehoi_rank.md`.]

| Metric | Mean +/- Std |
| --- | ---: |
| Top-1 candidate accuracy | 0.7499 +/- 0.0450 |
| Top-3 candidate accuracy | 0.9699 +/- 0.0161 |
| MRR | 0.8605 +/- 0.0221 |
| Pose MSE | 0.4301 +/- 0.0116 |
| Pose MAE | 0.4102 +/- 0.0051 |

The candidate ranker substantially exceeds the test-split candidate-0 and
position-only MRR baselines under stable UID ordering. Top-3 accuracy, however,
requires a more cautious reading because some samples have small candidate
sets. For that reason, first-3 and random Top-3 baselines are reported
alongside model metrics.

### 5.2 25-Clip Versus 50-Clip Comparison

The 50-clip protocol improves over the earlier 25-clip pilot:

| Setting | Top-1 | Top-3 | MRR | Pose MAE |
| --- | ---: | ---: | ---: | ---: |
| 25-clip, 3-seed pilot | 0.5624 | not reported | 0.7502 | 0.4412 |
| 50-clip, 5-seed primary protocol | 0.7499 +/- 0.0450 | 0.9699 +/- 0.0161 | 0.8605 +/- 0.0221 | 0.4102 +/- 0.0051 |

Figure 5 visualizes this comparison together with the 75-clip robustness
analysis described below.

[Figure 5 here: `paper/figures/fig5_25clip_vs_50clip_results.png`; PDF
version: `paper/figures/fig5_25clip_vs_50clip_results.pdf`.]

The improvement suggests that data expansion and split quality materially
affect this task. It does not establish final generalization to the complete
HOT3D release.

### 5.3 Robustness Analysis on a 75-Clip Expansion

We also expanded the local HOT3D-Clips subset to 75 shards and reran the same
five-seed candidate-ranker protocol. The expansion increased the proxy sample
count from 6500 to 9750 and increased the optimized eligible proxy classes from
23 to 30. However, the resulting split was broader and harder: validation and
test still missed some eligible classes, and the number of classes shared across
train, validation, and test decreased from 20 in the 50-clip protocol to 17 in
the 75-clip protocol.

| Setting | Top-1 | Top-3 | MRR | Pose MAE |
| --- | ---: | ---: | ---: | ---: |
| 50-clip, primary protocol | 0.7499 +/- 0.0450 | 0.9699 +/- 0.0161 | 0.8605 +/- 0.0221 | 0.4102 +/- 0.0051 |
| 75-clip, robustness protocol | 0.7115 +/- 0.0571 | 0.9789 +/- 0.0009 | 0.8340 +/- 0.0343 | 0.4676 +/- 0.0096 |

The 75-clip protocol maintained high Top-3 performance and had a lower
candidate-0 position baseline on the test split. At the same time, Top-1, MRR,
and pose-vector MAE were weaker than in the cleaner 50-clip protocol. We
therefore use the 50-clip protocol as the primary controlled evaluation and
report the 75-clip protocol as a robustness/scalability analysis under a larger
but less balanced local subset.

### 5.4 Exploratory Ablations

During development, metadata-only, object-aware, image-statistics, frozen-CLIP,
candidate-ranker, vision-language candidate-ranker, PreHOI-Former v1, and
PreHOI-Former v2 variants were tested as pilot experiments. Some early runs
were excluded because of leakage or candidate-order safety concerns.

The current manuscript should treat vision-language and PreHOI-Former variants
as exploratory ablations. They are useful for understanding the design space,
but the repeated-seed evidence currently favors the simpler order-safe
non-vision-language candidate ranker.

## 6. Discussion

The results support candidate ranking as the most evidence-backed formulation
in the current project. The model benefits from asking a local,
interaction-specific question: among the visible candidates, which object is
most likely to become the future hand-object target? This framing is closer to
the egocentric interaction problem than predicting a global object class.

The safety protocol is as important as the model itself. Because the target
proxy is derived from the forecast frame, any forecast-frame feature in the
input would make the task artificially easy. Candidate ordering can create a
similar problem when candidates are sorted by target-aware quantities. The
manuscript therefore reports explicit leakage and order-bias controls rather
than interpreting candidate-ranking metrics in isolation.

The finding that the non-vision-language ranker outperforms current
vision-language variants is also informative. It suggests that hand-object
geometry and candidate-level structure are strong signals for this proxy task.
Vision-language fusion may still be valuable, but it should be redesigned and
evaluated as an ablation under the same protocol instead of being claimed as
the central contribution.

## 7. Limitations and Threats to Validity

### Derived Proxy Labels

The target-object labels are derived from forecast-frame hand-object proximity.
They are not human-annotated action labels, direct contact annotations, or
official HOT3D target-object annotations. The proxy may fail when interaction
intent differs from closest-object geometry.

### Local 50-Clip Subset

The primary result uses 50 local HOT3D-Clips shards, not the complete dataset. A
75-clip robustness run was also completed, but it introduced a harder and less
balanced split and did not replace the 50-clip result as the primary controlled
evaluation. Full-dataset or larger-subset evaluation is still needed before
broad generalization claims.

### Residual Class Imbalance

The optimized split improves class coverage, but some imbalance remains. The
test split is missing `food_waffles`, `potato_masher`, and `spatula_red`, and
the train split has low counts for `bottle_ranch`, `cellphone`, and
`mug_white`. These warnings should remain visible in the final manuscript.

### Pose Metric Limitation

Pose evaluation currently uses MANO/UmeTrack pose-vector MSE and MAE. These
metrics are useful for pipeline validation, but they are not equivalent to 3D
joint MPJPE. Future work should convert pose representations to 3D joints if a
validated conversion path is available.

### Candidate Visibility Assumption

The candidate-ranking task assumes that the relevant object is represented in
the visible candidate set. If the future target is absent, occluded, incorrectly
detected, or missing from the candidate annotations, the ranking formulation
cannot select it correctly.

### Exploratory Model Scope

Vision-language and PreHOI-Former variants remain exploratory. Current evidence
does not justify claiming that those components are the main performance driver.

## 8. Data and Code Availability

HOT3D-Clips is a third-party dataset distributed by its original providers. The
authors do not redistribute raw HOT3D-Clips data, WebDataset shards, image
streams, object models, or restricted annotations. Readers should obtain the
dataset directly from the official provider and follow the provider's license,
access, and citation requirements.

The code can be released in a public repository after final cleanup. The
repository should include scripts for HOT3D-Clips inspection, proxy-label
generation, split optimization, leakage checks, candidate-order bias checks,
training, metric collection, and figure generation. Generated sample indexes
can be regenerated from downloaded HOT3D-Clips shards by authorized users.
Whether derived index files can be shared directly must be confirmed against
the dataset terms before submission.

The authors did not collect new private human-subject data. Trained
checkpoints, logs, and derived summaries should be shared only if allowed by
the dataset terms and only if they do not reveal restricted dataset content.

## 9. Ethics and Data Use

The authors did not collect new human-subject data for this study. Experiments
use HOT3D-Clips, a third-party dataset distributed by its original providers.
The raw dataset, video frames, WebDataset shards, object models, annotations,
and restricted dataset files are not redistributed in this submission package.

Users must obtain HOT3D-Clips through the official access route and comply with
the dataset license, access conditions, citation requirements, and data-use
terms. The derived proxy-label protocol and sample-index generation scripts are
intended to be reproducible by authorized users with their own downloaded copy
of the dataset.

## 10. Conflict of Interest

[Author confirmation required.] Draft statement: The authors declare that they
have no known competing financial interests or personal relationships that
could have appeared to influence the work reported in this paper.

## 11. Funding

[Author confirmation required.] Draft statement: This research did not receive
any specific grant from funding agencies in the public, commercial, or
not-for-profit sectors.

## 12. Acknowledgments

[Add acknowledgments after author confirmation, or state "None" if appropriate.]

## 13. Conclusion

PreHOI-Rank frames pre-contact hand-object target forecasting as candidate
ranking over visible objects. The formulation combines derived
affordance-grounded proxy labels, observation-frame-only inputs, stable
candidate ordering, and clip-level splitting to reduce common leakage paths in
temporal forecasting. On the current 50-clip local HOT3D-Clips subset, the
order-safe candidate ranker produces stable five-seed paper-candidate
diagnostics and improves over the earlier 25-clip pilot. The work is not a
complete-dataset benchmark, but it provides a reproducible and cautious
foundation for pre-contact hand-object candidate ranking.

## 14. References Placeholder Note

References should be generated from `references.bib` after final citation and
journal-style checks. The current draft uses citation-style placeholders such as
`[@hot3d2025]` for Markdown/Pandoc-style processing.

\newpage

## Figure Captions

# Figure Caption List

Status: draft captions for the formatted submission package.

## Figure 1

**Figure 1. Pre-contact candidate-ranking setup.** Given an observation window,
PreHOI-Rank ranks visible object candidates as likely future hand-object
targets. The forecast frame is used only to define a derived proxy target and
is not used as model input.

Files:

- `fig1_problem_overview.png`
- `fig1_problem_overview.pdf`

## Figure 2

**Figure 2. Derived target-object proxy construction.** The proxy target is
selected at the forecast frame using hand-object box overlap and normalized
center distance. These forecast-frame quantities define the supervised target
only and are excluded from model inputs.

Files:

- `fig2_proxy_label_generation.png`
- `fig2_proxy_label_generation.pdf`

## Figure 3

**Figure 3. PreHOI-Rank model overview.** The model encodes observation-window
metadata and object candidates, ranks visible candidates with a masked scoring
head, and regresses a future hand-pose vector. The current strongest model does
not require vision-language features.

Files:

- `fig3_prehoi_rank_architecture.png`
- `fig3_prehoi_rank_architecture.pdf`

## Figure 4

**Figure 4. Evaluation safety protocol.** Valid runs use clip-level splits,
observation-frame inputs, stable UID candidate ordering, and position
baselines. Runs with forecast-frame inputs or target-aware candidate ordering
are excluded.

Files:

- `fig4_protocol_safety.png`
- `fig4_protocol_safety.pdf`

## Figure 5

**Figure 5. Candidate-ranker protocol diagnostics across 25, 50, and 75 local
HOT3D-Clips subsets.** Expanding from 25 to 50 local shards improves Top-1
candidate accuracy, MRR, and pose-vector MAE under the same order-safe
candidate-ranking formulation. The 75-clip robustness split increases data
scale and class diversity but is harder and less balanced; it maintains high
Top-3 performance while Top-1, MRR, and pose-vector MAE are weaker than the
50-clip primary protocol. Bars show mean values with seed-standard-deviation
error bars where available. Lower is better for pose-vector MAE.

Files:

- `fig5_25clip_vs_50clip_results.png`
- `fig5_25clip_vs_50clip_results.pdf`

## Table Captions

# Table Caption List

Status: draft captions for the formatted submission package.

## Table 1

**Table 1. PreHOI-Rank candidate-ranker diagnostics on local HOT3D-Clips
subsets.** The table reports the 50-clip five-seed primary result, per-seed
diagnostics, a 25/50/75 clip scale comparison, and candidate-position
baselines. The 75-clip setting is reported as a robustness/scalability check
rather than replacing the 50-clip primary result.

Source file:

- `tables/results_table_prehoi_rank.md`

## Table 2

**Table 2. Protocol safety checks for leakage-safe candidate ranking.** The
table summarizes forecast-frame input exclusion, target-proxy use, stable UID
candidate ordering, clip-level splitting, candidate-order bias diagnostics, and
remaining split warnings.

Source file:

- `tables/protocol_safety_table.md`
