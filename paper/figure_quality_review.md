# PreHOI-Rank Figure Quality Review

Status: first quality-review pass completed.
Date: 2026-06-08.

The current figure set is schematic and does not use copyrighted HOT3D images
or raw dataset frames. Figures are intended for manuscript drafting and should
still receive a final journal-format review before submission.

## Summary

| Figure | Clarity | Readability | Journal suitability | Overclaim risk | Action taken |
| --- | --- | --- | --- | --- | --- |
| Fig. 1: Problem overview | Good | Good | Suitable for draft | Low | Simplified flow, moved arrows away from frame/list text, clarified observation-only input. |
| Fig. 2: Proxy generation | Good | Good | Suitable for draft | Low | Removed overlap between selected proxy and candidate boxes; corrected arrow direction so selection is attributed to scoring, not a non-selected object. |
| Fig. 3: Architecture | Good | Good | Suitable for draft | Low | Increased export quality and kept non-VL/VL wording as an ablation note. |
| Fig. 4: Protocol safety | Good | Good | Suitable for draft | Low | Improved checklist spacing and retained key safety fields: `input_uses_forecast_frame = false` and `candidate_order: stable_uid`. |
| Fig. 5: Results comparison | Good | Good | Suitable for draft | Moderate | Added seed standard-deviation bars and local-subset/proxy-label note to avoid overinterpreting pilot-to-protocol comparison. |

## Per-Figure Review

### Figure 1: Problem Overview

- Clarity: Shows observation frames, visible candidates, ranked output, and
  forecast-frame target construction.
- Readability: Text is large enough for manuscript drafting and arrows no
  longer cross the observation frame strip or ranked-list text.
- Caption match: Matches the manuscript caption about pre-contact candidate
  ranking and forecast-frame target construction.
- Overclaim risk: Low. The figure does not imply use of future-frame inputs.
- Remaining improvement: A later camera-ready version could use a more compact
  timeline if the journal requires single-column figures.

### Figure 2: Proxy-Label Generation

- Clarity: Shows forecast-frame annotations, hand union box, candidate object
  boxes, proximity scoring, and selected target-object proxy.
- Readability: Text and object labels are readable; selected-proxy box no longer
  covers candidate boxes.
- Caption match: Matches the manuscript distinction between derived proxy labels
  and human ground truth.
- Overclaim risk: Low. The bottom warning explicitly states that forecast-frame
  boxes are never model input.
- Remaining improvement: If space permits, the scoring formula can be added in a
  final version, but it should not make the schematic crowded.

### Figure 3: Architecture

- Clarity: Shows temporal metadata encoder, object candidate encoder, candidate
  mask, fusion, score head, and pose head.
- Readability: Good for a full-width figure.
- Caption match: Matches the current strongest non-VL candidate-ranker framing.
- Overclaim risk: Low. Vision-language components are only mentioned as
  ablations, not as the main result.
- Remaining improvement: Add exact loss labels in a final version if the Methods
  section needs tighter equation-to-figure alignment.

### Figure 4: Protocol Safety

- Clarity: Clearly separates allowed input, disallowed input, safe candidate
  ordering, excluded ordering, clip-level split, and position baselines.
- Readability: Good; checklist items are spaced enough for PDF export.
- Caption match: Matches the manuscript safety table and protocol discussion.
- Overclaim risk: Low. It frames unsafe runs as excluded from claims rather than
  implying the protocol removes every possible bias.
- Remaining improvement: A final journal version could add icons, but the
  current schematic is already clear without them.

### Figure 5: 25-Clip vs 50-Clip Results

- Clarity: Shows top-1, MRR, and pose MAE for the 25-clip pilot and 50-clip
  protocol.
- Readability: Bar labels, legend, and uncertainty bars are readable.
- Caption match: Matches the result table and current manuscript wording.
- Overclaim risk: Moderate because it compares a pilot subset with a larger
  protocol subset. The note now says mean +/- std, derived proxy labels, and
  local HOT3D-Clips subset.
- Remaining improvement: If reviewers ask for final-only results, move the
  25-vs-50 comparison to supplementary material.

## Export Quality

- PNG outputs are saved at 300 DPI.
- PDF outputs are generated for vector-friendly manuscript submission.
- PDF font type is configured for editable TrueType-compatible text embedding.

## Remaining Checks Before Submission

- Confirm the target journal's preferred figure format, size, and color mode.
- Check whether figures are legible after conversion to the journal template.
- Decide whether Figure 5 belongs in the main paper or supplementary material.
- Re-run the figure script after any final metric/table changes.
