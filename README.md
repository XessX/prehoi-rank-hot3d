# PreHOI-Rank

Affordance-grounded candidate ranking for pre-contact 3D hand-object
interaction forecasting in egocentric video.

This repository is the MVP research-code foundation for a manuscript targeted at **Machine Learning with Applications** with a Research4Life-aware submission route. The code starts honestly: it uses synthetic dummy tensors to prove the pipeline, model, losses, and metrics run end to end. Current HOT3D-Clips numbers are pilot/debug diagnostics only; the repository does **not** report or imply final paper-ready HOT3D results.

## Research Goal

The project investigates whether pre-contact egocentric observations can forecast:

- target object,
- future interaction/action label,
- future 3D hand pose,
- later: object affordance/contact region,
- later: vision-language cues for assistive AR guidance.

Primary dataset target: **HOT3D**.

Backup / cross-dataset target: **DexYCB**.

## Current Working Title and Direction

Working title:

**PreHOI-Rank: Affordance-Grounded Candidate Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting**

The current strongest stable pilot model is the order-safe
`candidate_ranker_non_vl` on the expanded 50-clip HOT3D-Clips subset. Its
three-seed pilot stability is top-1 `0.7711 +/- 0.0455`, MRR
`0.8713 +/- 0.0208`, and pose MAE `0.4131 +/- 0.0045`.

Vision-language and PreHOI-Former components remain in the repository as
exploratory pilot ablations and future extensions. They are not the main claim
yet because the non-VL candidate-ranking formulation is currently more stable
under repeated seeds.

All current HOT3D-Clips metrics are pilot/debug diagnostics only. Target-object
labels are derived proxy labels, not direct HOT3D ground truth.

## Current MVP

Implemented now:

- modular PyTorch repository structure,
- synthetic HOT3D-compatible dataset stub,
- temporal transformer baseline,
- object classification head,
- action classification head,
- future 3D hand-pose regression head,
- accuracy and MPJPE metrics,
- train/evaluate loop,
- clear TODOs for HOT3D annotation parsing.

Not implemented yet:

- real HOT3D download or parsing,
- real image backbone features,
- MANO decoding,
- contact-region labels,
- CLIP/open-vocabulary language embeddings,
- AR visualization,
- journal-ready real experiments.

## Environment Setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation scripts for the current session, use this safe
process-scoped bypass and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Confirm the environment:

```powershell
where.exe python
pip --version
python -m compileall src
python src/main.py --config configs/model_config.yaml --dataset-config configs/hot3d_config.yaml
```

Deactivate when finished:

```powershell
deactivate
```

If PyTorch installation needs a CUDA-specific wheel, install PyTorch from the official selector first, then install the rest of the requirements.

## Smoke Run

The default run uses synthetic tensors only.

```bash
python src/main.py --config configs/model_config.yaml --dataset-config configs/hot3d_config.yaml
```

Expected behavior:

- trains a tiny transformer for a few epochs on dummy data,
- prints synthetic validation metrics,
- writes logs to `results/logs/`,
- writes checkpoints to `results/checkpoints/`.

These numbers are only a pipeline sanity check. They are not dataset results.

## HOT3D Integration Plan

`src/datasets/hot3d_loader.py` is the integration point. Replace the synthetic branch with real parsing for:

- egocentric frame windows before contact,
- 3D hand joints or MANO parameters,
- object ID and object pose,
- future hand pose at the forecast horizon,
- interaction/action labels,
- contact or affordance labels if available,
- frame timestamps and calibration metadata.

## Dataset Integration Status

Current status:

- synthetic mode remains the default for smoke testing,
- official HOT3D schema notes are tracked in `paper/hot3d_schema_notes.md`,
- real mode recognizes the official full HOT3D VRS layout and HOT3D-Clips tar/WebDataset layout,
- real mode can inspect VRS sequence folders for `metadata.json`, `recording.vrs`, `dynamic_objects.csv`, `headset_trajectory.csv`, hand annotation files, masks, and device-specific metadata,
- real mode can inspect HOT3D-Clips roots for split folders, clip tar files, `clip_definitions.json`, and `clip_splits.json`,
- a sample index is saved/loaded at `data/processed/hot3d_sample_index.json`,
- pre-contact training windows are still blocked until contact/event labels or a documented proxy are implemented,
- validation checks report missing frame paths, missing annotations, missing required labels, and tensor-shape issues,
- dataset startup prints a compact summary before training.

Real-mode sample fields are designed to include:

