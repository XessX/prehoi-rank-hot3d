# Cover Letter Draft: PreHOI-Rank

Status: formatted draft. Five-author metadata has been filled and student
co-author consent responses/contribution roles have been received; final date,
fifth-author spelling check, and live submission-system checks remain pending.

[Date]

Editor-in-Chief / Handling Editor
Machine Learning with Applications

Dear Editor,

We are pleased to submit the manuscript "PreHOI-Rank: Affordance-Grounded
Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting" for
consideration as a research article in Machine Learning with Applications.

The manuscript presents a leakage-safe candidate-ranking formulation for
pre-contact hand-object interaction forecasting in egocentric video. Rather
than treating target-object prediction as global object-class classification,
the proposed formulation ranks visible object candidates in an observation
window and predicts a future hand-pose representation before contact. The work
centers on a reproducible HOT3D-Clips protocol with derived
affordance-grounded target-object proxy labels, clip-level splitting, and
explicit checks for forecast-frame leakage and candidate-order bias.

The main contribution is methodological and protocol-oriented. We define a
transparent target-object proxy from future-frame hand-object proximity while
restricting all model inputs to observation-frame information. We also enforce
stable candidate ordering so the model cannot benefit from target-correlated
candidate positions. On a local 50-clip HOT3D-Clips subset, the current
paper-candidate evaluation uses five repeated seeds and reports candidate
Top-1, Top-3, MRR, and MANO pose-vector MAE/MSE. These results are presented
with explicit limitations: the labels are derived proxies rather than
human-annotated contact/action labels, the subset is not the complete HOT3D
dataset, and the pose metric has not yet been converted to an MPJPE-style
3D-joint metric.

We also include a 75-clip robustness/scalability analysis. This larger local
subset increases data scale and class diversity, but it produces a harder and
less balanced split. We therefore report it as supporting robustness evidence
rather than as a replacement for the 50-clip primary controlled result.

We believe the manuscript fits Machine Learning with Applications because it
addresses an applied machine-learning problem in egocentric computer vision,
combines a practical dataset-processing pipeline with a model formulation, and
emphasizes reproducible, leakage-safe evaluation. The manuscript does not make
a benchmark-superiority claim; it presents a careful candidate-ranking method
and evaluation protocol for pre-contact hand-object forecasting under realistic
annotation constraints.

The manuscript is original, has not been published previously, and is not under
consideration elsewhere. The authors declare no competing interests. This
research did not receive any specific grant from funding agencies in the
public, commercial, or not-for-profit sectors. Data and code availability are
described in the manuscript: HOT3D-Clips is a third-party dataset and is not
redistributed, while the PreHOI-Rank code repository and Zenodo archive DOI are
provided.

Thank you for considering our manuscript. We would be grateful for the
opportunity to have it reviewed by Machine Learning with Applications.

Sincerely,

Al Jubair Hossain  
Corresponding author, on behalf of all authors  
American International University-Bangladesh (AIUB)  
jubair.hossain@aiub.edu
