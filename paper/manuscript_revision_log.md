# Manuscript Revision Log

Date: 2026-06-06.

## Changes Made

- Committed the expanded manuscript draft before starting the audit.
- Audited the manuscript against the final experiment protocol, final result
  note, research decision note, citation map, result table, and safety table.
- Replaced risky manuscript wording:
  - "state-of-the-art claim" -> "benchmark-superiority claim";
  - proxy-related "ground truth" phrasing -> "official annotations" or
    "human annotations";
  - "full HOT3D" phrasing -> "complete HOT3D release";
  - "does not prove" -> "does not establish";
  - "target-contact labels" -> "target-object/contact annotations".
- Created `paper/manuscript_quality_audit.md`.
- Updated `paper/submission_readiness_checklist.md` to mark the manuscript
  quality audit as completed while keeping citation verification, final
  formatting, and figure quality review pending.

## What Remains Weak

- Related work still uses TODO placeholders for contact/affordance reasoning,
  active-object ranking, candidate-ranking methodology, and temporal leakage.
- Some BibTeX entries are partial and need final verification.
- HOT3D-Clips license/access and derived-index sharing terms still need an
  official wording pass.
- The generated figures are first versions and still need journal-quality
  inspection.
- The final protocol uses a 50-clip local subset, not a larger or complete
  release.
- Pose metrics are not yet MPJPE-style 3D joint metrics.
- The paper may need an external or stronger baseline before submission.

## Before Submission

- Verify all citations and replace TODO placeholders.
- Finalize dataset license/access and ethics/data-use language.
- Decide whether to expand beyond 50 clips.
- Decide whether to implement MANO/UmeTrack-to-3D-joint conversion.
- Review figures for resolution, readability, and journal formatting.
- Convert the manuscript to the journal-required format.
- Confirm Machine Learning with Applications article type, APC, and waiver route.
