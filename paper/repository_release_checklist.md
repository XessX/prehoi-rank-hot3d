# Repository Release Checklist

Target future repository:
`https://github.com/XessX/prehoi-rank-hot3d`

Status: release preparation draft. The GitHub repository is available at
`https://github.com/XessX/prehoi-rank-hot3d`. The archive DOI is pending.

Pre-push audit: completed on 2026-06-17 in
`paper/pre_github_push_audit.md`.

## Required Public Files

- [x] `README.md` exists.
- [x] `REPRODUCIBILITY.md` exists.
- [x] `DATA_USAGE.md` exists.
- [x] `MODEL_CARD.md` exists.
- [x] Paper protocol notes exist under `paper/`.
- [x] Figure-generation code exists under `src/visualization/`.
- [x] Pre-GitHub push audit exists:
      `paper/pre_github_push_audit.md`.

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
- [ ] Zenodo/archive DOI pending.
- [ ] Final author consent pending.
- [ ] Student co-author CRediT role confirmation pending.
- [ ] HOT3D-Clips license/access wording pending final official check.
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
