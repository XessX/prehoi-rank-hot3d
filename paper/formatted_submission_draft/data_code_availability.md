# Data and Code Availability Draft

Status: draft. Confirm dataset license/access wording before submission.

## Data Availability

This study uses HOT3D-Clips, a third-party dataset distributed by its original
providers. The authors do not redistribute HOT3D-Clips data, video frames,
WebDataset shards, object models, annotations, or restricted dataset files.
Readers should obtain HOT3D-Clips directly from the official provider and
follow the applicable license, access, and usage terms.

The primary local experiments in the current draft use a 50-clip HOT3D-Clips
subset. A 75-clip local expansion is reported as robustness/scalability
analysis. The selected clip IDs, split-generation procedure, derived
proxy-label procedure, and inspection commands should be documented so
authorized users can regenerate the sample indexes from their own downloaded
copy of the dataset.

## Derived Sample Indexes and Proxy Labels

The target-object labels used in this work are derived proxy labels, not
human-annotated contact or action labels. The proxy-label protocol is based on
future-frame hand-object proximity and is documented in the manuscript and
repository scripts. Generated sample-index files can be regenerated from the
official HOT3D-Clips shards without redistributing restricted dataset content.

Before submission, decide whether derived index JSON files can be shared
directly. If they contain only metadata and no restricted content, they may be
released if allowed by the dataset terms. If the dataset terms do not allow
sharing derived metadata, provide regeneration scripts and clip-selection
instructions instead.

## Code Availability

The implementation can be released in a public GitHub repository after final
cleanup. The PreHOI-Rank repository URL is currently pending. A suggested
future repository name is `https://github.com/XessX/prehoi-rank-hot3d`, but no
repository or archive DOI is claimed in this manuscript package yet.

The code should include:

- HOT3D-Clips inspection scripts;
- proxy-label generation scripts;
- split optimization and split-quality checking scripts;
- candidate-order bias and forecast-frame leakage checks;
- training scripts for the PreHOI-Rank candidate-ranker protocol;
- figure-generation scripts;
- configuration files for reproducible runs.

The repository should not include downloaded HOT3D-Clips shards, generated
large feature files, trained checkpoints, or logs unless their release is
explicitly allowed and useful.

## Trained Checkpoints and Logs

Trained checkpoints, metrics logs, and summary tables should be shared only if
allowed by the dataset terms and only if they do not reveal restricted dataset
content. If shared, they should be clearly marked as outputs from the
documented local subsets and derived proxy-label protocol.

## Human-Subject and Private Data Statement

The authors did not collect new human-subject data for this study. Experiments
are based on an existing third-party dataset. The authors do not redistribute
private participant data. The final manuscript should cite and follow the
official HOT3D-Clips data-use terms and ethics statements.

## Submission Follow-Up Items

- Verify the official HOT3D-Clips license and citation requirements.
- Confirm whether selected clip IDs and derived sample indexes may be shared.
- Create a clean public repository without ignored data artifacts.
- Add exact commands for regenerating the 50-clip primary split, the 75-clip
  robustness split, and proxy labels.
- Add a permanent archive link or release tag if required by the journal.
- Do not reuse the Scientific Reports sparse 3D Gaussian Splatting GitHub or
  Zenodo links for this PreHOI-Rank paper.
