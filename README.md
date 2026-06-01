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

## Setup

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
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

