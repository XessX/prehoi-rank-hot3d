# Hand Pose Conversion Feasibility

Status: feasibility audit, not an MPJPE result.
Date: 2026-06-08.

This note investigates whether HOT3D-Clips MANO/UmeTrack hand annotations can
be converted into 3D joints for MPJPE-style pose evaluation. No 3D joints were
created in this pass, and no MPJPE result should be reported yet.

## Official HOT3D/HOT3D-Clips Schema Notes

The official HOT3D project states that hand annotations are provided in both
UmeTrack and MANO formats. The official HOT3D-Clips documentation describes
each clip as a tar archive with per-frame `hands.json` files and a clip-level
`__hand_shapes.json__` file.

Officially documented hand fields:

- `<FRAME-ID>.hands.json`
  - `left` and/or `right`, each possibly missing.
  - `mano_pose`
    - `thetas`: MANO pose parameters.
    - `wrist_xform`: axis-angle orientation and translation in the format
      expected by `smplx`.
  - `umetrack_pose`
    - `joint_angles`.
    - wrist transform / world-from-wrist pose.
  - `boxes_amodal`.
  - `visibilities_modeled`.
- `__hand_shapes.json__`
  - `mano`: MANO beta shape parameters shared across the clip.
  - `umetrack`: serialized UmeTrack user profile.

The official HOT3D/HOT3D-Clips documentation recommends the
`hand_tracking_toolkit` for loading/visualizing hand annotations. For MANO,
the official HOT3D toolkit also requires licensed MANO model files
(`MANO_LEFT.pkl`, `MANO_RIGHT.pkl`) and the `smplx` path.

Sources checked:

- HOT3D project page: https://facebookresearch.github.io/hot3d/
- HOT3D Toolkit: https://github.com/facebookresearch/hot3d
- HOT3D-Clips README: https://github.com/facebookresearch/hot3d/blob/main/hot3d/clips/README.md
- Hand Tracking Toolkit: https://github.com/facebookresearch/hand_tracking_toolkit

## Local Field Inspection

Command:

```powershell
python src/datasets/inspect_hot3d_hand_pose_fields.py --root data/raw/hot3d_clips --max-shards 3 --max-frames 3
```

Local inspection summary:

- Local shards found: 50.
- Shards inspected: 3.
- Frames inspected per shard: 3.
- `__hand_shapes.json__` contains:
  - `mano`: list of 10 numeric beta parameters.
  - `umetrack`: dictionary with 14 top-level keys, including hand-scale and
    joint/profile metadata.
- `hands.json` contains both `left` and `right` in inspected frames.
- For both hands:
  - `mano_pose.thetas`: list length 15.
  - `mano_pose.wrist_xform`: list length 6.
  - `umetrack_pose.T_world_from_wrist`: dictionary with `quaternion_wxyz` and
    `translation_xyz`.
  - `umetrack_pose.joint_angles`: list length 22 in the inspected local shards.
  - `boxes_amodal` and `visibilities_modeled` are present.

Important caveat:

- The official HOT3D-Clips README text describes UmeTrack `joint_angles` as 20
  floats, but the inspected local train Aria shards contain 22 values. Before
  implementing UmeTrack MPJPE, the conversion code must follow the official
  toolkit behavior for the actual downloaded shard format rather than assuming
  a fixed count from prose alone.

## Current 42-D Pose Target

Command:

```powershell
python src/datasets/test_hand_pose_vector_shapes.py --index data/processed/hot3d_clips_train_optimized.json --max-samples 20
```

Observed output:

- Samples in train index: 4175.
- Samples inspected: 20.
- Vector dimension: 42 for all inspected samples.
- Left hand:
  - present in 20 / 20 inspected samples,
  - source `mano_pose`,
  - `thetas` length 15,
  - `wrist_xform` length 6.
- Right hand:
  - present in 20 / 20 inspected samples,
  - source `mano_pose`,
  - `thetas` length 15,
  - `wrist_xform` length 6.

Current interpretation:

