"""DexYCB integration placeholder.

DexYCB is planned as a backup or cross-dataset benchmark after the HOT3D MVP
is validated. No real DexYCB result should be reported from this file yet.
"""

from __future__ import annotations

from typing import Any

from torch.utils.data import Dataset


class DexYCBPreContactDataset(Dataset):
    """Placeholder Dataset for future DexYCB integration."""

    def __init__(self, config: dict[str, Any], split: str = "train") -> None:
        self.config = config
        self.split = split
        raise NotImplementedError(
            "DexYCB parsing is not part of the MVP. Use HOT3D synthetic mode first."
        )

