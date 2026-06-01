# Data

Large datasets are not committed to this repository.

Expected layout after manual dataset setup:

```text
data/
  raw/
    hot3d/
    dexycb/
  processed/
    hot3d_splits.json
    dexycb_splits.json
```

The MVP uses synthetic tensors by default. Set `use_synthetic: false` only after implementing and validating the real dataset parser.

