"""Figures for the README, built only from files in results/.

  docs/figures/split_recall.png   per-class recall, temporal vs stratified split (decision tree)
  docs/figures/nsga_pareto.png    NSGA-II subsets: features vs macro-F1 (validation and test)
  docs/figures/live_delay.png     verdict delay after flow end per window: no limit, 1 core, 1/2 core
  docs/figures/late_blocks.png    attack flows starting after their pair's block: flow-end vs export-delayed verdicts
  docs/figures/gap_units.png      random-minus-temporal macro-F1 gap with 95% CI per bootstrap cluster unit

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
    # The deployed (edge) tree, the model the paper reports throughout.
    t = json.loads((RESULTS / "baseline_temporal" / "metrics.json").read_text())["models"]["decision_tree_edge"]
    s = json.loads((RESULTS / "baseline_stratified" / "metrics.json").read_text())["models"]["decision_tree_edge"]
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


def read_md_table(path):
    """Parse the first pipe table in a results markdown file into a DataFrame of strings."""
    rows = [ln.strip().strip("|").split("|") for ln in path.read_text().splitlines()
            if ln.strip().startswith("|")]
    head, body = [c.strip() for c in rows[0]], rows[2:]
    return pd.DataFrame([[c.strip() for c in r] for r in body], columns=head)


def late_blocks():
    """Share of attack flows that start after their host pair is blocked (k = 1, MITM-ARP verdicts
    ignored), with each verdict stamped at flow end (as an offline evaluation does) or 15 s later
    (the idle timeout, i.e. when a live gateway exports the flow)."""
    w = read_md_table(RESULTS / "final" / "block_timing.md")
    w = w[(w["k"] == "1") & (w["MITM-ARP verdicts"] == "ignored")].set_index("verdict time")
    col = "attack flows after block (pooled)"
    rows = [("All, 60 s live windows", float(w.loc["(a) flow end", col]),
             float(w.loc["(b) flow end + 15 s", col]))]
    lg = read_md_table(RESULTS / "final" / "block_timing_long.md")
    lg = lg[(lg["k"] == "1") & (lg["MITM-ARP verdicts"] == "ignored") & (lg["horizon"] == "persistent")]
    lg = lg.set_index("verdict time")
    for label, c in [("All, 5.9 h test periods", "attack flows after block"), ("DDoS-SYN", "DDoS-SYN"),
                     ("BruteForce", "BruteForce"), ("Recon", "Recon"), ("DoS-HTTP", "DoS-HTTP"), ("Web", "Web")]:
        rows.append((label, float(lg.loc["(a) flow end", c]), float(lg.loc["(b) flow end + 15 s", c])))
    y = np.arange(len(rows))[::-1].astype(float)
    y[1:] -= 0.5  # gap between the live-window row and the 5.9 h rows
    fig, ax = plt.subplots(figsize=(COL_W, 2.4))
    for yi, (_, a, b) in zip(y, rows):
        ax.plot([b, a], [yi, yi], color=GREY, lw=1.2, zorder=1)
    ax.scatter([r[1] for r in rows], y, s=26, facecolors="white", edgecolors=GREY, linewidths=1.4, zorder=2,
               label="verdict at flow end (offline)")
    ax.scatter([r[2] for r in rows], y, s=26, color=BLUE, edgecolors="white", linewidths=0.6, zorder=3,
               label="verdict at flow end + 15 s (live export)")
    for yi, (_, a, b) in zip(y, rows):
        ax.text(b, yi + 0.22, f"{100 * b:.0f}%", ha="center", va="bottom", fontsize=7, color="#374151")
    ax.set_yticks(y, [r[0] for r in rows])
    ax.set_xlim(0, 1.02)
    ax.set_ylim(y.min() - 0.5, y.max() + 0.9)  # room for the value label above the top row
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0], ["0", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("attack flows that start after their block")
    ax.grid(axis="x", color="#e5e7eb", lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.4, 1.0), ncol=1, frameon=False, handletextpad=0.3,
              borderaxespad=0.1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "late_blocks.png", dpi=300)
    fig.savefig(OUT / "late_blocks.pdf")


def ci(text):
    lo, hi = text.strip("[]").split(",")
    return float(lo), float(hi)


def gap_units():
    """Paired bootstrap of random minus temporal macro-F1 (deployed tree; classes present in the
    resample), all classes and without BruteForce, for each cluster unit."""
    t = read_md_table(RESULTS / "final" / "gap_nobf_units.md")
    units = ["host pair", "attacker host", "attacker device", "capture"]
    series = [("all 8 classes", "all classes", BLUE, "o", 0.17),
              ("without BruteForce (7)", "without BruteForce", ORANGE, "s", -0.17)]
    fig, ax = plt.subplots(figsize=(COL_W, 1.85))
    y = np.arange(len(units))[::-1].astype(float)
    for key, label, color, marker, dy in series:
        rows = t[t["classes"] == key].set_index("clusters").loc[units]
        diff = rows["difference"].astype(float).to_numpy()
        lo, hi = zip(*[ci(c) for c in rows["paired CI, present"]])
        ax.errorbar(diff, y + dy, xerr=[diff - np.array(lo), np.array(hi) - diff], fmt=marker,
                    color=color, ms=4.5, elinewidth=1.4, capsize=2.5, label=label)
    ax.axvline(0, color="black", lw=0.8, ls="--")
    ax.set_yticks(y, units)
    ax.set_ylim(y.min() - 0.6, y.max() + 0.6)
    ax.set_xlabel("random minus temporal macro-F1 (95% CI)")
    ax.grid(axis="x", color="#e5e7eb", lw=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0)
    ax.legend(loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=2, frameon=False,
              handletextpad=0.3, columnspacing=1.2, borderaxespad=0.1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    fig.tight_layout(pad=0.3)
    fig.savefig(OUT / "gap_units.png", dpi=300)
    fig.savefig(OUT / "gap_units.pdf")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    split_recall()
    nsga_pareto()
    live_delay()
    late_blocks()
    gap_units()
    print(f"figures in {OUT}")
