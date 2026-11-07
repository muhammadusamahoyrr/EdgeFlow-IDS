"""Per-class live and offline test-flow counts and F1 for every detection run (review round 6).

Reads only logged results: results/live/<run>/live_vs_offline.json (per-class precision, recall,
F1, support; offline = the same windows' flows from the offline pcap export) and, where present,
results/live/<run>/flow_match.md (flow-by-flow match counts).

Runs: run1, run1_r2, run1_r3 (no CPU limit, ten windows), edge50, edge50_r2, edge50_r3 (half a
core, three windows), edge100 (one core, ten windows).

Fragility: for the small attack classes (support <= 25, true positives > 0), true positives TP,
false negatives FN and false positives FP are recovered from the rounded recall and precision
(TP = round(recall * support), FN = support - TP, FP = round(TP / precision) - TP), and the
macro-F1 change is computed for one more flow of the class detected (TP+1, same FP) and for one
detected flow missed (TP-1, FN+1). Macro-F1 averages over the classes present in that run's json.

Usage: python src/analysis/perclass_counts.py
Output: results/live/perclass_counts.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import pandas as pd  # noqa: E402

from config import RESULTS  # noqa: E402

RUNS = [("run1", "no limit"), ("run1_r2", "no limit"), ("run1_r3", "no limit"),
        ("edge50", "half core"), ("edge50_r2", "half core"), ("edge50_r3", "half core"),
        ("edge100", "one core")]


def f1(tp, fp, fn):
    d = 2 * tp + fp + fn
    return 2 * tp / d if d else 0.0


def main():
    count_rows, f1_rows, frag_rows, match_lines = [], [], [], []
    for tag, quota in RUNS:
        j = json.loads((RESULTS / "live" / tag / "live_vs_offline.json").read_text())
        for side in ("offline", "live"):
            pc = j[side]["per_class"]
            base = {"run": tag, "CPU": quota, "side": side, "flows": f"{j[side]['flows']:,}",
                    "macro-F1": round(j[side]["macro_f1"], 4)}
            count_rows.append({**base, **{c: v["support"] for c, v in pc.items()}})
            f1_rows.append({**base, **{c: v["f1"] for c, v in pc.items()}})
            k = len(pc)
            for c, v in pc.items():
                n = v["support"]
                tp = round(v["recall"] * n)
                if n > 25 or tp == 0:
                    continue
                fp = round(tp / v["precision"]) - tp
                fn = n - tp
                base_f1 = f1(tp, fp, fn)
                frag_rows.append({"run": tag, "side": side, "class": c, "support": n, "TP": tp, "FN": fn, "FP": fp,
                                  "F1 (json)": v["f1"], "F1 (recomputed)": round(base_f1, 3),
                                  "classes in macro": k,
                                  "macro change, +1 detected": round((f1(tp + 1, fp, fn) - base_f1) / k, 4),
                                  "macro change, 1 detected missed": round((f1(tp - 1, fp, fn + 1) - base_f1) / k, 4)})
        fm = RESULTS / "live" / tag / "flow_match.md"
        if fm.exists():
            match_lines.append(f"{tag}: " + next(line for line in fm.read_text().splitlines()
                                                  if line.startswith("Matched")))
    counts = pd.DataFrame(count_rows)
    f1s = pd.DataFrame(f1_rows)
    md = ["# Per-class live and offline flow counts and F1, every detection run", "",
          "Source: results/live/<run>/live_vs_offline.json. Offline = the same windows exported offline from the "
          "pcaps. No-limit and one-core runs: ten windows (eight classes); half-core runs: three windows "
          "(DDoS-SYN, DoS-HTTP, Mirai; four classes).", "",
          "## Test-flow counts per class", "", counts.to_markdown(index=False), "",
          "## Per-class F1", "", f1s.to_markdown(index=False), "",
          "## Fragility of the small classes (derived from rounded precision/recall; see docstring)", "",
          pd.DataFrame(frag_rows).to_markdown(index=False), "",
          "## Flow-by-flow match (where logged)", ""] + match_lines
    live = counts[counts.side == "live"]
    md += ["", "Range of live Mirai flows over all runs: "
           f"{int(live.Mirai.min())}--{int(live.Mirai.max())}; MITM-ARP (ten-window runs): "
           f"{int(live['MITM-ARP'].min())}--{int(live['MITM-ARP'].max())}; Web: "
           f"{int(live.Web.min())}--{int(live.Web.max())}; BruteForce: "
           f"{int(live.BruteForce.min())}--{int(live.BruteForce.max())}."]
    (RESULTS / "live" / "perclass_counts.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
