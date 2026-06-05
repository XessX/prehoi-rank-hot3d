# References Seed List

This is a working bibliography scaffold for PreHOI-Rank. Do not treat this as a
final BibTeX file. Entries marked `verified` were checked against an official
project page, publisher page, arXiv page, or repository page. Entries marked
`unverified` need bibliographic verification before citation in the manuscript.

## HOT3D Dataset/Toolkit

### HOT3D

- Tentative citation key: `HOT3D`
- Title: HOT3D: Hand and Object Tracking in 3D from Egocentric Multi-View Videos
- Authors: Prithviraj Banerjee; Sindi Shkodrani; Pierre Moulon; Shreyas
  Hampali; Fan Zhang; Jade Fountain; Edward Miller; Selen Basol; Richard
  Newcombe; Robert Wang; Jakob Julian Engel; Tomas Hodan
- Venue/year: CVPR 2025
- Why relevant: Primary dataset paper for HOT3D, the source dataset behind
  HOT3D-Clips and the annotations used by PreHOI-Rank.
- Source URL: https://openaccess.thecvf.com/content/CVPR2025/papers/Banerjee_HOT3D_Hand_and_Object_Tracking_in_3D_from_Egocentric_Multi-View_CVPR_2025_paper.pdf
- Status: verified

### HOT3D Toolkit

- Tentative citation key: `HOT3DToolkit`
- Title: HOT3D Toolkit
- Authors: Meta / Facebook Research HOT3D maintainers
- Venue/year: GitHub repository, accessed 2026-06-06
- Why relevant: Official loader/toolkit documentation for VRS HOT3D and
  HOT3D-Clips.
- Source URL: https://github.com/facebookresearch/hot3d
- Status: verified as toolkit source; formal citation recommendation still
  needs verification.

## HOT3D-Clips / BOP Benchmark

### HOT3D-Clips

- Tentative citation key: `HOT3DClips`
- Title: HOT3D-Clips
- Authors: HOT3D toolkit maintainers
- Venue/year: Official HOT3D toolkit documentation, accessed 2026-06-06
- Why relevant: Defines the WebDataset/HOT3D-Clips format used in this
  repository. The official docs describe HOT3D-Clips as curated HOT3D
  sub-sequences, 150 frames per clip, hosted on Hugging Face, and used in BOP
  Challenge 2024 and the Multiview Egocentric Hand Tracking Challenge.
- Source URL: https://github.com/facebookresearch/hot3d/blob/main/hot3d/clips/README.md
- Status: verified as documentation; formal standalone citation needs
  verification.

### BOP Challenge 2024

- Tentative citation key: `BOP2024`
- Title: BOP Challenge 2024 on Model-Based and Model-Free 6D Object Pose
  Estimation
- Authors: Van Nguyen Nguyen; Stephen Tyree; Andrew Guo; Mederic Fourmy; Anas
  Gouda; Taeyeop Lee; Sungphill Moon; Hyeontae Son; Lukas Ranftl; Jonathan
  Tremblay; Eric Brachmann; Bertram Drost; Vincent Lepetit; Carsten Rother;
  Stan Birchfield; Jiri Matas; Yann Labbe; Martin Sundermeyer; Tomas Hodan
- Venue/year: arXiv, 2025
- Why relevant: HOT3D-Clips documentation says the clips are used in BOP
  Challenge 2024; cite only if discussing the challenge or BOP-specific format.
- Source URL: https://arxiv.org/abs/2504.02812
- Status: verified

## 3D Hand-Object Interaction Datasets

### DexYCB

- Tentative citation key: `DexYCB`
- Title: DexYCB: A Benchmark for Capturing Hand Grasping of Objects
- Authors: Yu-Wei Chao; Wei Yang; Yu Xiang; Pavlo Molchanov; Ankur Handa;
  Jonathan Tremblay; Yashraj S. Narang; Karl Van Wyk; Umar Iqbal; Stan
  Birchfield; Jan Kautz; Dieter Fox
- Venue/year: CVPR 2021
- Why relevant: Major hand-object dataset for grasping, 6D object pose, and 3D
  hand pose benchmarks; useful comparison/backup dataset context.
- Source URL: https://dex-ycb.github.io/
- Status: verified

### HO-3D / HOnnotate

