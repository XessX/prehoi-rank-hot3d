# HOT3D-Clips Key Report

Inspection date: 2026-06-01

Local data inspected:

- `data/raw/hot3d_clips/train_aria/clip-001849.tar`
- `data/raw/hot3d_clips/clip_definitions.json`
- `data/raw/hot3d_clips/clip_splits.json`

The dataset files are ignored by Git and are not part of the repository.

## Shard Summary

- Shard name: `clip-001849.tar`
- Split: `train`
- Device: `Aria`
- Sequence ID: `P0001_23fa0ee8`
- Participant ID: `P0001`
- Number of tar members: 1201
- Number of frame IDs: 150
- First frame IDs: `000000`, `000001`, `000002`, `000003`, `000004`

Root metadata:

- `clip_definitions.json`: 3832 clip definitions
- `clip_splits.json`: split keys `train`, `test_bop`, `test_ht_pose`, `test_ht_shape`
- `clip_splits.json` places clip `1849` under `train` / `Aria`

## Per-Frame Keys

Each inspected frame has:

- `cameras.json`
- `hand_crops.json`
- `hands.json`
- `image_1201-1.jpg`
- `image_1201-2.jpg`
- `image_214-1.jpg`
- `info.json`
- `objects.json`

Non-frame member:

- `__hand_shapes.json__`

First-frame member sizes:

- `000000.cameras.json`: 4337 bytes
- `000000.hands.json`: 4135 bytes
- `000000.hand_crops.json`: 2068 bytes
- `000000.objects.json`: 59218 bytes
- `000000.info.json`: 244 bytes
- `000000.image_214-1.jpg`: 426041 bytes
- `000000.image_1201-1.jpg`: 82055 bytes
- `000000.image_1201-2.jpg`: 89449 bytes
- `__hand_shapes.json__`: 386856 bytes

## Image Streams

The Aria clip contains three image streams:

- `214-1`: RGB image, 1408 x 1408 x 3, camera label `camera-rgb`
- `1201-1`: grayscale image, 640 x 480, camera label `camera-slam-left`
- `1201-2`: grayscale image, 640 x 480, camera label `camera-slam-right`

## JSON Structures Found

`info.json` contains:

- `device`
- `image_timestamps_ns`
- `participant_id`
- `ref_timestamp_ns`
- `sequence_id`

`cameras.json` is keyed by stream ID:

- `1201-1`
- `1201-2`
- `214-1`

Each stream entry contains:

- `T_world_from_camera`
- `calibration`

The calibration block includes stream ID, label, serial number, image size, projection model type, projection parameters, `T_device_from_camera`, and max solid angle.

`hands.json` contains:

- `left`
- `right`

Each hand entry can contain:

- `boxes_amodal`
- `mano_pose`
- `umetrack_pose`
- `visibilities_modeled`

`mano_pose` contains `thetas` and `wrist_xform`. `umetrack_pose` contains `T_world_from_wrist` and `joint_angles`.

`objects.json` is keyed by object/BOP-like IDs. In the first frame the keys were:

- `1`
- `24`
- `28`
- `29`
- `31`
- `32`

Each object entry can contain:

- `T_world_from_object`
- `boxes_amodal`
- `object_bop_id`
- `object_name`
- `object_uid`
- `visibilities_modeled`
- `masks_amodal`
- likely additional mask/visibility fields depending on the object instance

`__hand_shapes.json__` contains:

- `mano`
- `umetrack`

The MANO section is a 10-value shape vector. The UmeTrack section is a large hand profile with dense weights and joint metadata.

## Available Modalities

Directly available in this shard:

- egocentric images
- camera calibration and world-camera pose
- hand pose parameters in MANO and UmeTrack formats
- hand boxes and visibility
- object pose, object name, BOP ID, UID, boxes, masks, and visibility
- per-frame timestamps and sequence metadata
- hand-shape metadata

Not directly available in this shard:

- gaze
- natural-language action labels
- explicit contact frame labels
- explicit contact-region or affordance labels
- object model meshes, because `object_models` / `object_models_eval` were not downloaded

## Direct Use for This Paper

Can support directly after parsing:

