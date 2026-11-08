#!/usr/bin/env python3
"""Figure 10. Coordination-path latency by scenario and configuration.

Values are those of Table 6.  The figure is drawn at the print size
(5.03 x 4.30 in) with a dot-and-range encoding so that mean, p95 and p99 can
be read at 100 % scale.

The measure ends at the commit acknowledgment and excludes ledger block
finality (Sections 5.2 and 6.2).
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

DATA = [
    ("License verification", [
        ("Native", 385.2, 412.7, 468.3, "#4472C4"),
        ("DSAL", 470.1, 498.6, 563.2, "#ED7D31"),
        ("Cacti/WeCross", 425.3, 456.8, 521.4, "#A5A5A5"),
    ]),
    ("Enterprise qualification", [
        ("Native", 892.4, 945.1, 1023.7, "#4472C4"),
        ("DSAL", 977.6, 1032.4, 1128.5, "#ED7D31"),
        ("Cacti/WeCross", 935.8, 991.2, 1075.3, "#A5A5A5"),
    ]),
    ("Real estate registration", [
        ("Native", 1245.3, 1312.8, 1425.6, "#4472C4"),
        ("DSAL", 1358.7, 1432.5, 1567.2, "#ED7D31"),
        ("Cacti/WeCross", 1298.4, 1367.2, 1489.3, "#A5A5A5"),
    ]),
]

fig, ax = plt.subplots(figsize=(5.03, 4.30))
fig.subplots_adjust(left=0.30, right=0.97, top=0.86, bottom=0.14)

y = 0
yticks, ylabels, group_marks = [], [], []
for group, rows in DATA:
    group_marks.append((y, group))
    for name, mean, p95, p99, color in rows:
        ax.plot([mean, p99], [y, y], color=color, linewidth=1.4, alpha=0.55,
                solid_capstyle="round", zorder=1)
        ax.plot([p95], [y], marker="|", markersize=6, markeredgewidth=1.0,
                color=color, zorder=2)
        ax.plot([mean], [y], marker="o", markersize=4.2, color=color,
                markeredgecolor="black", markeredgewidth=0.4, zorder=3)
        ax.text(p99 + 22, y, f"{mean:,.1f}", va="center", fontsize=5.2,
                color="#111827")
        yticks.append(y)
        ylabels.append(name)
        y += 1
    y += 1.6

ax.set_yticks(yticks)
ax.set_yticklabels(ylabels, fontsize=5.6)
ax.set_ylim(-1.0, y - 0.9)
ax.invert_yaxis()
ax.set_xlim(300, 1720)
ax.set_xlabel("Coordination-path latency (ms)", fontsize=6.4)
ax.tick_params(axis="x", labelsize=5.6)
ax.grid(axis="x", alpha=0.35, linestyle=":", linewidth=0.5)
ax.set_axisbelow(True)
for spine in ("top", "right", "left"):
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_linewidth(0.8)
ax.tick_params(axis="y", length=0)

for ypos, label in group_marks:
    ax.text(310, ypos - 0.78, label, ha="left", va="center", fontsize=6.0,
            fontweight="bold", color="#111827")

ax.plot([], [], "o", color="#666666", markersize=4.2, label="mean")
ax.plot([], [], "|", color="#666666", markersize=6, label="p95")
ax.plot([], [], "-", color="#666666", linewidth=1.4, alpha=0.55,
        label="mean-p99")
ax.legend(loc="lower right", frameon=False, fontsize=5.4, ncol=3,
          handlelength=1.4, columnspacing=1.0, borderpad=0.2)

ax.set_title("Fixed-workload coordination-path latency\n"
             "(segments run from the mean to p99; ledger finality excluded)",
             fontsize=7.4, pad=4)

plt.savefig("fig10_latency.png", dpi=400)
plt.savefig("fig10_latency.pdf")
print("saved fig10_latency.png")