- Tentative citation key: `HO3D`
- Title: HOnnotate: A method for 3D Annotation of Hand and Object Poses
- Authors: Shreyas Hampali; Mahdi Rad; Markus Oberweger; Vincent Lepetit
- Venue/year: CVPR 2020
- Why relevant: Introduces HO-3D, a canonical hand-object 3D pose dataset used
  for comparison in HOT3D and related work.
- Source URL: https://arxiv.org/abs/1907.01481
- Status: verified

### HO-3D v3

- Tentative citation key: `HO3Dv3`
- Title: HO-3D_v3: Improving the Accuracy of Hand-Object Annotations of the
  HO-3D Dataset
- Authors: Shreyas Hampali; Sayan Deb Sarkar; Vincent Lepetit
- Venue/year: arXiv, 2021
- Why relevant: Useful if discussing improved hand-object annotation accuracy
  and contact regions in HO-3D.
- Source URL: https://arxiv.org/abs/2107.00887
- Status: verified

### First-Person Hand Action Benchmark

- Tentative citation key: `FPHA`
- Title: First-Person Hand Action Benchmark with RGB-D Videos and 3D Hand Pose
  Annotations
- Authors: Guillermo Garcia-Hernando; Shanxin Yuan; Seungryul Baek; Tae-Kyun
  Kim
- Venue/year: CVPR 2018
- Why relevant: Egocentric hand-action dataset with RGB-D, 3D hand pose, and
  object interaction context.
- Source URL: https://kcvl-kaist.github.io/FPHA/
- Status: verified

### AssemblyHands

- Tentative citation key: `AssemblyHands`
- Title: AssemblyHands: Towards Egocentric Activity Understanding via 3D Hand
  Pose Estimation
- Authors: TBD
- Venue/year: arXiv/project page, 2023
- Why relevant: Large egocentric 3D hand pose dataset connected to activity
  understanding and challenging hand-object interactions.
- Source URL: https://assemblyhands.github.io/
- Status: partially verified; authors/venue need verification.

### HOI4D

- Tentative citation key: `HOI4D`
- Title: HOI4D: A 4D Egocentric Dataset for Category-Level Human-Object
  Interaction
- Authors: TBD
- Venue/year: TBD
- Why relevant: Often cited for egocentric hand-object interaction with 3D/4D
  annotations; useful related work if verified.
- Source URL: TBD
- Status: unverified

## 3D Hand Pose / MANO / UmeTrack

### MANO / SMPL+H

- Tentative citation key: `MANO`
- Title: Embodied Hands: Modeling and Capturing Hands and Bodies Together
- Authors: Javier Romero; Dimitrios Tzionas; Michael J. Black
- Venue/year: ACM Transactions on Graphics / SIGGRAPH Asia 2017
- Why relevant: Introduces MANO, the hand model used by HOT3D annotations and
  future pose-vector targets.
- Source URL: https://arxiv.org/abs/2201.02610
- Status: verified

### UmeTrack

- Tentative citation key: `UmeTrack`
- Title: UmeTrack: Unified multi-view end-to-end hand tracking for VR
- Authors: Shangchen Han; Po-chen Wu; Yubo Zhang; Beibei Liu; Linguang Zhang;
  Zheng Wang; Weiguang Si; Peizhao Zhang; Yujun Cai; Tomas Hodan; Randi
  Cabezas; Luan Tran; Muzaffer Akbay; Tsz-Ho Yu; Cem Keskin; Robert Wang
- Venue/year: SIGGRAPH Asia 2022
- Why relevant: HOT3D includes UmeTrack hand representation; relevant for pose
  target interpretation and future 3D joint conversion.
- Source URL: https://arxiv.org/abs/2211.00099
- Status: verified

## Egocentric Hand-Object Interaction Understanding

### EPIC-KITCHENS

- Tentative citation key: `EPICKitchens`
- Title: The EPIC-KITCHENS Dataset: Collection, Challenges and Baselines
- Authors: Dima Damen et al.
- Venue/year: TPAMI preprint / arXiv, 2020
- Why relevant: Major egocentric video dataset with action recognition,
  detection, and anticipation tasks; useful context for egocentric forecasting.
- Source URL: https://arxiv.org/abs/2005.00343
- Status: partially verified; complete author list and final venue should be
  verified.

### EPIC-KITCHENS VISOR

