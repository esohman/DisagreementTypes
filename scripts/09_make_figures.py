#!/usr/bin/env python3
"""Generate publication figures from derived analysis tables.

This file records the final visual conventions used in the manuscript:

- Lift heatmaps use a shared 0--2.5 scale centered at lift = 1.
- Figure 1 retains its original larger in-cell number size.
- Figure 2 uses enlarged in-cell numbers for readability after scaling.
- Figure 3 is split into separate A1 and A3 panels; the legend appears on panel (b) only.
- Figure 6 uses separate panels for presence and conditional-intensity disagreement.

Because local output filenames produced by scripts 01--07 may differ across repository
versions, set the paths in CONFIG below to the corresponding derived CSV files before
running this script.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

CONFIG = {
    # TOMATS / BRIGHTER lift tables
    "tomats_cross_lift": ROOT / "outputs" / "tomats_A1_A3_overlap_lift.csv",
    "brighter_cooccurrence": ROOT / "outputs" / "brighter_emotion_cooccurrence.csv",
    "tomats_a1_within_lift": ROOT / "outputs" / "tomats_A1_within_lift.csv",
    "tomats_a3_within_lift": ROOT / "outputs" / "tomats_A3_within_lift.csv",
    # Optional precomputed figure-ready tables for the remaining figures
    "goemotions_breadth": ROOT / "outputs" / "goemotions_breadth.csv",
    "goemotions_boundaries": ROOT / "outputs" / "goemotions_boundary_residuals.csv",
    "brighter_presence_intensity": ROOT / "outputs" / "brighter_presence_intensity_summary.csv",
}

COLORS = [
    "#8c460d", "#c56b05", "#e58508", "#f6aa43", "#fbd7a5",
    "#ffffff",
    "#d9dbea", "#b9b4d4", "#9388b8", "#6d55a0", "#3b0066",
]
CMAP = LinearSegmentedColormap.from_list("lift", COLORS, N=256)
NORM = TwoSlopeNorm(vmin=0.0, vcenter=1.0, vmax=2.5)
LIFT_TICKS = [0, 0.5, 1, 1.5, 2, 2.5]


def text_color(v: float) -> str:
    return "white" if (v < 0.35 or v > 2.0) else "#2f2437"


def plot_lift_heatmap(matrix, labels, title, outfile, number_font=10, show_colorbar=True):
    arr = np.asarray(matrix, dtype=float)
    fig, ax = plt.subplots(figsize=(7.2, 6.2))
    im = ax.imshow(arr, cmap=CMAP, norm=NORM, aspect="equal")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title(title)
    ax.tick_params(length=0)
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=0.8)
    ax.tick_params(which="minor", bottom=False, left=False)

    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            if not np.isfinite(arr[i, j]):
                continue
            v = arr[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center",
                    fontsize=number_font, fontweight="semibold",
                    color=text_color(v))

    if show_colorbar:
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("Lift")
        cbar.set_ticks(LIFT_TICKS)

    fig.tight_layout()
    fig.savefig(outfile, bbox_inches="tight")
    plt.close(fig)


def main():
    missing = [str(p) for p in CONFIG.values() if not p.exists()]
    if missing:
        print("Figure script scaffold installed successfully.")
        print("Before running it, update CONFIG to match the filenames written by scripts 01--07.")
        print("Currently missing:")
        for p in missing:
            print(" -", p)
        return

    # Implement project-specific loading here once derived-output filenames are frozen.
    print("All configured derived tables were found.")
    print("Add the final table-to-figure calls here after freezing the output schema.")


if __name__ == "__main__":
    main()
