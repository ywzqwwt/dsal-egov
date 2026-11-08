#!/usr/bin/env python3
"""Figure 3. Three-layer DSAL architecture, drawn at final print size.

Canvas = 5.03 x 4.30 in (text-column
width), so type is reproduced at the designed size.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6,
                     "pdf.fonttype": 42, "ps.fonttype": 42})

W, H = 5.03, 4.30
fig, ax = plt.subplots(figsize=(W, H))
fig.subplots_adjust(left=0.0, right=1.0, top=0.94, bottom=0.0)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")


def band(y0, h, title, subtitle, color):
    ax.add_patch(FancyBboxPatch((3.0, y0), 94, h,
                                boxstyle="round,pad=0.4,rounding_size=1.2",
                                facecolor=color, edgecolor="#1F2937", linewidth=0.8))
    ax.text(5.0, y0 + h - 3.4, title, fontsize=7.2, fontweight="bold", va="center")
    ax.text(95.0, y0 + h - 3.4, subtitle, fontsize=5.6, color="#374151",
            ha="right", va="center")


def chip(x, y, w, h, text, size=5.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.3,rounding_size=0.8",
                                facecolor="white", edgecolor="#374151", linewidth=0.7))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size)


ax.add_patch(FancyBboxPatch((3.0, 86.5), 94, 8.0,
                            boxstyle="round,pad=0.4,rounding_size=1.2",
                            facecolor="#F3F4F6", edgecolor="#1F2937", linewidth=0.8))
ax.text(50, 90.5, "E-government applications",
        ha="center", va="center", fontsize=7.0, fontweight="bold")
ax.text(50, 87.9, "commerce \u00b7 taxation \u00b7 property registration",
        ha="center", va="center", fontsize=5.6, color="#374151")

band(69.0, 13.5, "Standard Interface Layer", "platform-agnostic API", "#DBEAFE")
for i, api in enumerate(["createIsolationDomain()", "deployBusinessFlow()",
                         "invokeCrossDomainTransaction()"]):
    chip(5.5 + i * 30.5, 71.5, 28.5, 6.0, api, 5.0)

band(48.0, 16.5, "Adaptation Logic Layer", "translation and enforcement", "#FEF3C7")
for i, comp in enumerate(["Concept Mapping\nEngine", "Business Logic\nTranslator",
                          "Security and\nCompliance Module"]):
    chip(5.5 + i * 30.5, 50.5, 28.5, 8.5, comp, 5.4)

band(27.0, 16.5, "Domain Concept Layer", "shared vocabulary", "#D1FAE5")
for i, comp in enumerate(["Organization", "Isolation Domain", "Business Flow",
                          "Permission Policy"]):
    chip(5.0 + i * 23.3, 29.5, 21.3, 6.5, comp, 5.2)

ax.add_patch(FancyBboxPatch((3.0, 4.0), 94, 17.0,
                            boxstyle="round,pad=0.4,rounding_size=1.2",
                            facecolor="#F3F4F6", edgecolor="#1F2937", linewidth=0.8))
ax.text(26, 12.5, "Hyperledger Fabric v2.4", ha="center", va="center",
        fontsize=6.8, fontweight="bold")
ax.text(74, 12.5, "FISCO BCOS v3.0", ha="center", va="center",
        fontsize=6.8, fontweight="bold")
ax.text(50, 17.6, "platform adapters", ha="center", va="center",
        fontsize=5.2, color="#4B5563",
        bbox=dict(facecolor="#F3F4F6", edgecolor="none", pad=1.2))

fig.text(0.5, 0.965, "Three-layer architecture of the DSAL prototype",
         ha="center", fontsize=8.6, fontweight="bold", color="#111827")

plt.savefig("fig3_architecture.png", dpi=400)
plt.savefig("fig3_architecture.pdf")
print("saved fig3_architecture.png")
