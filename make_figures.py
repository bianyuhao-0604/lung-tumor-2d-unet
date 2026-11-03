"""make_figures.py — generate README figures from training artifacts

Usage:
  python make_figures.py --log data/checkpoints/train_log.txt \
                         --csv data/preds_v4/dice_per_slice.csv \
                         --out docs/figures

Outputs:
  training_curves.png    loss / val-Dice curves of the most recent training run
  dice_distribution.png  per-slice Dice distribution (tumor vs empty) + failures per case
"""
import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3, "figure.dpi": 150})


def parse_log(path):
    """Parse train_log.txt; return the most recent run as arrays."""
    blocks, cur = [], None
    for line in open(path, encoding="utf-8"):
        if line.startswith("#"):
            cur = []
            blocks.append(cur)
            continue
        m = re.match(r"\[\s*(\d+)/\d+\]\s+train_loss=([\d.]+)\s+val_loss=([\d.]+)"
                     r"\s+val_dice=([\d.]+)", line)
        if m and cur is not None:
            cur.append((int(m.group(1)), float(m.group(2)),
                        float(m.group(3)), float(m.group(4))))
    if not blocks or not blocks[-1]:
        raise SystemExit(f"{path}: no parsable training records")
    ep, tr, va, dc = zip(*blocks[-1])
    return np.array(ep), np.array(tr), np.array(va), np.array(dc)


def fig_training_curves(ep, tr, va, dc, out):
    best_i = int(dc.argmax())
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    ax1.plot(ep, tr, label="train loss (BCE+Dice)", lw=1.8)
    ax1.plot(ep, va, label="val loss", lw=1.8)
    ax1.set_xlabel("epoch"); ax1.set_ylabel("loss"); ax1.legend()
    ax1.set_title("Loss")
    ax2.plot(ep, dc, lw=1.5, label="val Dice (macro, per-slice)")
    ax2.scatter([ep[best_i]], [dc[best_i]], c="tab:red", zorder=3,
                label=f"best = {dc[best_i]:.4f} @ epoch {ep[best_i]}")
    ax2.set_xlabel("epoch"); ax2.set_ylabel("Dice"); ax2.set_ylim(0, 1)
    ax2.legend(); ax2.set_title("Validation Dice")
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)
    print("written", out)


def fig_dice_distribution(csv_path, out):
    dice, gpos, case_fail = [], [], defaultdict(lambda: [0, 0])
    for r in csv.DictReader(open(csv_path, encoding="utf-8")):
        d = float(r["dice"]); gp = r["gt_pos"] == "1"
        dice.append(d); gpos.append(gp)
        if d < 0.1 and "_z" in r["name"]:
            case_fail[r["name"].rsplit("_z", 1)[0]][0 if gp else 1] += 1
    dice = np.array(dice); gpos = np.array(gpos)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4))
    bins = np.linspace(0, 1, 21)
    ax1.hist(dice[~gpos], bins=bins, alpha=0.65,
             label=f"empty slices (n={int((~gpos).sum())})", color="tab:blue")
    ax1.hist(dice[gpos], bins=bins, alpha=0.65,
             label=f"tumor slices (n={int(gpos.sum())})", color="tab:red")
    ax1.set_xlabel("per-slice Dice"); ax1.set_ylabel("slices")
    ax1.set_title("Per-slice Dice distribution (thr = 0.5)"); ax1.legend()

    if case_fail:
        cases = sorted(case_fail)
        pf = [case_fail[c][0] for c in cases]
        ef = [case_fail[c][1] for c in cases]
        y = np.arange(len(cases))
        ax2.barh(y, pf, label="failed tumor slices", color="tab:red")
        ax2.barh(y, ef, left=pf, label="failed empty slices", color="tab:blue")
        ax2.set_yticks(y); ax2.set_yticklabels(cases, fontsize=8)
        ax2.invert_yaxis(); ax2.set_xlabel("slices with Dice < 0.1")
        ax2.set_title("Complete failures per case"); ax2.legend()
    fig.tight_layout()
    fig.savefig(out); plt.close(fig)
    print("written", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default="data/checkpoints/train_log.txt")
    ap.add_argument("--csv", default=None, help="dice_per_slice.csv (optional)")
    ap.add_argument("--out", default="docs/figures")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    ep, tr, va, dc = parse_log(args.log)
    fig_training_curves(ep, tr, va, dc, out / "training_curves.png")
    if args.csv:
        fig_dice_distribution(args.csv, out / "dice_distribution.png")


if __name__ == "__main__":
    main()
