# HOT3D Schema Notes

Sources reviewed:

- Official HOT3D toolkit: https://github.com/facebookresearch/hot3d
- Full HOT3D download page: https://www.projectaria.com/datasets/hot3D/
- HOT3D-Clips Hugging Face page: https://huggingface.co/datasets/bop-benchmark/hot3d
- HOT3D paper: https://arxiv.org/pdf/2411.19167

## Official Dataset Formats

HOT3D has two official access patterns.

1. Full HOT3D dataset in VRS-based format.
   The toolkit exposes this through `Hot3dDataProvider`, `projectaria_tools`, and `vrs`. A sequence folder is expected to contain files such as `metadata.json`, `recording.vrs`, `dynamic_objects.csv`, `headset_trajectory.csv`, and `mano_hand_pose_trajectory.jsonl`.

2. HOT3D-Clips in WebDataset/tar format.
   This is a curated subset of fixed clips. The official clips documentation states each clip has 150 frames, and the root contains split folders such as `train_aria`, `train_quest3`, `test_aria`, and `test_quest3`.

## Full VRS Required Files

From the official toolkit path provider:

- `metadata.json`
- `recording.vrs`
- `dynamic_objects.csv`
- `headset_trajectory.csv`
- `mano_hand_pose_trajectory.jsonl`

Quest 3 sequences also require:

- `camera_models.json`

Common optional or auxiliary files:

- `umetrack_hand_pose_trajectory.jsonl`
- `umetrack_hand_user_profile.json`
- `box2d_objects.csv`
- `box2d_hands.csv`
- `masks/*.csv`
- Aria `mps/` data, including eye gaze and SLAM outputs when present
- object library under an assets folder, including `instance.json` and `.glb` object models

## Full VRS Available Fields

Directly available through the official API:

- image streams from `recording.vrs`, indexed by `stream_id` and `timestamp_ns`
- camera calibration and extrinsics
- headset/device trajectory
- dynamic object poses from `dynamic_objects.csv`
- object IDs as `object_uid`; object names and BOP IDs can be mapped through the object library
- hand annotations in MANO and UmeTrack formats
- 2D object and hand boxes when the corresponding CSVs are present
- masks for pose availability, visibility, exposure, and QA status
- Aria eye-gaze data through MPS when available

Important timestamp convention:

- Pose/mask files are timestamped with `timestamp[ns]`.
- Official providers query data by timestamp and use `TimeDomain.TIME_CODE`.

## HOT3D-Clips Format

The clips root may include:

- `object_models`
- `object_models_eval`
- `train_aria`
- `train_quest3`
- `test_aria`
- `test_quest3`
- `clip_definitions.json`
- `clip_splits.json`
- visualization folders such as `vis_mano` and `vis_umetrack`

Each clip tar uses members like:

- `<FRAME-ID>.image_214-1.jpg`
- `<FRAME-ID>.image_1201-1.jpg`
- `<FRAME-ID>.image_1201-2.jpg`
- `<FRAME-ID>.cameras.json`
- `<FRAME-ID>.hands.json`
- `<FRAME-ID>.hand_crops.json`
- `<FRAME-ID>.objects.json`
- `<FRAME-ID>.info.json`
- `__hand_shapes.json__`

Aria clips include one RGB stream `214-1` and two monochrome streams `1201-1`, `1201-2`. Quest 3 clips include two monochrome streams `1201-1`, `1201-2`.

## Directly Usable for This Paper

Useful without inventing labels:

- pre-contact observation frames from VRS image streams or clip images
- future hand-pose targets after converting MANO/UmeTrack annotations to 3D joints
- target-object candidates from dynamic object pose streams and object visibility
- object pose trajectories for distance and visibility reasoning
- masks for filtering valid timestamps
- camera calibration for view selection and image projection
- gaze as an optional attention cue when available

## Fields That Need Derived Labels or Proxies

Not directly provided for the current forecasting task:

- action labels such as pick, place, pour, push, handover
- physical contact frame labels
- contact/affordance region labels
- AR guidance cue labels

Potential derived proxies, to be used only after documentation and validation:

- contact/event frame from minimum hand-object distance using 3D hand joints and object meshes
- target object from closest visible dynamic object near the predicted contact frame
- contact region from nearest object mesh vertices to hand landmarks
- action label from manual annotation or a separately documented taxonomy, not silent inference

## Limitations for Pre-Contact Forecasting

- Full VRS sequences require official toolkit dependencies and licensed data access.
- MANO requires accepting the MANO license and supplying `MANO_RIGHT.pkl` and `MANO_LEFT.pkl`.
- HOT3D test participant sequences may lack ground-truth data; official docs identify held-out participant IDs and note `gt_available_status` in `metadata.json`.
- HOT3D-Clips are curated pose/hand/object clips, not automatically action-anticipation clips.
- No real result should be reported until splits, timestamp windows, label definitions, and evaluation protocol are frozen.

