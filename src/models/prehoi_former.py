"""Future PreHOI-Former model slot.

The MVP trains BaselineTransformer. This file reserves the final model name so
later affordance and vision-language modules have a stable place to land.
"""

from __future__ import annotations

from src.models.baseline_transformer import BaselineTransformer


class PreHOIFormer(BaselineTransformer):
    """Temporary alias for the baseline until multimodal branches are added."""

    pass