```text
[left MANO thetas(15) + wrist_xform(6),
 right MANO thetas(15) + wrist_xform(6)] = 42 values
```

This is a MANO pose-parameter vector target. It is not a 3D joint target and
therefore cannot be interpreted as MPJPE.

Detailed report:

```text
paper/hand_pose_vector_target_report.md
```

## Dependency Inspection

Current project dependency files do not include the official hand-conversion
dependencies:

- `requirements.txt`: no `smplx`, `hand_tracking_toolkit`, `trimesh`,
  `pytorch3d`, `manopth`, or `chumpy`.
- `environment.yml`: no `smplx`, `hand_tracking_toolkit`, `trimesh`,
  `pytorch3d`, `manopth`, or `chumpy`.

Current installed package probe:

```text
smplx: False
manopth: False
pytorch3d: False
trimesh: False
hand_tracking_toolkit: False
chumpy: False
```

No heavy dependency was installed during this audit.

## MANO Conversion Feasibility

Feasibility: **feasible with dependency and licensed model assets**.

The local HOT3D-Clips fields appear sufficient in principle for MANO
reconstruction:

- MANO pose: `mano_pose.thetas`.
- Global wrist pose: `mano_pose.wrist_xform`.
- Shape: `__hand_shapes.json__.mano`.
- Hand side: `left` or `right`.

Blockers before valid MPJPE:

- Install and verify `smplx` or the official HOT3D/hand-tracking-toolkit MANO
  path.
- Obtain licensed MANO model assets (`MANO_LEFT.pkl`, `MANO_RIGHT.pkl`) through
  the official MANO license route.
- Confirm coordinate frame and units for reconstructed joints.
- Confirm joint ordering and whether wrist/root alignment is needed before
  computing MPJPE.
- Convert both predictions and targets through the same verified path.

## UmeTrack Conversion Feasibility

Feasibility: **feasible with official toolkit dependency, but locally blocked
until verified**.

The local fields appear sufficient for an official UmeTrack conversion path:

- UmeTrack pose: `umetrack_pose.joint_angles`.
- Wrist/world pose: `umetrack_pose.T_world_from_wrist`.
- UmeTrack profile: `__hand_shapes.json__.umetrack`.

Blockers before valid MPJPE:

- Install and verify `hand_tracking_toolkit`.
- Identify the official API that maps local HOT3D-Clips UmeTrack profile +
  joint angles to 3D joints.
- Resolve the observed local `joint_angles` length of 22 versus the official
  README prose description.
- Confirm the coordinate frame and units of output joints.

Official toolkit notes suggest UmeTrack may be the stronger path for HOT3D
supervision because the hand-tracking-toolkit README states that MANO
annotations are solved from UmeTrack and may be slightly less accurate.

## Placeholder-Safe Code Added

`src/features/hand_pose_to_joints.py` now defines:

- `mano_to_joints(...)`
- `umetrack_to_joints(...)`
- `compute_mpjpe(pred_joints, target_joints)`

The conversion functions raise `NotImplementedError` until the official model
path and required assets are installed and validated. `compute_mpjpe` only works
on already-valid matching joint arrays and does not perform pose conversion.

## Recommendation

Decision: **feasible with dependencies; blocked locally for MPJPE today**.

Recommended next technical step:

1. Prefer UmeTrack conversion through the official `hand_tracking_toolkit` if
   the API can output 3D joints from `joint_angles`, `T_world_from_wrist`, and
   the serialized profile.
2. Use MANO conversion through `smplx` only after obtaining licensed MANO model
   files and confirming the HOT3D wrist transform convention.
3. Do not report MPJPE until both predicted and target pose parameters are
   converted to 3D joints through the same verified path.

Fallback if conversion takes too long:

- Keep the current pose-vector MAE/MSE as an auxiliary diagnostic.
- State clearly in the manuscript that MPJPE is future work.
- The 75-clip expansion path has been completed and should be treated as a
  robustness/scalability analysis. Do not use it to hide the unresolved MPJPE
  limitation.