- `frames` when `load_frames: true`, otherwise `frame_paths`,
- `hand_pose_3d`,
- `object_id`,
- `object_pose` when available, with `has_object_pose` marking availability,
- `future_hand_pose_3d`,
- `action_label` and `interaction_label`,
- `contact_region` when available, with `has_contact_region` marking availability,
- metadata such as `sequence_id`, `frame_start`, `frame_end`, `event_frame`, and `forecast_frame`.

Missing real labels or future hand-pose targets are not fabricated. If required
HOT3D annotations are unavailable or use an unconfirmed schema, real mode raises
or skips samples and reports TODO-style missing-field counts. Keep
`use_synthetic: true` until the official HOT3D layout is verified locally.

Inspect a local HOT3D root without training:

```powershell
python src/datasets/inspect_hot3d.py data/raw/hot3d
```

## HOT3D-Clips First Workflow

For the first real-data path, start with HOT3D-Clips/WebDataset rather than the
full VRS dataset. Place downloaded HOT3D-Clips data like this:

```text
data/raw/hot3d_clips/
  clip_definitions.json
  clip_splits.json
  object_models/
  object_models_eval/
  train_aria/
    clip-*.tar
  train_quest3/
    clip-*.tar
  test_aria/
    clip-*.tar
  test_quest3/
    clip-*.tar
```

Inspect the clips without training:

```powershell
python src/datasets/inspect_hot3d_clips.py data/raw/hot3d_clips
```

Optional, only if `webdataset` is installed:

```powershell
python src/datasets/inspect_hot3d_clips.py data/raw/hot3d_clips --use-webdataset
```

The inspector reports shard counts, sample/frame keys, image stream keys,
whether hand/object/camera/metadata files appear, and whether gaze-like keys are
present. It does not decode labels, train models, or create publishable results.

## Downloading a Small HOT3D-Clips Sample

HOT3D-Clips is hosted on Hugging Face under `bop-benchmark/hot3d`. Review the
dataset page and license/access requirements before downloading data. If access
requires authentication, login first:

```powershell
huggingface-cli login
```

Always start with a dry run that lists matching files without downloading:

```powershell
python src/datasets/download_hot3d_clips_sample.py --repo-id bop-benchmark/hot3d --pattern "train_aria/*.tar" --max-files 1
```

After reviewing the selected file and approving the download, fetch only that
small sample:

```powershell
python src/datasets/download_hot3d_clips_sample.py --repo-id bop-benchmark/hot3d --pattern "train_aria/*.tar" --max-files 1 --output-dir data/raw/hot3d_clips --confirm-download --allow-large-files
```

Then inspect it:

```powershell
python src/datasets/inspect_hot3d_clips.py data/raw/hot3d_clips
```

Downloaded datasets, tar shards, VRS files, archives, videos, logs, and
checkpoints must not be committed. The current code still treats all real-data
inspection as preparation only; no real HOT3D result has been produced yet.

## Building a HOT3D-Clips Sample Index

After a shard has been downloaded and inspected, build a lightweight JSON index
for pre-contact forecasting samples. This step records tar member names and
annotation metadata only. It does not decode image tensors, train a model, or
choose final target-object/contact/action labels.

```powershell
python src/datasets/build_hot3d_clips_samples.py --root data/raw/hot3d_clips --output data/processed/hot3d_clips_sample_index.json --observation-frames 16 --forecast-horizon 5
python src/datasets/inspect_hot3d_clips_samples.py data/processed/hot3d_clips_sample_index.json
```

The generated samples contain observation frame IDs, image member paths for the
three HOT3D-Clips streams, future hand-pose payloads from `hands.json`, visible
object candidates from `objects.json`, and sequence metadata from `info.json`.
If no visible future hand or object is available, that candidate window is
skipped. If multiple objects are visible, all candidates are stored and the
final target-object decision remains postponed until a documented selection rule
is implemented.

To build an index with the first derived target-object proxy label:

```powershell
python src/datasets/build_hot3d_clips_samples.py --root data/raw/hot3d_clips --output data/processed/hot3d_clips_sample_index_proxy_v1.json --observation-frames 16 --forecast-horizon 5 --assign-target-proxy
python src/datasets/inspect_hot3d_clips_samples.py data/processed/hot3d_clips_sample_index_proxy_v1.json
```

Because direct action/contact labels are not available in HOT3D-Clips, Target
Object Proxy v1 chooses a visible object at the forecast frame by hand-object
box proximity. It computes overlap and normalized center distance between the
union of visible hand boxes and each visible object's box, stores all candidate
scores, and selects the highest-scoring object as a **derived proxy target**.
This label must not be described as direct HOT3D ground truth.

