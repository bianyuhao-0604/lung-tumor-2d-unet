# Data — MSD Task06 (Lung)

This page documents where the data comes from, how it is laid out on disk,
and how the 2D slice pipeline is derived from the raw 3D volumes. Everything
here is reproducible with the scripts in the repository root — no manual
steps. No real data is ever committed (`data/` is gitignored).

## 1. Source dataset

| | |
|---|---|
| Dataset | [Medical Segmentation Decathlon](https://medicaldecathlon.com/) — **Task06 Lung** |
| Content | 63 training CT volumes, 512×512 axial slices, binary lung-tumor masks |
| Test set | labels are withheld by MSD — all evaluation in this repo is therefore on held-out *training* cases |
| License | **CC-BY-SA 4.0** (see [Licensing](../README.md#license)) |

Download (registration required): <https://medicaldecathlon.com/> — place the
archive contents under:

```
data/msd_task06/Task06_Lung/
├── dataset.json        # case list — the split below is derived from it
├── imagesTr/*.nii.gz
├── labelsTr/*.nii.gz
└── imagesTs/           # unlabeled test volumes shipped with the archive; unused here
```

## 2. Patient-wise split (no leakage)

`prepare_slices.py` and `msd_2d_dataset.py` apply the same deterministic rule:

- **train** = the first `N − val_cases` entries of `dataset.json["training"]`
- **val** = the **last** `val_cases` entries (default **10** → 53 train / 10 val cases)
- the hold-out is at the **case level**: a patient is either fully train or fully val
- `prepare_slices.py` writes `leakage_check` into `meta.json` and asserts it passes

Because MSD provides no public test labels, the 10 held-out cases serve both
model selection and reporting.

## 3. Slice extraction contract (`prepare_slices.py`)

| step | rule |
|---|---|
| HU window | clip to **[−1000, 400]**, rescale to **[0, 1]** |
| geometry | `--resize` (recommended): full-view bilinear resize to `size²`, nearest-neighbor for the mask — peripheral tumors are never cropped away; default: center crop/pad to `size²` |
| train slices | all tumor slices + `neg_ratio × n_pos` randomly drawn empty slices (default **1:1**) |
| val slices | all tumor slices + an equal number of empty slices (the on-the-fly loader caps positives at 30 per case and samples uniformly) |
| no-tumor case | 30 (train) / 15 (val) uniformly spaced empty slices |

Negative-slice sampling is seeded per case (`--seed`, default 42).

Output (~0.3 MB per slice):

```
data/slices/
├── train/{case}_z{zzzz}.npz    # img float32 [0,1] · msk uint8 {0,1}
├── val/{case}_z{zzzz}.npz
└── meta.json                   # per-split case/pos/neg counts + leakage_check
```

With the released configuration (`--size 256 --resize --val_cases 10`) this
yields **2,964 train / 350 val slices** (173 tumor / 177 empty in val).

## 4. Reproduce the pipeline

```bash
# one-time offline slicing — then epochs are ~12× faster than on-the-fly decoding
python prepare_slices.py --data_root data/msd_task06/Task06_Lung \
                         --out data/slices --size 256 --resize --val_cases 10

# training on prepared slices
python train.py --prepared data/slices --epochs 100

# evaluation on exactly the validation set used during training
python infer_eval.py --prepared data/slices \
                     --ckpt data/checkpoints/best.pth --out data/preds
```

Keep `--val_cases / --size / --seed` identical between training and
evaluation — otherwise you are evaluating a different set. The `--prepared`
mode makes this explicit by pointing both scripts at the same directory.

## 5. Smoke data (no download needed)

`make_dummy_data.py` writes a *structurally identical* fake Task06 tree
(`--out data/smoke --cases 14`), and CI runs the entire pipeline — slicing,
training, evaluation, figure generation — on it for every push.
