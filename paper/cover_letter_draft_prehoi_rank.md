# Cover Letter Draft: PreHOI-Rank

Status: draft. Replace bracketed placeholders before submission.

[Date]

Editor-in-Chief / Handling Editor  
Machine Learning with Applications

Dear Editor,

We are pleased to submit our manuscript entitled "PreHOI-Rank:
Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object
Interaction Forecasting" for consideration as a research article in Machine
Learning with Applications.

This manuscript presents a leakage-safe candidate-ranking formulation for
pre-contact hand-object interaction forecasting in egocentric video. Rather
than treating target-object prediction as a global object-class classification
problem, our approach ranks the visible object candidates in an observation
window and predicts the future hand-pose representation before contact. The
work focuses on a reproducible protocol using HOT3D-Clips, derived
affordance-grounded target-object proxy labels, clip-level splitting, and
explicit checks against forecast-frame leakage and candidate-order bias.

The main contribution is methodological and protocol-oriented. We define a
transparent target-object proxy from future-frame hand-object proximity while
restricting all model inputs to observation-frame information. We also enforce
stable candidate ordering so that the model cannot benefit from target-correlated
candidate positions. On a local 50-clip HOT3D-Clips subset, the current
paper-candidate evaluation uses five repeated seeds and reports candidate
Top-1, Top-3, MRR, and MANO pose-vector MAE/MSE. We present these results with
clear limitations: the labels are derived proxies rather than human
ground-truth contact/action labels, the subset is not the full HOT3D dataset,
and the pose metric has not yet been converted to an MPJPE-style 3D-joint
metric.

We believe the manuscript fits Machine Learning with Applications because it
addresses an applied machine-learning problem in egocentric computer vision,
combines a practical dataset-processing pipeline with a model formulation, and
places special emphasis on reproducible and leakage-safe evaluation. We do not
claim state-of-the-art performance; instead, we position the paper as a careful
candidate-ranking method and evaluation protocol for pre-contact hand-object
forecasting under realistic annotation constraints.

The manuscript is original, has not been published previously, and is not under
consideration elsewhere. All authors have approved the submission. The authors
declare [insert conflict of interest statement]. Funding information is [insert
funding statement]. Data and code availability are described in the manuscript:
HOT3D-Clips is a third-party dataset and is not redistributed, while the code
and regeneration protocol can be released through a public repository.

Thank you for considering our manuscript. We would be grateful for the
opportunity to have it reviewed by Machine Learning with Applications.

Sincerely,

[Corresponding author name]  
[Affiliation]  
[Email]  
On behalf of all authors