## Selecting Diverse HOT3D-Clips Shards

Before training, inspect the root HOT3D-Clips metadata and choose a small,
diverse set of shards. This keeps the next download deliberate and avoids
building an early classifier around one object class.

```powershell
python src/datasets/summarize_hot3d_clip_definitions.py --root data/raw/hot3d_clips
python src/datasets/select_hot3d_diverse_clips.py --root data/raw/hot3d_clips --num-clips 8 --output data/processed/hot3d_diverse_clip_selection.json
```

The selector avoids already downloaded clip IDs and prefers the train split. If
object metadata is available in `clip_definitions.json`, it uses it for
diversity. If not, it falls back to participant, device, and sequence diversity
and says so in the output. The script prints reviewable downloader commands for
the selected shards but does not download them unless `--confirm-download` is
explicitly passed.

Download only the reviewed selected shards:

```powershell
python src/datasets/download_selected_hot3d_clips.py --selection data/processed/hot3d_diverse_clip_selection.json --output-dir data/raw/hot3d_clips --max-clips 8 --max-total-gb 2
python src/datasets/download_selected_hot3d_clips.py --selection data/processed/hot3d_diverse_clip_selection.json --output-dir data/raw/hot3d_clips --max-clips 8 --max-total-gb 2 --confirm-download
```

After download, rebuild and inspect the proxy index across all local shards:

```powershell
python src/datasets/build_hot3d_clips_samples.py --root data/raw/hot3d_clips --output data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --observation-frames 16 --forecast-horizon 5 --assign-target-proxy
python src/datasets/inspect_hot3d_clips_samples.py data/processed/hot3d_clips_sample_index_proxy_v1_multi.json
```

## Real HOT3D-Clips Dataset v1

The first real PyTorch dataset uses the verified HOT3D-Clips sample index and
Target Object Proxy v1 labels. These labels are derived from hand/object box
proximity and must not be described as direct HOT3D ground truth. Any training
with this dataset is a debug or pilot run until label quality, split policy, and
feature extraction are fully documented.

Create clip-level splits to avoid sample-level leakage:

```powershell
python src/datasets/split_hot3d_clips.py --index data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --output-dir data/processed --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15
```

Inspect the dataset in fast metadata-only mode:

```powershell
python src/datasets/inspect_hot3d_clips_dataset.py --index data/processed/hot3d_clips_train.json --mode metadata_only
```

Check split quality before any debug training:

```powershell
python src/datasets/check_hot3d_split_quality.py --train data/processed/hot3d_clips_train.json --val data/processed/hot3d_clips_val.json --test data/processed/hot3d_clips_test.json --label-map data/processed/hot3d_target_object_label_map.json
```

## Optimized Clip-Level Split

Because HOT3D-Clips root metadata does not expose object names, use the proxy
index itself to build a clip-by-class matrix before choosing evaluation splits.
The optimized splitter still splits only by `clip_id`; it never performs random
sample-level splitting.

```powershell
python src/datasets/summarize_hot3d_clip_class_matrix.py --index data/processed/hot3d_clips_sample_index_proxy_v1_multi.json
python src/datasets/optimize_hot3d_clip_split.py --index data/processed/hot3d_clips_sample_index_proxy_v1_multi.json --output-dir data/processed --train-ratio 0.7 --val-ratio 0.15 --test-ratio 0.15 --min-class-samples 30 --min-class-clips 2 --num-attempts 1000
python src/datasets/check_hot3d_split_quality.py --train data/processed/hot3d_clips_train_optimized.json --val data/processed/hot3d_clips_val_optimized.json --test data/processed/hot3d_clips_test_optimized.json --label-map data/processed/hot3d_target_object_label_map.json
```

Dataset v1 returns lightweight frame features, a flattened forecast-frame MANO
pose vector, integer proxy target label, proxy confidence, clip/sample IDs, and
metadata. Image mode can load one image stream from tar shards for inspection,
but metadata-only remains the default for quick debugging.

## Pilot Metadata-Only Baseline

This baseline is only a pipeline validation run. It uses `metadata_only`
features, derived target-object proxy labels, and forecast-frame MANO pose
vectors. It does not use image data and must not be described as a final paper
result.

```powershell
python src/training/train_hot3d_metadata_baseline.py --config configs/hot3d_metadata_baseline.yaml
```

