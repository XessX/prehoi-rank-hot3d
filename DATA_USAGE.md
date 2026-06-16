# Data Usage

This repository does not redistribute HOT3D-Clips data.

## Third-Party Dataset

HOT3D-Clips is a third-party dataset. Users must obtain it from official
HOT3D/HOT3D-Clips sources and follow the official access, license, and citation
terms.

This repository should not include:

- raw HOT3D-Clips shards;
- VRS files;
- extracted frames;
- object models;
- restricted annotations;
- large generated feature files;
- logs, checkpoints, caches, or model weights.

## Derived Proxy Labels

PreHOI-Rank uses locally generated derived target-object proxy labels. The
proxy is computed from forecast-frame hand-object proximity and is used only as
a supervised target. It is not direct HOT3D ground truth and should not be
described as a human action/contact annotation.

## Processed Outputs

Processed indexes, split files, logs, metrics, and checkpoints should be shared
only if allowed by HOT3D/HOT3D-Clips terms and only if they do not expose
restricted dataset content. If sharing processed outputs is not allowed,
provide regeneration scripts and clip-selection instructions instead.

## Public Release Guidance

For a public GitHub release, include code, configuration files, paper notes, and
reproducibility instructions. Exclude raw data, generated large artifacts,
checkpoints, and local caches.

Release metadata files are prepared in `CITATION.cff` and `.zenodo.json`.
Zenodo/archive DOI remains pending until a GitHub release is archived.
