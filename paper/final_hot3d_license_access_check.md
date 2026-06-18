# Final HOT3D/HOT3D-Clips License and Access Check

Date: 2026-06-18

Status: documented for final submission preparation. This note is based on the
local official-source notes already saved in the repository and keeps the
manuscript wording cautious. It does not replace final author-side verification
against the current official HOT3D/HOT3D-Clips pages immediately before
submission.

## Official Wording Summary

The manuscript and repository should use cautious data-use wording:

- raw HOT3D-Clips data is not redistributed;
- users must obtain HOT3D/HOT3D-Clips from official sources;
- users must follow official HOT3D/HOT3D-Clips access, license, and citation
  terms;
- different data types may be subject to different license terms;
- HOT3D API/toolkit code and HOT3D dataset data have separate licensing;
- MANO/SMPLX or related hand-model dependencies have their own licenses if used;
- derived proxy labels are generated locally and are not direct HOT3D
  ground-truth contact labels.

## What This Paper and Code Do

The PreHOI-Rank repository provides scripts and documentation for:

- inspecting locally downloaded HOT3D-Clips shards;
- building local sample indexes;
- deriving target-object proxy labels from forecast-frame hand-object proximity;
- optimizing clip-level splits;
- checking candidate-order and forecast-frame leakage;
- training and evaluating the PreHOI-Rank candidate-ranking protocol.

The paper reports results on local HOT3D-Clips subsets using derived proxy
labels. It does not claim that the proxy labels are official HOT3D contact
annotations.

## What Is Not Redistributed

The public repository and manuscript package should not redistribute:

- HOT3D-Clips WebDataset shards;
- raw frames or video;
- HOT3D object models;
- original HOT3D annotations;
- generated large feature caches;
- logs, checkpoints, or weights unless later confirmed allowable;
- any restricted dataset content.

## Why the Data/Code Statement Is Cautious

The data/code statement is intentionally cautious because HOT3D-Clips is a
third-party dataset and the exact sharing status of derived sample indexes,
logs, checkpoints, and clip-selection metadata must be interpreted under the
current official dataset terms. The safest public release path is to provide
code and regeneration instructions, while requiring authorized users to obtain
the raw dataset from official sources.

## Final Author-Side Responsibility

Before submission or artifact sharing, the author should:

- recheck the official HOT3D/HOT3D-Clips access and license pages;
- confirm whether any derived indexes or metadata may be shared;
- confirm required HOT3D/HOT3D-Clips citations;
- confirm whether MANO/SMPLX assets or dependencies are referenced or required;
- ensure no raw HOT3D-Clips data or restricted files are included in the public
  repository, final package, or supplementary material.
