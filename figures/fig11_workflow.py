#!/usr/bin/env python3
"""Figure 11. Cross-department approval: before and after DSAL, as a process view.

Shows the structure of the cross-department approval workflow before and after
DSAL adoption.  Timing is not plotted: the figure makes no timing claim and
defers to the latency measurements of Section 6.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

W, H = 5.03, 2.55
fig, ax = plt.subplots(figsize=(W, H))
fig.subplots_adjust(left=0.0, right=1.0, top=0.86, bottom=0.02)
ax.set_xlim(0, 100)
ax.set_ylim(33, 99)
ax.axis("off")


def node(x, y, w, h, text, color, size=5.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.4,rounding_size=1.0",
                                facecolor=color, edgecolor="#1F2937", linewidth=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size)


def arrow(x1, y1, x2, y2, style="-|>"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style,
                                 mutation_scale=6, linewidth=0.7, color="#374151"))


# ---------------- before ----------------
ax.text(2, 92, "(a) Before: point-to-point integration", fontsize=6.6,
        fontweight="bold", va="center")

before_y, bh = 76, 10
node(2, before_y, 13, bh, "Agency\napplication", "#F3F4F6")
node(19, before_y, 15, bh, "Custom Fabric\nadapter", "#FCE7F3")
node(39, before_y, 15, bh, "Manual field\nreconciliation", "#FEE2E2")
node(59, before_y, 15, bh, "Custom BCOS\nadapter", "#FCE7F3")
node(79, before_y, 15, bh, "Manual audit\ntrail", "#FEE2E2")
for x in (15, 34, 54, 74):
    arrow(x + 0.6, before_y + bh / 2, x + 3.8, before_y + bh / 2)
ax.text(2, 71.5, "two bespoke adapters, a manual reconciliation step and a separate audit record",
        fontsize=5.2, color="#4B5563")

# ---------------- after ----------------
ax.text(2, 60, "(b) After: DSAL mediation", fontsize=6.6,
        fontweight="bold", va="center")

after_y, ah = 42, 10
node(2, after_y, 13, ah, "Agency\napplication", "#F3F4F6")
node(19, after_y, 15, ah, "DSAL standard\ninterface", "#DBEAFE")
node(38, after_y, 15, ah, "Concept\nmapping", "#FEF3C7")
node(57, after_y, 15, ah, "Rule\ntranslation", "#FEF3C7")
node(76, after_y, 18, ah, "2PC coordination\nFabric + BCOS", "#D1FAE5")
for x in (15, 34, 53, 72):
    arrow(x + 0.6, after_y + ah / 2, x + 3.8, after_y + ah / 2)

ax.text(2, 37.0, "one interface; the platform artifacts are generated from the same flow definition",
        fontsize=5.2, color="#4B5563")

fig.text(0.5, 0.945, "Cross-department approval workflow: before and after DSAL",
         ha="center", fontsize=7.6, fontweight="bold", color="#111827")

plt.savefig("fig11_workflow.png", dpi=400)
plt.savefig("fig11_workflow.pdf")
print("saved fig11_workflow.png")
