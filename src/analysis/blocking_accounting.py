"""Blocking evaluation, full accounting (reviewer request; no new experiments).

(a) Every false block of the enforced k=1 run (results/live/enforce_k1), by the triggering
    verdict class and by whether a host of the pair is that window's attacker/victim.
(b) Per-window denominators: host pairs seen in the window, attacker pairs, benign pairs (no
    attack flow in the window = eligible to be falsely blocked), benign pairs with >= 1 attack
    verdict, false blocks; for the two enforced runs and the run-1 simulation.
(c) The run-1 k-curve (block_curve.py logic) with one column per attack class, so the attacker
    pairs add up to the 26 in the paper table; and the per-class split of the enforced runs.
(d) One-core (edge100) live macro-F1 0.810 vs 0.804: per-class decomposition from the logged
    live_vs_offline.json files, against the spread of the repeated runs.

Definitions as in round2_checks.py / block_curve.py: flows in a window = eval_live.in_window,
labels = extract_flows.label_flows with data/attackers.json; a block is false if the blocked
pair has no attack flow in that window.

Usage: python src/analysis/blocking_accounting.py
Output: results/blocking_accounting.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import pandas as pd  # noqa: E402

from analysis.block_curve import KS, simulate  # noqa: E402
from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RESULTS  # noqa: E402
from eval_live import in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402

ATTACKERS = json.loads(ATTACKERS_FILE.read_text())
ATTACK_CLASSES = ["BruteForce", "DDoS-SYN", "DoS-HTTP", "MITM-ARP", "Mirai", "Recon", "Web"]


def windows(tag):
    run = RESULTS / "live" / tag
    meta = json.loads((run / "windows.json").read_text())
    live = pd.read_csv(run / "flows.csv")
    out = []
    for w in meta["windows"]:
        d = label_flows(in_window(live, w).copy(), FOLDER_TO_CLASS[w["folder"]], ATTACKERS.get(w["folder"], {}))
        d["pair"] = [tuple(sorted(p)) for p in zip(d.src_ip, d.dst_ip)]
        out.append((w["folder"], d.sort_values("verdict_ms")))
    return out


def role_hosts(folder):
    info = ATTACKERS.get(folder, {})
    return set(info.get("attackers", [])), set(info.get("victims", []))


def denominators(d, blocked_pairs):
    att_pairs = set(d[d.label != "Benign"].pair)
    pairs = set(d.pair)
    benign_pairs = pairs - att_pairs
    flagged = set(d[(d.pred != "Benign")].pair) - att_pairs
    flagged_nm = set(d[(d.pred != "Benign") & (d.pred != "MITM-ARP")].pair) - att_pairs
    false = set(blocked_pairs) - att_pairs
    nb = d[d.label == "Benign"]
    return {"host pairs": len(pairs), "attacker pairs": len(att_pairs), "benign pairs (eligible)": len(benign_pairs),
            "benign pairs with >=1 attack verdict": len(flagged),
            "same, MITM-ARP verdicts ignored": len(flagged_nm),
            "pairs blocked": len(blocked_pairs), "false blocks": len(false),
            "false-block rate (per eligible pair)": round(len(false) / len(benign_pairs), 4) if benign_pairs else None,
            "benign flows": len(nb), "benign flows with attack verdict": int((nb.pred != "Benign").sum())}


def enforced(tag):
    """Per-window denominators and per-false-block detail of an enforced run."""
    den, detail, cls_rows = [], [], {}
    for folder, d in windows(tag):
        trig = d[d.blocked_now == 1]
        blocked = list(trig.pair)
        den.append({"window": folder, **denominators(d, blocked)})
        att = d[d.label != "Benign"]
        att_pairs = set(att.pair)
        pair_cls = att.groupby("pair").label.first().to_dict()
        for p in att_pairs:
            t, h = cls_rows.get(pair_cls[p], (0, 0))
            cls_rows[pair_cls[p]] = (t + 1, h + (p in set(blocked)))
        attackers, victims = role_hosts(folder)
        for _, r in trig.iterrows():
            if r.pair in att_pairs:
                continue
            hosts = set(r.pair)
            if hosts & attackers:
                role = "attacker host, non-attack traffic"
            elif hosts & victims:
                role = "victim host, non-attack traffic"
            else:
                role = "uninvolved benign hosts"
            pb = d[d.pair == r.pair]
            detail.append({"window": folder, "pair": f"{r.pair[0]} - {r.pair[1]}", "trigger verdict": r.pred,
                           "trigger dst_port": int(r.dst_port), "protocol": int(r.protocol),
                           "role": role, "pair flows in window": len(pb),
                           "pair flows with attack verdict": int((pb.pred != "Benign").sum())})
    return pd.DataFrame(den), pd.DataFrame(detail), cls_rows


def run1_curve(tag="run1"):
    ws = windows(tag)
    rows, den = [], []
    for ignore in (False, True):
        for k in KS:
            per_class, n_blocked, n_false, n_att = {}, 0, 0, 0
            false_by_pred = {}
            for folder, d in ws:
                blocked = simulate(d, k, ignore)
                att = d[d.label != "Benign"]
                att_pairs = set(att.pair)
                pair_cls = att.groupby("pair").label.first().to_dict()
                n_blocked += len(blocked)
                fp = set(blocked) - att_pairs
                n_false += len(fp)
                n_att += len(att_pairs)
                # trigger verdict of each false block = the k-th counted attack verdict of the pair
                for p in fp:
                    t = blocked[p]
                    pred = d[(d.pair == p) & (d.verdict_ms == t) & (d.pred != "Benign")].pred.iloc[-1]
                    false_by_pred[pred] = false_by_pred.get(pred, 0) + 1
                for p in att_pairs:
                    t_, h = per_class.get(pair_cls[p], (0, 0))
                    per_class[pair_cls[p]] = (t_ + 1, h + (p in blocked))
                if k == 1:
                    den.append({"ignore MITM-ARP": ignore, "window": folder, **denominators(d, list(blocked))})
            hit = sum(h for _, h in per_class.values())
            rows.append({"k": k, "MITM-ARP ignored": ignore, "blocked": n_blocked, "false": n_false,
                         "attackers": f"{hit}/{n_att}",
                         **{c: f"{per_class.get(c, (0, 0))[1]}/{per_class.get(c, (0, 0))[0]}" for c in ATTACK_CLASSES},
                         "false blocks by trigger verdict": ", ".join(f"{c} {n}" for c, n in sorted(false_by_pred.items()))})
            print(rows[-1])
    return pd.DataFrame(rows), pd.DataFrame(den)


def one_core():
    rows = []
    for tag in ("run1", "run1_r2", "run1_r3", "edge100", "edge50", "edge50_r2", "edge50_r3"):
        j = json.loads((RESULTS / "live" / tag / "live_vs_offline.json").read_text())
        r = {"run": tag, "CPU quota": j.get("cpu_quota"), "windows": len(j["windows"]),
             "offline macro-F1": round(j["offline"]["macro_f1"], 4), "live macro-F1": round(j["live"]["macro_f1"], 4)}
        for c, v in j["live"]["per_class"].items():
            r[f"{c} F1 (n)"] = f"{v['f1']} ({v['support']})"
        rows.append(r)
    t = pd.DataFrame(rows)
    a = json.loads((RESULTS / "live" / "run1" / "live_vs_offline.json").read_text())["live"]["per_class"]
    b = json.loads((RESULTS / "live" / "edge100" / "live_vs_offline.json").read_text())["live"]["per_class"]
    k = len(a)
    dec = pd.DataFrame([{"class": c, "run1 live F1 (n)": f"{a[c]['f1']} ({a[c]['support']})",
                         "edge100 live F1 (n)": f"{b[c]['f1']} ({b[c]['support']})",
                         "contribution to macro-F1 difference": round((b[c]["f1"] - a[c]["f1"]) / k, 4)}
                        for c in a])
    return t, dec


def main():
    md = ["# Blocking evaluation: full accounting", "",
          "Definitions as in src/analysis/round2_checks.py and block_curve.py: a block is false if the blocked "
          "host pair has no attack flow in that window (labels: extract_flows.label_flows + data/attackers.json; "
          "window flows: eval_live.in_window). Enforced runs: the trigger flow is the one with blocked_now = 1.", ""]
    for tag in ("enforce_k1", "enforce_policy"):
        den, det, cls_rows = enforced(tag)
        tot = den.drop(columns="window").sum(numeric_only=True)
        md += [f"## Enforced run {tag}", "",
               "### (b) Per-window denominators", "", den.to_markdown(index=False), "",
               f"Totals: {int(tot['host pairs']):,} host-pair-windows, {int(tot['attacker pairs'])} attacker pairs, "
               f"{int(tot['benign pairs (eligible)']):,} benign pairs eligible to be falsely blocked, "
               f"{int(tot['benign pairs with >=1 attack verdict'])} of them with >= 1 attack verdict, "
               f"{int(tot['false blocks'])} false blocks "
               f"({tot['false blocks'] / tot['benign pairs (eligible)']:.4f} per eligible pair; "
               f"{tot['benign flows with attack verdict'] / tot['benign flows']:.4f} of {int(tot['benign flows']):,} "
               "benign flows got an attack verdict).", "",
               "Attacker pairs blocked by class: " + ", ".join(f"{c} {h}/{t}" for c, (t, h) in sorted(cls_rows.items()))
               + f" (total {sum(h for _, h in cls_rows.values())}/{sum(t for t, _ in cls_rows.values())}).", ""]
        if len(det):
            md += ["### (a) False blocks by trigger verdict and host role", "",
                   pd.crosstab(det["trigger verdict"], det.role, margins=True, margins_name="total").to_markdown(), "",
                   "By window and trigger verdict:", "",
                   pd.crosstab(det.window, det["trigger verdict"], margins=True, margins_name="total").to_markdown(), "",
                   "All false blocks:", "", det.to_markdown(index=False), ""]
    curve, den1 = run1_curve()
    md += ["## (c) Run-1 k-curve (simulated per window), all attack classes", "",
           "Columns per class: attacker pairs blocked / attacker pairs in the windows. The class columns sum to "
           "the Attackers column.", "", curve.to_markdown(index=False), "",
           "### (b) Run-1 per-window denominators at k = 1", "", den1.to_markdown(index=False), ""]
    t, dec = one_core()
    md += ["## (d) One-core run (edge100) macro-F1 0.810 vs 0.804", "",
           "Live per-class F1 (support) of every detection run (from results/live/<run>/live_vs_offline.json):", "",
           t.to_markdown(index=False), "", "Decomposition of edge100 minus run1 (live, same ten windows):", "",
           dec.to_markdown(index=False), "",
           f"Sum of contributions: {dec['contribution to macro-F1 difference'].sum():+.4f} "
           "(per-class F1 rounded to 3 decimals in the json)."]
    (RESULTS / "blocking_accounting.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