- observation frames from `image_214-1.jpg`, `image_1201-1.jpg`, and `image_1201-2.jpg`
- camera metadata from `cameras.json`
- target-object candidates from `objects.json`
- object pose trajectories from `objects.json`
- future hand-pose targets after converting `hands.json` MANO or UmeTrack parameters to joints
- sequence metadata and timestamps from `info.json` and `clip_definitions.json`

Needs conversion:

- MANO/UmeTrack hand parameters to 3D joints
- quaternion and translation blocks to 4x4 transforms
- object IDs / BOP IDs / UIDs to stable class labels
- masks from RLE to dense masks if contact/affordance proxies need pixel or mesh regions

Needs derived proxy or external labels:

- interaction/action label
- contact frame
- contact region
- AR guidance cue

## Proposed MVP Label Plan

Use now, after parser validation:

- `target_object`: derive from `objects.json`, initially using visible object candidates and later a documented closest-approach/contact proxy
- `future_hand_pose`: derive from `hands.json` after MANO/UmeTrack conversion
- `observation_frames`: use image streams, starting with RGB `214-1`
- `camera_metadata`: use `cameras.json`

Postpone:

- `action_label`
- `contact_region`
- `contact_frame`

These must wait until a defensible proxy or manual/external annotation source is defined.

## MVP Sample Definition

The first verified HOT3D-Clips preparation step builds a JSON sample index from
tar member names and annotation files. The index is preparation metadata only,
not a trained dataset result.

Default windowing:

- observation length: 16 frames
- forecast horizon: 5 frames
- forecast frame: `start + observation_length + forecast_horizon - 1`
- frame data: stored as tar member names, not decoded image tensors

Each sample records:

- `sample_id`, `shard`, and `clip_id`
- `observation_frame_ids`
- `forecast_frame_id`
- `image_streams` for `image_214-1`, `image_1201-1`, and `image_1201-2`
- `hand_source` and `available_hands`
- `future_hand_pose` from `hands.json`, currently using MANO or UmeTrack payloads directly
- `target_object_candidates` from visible objects in `objects.json`
- `metadata` with sequence ID, participant ID, device, start/end frame, forecast frame, and timestamps

Safety rules:

- skip a window if no future hand is visible in the forecast frame
- skip a window if no object is visible in the forecast frame
- store all visible object candidates when multiple objects are visible
- leave `target_object_label`, `action_label`, and `contact_label` unset

Remaining TODOs before training:

- define and validate a target-object selection rule
- convert MANO/UmeTrack hand pose payloads to the model's 3D joint tensor target
- define contact/action labels through a documented proxy or additional annotation source
- verify train/test split usage against `clip_splits.json`

## Target Object Proxy Label v1

HOT3D-Clips provides per-frame hand and object annotations, but this inspected
shard does not provide direct action labels, explicit contact frames, or
interaction-object labels. For supervised forecasting experiments, the first
safe target-object label is therefore a derived proxy:

`target_object_proxy_v1_hand_object_box_proximity`

Rule:

- use the forecast frame only
- collect visible hand boxes from `hands.json` / `boxes_amodal`
- collect visible object boxes from `objects.json` / `boxes_amodal`
- for each camera stream shared by the hands and an object, compute:
  - IoU between the union visible-hand box and the object box
  - center distance normalized by image diagonal
  - `proxy_score = IoU - normalized_center_distance`
- score each object by its best stream score
- select the object with the highest proxy score
- store all candidate scores and a proxy confidence value

This rule is intended to support early MVP experiments only. It is not a direct
HOT3D ground-truth interaction label and should be reported as a derived label.
Its main limitations are that bounding-box proximity can choose a nearby but
non-interacted object, amodal boxes may overlap even without contact, and the
rule does not model temporal intent or physical contact. Action labels,
contact-region labels, and contact-frame labels remain unavailable until a
separate proxy or annotation source is defined.

## MVP Readiness

This shard is enough to build a first real-data loader that reads frames, metadata, object annotations, and hand-pose parameters. It is not enough to train the final supervised pre-contact forecasting task because action/contact labels are not directly present and hand parameters still need conversion to 3D joint tensors.

No training has been run on this shard, and no real HOT3D result has been produced.