- Tentative citation key: `VISOR`
- Title: EPIC-KITCHENS VISOR
- Authors: TBD
- Venue/year: NeurIPS dataset/benchmark, 2022
- Why relevant: Pixel-wise hand/active-object segmentation and contact
  relations; useful for active object and contact-related context.
- Source URL: https://epic-kitchens.github.io/
- Status: unverified

## Affordance/Contact Reasoning

### ContactPose

- Tentative citation key: `ContactPose`
- Title: ContactPose
- Authors: TBD
- Venue/year: TBD
- Why relevant: Commonly cited hand-object contact dataset; relevant to
  affordance/contact reasoning and proxy-label limitations.
- Source URL: TBD
- Status: unverified

### ObMan

- Tentative citation key: `ObMan`
- Title: Learning joint reconstruction of hands and manipulated objects
- Authors: Yana Hasson et al.
- Venue/year: CVPR 2019
- Why relevant: Synthetic hand-object interaction dataset and hand-object
  reconstruction baseline context.
- Source URL: https://openaccess.thecvf.com/content_CVPR_2019/papers/Hasson_Learning_Joint_Reconstruction_of_Hands_and_Manipulated_Objects_CVPR_2019_paper.pdf
- Status: partially verified; complete bibliographic metadata needs checking.

## Candidate Ranking / Object Interaction Forecasting

### Active Object / Candidate Ranking Placeholder

- Tentative citation key: `ActiveObjectRanking`
- Title: TBD
- Authors: TBD
- Venue/year: TBD
- Why relevant: Need papers on active-object prediction, object proposal
  ranking, or candidate scoring in egocentric interaction tasks.
- Source URL: TBD
- Status: unverified

### Ranking Loss Placeholder

- Tentative citation key: `CandidateRankingLoss`
- Title: TBD
- Authors: TBD
- Venue/year: TBD
- Why relevant: Need a methodological citation for masked candidate scoring or
  ranking formulation if using more than standard cross-entropy.
- Source URL: TBD
- Status: unverified

## Leakage-Safe Temporal Evaluation

### Temporal Leakage Placeholder

- Tentative citation key: `TemporalLeakage`
- Title: TBD
- Authors: TBD
- Venue/year: TBD
- Why relevant: Need a citation on temporal leakage, video split leakage, or
  sequence-level split practice in forecasting/evaluation.
- Source URL: TBD
- Status: unverified

### Repeated Seeds / Reproducibility Placeholder

- Tentative citation key: `SeedStability`
- Title: TBD
- Authors: TBD
- Venue/year: TBD
- Why relevant: Need support for reporting mean/std across random seeds and
  avoiding single-run claims.
- Source URL: TBD
- Status: unverified

## CLIP / Vision-Language Baselines

### CLIP

- Tentative citation key: `CLIP`
- Title: Learning Transferable Visual Models From Natural Language Supervision
- Authors: Alec Radford; Jong Wook Kim; Chris Hallacy; Aditya Ramesh; Gabriel
  Goh; Sandhini Agarwal; Girish Sastry; Amanda Askell; Pamela Mishkin; Jack
  Clark; Gretchen Krueger; Ilya Sutskever
- Venue/year: ICML 2021 / arXiv 2021
- Why relevant: Used for exploratory frozen vision-language/text/visual
  features in project ablations, not the main claim.
- Source URL: https://arxiv.org/abs/2103.00020
- Status: verified

### OpenCLIP

- Tentative citation key: `OpenCLIP`
- Title: OpenCLIP
- Authors: TBD
- Venue/year: repository/tooling, TBD
- Why relevant: The project used `open-clip-torch` for frozen CLIP feature
  extraction. Need correct software citation if included in manuscript.
- Source URL: https://github.com/mlfoundations/open_clip
- Status: unverified

## Machine Learning with Applications Target Journal Notes

### Machine Learning with Applications

- Tentative citation key: `MLWA`
- Title: Machine Learning with Applications
- Authors: Elsevier
- Venue/year: journal information page, accessed 2026-06-06
- Why relevant: Target journal scope and open-access/APC planning. Not a
  manuscript reference unless journal metadata or software-publication route is
  discussed in internal planning.
- Source URL: https://www.sciencedirect.com/journal/machine-learning-with-applications
- Status: verified as journal information; APC and Research4Life route must be
  rechecked before submission.
