# Affordance-Grounded PreHOI-Former

Vision-language guided pre-contact forecasting of 3D hand-object interactions for assistive augmented reality.

This repository is the MVP research-code foundation for a manuscript targeted at **Machine Learning with Applications** with a Research4Life-aware submission route. The code starts honestly: it uses synthetic dummy tensors to prove the pipeline, model, losses, and metrics run end to end. It does **not** report or imply real HOT3D results until the real parser and experiments are implemented.

## Research Goal

The project investigates whether pre-contact egocentric observations can forecast:

- target object,
- future interaction/action label,
- future 3D hand pose,
- later: object affordance/contact region,
- later: vision-language cues for assistive AR guidance.

Primary dataset target: **HOT3D**.

Backup / cross-dataset target: **DexYCB**.

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

No real HOT3D results have been produced by this repository yet.

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