The script prints `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`, saves metrics to
`results/logs/hot3d_metadata_baseline_pilot.json`, and saves a checkpoint to
`results/checkpoints/hot3d_metadata_baseline_pilot.pt`.

## Pilot Object-Aware Metadata Baseline

This pilot adds `object_metadata` inputs without using image tensors. Each
sample includes the 16-frame metadata sequence, top-K observation-frame
object-candidate geometry and proxy-score features from HOT3D-Clips
annotations, a candidate mask, the derived target-object proxy label, and the
forecast-frame MANO vector.

```powershell
python src/training/train_hot3d_object_aware_baseline.py --config configs/hot3d_object_aware_baseline.yaml
```

The script prints `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`, saves metrics to
`results/logs/hot3d_object_aware_baseline_pilot.json`, and saves a checkpoint to
`results/checkpoints/hot3d_object_aware_baseline_pilot.pt`. Proxy labels remain
derived labels, not direct HOT3D ground truth, and this baseline is only for
pipeline validation before image training or paper-facing evaluation.

Object-aware inputs must be extracted from observation frames only. The
target-object proxy may be computed at the forecast frame, but forecast-frame
object boxes, hand boxes, proximity scores, IoU, and center-distance features
must not be used as model input.

## Cached Visual Feature Extraction

This stage extracts lightweight visual features from observation-frame images
and writes them under `data/processed/features/`. It does not train a model and
does not use forecast-frame images. The default `image_stats` feature is
CPU-friendly: mean, standard deviation, min, and max per RGB-like channel for
each observation frame.

```powershell
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_train_optimized.json --output data/processed/features/hot3d_visual_features_image_stats_train.npz --feature-type image_stats

python src/features/inspect_hot3d_visual_features.py data/processed/features/hot3d_visual_features_image_stats_train.npz
```

Repeat extraction for validation and test split files before using
`mode="object_visual_metadata"`. Cached features remain generated data and must
not be committed.

## Frozen CLIP Visual Feature Extraction

Frozen CLIP extraction caches observation-frame embeddings without training
CLIP. Start with a tiny smoke extraction on CPU before attempting full split
extraction.

```powershell
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_train_optimized.json --output data/processed/features/hot3d_visual_features_clip_train_smoke.npz --feature-type clip --max-samples 20 --batch-size 4 --device cpu

python src/features/inspect_hot3d_visual_features.py data/processed/features/hot3d_visual_features_clip_train_smoke.npz
```

Full extraction commands, after the smoke run is validated:

```powershell
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_train_optimized.json --output data/processed/features/hot3d_visual_features_clip_train.npz --feature-type clip --batch-size 8 --device cpu
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_val_optimized.json --output data/processed/features/hot3d_visual_features_clip_val.npz --feature-type clip --batch-size 8 --device cpu
python src/features/extract_hot3d_visual_features.py --index data/processed/hot3d_clips_test_optimized.json --output data/processed/features/hot3d_visual_features_clip_test.npz --feature-type clip --batch-size 8 --device cpu
```

These cached embeddings are still pilot/debug features. They use observation
frames only and must not be reported as final paper evidence before the full
pipeline, labels, and splits are validated.

## Pilot Frozen CLIP Visual-Object Baseline

This pilot uses cached frozen CLIP image embeddings with the same
`object_visual_metadata` dataset path. CLIP is not trained; the model only
trains the small temporal/fusion heads on top of cached observation-frame
features, observation-frame object candidates, and metadata features.

```powershell
python src/training/train_hot3d_clip_visual_object_baseline.py --config configs/hot3d_clip_visual_object_baseline.yaml
```

This remains a `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`. Proxy labels are
derived labels, not direct HOT3D ground truth, and this run must not be used for
final research claims.

## Pilot Candidate-Ranking Baseline

This pilot scores the observed object candidates instead of predicting one
global class label. A sample is rankable only when the forecast-frame target
proxy object is also present among the observation-frame candidate list. The
ranking loss uses observation-frame candidate features only. Candidate ordering
must not leak the proxy answer: the default dataset order is `stable_uid`, which
sorts by object identity rather than proxy score. Use `as_is` only for explicit
debugging because the raw proxy-score order can make candidate 0 a strong
position-only baseline.

```powershell
python src/datasets/check_hot3d_candidate_order_bias.py --index data/processed/hot3d_clips_train_optimized.json --candidate-order stable_uid

python src/datasets/inspect_hot3d_candidate_ranking.py --index data/processed/hot3d_clips_train_optimized.json

python src/training/train_hot3d_candidate_ranker.py --config configs/hot3d_candidate_ranker.yaml
```

