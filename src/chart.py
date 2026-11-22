"""Scatter of each sign's rate on unicorn seals vs other-animal seals. Writes figures/signs_vs_animal.png."""
import json
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from corpus import seals_with_animal, ROOT

d = seals_with_animal()
signs = sorted({s for q in d.seq for s in q})
X = np.array([[int(s in set(q)) for s in signs] for q in d.seq]); y = d.unicorn.values
fu, fo = X[y == 1].mean(0) * 100, X[y == 0].mean(0) * 100
keep = X.sum(0) >= 8
res = json.load(open(ROOT / "results" / "icon_test.json"))
auc = res["A_unicorn_vs_other"]["auc"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
fig, ax = plt.subplots(figsize=(7.2, 7.4), dpi=200)
fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
m = max(fu[keep].max(), fo[keep].max()) * 1.08
ax.plot([0, m], [0, m], color="#b9b8b2", lw=1.2, ls="--", zorder=1)
ax.text(m * 0.62, m * 0.66, "same rate on both", rotation=45, color="#52514e", fontsize=10, ha="center")
ax.scatter(fu[keep], fo[keep], s=46, color="#2a78d6", edgecolor="#fcfcfb", lw=1.5, zorder=3, alpha=0.9)
for j in np.where(keep)[0]:
    if max(fu[j], fo[j]) > 12:
        ax.annotate(f"sign {signs[j]}", (fu[j], fo[j]), xytext=(6, -4), textcoords="offset points", fontsize=9, color="#52514e")
ax.set_xlim(0, m); ax.set_ylim(0, m); ax.set_aspect("equal")
ax.set_xlabel(f"% of unicorn seals with the sign (n={int((y == 1).sum())})", color="#52514e")
ax.set_ylabel(f"% of other-animal seals with the sign (n={int((y == 0).sum())})", color="#52514e")
ax.grid(color="#e6e5e0", lw=0.8); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
for s in ["left", "bottom"]: ax.spines[s].set_color("#b9b8b2")
ax.tick_params(colors="#52514e")
ax.set_title("Indus seals: the writing doesn't depend\non the animal carved below it", loc="left", fontsize=14, fontweight="bold", color="#0b0b0b")
fig.text(0.01, 0.01, f"Each dot is one sign used on 8+ seals ({int(keep.sum())} signs). Koskenniemi & Parpola 1979 corpus, {len(y)} seals\n"
         f"after removing duplicates. Held-out AUC for guessing unicorn vs other from the text: {auc:.2f} (chance 0.50).", fontsize=8, color="#52514e")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(ROOT / "figures" / "signs_vs_animal.png", facecolor=fig.get_facecolor())
print("wrote figures/signs_vs_animal.png")
