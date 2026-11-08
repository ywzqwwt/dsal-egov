#!/usr/bin/env python3
"""Figure 6. Two-stage concept-mapping pipeline, drawn at final print size.

Stage 1 retrieves the K = 10 platform concepts that are closest to the source
description under static embeddings.  Stage 2 encodes the source description and
each retained candidate with a shared Bi-LSTM and scores the pairs.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 5.4,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

W, H = 5.03, 2.30
fig, ax = plt.subplots(figsize=(W, H))
fig.subplots_adjust(left=0.0, right=1.0, top=0.86, bottom=0.02)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def box(x, y, w, h, title, body, color, size=4.9):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.4,rounding_size=1.0",
                                facecolor=color, edgecolor="#1F2937", linewidth=0.7))
    ax.text(x + w / 2, y + h - 4.2, title, ha="center", va="center",
            fontsize=5.6, fontweight="bold")
    ax.text(x + w / 2, y + h / 2 - 3.0, body, ha="center", va="center",
            fontsize=size, linespacing=1.35)


def arrow(x1, x2, y):
    ax.add_patch(FancyArrowPatch((x1, y), (x2, y), arrowstyle="-|>",
                                 mutation_scale=7, linewidth=0.8, color="#374151"))


y, h = 42, 26
box(1, y, 15, h, "Source", "DSAL concept\ndescription", "#DBEAFE")
box(19, y, 20, h, "Stage 1", "static-embedding\ncosine similarity\nkeep K = 10", "#D1FAE5")
box(42, y, 18, h, "Stage 2a", "shared Bi-LSTM\n64 units per direction\nmasked mean pooling", "#EDE9FE")
box(63, y, 18, h, "Stage 2b", "pair features\nMLP + softmax\nover K candidates", "#FCE7F3")
box(84, y, 15, h, "Output", "mapped\nplatform term", "#FEF3C7")

for x1, x2 in [(16.4, 18.6), (39.4, 41.6), (60.4, 62.6), (81.4, 83.6)]:
    arrow(x1, x2, y + h / 2)

ax.text(50, 24,
        "Stage 1 bounds recall; Stage 2 can only rerank what Stage 1 retains.",
        ha="center", fontsize=4.8, color="#4B5563")
ax.text(50, 15,
        "Gold labels in the released benchmark are exact by construction.",
        ha="center", fontsize=4.8, color="#4B5563")

fig.text(0.5, 0.955, "Two-stage concept-mapping pipeline",
         ha="center", fontsize=7.6, fontweight="bold", color="#111827")

plt.savefig("fig6_pipeline.png", dpi=400)
plt.savefig("fig6_pipeline.pdf")
print("saved fig6_pipeline.png")
