# Repository Release Checklist

Target future repository:
`https://github.com/XessX/prehoi-rank-hot3d`

Status: release complete for the final/current `v0.1.2` software archive. The
GitHub repository is available at
`https://github.com/XessX/prehoi-rank-hot3d`. The final/current `v0.1.2` Zenodo
archive DOI is `10.5281/zenodo.20736962`.

Pre-push audit: completed on 2026-06-17 in
`paper/pre_github_push_audit.md`.

## Required Public Files

- [x] `README.md` exists.
- [x] `REPRODUCIBILITY.md` exists.
- [x] `DATA_USAGE.md` exists.
- [x] `MODEL_CARD.md` exists.
- [x] `CITATION.cff` exists.
- [x] `.zenodo.json` exists.
- [x] Paper protocol notes exist under `paper/`.
- [x] Figure-generation code exists under `src/visualization/`.
- [x] Pre-GitHub push audit exists:
      `paper/pre_github_push_audit.md`.
- [x] Final post-DOI release audit exists:
      `paper/final_post_doi_release_audit.md`.
- [x] Zenodo release plan exists:
      `paper/zenodo_release_plan.md`.
- [x] Final/current v0.1.2 release notes exist:
      `paper/release_v0_1_0_notes.md`.

## Ignored Data and Generated Artifacts

- [x] `data/raw/` ignored.
- [x] `data/processed/` ignored.
- [x] `results/logs/` ignored.
- [x] `results/checkpoints/` ignored.
- [x] `results/cache/` ignored.
- [x] tar shards ignored.
- [x] VRS/video/archive files ignored.
- [x] model weights ignored with `*.pt`, `*.pth`, and `*.ckpt`.
- [x] large cached feature files ignored with `*.npz`.
- [x] Pre-push tracked risky file check completed.
- [x] Public-facing scan completed for old SciRep links, student IDs, and
      unresolved editing markers.

## Release Blockers

- [x] Final repository URL available:
      `https://github.com/XessX/prehoi-rank-hot3d`.
- [x] Zenodo metadata prepared.
- [x] GitHub release `v0.1.2` archived.
- [x] Zenodo/archive DOI added: `10.5281/zenodo.20736962`.
- [x] Older `v0.1.0` DOI is not used for manuscript citation.
- [x] Superseded `v0.1.1` DOI is not used for manuscript citation.
- [x] Student co-author consent received.
- [x] Student co-author CRediT role confirmations received.
- [x] Final Seyam Rahman Nayem spelling confirmed.
- [x] Cautious HOT3D-Clips license/access wording is present in the manuscript
      package.
- [ ] HOT3D-Clips license/access wording pending final author-side official
      check before submission/artifact sharing.
- [ ] Decision pending on whether derived indexes/logs/checkpoints can be
      shared under dataset terms.

## Scan Notes

Expected scan hits:

- `data/raw`, `.tar`, `.pt`, `.pth`, and checkpoint terms appear in `.gitignore`,
  documentation, and release guidance as ignore/reproduction notes.
- Student IDs may appear only in internal author metadata files:
  `paper/author_information_template.md`, `paper/fill_author_details_form.md`,
  and `paper/multi_author_metadata_update_note.md`.

Unexpected scan hits to remove before public release:

- old Scientific Reports sparse 3D Gaussian Splatting repository link;
- old Scientific Reports Zenodo DOI;
- student IDs in public-facing root docs;
- raw data paths staged for commit;
- model checkpoints or downloaded shards staged for commit.
