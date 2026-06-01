"""Language-prompt helpers for later CLIP/open-vocabulary guidance."""

from __future__ import annotations


def build_interaction_prompt(object_name: str, action_name: str) -> str:
    """Create a plain prompt for future vision-language feature extraction."""
    object_name = object_name.strip()
    action_name = action_name.strip()
    if not object_name or not action_name:
        raise ValueError("object_name and action_name must be non-empty.")
    return f"a person is about to {action_name} the {object_name}"

