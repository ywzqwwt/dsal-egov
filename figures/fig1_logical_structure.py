#!/usr/bin/env python3
"""Figure 1. Logical organization of the paper, drawn at final print size.

The canvas is 5.03 x 3.90 in, i.e. the width of the
manuscript's text column, so the type is reproduced at the designed size.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

W, H = 5.03, 3.90
fig, ax = plt.subplots(figsize=(W, H))
fig.subplots_adjust(left=0, right=1, top=0.90, bottom=0.03)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

STAGES = [
    ("1", "Problem framing", "Sec. 1-3",
     "agency-level ledger fragmentation  \u00b7  requirements  \u00b7  gap"),
    ("2", "Design", "Sec. 4",
     "domain conceptual model  \u00b7  mapping  \u00b7  rule translation"),
    ("3", "Implementation and bounded check", "Sec. 5",
     "prototype  \u00b7  coordination protocol  \u00b7  TLA+ model"),
    ("4", "Evaluation", "Sec. 6",
     "three scenarios  \u00b7  effort, latency, consistency"),
    ("5", "Interpretation", "Sec. 7-8",
     "scope of the evidence  \u00b7  limitations  \u00b7  outlook"),
]

COLORS = ["#DBEAFE", "#E0E7FF", "#FEF3C7", "#D1FAE5", "#F3F4F6"]
top, height, gap = 86.0, 12.0, 6.0

for i, ((num, title, sec, detail), color) in enumerate(zip(STAGES, COLORS)):
    y = top - i * (height + gap)
    ax.add_patch(FancyBboxPatch((13, y - height), 85, height,
                                boxstyle="round,pad=0.3,rounding_size=1.4",
                                facecolor=color, edgecolor="#1F2937", linewidth=0.8))
    ax.add_patch(plt.Circle((8.0, y - height / 2), 3.4, facecolor="white",
                            edgecolor="#1F2937", linewidth=0.8, zorder=3))
    ax.text(8.0, y - height / 2, num, ha="center", va="center",
            fontsize=7.5, fontweight="bold", zorder=4)
    ax.text(14.5, y - 4.0, title, fontsize=7.4, fontweight="bold", va="center")
    ax.text(97.0, y - 4.0, sec, fontsize=6.2, color="#4B5563",
            ha="right", va="center")
    ax.text(14.5, y - 8.8, detail, fontsize=6.1, color="#111827", va="center")
    if i < len(STAGES) - 1:
        ax.add_patch(FancyArrowPatch((8.0, y - height - 0.6),
                                     (8.0, y - height - gap + 0.6),
                                     arrowstyle="-|>", mutation_scale=7,
                                     linewidth=0.8, color="#374151"))

fig.text(0.5, 0.955, "Logical organization of the paper", ha="center",
         fontsize=9, fontweight="bold", color="#111827")
fig.text(0.5, 0.012,
         "Each stage states the claim the reader should carry forward.",
         ha="center", fontsize=6.0, color="#4B5563")

plt.savefig("fig1_logical_structure.png", dpi=400)
plt.savefig("fig1_logical_structure.pdf")
print("saved fig1_logical_structure.png")
