#!/usr/bin/env python3
"""Figure 9. Throughput at the fixed Real Estate Registration workload point.

Values are those reported in Section 6.3: mean TPS over five runs per
configuration, with 95% t-based confidence intervals (t = 2.776, df = 4).
The intervals overlap, which is why the text does not claim a significant
difference between the native implementation and DSAL at this workload point.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

DATA = [("Native", 98.4, 8.1, "#4472C4"),
        ("DSAL", 89.7, 8.8, "#ED7D31"),
        ("Cacti/WeCross", 94.1, 7.8, "#A5A5A5")]

fig, ax = plt.subplots(figsize=(5.03, 2.95))
fig.subplots_adjust(left=0.13, right=0.97, top=0.83, bottom=0.16)

x = np.arange(len(DATA))
for i, (name, m, ci, color) in enumerate(DATA):
    ax.bar(i, m, width=0.52, color=color, edgecolor="black", linewidth=0.6,
           yerr=ci, capsize=4, error_kw=dict(elinewidth=0.9, capthick=0.9,
                                             ecolor="#1F2937"))
    ax.text(i, m + ci + 1.6, f"{m:.1f}", ha="center", va="bottom", fontsize=6.4)

ax.set_xticks(x)
ax.set_xticklabels([d[0] for d in DATA], fontsize=6.6)
ax.set_ylabel("Throughput (TPS)", fontsize=6.8)
ax.set_ylim(0, 125)
ax.grid(axis="y", alpha=0.3, linestyle=":", linewidth=0.5)
ax.set_axisbelow(True)
for spine in ("top", "right"):
    ax.spines[spine].set_visible(False)
ax.tick_params(axis="y", labelsize=6.0)

ax.set_title("Real Estate Registration: mean throughput over five runs\n"
             "(error bars = 95% t-based confidence interval)",
             fontsize=7.4, pad=5)

plt.savefig("fig9_tps.png", dpi=400)
plt.savefig("fig9_tps.pdf")
print("saved fig9_tps.png")
