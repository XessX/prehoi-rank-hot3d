"""HOT3D dataset integration point.

The MVP intentionally uses synthetic tensors by default. Real HOT3D parsing
must be implemented before reporting any dataset result.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
from torch.utils.data import Dataset


class HOT3DPreContactDataset(Dataset):
    """PyTorch Dataset for HOT3D-style pre-contact forecasting samples.

    Synthetic mode is for pipeline testing only. It produces deterministic
    dummy tensors with the same keys the real parser should return.
    """

    def __init__(self, config: dict[str, Any], split: str = "train") -> None:
        self.config = config
        self.split = split
        self.use_synthetic = bool(config.get("use_synthetic", True))

        self.root_dir = Path(config.get("root_dir", "data/raw/hot3d"))
        self.annotation_dir = Path(config.get("annotation_dir", self.root_dir / "annotations"))
        self.seq_len = int(config.get("seq_len", 16))
        self.feature_dim = int(config.get("feature_dim", 128))
        self.image_size = int(config.get("image_size", 32))
        self.future_steps = int(config.get("future_steps", 5))
        self.num_hand_joints = int(config.get("num_hand_joints", 21))
        self.num_objects = int(config.get("num_objects", 33))
        self.num_actions = int(config.get("num_actions", 8))
        self.synthetic_num_samples = int(config.get("synthetic_num_samples", 64))
        self.synthetic_seed = int(config.get("synthetic_seed", 123))

        if self.use_synthetic:
            self.samples = list(range(self.synthetic_num_samples))
            return

        if not self.root_dir.exists():
            raise FileNotFoundError(
                f"HOT3D root directory does not exist: {self.root_dir}. "
                "Set use_synthetic: true for the MVP smoke test, or configure "
                "root_dir after downloading HOT3D."
            )

        if not self.annotation_dir.exists():
            raise FileNotFoundError(
                f"HOT3D annotation directory does not exist: {self.annotation_dir}. "
                "Update annotation_dir to match the downloaded HOT3D layout."
            )

        self.samples = self._load_real_index()

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        if self.use_synthetic:
            return self._make_synthetic_sample(index)
        return self._load_real_sample(index)

    def _make_synthetic_sample(self, index: int) -> dict[str, Any]:
        generator = torch.Generator().manual_seed(self.synthetic_seed + int(index))

        features = torch.randn(self.seq_len, self.feature_dim, generator=generator)
        frames = torch.randn(
            self.seq_len,
            3,
            self.image_size,
            self.image_size,
            generator=generator,
        )
        hand_pose_3d = torch.randn(
            self.seq_len,
            self.num_hand_joints,
            3,
            generator=generator,
        )

        # A smooth dummy target makes the loss finite without pretending to be real.
        final_pose = hand_pose_3d[-1:].repeat(self.future_steps, 1, 1)
        future_noise = 0.05 * torch.randn(
            self.future_steps,
            self.num_hand_joints,
            3,
            generator=generator,
        )
        future_hand_pose_3d = final_pose + future_noise

        object_pose = torch.eye(4, dtype=torch.float32)
        object_id = torch.randint(self.num_objects, size=(), generator=generator)
        interaction_label = torch.randint(self.num_actions, size=(), generator=generator)

        return {
            "features": features.float(),
            "frames": frames.float(),
            "hand_pose_3d": hand_pose_3d.float(),
            "object_id": object_id.long(),
            "object_pose": object_pose,
            "future_hand_pose_3d": future_hand_pose_3d.float(),
            "interaction_label": interaction_label.long(),
            "sample_id": f"synthetic-{index}",
            "is_synthetic": torch.tensor(True),
        }

    def _load_real_index(self) -> list[dict[str, Any]]:
        """Load a real HOT3D sample index.

        TODO:
        - Read the official split file or generate reproducible splits.
        - Resolve frame paths, timestamps, hand annotations, object IDs, poses,
          and forecast targets.
        - Store only lightweight metadata in the index.
        """
        raise NotImplementedError(
            "Real HOT3D indexing is not implemented yet. Keep use_synthetic: true "
            "until frame and annotation parsing are added."
        )

    def _load_real_sample(self, index: int) -> dict[str, Any]:
        """Load a real HOT3D sample.

        TODO:
        - Decode image frames and apply deterministic preprocessing.
        - Load 3D hand joints or MANO-derived joints.
        - Load object pose and stable object class ID.
        - Build future hand-pose target at the configured horizon.
        - Add contact/affordance labels only when valid labels exist.
        """
        raise NotImplementedError(
            f"Real HOT3D sample loading is not implemented yet. Requested index {index}."
        )

