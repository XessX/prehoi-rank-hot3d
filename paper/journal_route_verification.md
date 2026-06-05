# Journal Route Verification

Status: route-check draft, not a final submission decision.
Date checked: 2026-06-06.

This note records the current target-journal route for the PreHOI-Rank
manuscript. APC, waiver, Research4Life, and submission requirements can change,
so every item here should be rechecked on the official pages immediately before
submission.

## Target Journal: Machine Learning with Applications

Primary target:

- Journal: Machine Learning with Applications
- Publisher: Elsevier
- Current manuscript direction: PreHOI-Rank: Affordance-Grounded Candidate
  Ranking for Pre-Contact 3D Hand-Object Interaction Forecasting
- Current status: likely scope fit, pending final formatting and author-route
  verification

Official sources to recheck:

- Machine Learning with Applications journal page:
  https://www.sciencedirect.com/journal/machine-learning-with-applications
- Machine Learning with Applications Guide for Authors:
  https://www.sciencedirect.com/journal/machine-learning-with-applications/publish/guide-for-authors
- Elsevier open access publishing options and Research4Life route:
  https://www.elsevier.com/en-au/researcher/author/open-access/choice
- Elsevier waiver policy support page:
  https://www.elsevier.support/publishing/answer/what-is-elseviers-waiver-policy-for-open-access-fees

## Scope Fit

Machine Learning with Applications describes itself as a peer-reviewed open
access journal focused on machine learning research and applications. The stated
scope includes computer vision, intelligent systems, neural networks, and
machine learning applications across engineering and other domains. The current
PreHOI-Rank manuscript appears to fit as an applied machine-learning paper
because it proposes and evaluates a reproducible candidate-ranking formulation
for egocentric pre-contact hand-object forecasting.

The manuscript should keep the scope fit clear by emphasizing:

- the machine-learning formulation: candidate-level target-object ranking;
- the applied computer-vision setting: egocentric HOT3D-Clips hand-object data;
- the evaluation protocol: leakage-safe temporal forecasting and clip-level
  splitting;
- the empirical result: 5-seed evaluation on a 50-clip local subset;
- the limitation: derived proxy labels and local subset, not full-dataset or
  state-of-the-art claims.

## Article Type Fit

Likely article type:

- Full length article or regular research paper.

The current paper is not best framed as a short technical note because it
contains a dataset-preprocessing protocol, derived label protocol, candidate
ranking method, leakage-safety protocol, seed-stability experiments, and
multiple limitations. The final article type should be confirmed inside the
Guide for Authors and the Editorial Manager submission form.

## Open Access/APC Route to Verify

Machine Learning with Applications is listed by Elsevier/ScienceDirect as an
open access journal. The official journal page currently lists an article
publishing charge of USD 2,460, excluding taxes. This amount must be checked
again before submission because APCs can change and may vary by publisher
program, tax rules, institutional agreements, or geographical pricing.

Before submission, verify:

- current APC on the MLWA journal page;
- whether taxes apply to the corresponding author's country/institution;
- whether an institutional open-access agreement covers the corresponding
  author;
- whether Elsevier's geographical pricing program applies;
- whether any funder agreement applies;
- whether a Research4Life waiver or discount applies.

## Research4Life/APC Waiver Route to Verify

Elsevier's official open-access page states that fully open access Elsevier
journals are included in its Research4Life open-access eligibility program and
that eligible authors see waiver/discount information after acceptance in the
rights and access workflow. The same page states that eligibility depends on the
locations of the authors' institutions, including whether all authors are from
Group A countries, all are from Group B countries, or there is a mix of Group A
and B countries.

Important caution:

- Do not claim Research4Life eligibility in the manuscript package yet.
- Eligibility must be verified using the current Research4Life country groups
  and the exact affiliations of the corresponding author and co-authors.
- Mixed affiliations can affect the waiver/discount outcome.
- If any co-author is from a non-Research4Life country, Elsevier's examples
  indicate that no Research4Life waiver or discount may apply.
- If the author team cannot afford the APC and does not qualify automatically,
  Elsevier's support page says individual waiver requests may be considered
  case by case for fully open access journals.

## Author Affiliation Caution

The route depends on the final author list and the formal corresponding author.
Before submission:

- choose the corresponding author intentionally;
- verify the corresponding author's institution in the Elsevier submission
  system;
- verify all co-author institutional countries against current Research4Life
  eligibility;
- contact the institution library or research office about open-access deals;
- do not rely on location, nationality, or residence alone.

## Backup Journal: PLOS ONE

PLOS ONE can remain a possible backup because it considers technically sound
research across disciplines and has explicit data-availability expectations.
However, it should stay secondary for now because the current manuscript is
more naturally positioned as an applied machine-learning/computer-vision
methods paper.

Official sources to recheck:

- PLOS ONE submission guidelines:
  https://journals.plos.org/plosone/s/submission-guidelines
- PLOS publication fees:
  https://plos.org/fees/
- PLOS data availability policy:
  https://plos.org/open-science-policies/

Backup-route cautions:

- PLOS fee assistance and institutional agreements must be checked before
  submission.
- PLOS data availability expectations are strict; since HOT3D-Clips is a
  third-party gated/licensed dataset, the paper must explain how readers can
  access the original dataset and regenerate indexes without redistributing
  restricted data.
- PLOS ONE should not be used to avoid strengthening the paper's methods,
  citations, or limitations.

## Submission Files Likely Needed

Likely required or useful files:

- main manuscript;
- title page with author names, affiliations, corresponding author details, and
  ORCID IDs if available;
- highlights if required or recommended by Elsevier;
- graphical abstract if required or optional for the chosen article type;
- individual figure files;
- tables in manuscript or separate editable files;
- references or BibTeX source;
- cover letter;
- conflict of interest declaration;
- funding statement;
- author contribution statement;
- data availability statement;
- code availability statement;
- ethics/data-use statement;
- APC, institutional agreement, or waiver note for internal planning.

## Risks and Uncertainties

- APC and waiver information may change before submission.
- Research4Life eligibility cannot be concluded until the final author list and
  affiliations are known.
- The paper currently uses a 50-clip local HOT3D-Clips subset, not the full
  dataset.
- Target-object labels are derived proxy labels, not human ground-truth
  contact/action labels.
- Current pose evaluation is MANO pose-vector MAE/MSE, not MPJPE.
- Some class imbalance remains after split optimization.
- Vision-language components are exploratory ablations, not the main result.
- Citation details and dataset-license wording still need final verification.
- Figure quality, resolution, and journal format requirements still need review.
