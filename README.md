# PreHOI-Rank

**PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting**

PreHOI-Rank is a research-code package for pre-contact hand-object interaction
forecasting on HOT3D-Clips. The central task is to rank visible object
candidates from an observation window before hand-object contact, while also
predicting a future MANO/UmeTrack pose-parameter vector.

Repository URL: `https://github.com/XessX/prehoi-rank-hot3d`.

Archive DOI: `10.5281/zenodo.20722666`.

Release metadata status: `CITATION.cff` and `.zenodo.json` are updated for the
corrected `v0.1.1` GitHub/Zenodo release.

## What This Repository Contains

- HOT3D-Clips inspection and safe sample-index generation scripts.
- Derived target-object proxy generation from forecast-frame hand-object
  proximity.
- Clip-level split optimization and split-quality checks.
- Candidate-order bias and forecast-frame leakage checks.
- PreHOI-Rank candidate-ranker training and repeated-seed protocol scripts.
- Figure-generation scripts and manuscript protocol notes.

The repository does not redistribute raw HOT3D-Clips data, downloaded shards,
large processed features, logs, checkpoints, or model weights.

## Task Definition

Given an observation window of egocentric frames and visible object candidates,
PreHOI-Rank predicts:

- a ranking score over observation-window object candidates;
- a future MANO/UmeTrack pose-parameter vector.

The target-object label is a **derived proxy label**, not direct HOT3D ground
truth. It is generated from forecast-frame hand-object proximity and used only
as a supervised target.

## Main Result Framing

The current manuscript uses:

- **50 clips** as the primary controlled evaluation;
- **75 clips** as a robustness/scalability check.

| Setting | Role | Top-1 | Top-3 | MRR | Pose MAE |
| --- | --- | ---: | ---: | ---: | ---: |
| 50 clips | Primary result | 0.7499 +/- 0.0450 | 0.9699 +/- 0.0161 | 0.8605 +/- 0.0221 | 0.4102 +/- 0.0051 |
| 75 clips | Robustness/scalability | 0.7115 +/- 0.0571 | 0.9789 +/- 0.0009 | 0.8340 +/- 0.0343 | 0.4676 +/- 0.0096 |

Pose metrics are MANO/UmeTrack pose-parameter vector MAE/MSE. MPJPE is not
reported.

## Safety Protocol

All paper-facing candidate-ranker runs must satisfy:

- `candidate_order=stable_uid`;
- `input_uses_forecast_frame=false`;
- clip-level train/validation/test split;
- observation-frame inputs only;
- forecast-frame proxy used only as target;
- derived proxy labels described as derived labels, not ground truth.

Unsafe runs using forecast-frame inputs, sample-level random splitting, or
target/proxy-sorted candidate order should be excluded.

## Installation

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation scripts for the current process:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Smoke check:

```powershell
python -m compileall src scripts
python src/main.py --config configs/model_config.yaml --dataset-config configs/hot3d_config.yaml
```

## Data Access

HOT3D-Clips must be obtained from official HOT3D/HOT3D-Clips sources. This
repository does not include raw data. Users are responsible for following the
official access, license, and citation terms.

Expected local layout after authorized download:

```text
data/raw/hot3d_clips/
  clip_definitions.json
  clip_splits.json
  train_aria/
    clip-*.tar
  train_quest3/
    clip-*.tar
```

`data/raw/`, `data/processed/`, logs, checkpoints, caches, archives, and model
weights are ignored by Git.

## Reproduction Commands

Build the sample index:

```powershell
python src/datasets/build_hot3d_clips_samples.py --root data/raw/hot3d_clips --output data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --observation-frames 16 --forecast-horizon 5 --assign-target-proxy
```

Optimize clip-level split:

```powershell
python src/datasets/optimize_hot3d_clip_split.py --index data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --output-dir data/processed --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 --min-class-samples 30 --min-class-clips 2 --num-attempts 1000
```

Check split quality and candidate-order baseline:

```powershell
python src/datasets/check_hot3d_split_quality.py --train data/processed/hot3d_clips_train_optimized.json --val data/processed/hot3d_clips_val_optimized.json --test data/processed/hot3d_clips_test_optimized.json --label-map data/processed/hot3d_target_object_label_map.json

python src/datasets/check_hot3d_candidate_order_bias.py --index data/processed/hot3d_clips_test_optimized.json --candidate-order stable_uid
```

Run the repeated-seed candidate-ranker protocol:

```powershell
python src/training/run_final_candidate_ranker_protocol.py --seeds 42 123 2026 7 99
python src/training/run_final_candidate_ranker_protocol.py --seeds 42 123 2026 7 99 --run-tag 75clip
```

Generate figures:

```powershell
python src/visualization/create_prehoi_rank_figures.py
```

More detailed steps are in [REPRODUCIBILITY.md](REPRODUCIBILITY.md).

## Paper Package

Manuscript and submission materials are under `paper/`. The current package is
not submission-ready until HOT3D license/access wording, Machine Learning with
Applications APC/waiver checks, and final formatting are confirmed.

## Citation

Citation metadata is available in `CITATION.cff`. The corrected `v0.1.1`
Zenodo archive DOI is `10.5281/zenodo.20722666`. For now, cite this repository
as:

```text
PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting.
Repository URL: https://github.com/XessX/prehoi-rank-hot3d.
Archive DOI: 10.5281/zenodo.20722666.
```
