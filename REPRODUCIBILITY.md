# Reproducibility Guide

This guide describes how to reproduce the PreHOI-Rank pipeline without
redistributing HOT3D-Clips data. It assumes authorized local access to
HOT3D-Clips.

## 1. Environment Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m compileall src scripts
```

## 2. Dataset Preparation Overview

Place authorized HOT3D-Clips files under:

```text
data/raw/hot3d_clips/
```

Raw data, tar shards, processed indexes, features, logs, checkpoints, and model
weights are ignored by Git.

Inspect local files:

```powershell
python src/datasets/inspect_hot3d_clips.py data/raw/hot3d_clips
```

## 3. Build Sample Index

```powershell
python src/datasets/build_hot3d_clips_samples.py --root data/raw/hot3d_clips --output data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --observation-frames 16 --forecast-horizon 5 --assign-target-proxy

python src/datasets/inspect_hot3d_clips_samples.py data/processed/hot3d_clips_sample_index_proxy_v1_multi.json
```

The target-object labels are derived proxy labels. They are not direct HOT3D
ground truth.

## 4. Split Optimization

```powershell
python src/datasets/summarize_hot3d_clip_class_matrix.py --index data/processed/hot3d_clips_sample_index_proxy_v1_multi.json

python src/datasets/optimize_hot3d_clip_split.py --index data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --output-dir data/processed --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 --min-class-samples 30 --min-class-clips 2 --num-attempts 1000

python src/datasets/check_hot3d_split_quality.py --train data/processed/hot3d_clips_train_optimized.json --val data/processed/hot3d_clips_val_optimized.json --test data/processed/hot3d_clips_test_optimized.json --label-map data/processed/hot3d_target_object_label_map.json
```

Splits must be by clip ID, not random sample ID.

## 5. Image-Stats Feature Extraction

Image-statistics features are lightweight observation-frame features. They are
used only when needed by visual-object pilot baselines.

```powershell
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_train_optimized.json --output data/processed/features/hot3d_visual_features_image_stats_train.npz --feature-type image_stats
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_val_optimized.json --output data/processed/features/hot3d_visual_features_image_stats_val.npz --feature-type image_stats
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_test_optimized.json --output data/processed/features/hot3d_visual_features_image_stats_test.npz --feature-type image_stats
```

## 6. Candidate-Ranker Protocol

Dry run:

```powershell
python src/training/run_final_candidate_ranker_protocol.py --dry-run
```

50-clip primary protocol:

```powershell
python src/training/run_final_candidate_ranker_protocol.py --seeds 42 123 2026 7 99
```

75-clip robustness protocol:

```powershell
python src/training/run_final_candidate_ranker_protocol.py --seeds 42 123 2026 7 99 --run-tag 75clip
```

Required safety settings:

- `candidate_order=stable_uid`;
- `input_uses_forecast_frame=false`;
- clip-level split;
- no forecast-frame image, object, hand, metadata, or proxy-score input.

## 7. Figure Generation

```powershell
python src/visualization/create_prehoi_rank_figures.py
```

Outputs are written under `paper/figures/`.

## 8. Known Limitations

- Results are tied to local 50-clip and 75-clip HOT3D-Clips subsets.
- Target-object labels are derived proxy labels, not human contact/action
  ground truth.
- Pose metrics are MANO/UmeTrack pose-parameter vector MAE/MSE, not MPJPE.
- Residual class imbalance remains in the optimized splits.
- The public repository and archive DOI are pending.
