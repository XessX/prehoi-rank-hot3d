# Submission Metadata

Status: five-author metadata filled where provided. PreHOI-specific
repository/archive and final journal-system checks remain pending.

This file collects metadata likely needed during journal submission. It does
not replace the target journal's online submission form or Guide for Authors.

## Title

PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting

## Short Title

PreHOI-Rank for Pre-Contact Hand-Object Forecasting

## Target Journal

Machine Learning with Applications

## Backup Journal

PLOS ONE

## Article Type

Regular research article / research paper, pending confirmation in the live
submission system.

## Authors and Corresponding Author

| Order | Author | Affiliation | Email | ORCID |
| --- | --- | --- | --- | --- |
| 1 | Al Jubair Hossain | American International University-Bangladesh (AIUB) | jubair.hossain@aiub.edu | 0009-0005-3498-5826 |
| 2 | ASIF SHAHRIAR SIAM | American International University-Bangladesh (AIUB) | On file internally | Not provided |
| 3 | MD. ABUBOKOR SIDDIK ROJAN | American International University-Bangladesh (AIUB) | On file internally | Not provided |
| 4 | Maria Sultana Alif | American International University-Bangladesh (AIUB) | On file internally | Not provided |
| 5 | Siam Rahman Nayem | American International University-Bangladesh (AIUB) | On file internally; final Siam/Seyam spelling check open | Not provided |

Shared affiliation: American International University-Bangladesh (AIUB),
Kuratoli, Khilkhet, Dhaka 1229, Bangladesh.

Corresponding author: Al Jubair Hossain, jubair.hossain@aiub.edu.

Student co-author consent and CRediT role confirmations have been received.
The final spelling check for `Siam Rahman Nayem` versus `Seyam Rahman Nayem`
remains open before submission.

## Abstract

Pre-contact hand-object forecasting asks whether an egocentric perception system
can anticipate the likely object of a future hand interaction before contact
occurs. This setting is important for assistive augmented reality, wearable
interfaces, and robot systems that must reason about human intent from partial
observation. We present PreHOI-Rank, a leakage-safe candidate-ranking
formulation for pre-contact 3D hand-object interaction forecasting. Instead of
predicting a target from a global closed-set object vocabulary, PreHOI-Rank
scores the visible object candidates in an observation window and jointly
predicts a future hand-pose representation. We construct derived
affordance-grounded target-object proxy labels from HOT3D-Clips using
forecast-frame hand-object proximity, while strictly preventing forecast-frame
images, annotations, candidate scores, or metadata from entering the model
input. We also enforce stable candidate ordering to avoid candidate-position
leakage. On a local 50-clip HOT3D-Clips subset with clip-level splits, the
order-safe non-vision-language candidate ranker achieves five-seed
paper-candidate diagnostics of 0.7499 +/- 0.0450 Top-1 candidate accuracy,
0.9699 +/- 0.0161 Top-3 candidate accuracy, 0.8605 +/- 0.0221 MRR, and
0.4102 +/- 0.0051 future pose-vector MAE. These results support candidate
ranking as a practical formulation for pre-contact target forecasting under
derived labels, while the study remains limited by the local 50-clip subset,
residual class imbalance, proxy-label assumptions, and pose-vector rather than
MPJPE-style evaluation.

## Keywords

- Egocentric video
- Hand-object interaction
- Pre-contact forecasting
- Candidate ranking
- HOT3D-Clips
- Affordance proxy labels
- Leakage prevention
- 3D hand pose

## Highlights

- PreHOI-Rank frames pre-contact hand-object forecasting as candidate-level ranking over visible objects.
- Derived affordance-grounded proxy labels are constructed from forecast-frame hand-object proximity while forecast-frame features are excluded from model inputs.
- The evaluation protocol uses clip-level splits, stable candidate ordering, and position baselines to reduce temporal and candidate-order leakage.
- The 50-clip HOT3D-Clips local subset is used as the primary controlled result, with a 75-clip expansion reported as a robustness/scalability check.
- Pose metrics are reported as MANO/UmeTrack pose-parameter vector MAE/MSE; MPJPE is not reported.

## Suggested Reviewers

No suggested reviewers were provided. This remains optional unless requested by
the journal.

## Opposed Reviewers

No opposed reviewers were provided. This remains optional unless there is a
legitimate conflict to disclose.

## Cover Letter Status

- Draft file: `paper/submission_package/cover_letter.md`
- Status: corresponding author details filled; final article type and date still require submission-time review.

## Data and Code Availability Statement

Draft file: `paper/submission_package/data_code_availability.md`

Required PreHOI-specific decisions:

- final public PreHOI-Rank repository/archive URL;
- whether derived sample indexes can be shared;
- exact wording for HOT3D-Clips license/access requirements;
- whether checkpoints/logs will be shared.

Do not use Scientific Reports sparse 3D Gaussian Splatting GitHub or Zenodo
links for this PreHOI-Rank paper.

## Ethics and Data-Use Statement

Draft file: `paper/submission_package/ethics_data_use_statement.md`

Current position:

- no new human-subject data collected by the authors;
- HOT3D-Clips is third-party data;
- raw data is not redistributed;
- users must follow official access and license terms.

## Submission System Notes

- Confirm whether MLWA requests a separate title page.
- Confirm whether highlights are required or optional.
- Confirm whether a graphical abstract is required or optional.
- Confirm whether figures should be uploaded as separate source files.
- Confirm whether tables should be embedded in the manuscript or uploaded as separate files.
