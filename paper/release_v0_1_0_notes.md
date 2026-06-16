# Release Notes: v0.1.1

Note: these notes supersede the earlier draft `v0.1.0` release notes. Use the
corrected `v0.1.1` Zenodo DOI `10.5281/zenodo.20722666` for archive citation.

Status: release notes for the corrected first GitHub/Zenodo archive.

## Summary

Initial research-code release for PreHOI-Rank: Affordance-Grounded Candidate
Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting.

## Included

- HOT3D-Clips inspection utilities.
- Derived target-object proxy-label generation scripts.
- Clip-level split optimization and split-quality checking.
- Candidate-order bias and forecast-frame leakage checks.
- PreHOI-Rank candidate-ranker training protocol.
- 50-clip primary and 75-clip robustness/scalability protocol documentation.
- Manuscript-support notes, figures, tables, and submission package drafts.
- Reproducibility, data-usage, and model-card documentation.

## Excluded

- Raw HOT3D-Clips data.
- Downloaded WebDataset shards.
- Processed HOT3D sample indexes and feature caches.
- Training logs.
- Checkpoints.
- Model weights.
- Local virtual environments and caches.

## Current Limitations

- Target-object labels are derived proxy labels, not direct HOT3D ground truth.
- The primary evaluation uses a local 50-clip HOT3D-Clips subset.
- The 75-clip expansion is reported as robustness/scalability analysis.
- Pose metrics are MANO/UmeTrack pose-parameter vector MAE/MSE; MPJPE is not
  reported.
- Final co-author consent, student CRediT confirmation, and HOT3D license/access
  wording still require author-side confirmation before manuscript submission.

## Data Use

Users must obtain HOT3D-Clips through official sources and follow the official
access, license, and citation terms. This repository does not redistribute raw
dataset files.
