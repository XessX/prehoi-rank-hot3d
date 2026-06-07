# Hand Pose Vector Target Report

Status: current target-vector audit.

This report documents the current future hand-pose target used by the
HOT3D-Clips dataset class. It does not claim MPJPE and does not convert
MANO/UmeTrack parameters to 3D joints.

## Source

- Index: `data\processed\hot3d_clips_train_optimized.json`
- Samples in index: 4175
- Observation frames: 16
- Forecast horizon: 5
- Requested hand source: mano_pose

## Current 42-D Target Interpretation

- Hand order: `left, right`
- Per hand: first 15 MANO `thetas` values + first 6 `wrist_xform` values.
- Per-hand dimension: 21
- Both-hands dimension: 42
- Missing hands are zero-padded by the dataset class.
- This is a pose-parameter vector target, not a 3D joint target.

## Inspected Dimension Counts

- Vector dimension 42: 20 inspected samples

## Availability Counts

- left.present=True: 20
- left.source=mano_pose: 20
- left.theta_len=15: 20
- left.wrist_xform_len=6: 20
- right.present=True: 20
- right.source=mano_pose: 20
- right.theta_len=15: 20
- right.wrist_xform_len=6: 20

## First Inspected Samples

### `000023_000000_000015_f000020`

- Vector dimension: 42
- Available hands in index: ['left', 'right']
- left: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False
- right: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False

### `000023_000001_000016_f000021`

- Vector dimension: 42
- Available hands in index: ['left', 'right']
- left: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False
- right: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False

### `000023_000002_000017_f000022`

- Vector dimension: 42
- Available hands in index: ['left', 'right']
- left: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False
- right: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False

### `000023_000003_000018_f000023`

- Vector dimension: 42
- Available hands in index: ['left', 'right']
- left: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False
- right: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False

### `000023_000004_000019_f000024`

- Vector dimension: 42
- Available hands in index: ['left', 'right']
- left: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False
- right: present=True, source=mano_pose, theta_len=15, wrist_xform_len=6, padded=False

## MPJPE Status

MPJPE is not available from this vector directly. A valid MPJPE pipeline
requires verified MANO or UmeTrack model conversion to 3D joints and
matching predicted/target joint arrays in the same coordinate frame.
