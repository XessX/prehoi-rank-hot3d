"""Reproducibility helpers."""

from __future__ import annotations

import os
import random

import torch

try:
    import numpy as np
except ImportError:  # pragma: no cover - used only before requirements install.
    np = None


def seed_everything(seed: int) -> None:
    """Set common random seeds for reproducible smoke tests."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = False
    torch.backends.cudnn.benchmark = True
