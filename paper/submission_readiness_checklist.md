# Submission Readiness Checklist

This checklist tracks what remains before the PreHOI-Rank manuscript should be
treated as submission-ready. Current results are paper-candidate diagnostics,
not a completed journal submission.

## Data and Experimental Scope

- [x] Decide result framing: use the 50-clip protocol as the primary controlled
      result and report the 75-clip protocol as robustness/scalability analysis.
- [x] Expanded to 75 clips and reran proxy indexing, split optimization,
      split-quality checks, candidate-order diagnostics, image-stat feature
      refresh, and final-protocol candidate-ranker training.
- [x] Final 50-vs-75 manuscript decision completed.
- [ ] Resolve or explicitly discuss remaining class-coverage warnings.
- [x] Check official HOT3D-Clips license/access sources and record the current
      license wording in the package audit and placeholder scan.
- [x] Document final cautious HOT3D/HOT3D-Clips license/access wording:
      `paper/final_hot3d_license_access_check.md`.
- [ ] Finalize HOT3D-Clips access/license wording for the exact manuscript and
      any public release artifacts.
- [ ] Confirm downloaded data remains ignored by Git.

## Labels and Metrics

- [ ] Keep target-object labels described as derived proxy labels, not ground
      truth.
- [x] Check MANO/UmeTrack-to-3D-joint conversion feasibility:
      `paper/hand_pose_conversion_feasibility.md`.
- [ ] Decide whether to install official hand-conversion dependencies and
      licensed MANO/UmeTrack assets.
- [ ] Add MPJPE-style pose metrics if conversion is validated.
- [ ] Report proxy confidence statistics in the manuscript.
- [ ] Include candidate-position baselines next to ranking metrics.

## Models and Baselines

- [ ] Decide whether to add a stronger external baseline.
- [ ] Rerun required baselines on the locked final split.
- [ ] Keep vision-language and PreHOI-Former variants as exploratory ablations
      unless they outperform the candidate ranker under the same protocol.
- [ ] Confirm all final runs use `candidate_order: stable_uid`.
- [ ] Confirm all final runs have `input_uses_forecast_frame=false`.

## Writing and Figures

- [x] Create expanded journal-style manuscript draft.
- [x] Complete manuscript quality audit.
- [x] Complete full consistency audit after the 75-clip robustness update.
- [x] Assemble pre-submission package:
      `paper/submission_package/`.
- [x] Create author information template:
      `paper/author_information_template.md`.
- [x] Create submission metadata template:
      `paper/submission_metadata_template.md`.
- [x] Create author metadata remaining-items list:
      `paper/author_metadata_remaining_items.md`.
- [x] Fill five-author metadata from provided author details:
      `paper/scirep_metadata_transfer_note.md` and
      `paper/multi_author_metadata_update_note.md`.
- [x] Confirm funding statement: no specific funding.
- [x] Confirm competing interests statement: no competing interests.
- [x] Add student author metadata in internal files only.
- [x] Record student co-author consent for all four student co-authors.
- [x] Confirm student co-author contribution roles.
- [x] Confirm final spelling for Seyam Rahman Nayem.
- [ ] Confirm student co-author ORCID IDs or keep them as not provided.
- [x] Assemble formatted Markdown submission draft:
      `paper/formatted_submission_draft/`.
- [x] Create draft export workflow:
      `scripts/export_submission_draft.py`.
- [x] Generate combined Markdown draft under `paper/exported_drafts/`.
- [x] Complete author-voice polish pass:
      `paper/paraphrase_author_voice_audit.md`.
- [x] Complete post-polish final scan:
      `paper/post_polish_final_scan.md`.
- [x] Generate DOCX/PDF draft exports:
      `paper/final_submission_files/`.
- [x] Create author details fill-in form:
      `paper/fill_author_details_form.md`.
- [x] Create final submission blockers list:
      `paper/final_submission_blockers.md`.
- [ ] Complete final live submission-system metadata checks.
- [x] Create public PreHOI-Rank repository at
      `https://github.com/XessX/prehoi-rank-hot3d`.
- [x] Add final PreHOI-Rank repository URL.
- [x] Add final/current Zenodo archive DOI.
- [x] Confirm final GitHub/Zenodo release `v0.1.2`.
- [x] Create final formatting workflow and draft DOCX/PDF files.
- [ ] Visually inspect final DOCX/PDF before upload.
- [x] Complete core related-work citation verification.
- [x] Confirm no missing-citation markers or unresolved reference-key
      placeholders remain in the current submission manuscript.
- [x] Remove optional commented citation placeholders from the submission
      package references file when they are not cited in the manuscript.
- [x] Generate Fig. 1 problem overview.
- [x] Generate Fig. 2 proxy-label construction diagram.
- [x] Generate Fig. 3 model architecture diagram.
- [x] Generate Fig. 4 leakage/order-bias protocol diagram.
- [x] Generate Fig. 5 results summary figure.
- [x] Review generated figure quality, resolution, fonts, and journal-style
      readability.
- [ ] Add dataset license/access note.
- [x] Add ethics and data-use note.
- [x] Add threats-to-validity section or expand limitations.
- [x] Add author contribution statement.
- [x] Add data/code availability statement.

## Journal and Submission Logistics

- [ ] Verify target journal formatting requirements.
- [x] Check Machine Learning with Applications scope fit, article type language,
      APC listing, Guide for Authors basics, and Elsevier Research4Life/waiver
      route from official sources on 2026-06-09.
- [ ] Finalize Machine Learning with Applications formatting requirements
      against the live Guide for Authors before upload.
- [ ] Verify final APC, taxes, institutional agreement coverage, waiver, or
      Research4Life route using the filled AIUB/Bangladesh affiliation.
