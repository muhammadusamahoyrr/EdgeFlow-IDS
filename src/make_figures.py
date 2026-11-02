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


SHORT = {"Benign": "Benign", "BruteForce": "BruteF", "DDoS-SYN": "DDoS", "DoS-HTTP": "DoS-HTTP",
         "MITM-ARP": "MITM", "Mirai": "Mirai", "Recon": "Recon", "Web": "Web",
         "Benign_Final": "Benign", "CommandInjection": "CmdInj", "DDoS-SYN_Flood": "DDoS",
         "DictionaryBruteForce": "BruteF", "DoS-HTTP_Flood": "DoS-HTTP", "MITM-ArpSpoofing": "MITM",
         "Mirai-udpplain": "Mirai", "Recon-PortScan": "Recon", "SqlInjection": "SQLi", "XSS": "XSS"}
# Paper figures are placed at \columnwidth (about 3.5 in), so sizes below are true print sizes.
COL_W = 3.5
plt.rcParams.update({"font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 8,
                     "ytick.labelsize": 8, "legend.fontsize": 8})


def split_recall():
    t = json.loads((RESULTS / "baseline_temporal" / "metrics.json").read_text())["models"]["decision_tree"]
    s = json.loads((RESULTS / "baseline_stratified" / "metrics.json").read_text())["models"]["decision_tree"]
    classes = list(t["per_class"])
    x = np.arange(len(classes))
    fig, ax = plt.subplots(figsize=(COL_W, 2.3))
    ax.bar(x - 0.2, [s["per_class"][c]["recall"] for c in classes], 0.4, color=GREY,
           label=f"random (macro-F1 {s['macro_f1']:.3f})")
    ax.bar(x + 0.2, [t["per_class"][c]["recall"] for c in classes], 0.4, color=BLUE,
           label=f"temporal (macro-F1 {t['macro_f1']:.3f})")
    ax.set_xticks(x, [SHORT.get(c, c) for c in classes], rotation=35, ha="right", rotation_mode="anchor")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("recall")
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, frameon=False,
              handlelength=1.2, columnspacing=1.0, borderaxespad=0.2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "split_recall.png", dpi=300)


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
    fig, ax = plt.subplots(figsize=(COL_W, 2.4))
    width = 0.28
    for i, (tag, label, color) in enumerate(runs):
        vals = [data.get(tag, {}).get(w) for w in windows]
        ax.bar(x + (i - 1) * width, [v if v is not None else 0 for v in vals], width, color=color, label=label)
    ax.axhline(15, color="black", lw=0.8, ls="--")
    ax.set_xticks(x, [SHORT.get(w, w) for w in windows], rotation=45, ha="right", rotation_mode="anchor")
    ax.set_xlim(-0.6, len(windows) - 0.4)
    ax.set_ylabel("median delay after\nflow end (s)")
    ax.legend(loc="upper right", frameon=False, handlelength=1.2)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "live_delay.png", dpi=300)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    split_recall()
    nsga_pareto()
    live_delay()
    print(f"figures in {OUT}")
