"""Affordance feature placeholders.

This module must not be interpreted as real affordance estimation. It only
defines the expected interface for future contact/affordance features.
"""

from __future__ import annotations

import torch


def zero_affordance_placeholder(num_regions: int, device: torch.device | None = None) -> torch.Tensor:
    """Return a zero vector for synthetic smoke tests."""
    if num_regions <= 0:
        raise ValueError("num_regions must be positive.")
    return torch.zeros(num_regions, device=device)

