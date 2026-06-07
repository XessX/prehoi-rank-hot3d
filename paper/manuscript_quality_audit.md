# Manuscript Quality Audit: PreHOI-Rank

Status: internal audit draft.
Date: 2026-06-06.

Files reviewed:

- `paper/manuscript_prehoi_rank_draft.md`
- `paper/final_experiment_protocol.md`
- `paper/final_candidate_ranker_result_note.md`
- `paper/research_decision_note.md`
- `paper/submission_readiness_checklist.md`
- `paper/references.bib`
- `paper/citation_key_map.md`
- `paper/tables/results_table_prehoi_rank.md`
- `paper/tables/protocol_safety_table.md`

## Overall Assessment

The manuscript is internally aligned with the current evidence: PreHOI-Rank is
presented as a candidate-ranking formulation, the final metrics are tied to the
50-clip local HOT3D-Clips subset, and derived labels are not treated as official
annotations. The draft is not yet submission-ready because citation
verification, figure-quality review, final journal formatting, dataset
license/access wording, and optional stronger baselines remain open.

## Audit Areas

| Area | Status | Notes |
| --- | --- | --- |
| Title alignment | Pass | The title matches the current research decision: PreHOI-Rank as affordance-grounded candidate ranking. |
| Abstract accuracy | Pass with caveats | The abstract reports the 50-clip five-seed result and states limitations. It should be revisited after final citation/license checks. |
| Contribution strength | Pass | Contributions are defensible and protocol-oriented. They avoid benchmark-superiority framing. |
| Dataset description accuracy | Pass with caveats | The manuscript consistently says 50-clip local HOT3D-Clips subset, not the complete release. License/access wording remains pending. |
| Proxy-label wording | Improved | Risky "ground truth" wording in the manuscript was replaced with "official annotations" or "human annotations." Supporting protocol files still contain safe negative reminders. |
| Leakage/order-bias safety wording | Pass | `input_uses_forecast_frame=false`, observation-only input, clip-level split, and `candidate_order: stable_uid` are clearly stated. |
| Method/result consistency | Pass | Main method is the non-VL candidate ranker, consistent with the final result note and research decision. |
| Figure/table references | Partial | Figure and table references exist, but journal-ready captions, numbering, and placement still need formatting. |
| Citation placeholders | Not ready | Several TODO placeholders remain: contact/affordance reasoning, active-object ranking, learning-to-rank, and temporal leakage. |
| Limitations completeness | Pass | The draft includes proxy-label, subset, class imbalance, pose metric, candidate visibility, and exploratory-model limitations. |
| Journal-readiness risk | Medium | The scientific framing is cautious, but the paper still needs final references, license/access wording, figure review, and journal formatting. |

## Risky Wording Audit

| Phrase | Found | Action |
| --- | --- | --- |
| "ground truth" | Yes | Replaced in the manuscript when referring to proxy labels. Safe negative reminders remain in protocol/result/table files. |
| "state-of-the-art" | Yes | Replaced in the manuscript with "benchmark-superiority claim." |
| "real-time" | No | No action needed. |
| "full HOT3D" | Yes | Replaced in the manuscript with "complete HOT3D release" or "complete HOT3D or HOT3D-Clips release." |
| "proves" | Yes | Replaced in the manuscript with "does not establish." |
| "guarantees" | No | No action needed. |
| "vision-language guided" as main claim | Found only in research decision note as rejected framing | No manuscript change needed; keep historical note. |
| "contact label" | Yes | Reworded manuscript phrasing to "target-object/contact annotations" or "contact annotations." |

## Internal Consistency Notes

- The manuscript, result table, and final result note agree on the five-seed
  50-clip result: Top-1 `0.7499 +/- 0.0450`, Top-3
  `0.9699 +/- 0.0161`, MRR `0.8605 +/- 0.0221`, pose MSE
  `0.4301 +/- 0.0116`, and pose MAE `0.4102 +/- 0.0051`.
- The manuscript and protocol safety table agree on train/validation/test
  sample counts: 4175 / 1040 / 910.
- The manuscript correctly keeps vision-language and PreHOI-Former experiments
  exploratory.
- The research decision note still includes historical "pilot/debug" wording
  for earlier checkpoints. This is acceptable as provenance, but the final
  manuscript should use "paper-candidate" for the completed five-seed protocol.

## Remaining Weaknesses

- Related work is still a scaffold with TODO citations.
- HOT3D-Clips license/access wording must be verified from official terms.
- Figures are generated but need quality and formatting review.
- Pose metrics are still MANO/UmeTrack pose-vector metrics, not MPJPE.
- The 50-clip subset may be considered small for journal review.
- No external baseline has been added yet.
- Final Machine Learning with Applications formatting and APC/waiver route are
  not complete.