- [x] Document final MLWA/APC/Research4Life live-check requirements:
      `paper/final_mlwa_apc_research4life_check.md`.
- [x] Create submission-readiness decision audit:
      `paper/submission_readiness_decision_audit.md`.
- [x] Complete 75-clip expansion and decide it is a robustness/scalability
      analysis, not the primary result.
- [ ] Decide whether to strengthen further with MPJPE-style pose evaluation or
      a stronger fair baseline.
- [x] Complete official-source journal route verification pass; see
      `paper/final_placeholder_scan.md` and
      `paper/journal_route_verification.md`.
- [ ] Research4Life verification pending for filled AIUB/Bangladesh affiliation
      and live submission context.
- [x] Prepare cover letter draft:
      `paper/cover_letter_draft_prehoi_rank.md`.
- [x] Prepare data/code availability draft:
      `paper/data_code_availability_draft.md`.
- [x] Prepare highlights draft:
      `paper/submission_package/highlights.md`.
- [x] Prepare conflict of interest, funding, and ethics/data-use statement
      drafts in `paper/submission_package/`.
- [x] Add multi-author names, shared affiliation, corresponding author, funding
      statement, and competing interests statement from provided metadata.
- [x] Record student co-author consent and CRediT role confirmations.
- [x] Confirm final spelling for Seyam Rahman Nayem.
- [ ] Add final phone/contact field only if required by the submission system.
- [x] Run final placeholder scan for the current paper folder and submission
      package:
      `paper/final_placeholder_scan.md`.
- [ ] Replace cover-letter bracket placeholders after author details are final.
- [ ] Prepare graphical abstract if required.
- [ ] Confirm all tables and figures are cited in text.
- [ ] Confirm generated logs/checkpoints are not committed.
- [ ] Create a clean release tag or archive after final review.
- [x] Create GitHub release preparation checklist:
      `paper/repository_release_checklist.md`.
- [x] Complete pre-GitHub push safety audit:
      `paper/pre_github_push_audit.md`.
- [x] Prepare Zenodo/GitHub release metadata:
      `CITATION.cff`, `.zenodo.json`, and
      `paper/zenodo_release_plan.md`.
- [x] Archive final/current GitHub release `v0.1.2` with Zenodo.
- [x] Add generated Zenodo DOI: `10.5281/zenodo.20736962`.
- [x] Complete final post-DOI release audit:
      `paper/final_post_doi_release_audit.md`.
- [x] Complete final pre-formatting submission audit:
      `paper/final_pre_formatting_audit.md`.
- [x] Complete final formatting audit:
      `paper/final_submission_files/final_formatting_audit.md`.
- [x] Complete final submission-file QA checklist:
      `paper/final_submission_files/final_file_qa_checklist.md`.
- [x] Create human visual-review checklist:
      `paper/final_submission_files/human_visual_review_checklist.md`.
- [ ] Complete human visual review of generated DOCX/PDF.

## Current Readiness Summary

- Working title: done.
- Candidate-ranking method framing: done.
- 50-clip final-protocol candidate-ranker run: done.
- 75-clip final-protocol candidate-ranker run: completed; comparison note
  created, with recommendation to treat it as a harder robustness check rather
  than an automatic replacement for the 50-clip result.
- First manuscript draft: expanded journal-style draft created.
- Manuscript quality audit: completed; revision log created.
- Related work: expanded draft started, citations incomplete.
- Figures: reviewed draft versions generated with PNG and PDF exports.
- Pre-submission package: assembled under `paper/submission_package/`; not yet
  submission-ready.
- Submission decision audit: completed; current recommendation is to keep the
  50-clip result primary, report the 75-clip result as robustness analysis, and
  strengthen further only with validated MPJPE or a fair baseline if feasible.
- Hand pose conversion feasibility: checked. MPJPE is feasible with official
  dependencies/assets but blocked locally until that path is validated.
- Journal route verification: official-source pass completed on 2026-06-09;
  APC/Research4Life status still depends on final author-side details.
- Final placeholder scan: completed for the current submission package.
- Cover letter, highlights, contribution, ethics/data-use, conflict of
  interest, funding, and data/code availability drafts: started.
- Author information and declarations: five-author metadata added.
- Student co-author metadata: added; consent and contribution roles confirmed.
- Final Seyam Rahman Nayem spelling is confirmed.
- PreHOI-Rank repository URL: `https://github.com/XessX/prehoi-rank-hot3d`;
  do not reuse prior Scientific Reports sparse 3D Gaussian Splatting links.
- Archive DOI: `10.5281/zenodo.20736962`.
- GitHub/Zenodo release: complete for `v0.1.2`.
- Final formatting workflow: completed for draft DOCX/PDF generation.
- Formatted Markdown submission draft: assembled; DOCX/PDF drafts generated.
- HOT3D/HOT3D-Clips license/access wording: documented cautiously; final
  author-side official check remains pending.
- MLWA/APC/Research4Life route: documented cautiously; final live verification
  remains pending.
- Draft export workflow: created; combined Markdown export available. DOCX/PDF
  export remains pending because Pandoc is not available on PATH.
- Author-voice polish: completed and scanned.
- Post-polish final scan: completed; intentional human-input placeholders
  remain.
- Final pre-formatting audit: completed.
- Final submission-file QA checklist: completed.
- Human visual-review checklist: created; completion remains pending until the
  author opens and checks the DOCX/PDF manually.
- Author details fill-in form and final blocker list: updated for the
  five-author metadata; student consent, contribution roles, and final author
  spelling are confirmed.
- Submission-ready status: not yet.
