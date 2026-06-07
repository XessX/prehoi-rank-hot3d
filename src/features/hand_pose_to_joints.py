"""Interfaces for converting HOT3D-Clips hand poses to 3D joints.

This module intentionally does not fake MANO or UmeTrack joint reconstruction.
Valid conversion requires the official hand model/toolkit path and matching
model assets. Until that path is verified, conversion functions raise
NotImplementedError.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def mano_to_joints(
    *,
    mano_pose: dict[str, Any],
    mano_shape: Any,
    hand_side: str,
    mano_model_dir: str | None = None,
) -> np.ndarray:
    """Convert MANO pose/shape parameters to 3D joints.

    Required inputs, based on the HOT3D-Clips schema:
    - `mano_pose["thetas"]`: MANO pose parameters.
    - `mano_pose["wrist_xform"]`: axis-angle orientation and translation from
      world to wrist in the format expected by the `smplx` library.
    - `mano_shape`: MANO beta parameters from `__hand_shapes.json__`.
    - `hand_side`: `left` or `right`.
    - `mano_model_dir`: local folder containing licensed MANO model assets
      such as `MANO_LEFT.pkl` and `MANO_RIGHT.pkl`.

    This function should use the official HOT3D/hand-tracking-toolkit/smplx
    path once dependencies and MANO assets are available.
    """
    raise NotImplementedError(
        "MANO-to-joints conversion is not verified in this repository yet. "
        "Install and validate the official HOT3D/hand_tracking_toolkit + smplx "
        "path with licensed MANO assets before reporting MPJPE."
    )


def umetrack_to_joints(
    *,
    umetrack_pose: dict[str, Any],
    umetrack_profile: Any,
    hand_side: str,
) -> np.ndarray:
    """Convert UmeTrack joint angles/profile data to 3D joints.

    Required inputs, based on the HOT3D-Clips schema:
    - `umetrack_pose["joint_angles"]`: 20 UmeTrack joint-angle values.
    - `umetrack_pose["wrist_xform"]` or `T_world_from_wrist`: 3D wrist pose.
    - `umetrack_profile`: serialized UmeTrack UserProfile from
      `__hand_shapes.json__`.
    - `hand_side`: `left` or `right`.

    This function should use the official hand_tracking_toolkit path once the
    dependency and its model/profile utilities are installed and verified.
    """
    raise NotImplementedError(
        "UmeTrack-to-joints conversion is not verified in this repository yet. "
        "Use the official hand_tracking_toolkit conversion/evaluation utilities "
        "before reporting MPJPE."
    )


def compute_mpjpe(pred_joints: Any, target_joints: Any) -> float:
    """Compute mean per-joint position error for matching joint arrays.

    Parameters must already be valid 3D joint arrays in the same coordinate
    frame with identical shape `[..., num_joints, 3]`. This helper does not
    perform alignment, unit conversion, or model-parameter conversion.
    """
    pred = np.asarray(pred_joints, dtype=np.float64)
    target = np.asarray(target_joints, dtype=np.float64)
    if pred.shape != target.shape:
        raise ValueError(f"pred_joints and target_joints must have the same shape, got {pred.shape} and {target.shape}")
    if pred.ndim < 2 or pred.shape[-1] != 3:
        raise ValueError(f"Expected joint arrays with shape [..., J, 3], got {pred.shape}")
    distances = np.linalg.norm(pred - target, axis=-1)
    return float(np.mean(distances))
