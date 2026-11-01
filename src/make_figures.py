"""Figures for the README, built only from files in results/.

  docs/figures/split_recall.png   per-class recall, temporal vs stratified split (decision tree)
  docs/figures/nsga_pareto.png    NSGA-II subsets: features vs macro-F1 (validation and test)
  docs/figures/live_delay.png     verdict delay after flow end per window: no limit, 1 core, 1/2 core

Usage: python src/make_figures.py
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from config import ROOT, RESULTS  # noqa: E402

OUT = ROOT / "docs" / "figures"
BLUE, ORANGE, GREY, GREEN = "#2563eb", "#ea580c", "#6b7280", "#16a34a"


def split_recall():
    t = json.loads((RESULTS / "baseline_temporal" / "metrics.json").read_text())["models"]["decision_tree"]
    s = json.loads((RESULTS / "baseline_stratified" / "metrics.json").read_text())["models"]["decision_tree"]
    classes = list(t["per_class"])
    x = np.arange(len(classes))
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.bar(x - 0.2, [s["per_class"][c]["recall"] for c in classes], 0.4, color=GREY,
           label=f"stratified random split (macro-F1 {s['macro_f1']:.3f})")
    ax.bar(x + 0.2, [t["per_class"][c]["recall"] for c in classes], 0.4, color=BLUE,
           label=f"temporal split (macro-F1 {t['macro_f1']:.3f})")
    for i, c in enumerate(classes):
        ax.text(i + 0.2, 1.02, f"n={int(t['per_class'][c]['support']):,}", ha="center", fontsize=7, color=BLUE)
    ax.set_xticks(x, classes, fontsize=9)
    ax.set_ylim(0, 1.12)
    ax.set_ylabel("recall")
    ax.set_title("Decision tree recall per class: a random split hides the brute-force shift", fontsize=10)
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.1), ncol=2, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "split_recall.png", dpi=160)


def nsga_pareto():
    p = pd.read_csv(RESULTS / "nsga" / "pareto.csv")
    pick = (RESULTS / "nsga" / "edge_pick.txt").read_text().strip()
    sub = p[p.subset != "all_features"]
    full = p[p.subset == "all_features"].iloc[0]
    chosen = p[p.features == pick].iloc[0]
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.scatter(sub.n_features, sub.val_macro_f1_capped_fit, s=18, color=GREY, label="Pareto subsets: validation F1")
    ax.scatter(sub.n_features, sub.test_macro_f1, s=18, color=BLUE, marker="x", label="same subsets: test F1")
    ax.scatter([full.n_features], [full.test_macro_f1], s=70, color=ORANGE, label=f"all {full.n_features} features: test F1")
    ax.scatter([chosen.n_features], [chosen.test_macro_f1], s=110, facecolors="none", edgecolors=GREEN,
               linewidths=2, label=f"edge pick ({chosen.n_features} features, chosen on validation)")
    ax.set_xlabel("number of features")
    ax.set_ylabel("macro-F1")
    ax.set_title("NSGA-II feature selection (decision tree)", fontsize=10)
    ax.legend(fontsize=7, loc="lower right")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "nsga_pareto.png", dpi=160)


def live_delay():
    runs = [("run1", "no CPU limit", GREY), ("edge100", "1 core", BLUE), ("edge50", "1/2 core", ORANGE)]
    data = {}
    for tag, _, _ in runs:
        f = RESULTS / "live" / tag / "live_vs_offline.json"
        if f.exists():
            data[tag] = {w["window"]: w["median_verdict_after_flow_end_s"]
                         for w in json.loads(f.read_text())["windows"]}
    windows = list(data.get("run1", {}))
    x = np.arange(len(windows))
    fig, ax = plt.subplots(figsize=(10, 3.8))
    width = 0.27
    for i, (tag, label, color) in enumerate(runs):
        vals = [data.get(tag, {}).get(w) for w in windows]
        ax.bar(x + (i - 1) * width, [v if v is not None else 0 for v in vals], width, color=color, label=label)
    ax.axhline(15, color="black", lw=0.8, ls="--")
    ax.text(len(windows) - 0.5, 16, "idle timeout 15 s", fontsize=8, ha="right")
    ax.set_xticks(x, [w.replace("_", " ").replace("-", "-\n", 1) for w in windows], fontsize=7)
    ax.set_ylabel("median verdict after flow end (s)")
    ax.set_title("Live gateway: verdict delay per window and CPU budget (1/2 core: 3 heaviest windows only)", fontsize=10)
    ax.legend(fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "live_delay.png", dpi=160)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    split_recall()
    nsga_pareto()
    live_delay()
    print(f"figures in {OUT}")
