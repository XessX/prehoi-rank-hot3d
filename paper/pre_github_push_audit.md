# Pre-GitHub Push Audit

Date: 2026-06-17

Target GitHub repository:
`https://github.com/XessX/prehoi-rank-hot3d`

Status: safety audit completed before first GitHub push. The repository appears
safe to push after this audit file and checklist updates are reviewed and
committed.

## Tracked Risky File Check

Command:

```powershell
git ls-files | Select-String -Pattern '\.(tar|pt|pth|ckpt|npz|zip)$|^data/raw/|^data/processed/|^results/logs/|^results/checkpoints/|^results/cache/'
```

Result:

- No tracked `.tar`, `.pt`, `.pth`, `.ckpt`, `.npz`, or `.zip` files.
- No tracked raw HOT3D-Clips shards.
- No tracked generated processed outputs.
- No tracked logs, caches, checkpoints, or model weights.
- Expected tracked placeholders only:
  - `data/raw/.gitkeep`
  - `data/processed/.gitkeep`
  - `results/checkpoints/.gitkeep`
  - `results/logs/.gitkeep`

## Public-Facing Text Scan

Public-facing files scanned:

- `README.md`
- `REPRODUCIBILITY.md`
- `DATA_USAGE.md`
- `MODEL_CARD.md`
- `paper/submission_package/`
- `paper/formatted_submission_draft/`
- `paper/exported_drafts/`

Patterns searched:

- old Scientific Reports sparse3D repository string;
- old Scientific Reports Zenodo DOI;
- student ID numbers;
- `TODO`;
- `TBD`;
- `FIXME`;
- `citation needed`.

Result:

- No old Scientific Reports sparse3D repository string found.
- No old Scientific Reports Zenodo DOI found.
- No student ID numbers found in public-facing release files.
- No `TODO`, `TBD`, `FIXME`, or `citation needed` markers found in the
  public-facing release files checked.

## Internal Student ID Location

Student IDs remain only in internal author metadata files:

- `paper/author_information_template.md`
- `paper/fill_author_details_form.md`
- `paper/multi_author_metadata_update_note.md`

They are not present in the public-facing root docs, formatted manuscript,
submission package manuscript/cover letter, or exported combined draft.

## Ignored Data Status

`git check-ignore -v` confirmed ignore coverage for:

- HOT3D-Clips tar shards under `data/raw/hot3d_clips/`;
- generated files under `data/processed/`;
- logs under `results/logs/`;
- checkpoints under `results/checkpoints/`;
- caches under `results/cache/`;
- `.pt`, `.pth`, `.ckpt`, `.npz`, and `.zip` artifacts.

Large local files are present under `.venv/`, `data/raw/`, and
`data/processed/`, but they are ignored or untracked and are not staged for
push.

## Remaining Blockers

- GitHub repository exists according to the user, but this local branch has not
  yet been pushed.
- Zenodo/archive DOI was not yet available at the time of this pre-push audit;
  it was later updated to `10.5281/zenodo.20722666`.
- Co-author consent is pending.
- Student co-author contribution confirmation is pending.
- HOT3D-Clips license/access wording needs final official confirmation before
  manuscript submission and release artifact decisions.

## Push Recommendation

Safe to push after committing this audit layer, assuming `git status` shows
only intended audit/checklist changes and no ignored data artifacts are forced
into the index.