This is still a `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`. Proxy labels are
derived labels, not direct HOT3D ground truth, and candidate-ranking metrics are
not directly comparable with global object-class accuracy.

## Pilot Vision-Language Candidate Ranker

This pilot extends the order-safe candidate ranker with frozen CLIP text
features for candidate object names. It does not train CLIP, does not use
forecast-frame object candidates as input, and keeps `candidate_order:
stable_uid` so candidate position does not leak the proxy target.

```powershell
python src/features/extract_hot3d_text_features.py --label-map data/processed/hot3d_target_object_label_map.json --output data/processed/features/hot3d_object_text_features_clip.npz

python src/features/inspect_hot3d_text_features.py data/processed/features/hot3d_object_text_features_clip.npz

python src/training/train_hot3d_vl_candidate_ranker.py --config configs/hot3d_vl_candidate_ranker.yaml
```

This is still a `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`. The target labels
are derived proxy labels, the text embeddings are frozen object-name features,
and the run must be compared against candidate-0, first-3, random, and
non-vision-language pilot baselines before making any research claim.

## PreHOI-Former v1 Pilot

`PreHOI-Former v1` is the first model-development pass beyond simple baseline
fusion. It encodes observation-frame hand/context metadata, object-candidate
geometry, and frozen CLIP object-name embeddings, then applies candidate-level
multimodal attention before ranking candidates and regressing the future MANO
pose vector.

```powershell
python src/training/train_prehoi_former_v1.py --config configs/prehoi_former_v1.yaml
```

This remains a `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`. Candidate targets
are derived proxy labels, CLIP text embeddings are frozen, `candidate_order:
stable_uid` is required, and no forecast-frame candidate features are used as
input. The config includes ablation flags for `use_text` and
`use_candidate_attention`.

## PreHOI-Former v1 Ablation Pilot

Run controlled pilot ablations to separate the effects of frozen text
embeddings, candidate-level attention, and pose-loss weighting. The runner uses
the same optimized clip-level split and keeps `candidate_order: stable_uid`.

```powershell
python src/training/run_prehoi_former_v1_ablation.py --config configs/prehoi_former_v1_ablation.yaml

python src/training/summarize_prehoi_ablation.py --summary results/tables/prehoi_former_v1_ablation_summary.csv
```

This is still pilot/model-development evidence only. Do not describe proxy
targets as HOT3D ground truth or use the ablation table as final paper results.

## PreHOI-Former v2 Dual-Branch Pilot

`PreHOI-Former v2` separates candidate ranking and future MANO-pose regression
into dual branches. The temporal hand/context encoder is shared, but ranking
uses its own candidate-scoring branch and pose regression uses a separate pose
decoder. The default pilot starts with geometry-only candidate inputs, no
candidate attention, and `candidate_order: stable_uid`.

```powershell
python src/training/train_prehoi_former_v2.py --config configs/prehoi_former_v2.yaml
```

This is still a `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`. Proxy targets are
derived labels, not direct HOT3D ground truth. Inputs must remain
observation-frame only, and the training script rejects forecast-frame candidate
features.

## Pilot Result Registry

Collect all current pilot/debug metrics into one summary table before comparing
models or drafting paper text:

```powershell
python src/training/collect_pilot_results.py

python src/training/print_best_pilot_models.py --summary results/tables/pilot_experiment_summary.csv
```

The registry writes `results/tables/pilot_experiment_summary.csv` and
`paper/pilot_experiment_summary.md`, and the static status registry lives at
`paper/pilot_experiment_registry.md`. All entries remain pilot/debug evidence
only. Invalid or superseded runs with leakage/order-bias risk are marked
separately and must be excluded from paper claims.

## Pilot Seed Stability

Run a small seed-stability check for the current best pilot candidates before
choosing any model for deeper experiments:

```powershell
python src/training/run_pilot_seed_stability.py --seeds 42 123 2026

python src/training/summarize_seed_stability.py --summary results/tables/pilot_seed_stability_summary.csv
```

The runner checks the non-VL candidate ranker, PreHOI-Former v1, and the
geometry-only/no-attention v1 ablation with `candidate_order: stable_uid`.
Results are saved under `results/logs/seed_stability/` and
`results/tables/pilot_seed_stability_summary.csv`; these generated artifacts
remain ignored by Git.

## Current Research Decision

The current working title is **PreHOI-Rank**. The best stable pilot is now the
order-safe non-VL candidate ranker on the expanded 50-clip HOT3D-Clips subset,
with three-seed top-1 `0.7711 +/- 0.0455`, MRR `0.8713 +/- 0.0208`, and pose MAE
`0.4131 +/- 0.0045`. This improves over the earlier 25-clip candidate-ranker
pilot.

PreHOI-Former v1 had a strong single run, but seed stability does not support
treating it as the final model yet. Vision-language components remain useful as
exploratory ablations and future extensions, not the main paper claim.

See `paper/research_decision_note.md` for the current model-selection decision.

## Final Experiment Protocol

Before making paper-ready claims, follow the formal protocol in
`paper/final_experiment_protocol.md`. The protocol keeps the current
PreHOI-Rank direction centered on leakage-safe candidate ranking, requires
`candidate_order: stable_uid`, requires `input_uses_forecast_frame=false`, and
continues to describe target-object labels as derived proxy labels rather than
direct HOT3D ground truth.

Dry-run the final candidate-ranker workflow before launching any repeated-seed
experiment:

```powershell
python src/training/run_final_candidate_ranker_protocol.py --dry-run
```

After reviewing the dry-run output, the planned 5-seed command is:

```powershell
python src/training/run_final_candidate_ranker_protocol.py --seeds 42 123 2026 7 99
```

The protocol runner saves candidate final-protocol logs under
`results/logs/final_protocol/` and the summary table at
`results/tables/final_candidate_ranker_summary.csv`. These artifacts are still
review-required and must not be treated as final paper claims until the split,
baselines, seed statistics, and proxy-label limitations are reviewed.

Current 50-clip 5-seed candidate-ranker protocol result:

- top-1 candidate accuracy: `0.7499 +/- 0.0450`
- top-3 candidate accuracy: `0.9699 +/- 0.0161`
- MRR: `0.8605 +/- 0.0221`
- pose MAE: `0.4102 +/- 0.0051`
- pose MSE: `0.4301 +/- 0.0116`

This is the first paper-candidate PreHOI-Rank diagnostic, but it still uses a
50-clip local subset and derived proxy labels. See
`paper/final_candidate_ranker_result_note.md` for limitations and the per-seed
table.

## Pilot Visual-Object Metadata Baseline

This pilot uses `mode="object_visual_metadata"` with cached `image_stats`
features, observation-frame object candidates, metadata features, and
forecast-frame MANO targets. It does not train a CNN or CLIP encoder; the visual
branch consumes only the cached mean/std/min/max image-stat features.

```powershell
python src/training/train_hot3d_visual_object_baseline.py --config configs/hot3d_visual_object_baseline.yaml
```

This is still a `PILOT DEBUG RUN -- NOT FINAL PAPER RESULT`. Proxy labels are
derived labels, not direct HOT3D ground truth, and the run must not be used for
final research claims. The training script verifies cached feature alignment by
`sample_id` and rejects forecast-frame visual/object input.

Keep synthetic mode on for smoke tests:

```yaml
synthetic_mode: true
use_synthetic: true
data_format: webdataset
clips_root: data/raw/hot3d_clips
```

Later, after downloading licensed data and validating HOT3D-Clips contents,
switch real mode deliberately:

```yaml
synthetic_mode: false
use_synthetic: false
clips_root: D:/path/to/hot3d_clips
data_format: webdataset
use_official_toolkit: false
```

Even after switching to real mode, do not claim real results until target-object
labels, future hand-pose conversion, action labels, contact/pre-contact windows,
and splits are validated and documented.

No final HOT3D paper results have been produced by this repository yet.

The intended real sample contract is:

```python
{
    "features": Tensor[seq_len, feature_dim],
    "frames": Tensor[seq_len, 3, H, W],
    "hand_pose_3d": Tensor[seq_len, num_hand_joints, 3],
    "object_id": Tensor[],
    "object_pose": Tensor[4, 4],
    "future_hand_pose_3d": Tensor[future_steps, num_hand_joints, 3],
    "interaction_label": Tensor[],
}
```

## Journal Route Note

The first target is **Machine Learning with Applications**. The waiver plan should be verified before submission against the current Elsevier and Research4Life policies, especially author affiliations, corresponding author rules, and funding status. This repository deliberately separates research code from publication-fee assumptions.

## Reproducibility Rules

- Synthetic results are labeled as synthetic.
- Real results must include dataset version, split definition, preprocessing details, seed, config, and commit hash.
- No state-of-the-art, first-ever, or real-time claims should be made before verified experiments.
- Contact-region claims require real contact annotations or a defensible proxy.
