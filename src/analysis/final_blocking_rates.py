"""False blocks per hour of replayed traffic and distinct benign hosts affected (final review M5 / A6).

Same definitions as blocking_accounting.py / block_curve.py: flows of a window = eval_live.in_window,
labels = extract_flows.label_flows + data/attackers.json, a block is false if the blocked host pair
has no attack flow in that window; enforced runs: trigger flow = blocked_now == 1; run-1 simulation:
block_curve.simulate per window (counts reset per window) for every k.

Exposure: (a) capture time replayed = sum over windows of (end_epoch - start_epoch) (60 s each);
(b) wall-clock replay time = sum of (replay_end_ms - replay_start_ms). False blocks per hour use both.
Distinct hosts: IPs that are an end of a falsely blocked pair, (1) all, (2) excluding the window's
listed attackers and victims ("uninvolved benign hosts"); counted per window and summed (a host in two
windows counts twice, the windows are separate captures), and as unique IPs over the run.

Also re-checks the blocking-policy selection rule of tune_block_policy.py on validation with
UNROUNDED coverage (share of attack flows after block): whether every policy lies within the 0.005
tolerance of the best (if so, the rule reduces to "fewest false blocks", i.e. the largest k).

Usage: python src/analysis/final_blocking_rates.py
Output: results/final/blocking_rates.md
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analysis.block_curve import KS, simulate  # noqa: E402
from analysis.blocking_accounting import ATTACKERS, windows  # noqa: E402
from config import RESULTS  # noqa: E402

OUT = RESULTS / "final"


def exposure(tag):
    meta = json.loads((RESULTS / "live" / tag / "windows.json").read_text())
    cap = sum(w["end_epoch"] - w["start_epoch"] for w in meta["windows"]) / 3600
    wall = sum(w["replay_end_ms"] - w["replay_start_ms"] for w in meta["windows"]) / 3.6e6
    return cap, wall, len(meta["windows"])


def summarise(label, per_window, cap_h, wall_h):
    """per_window: list of (folder, false_pairs set, eligible benign pairs)."""
    n_false = sum(len(f) for _, f, _ in per_window)
    elig = sum(e for _, _, e in per_window)
    hosts_w, hosts_u, unin_w, unin_u = 0, set(), 0, set()
    for folder, fp, _ in per_window:
        info = ATTACKERS.get(folder, {})
        roles = set(info.get("attackers", [])) | set(info.get("victims", []))
        h = {x for p in fp for x in p}
        hosts_w += len(h)
        hosts_u |= h
        unin_w += len(h - roles)
        unin_u |= (h - roles)
    return {"run / policy": label, "false blocks": n_false, "eligible benign pair-windows": elig,
            "per eligible pair": round(n_false / elig, 4) if elig else None,
            "per hour of capture time": round(n_false / cap_h, 1),
            "per hour of wall-clock replay": round(n_false / wall_h, 1),
            "distinct hosts (sum over windows / unique IPs)": f"{hosts_w} / {len(hosts_u)}",
            "distinct hosts excl. window's attackers+victims (sum / unique)": f"{unin_w} / {len(unin_u)}",
            "windows with >= 1 false block": sum(1 for _, f, _ in per_window if f)}


def policy_check():
    from sklearn.tree import DecisionTreeClassifier

    from config import EDGE_TREE, PROCESSED, feature_columns
    from nsga_select import inner_split
    from train_baseline import temporal_split
    from tune_block_policy import KS as VKS

    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, _ = temporal_split(df)
    feats = feature_columns(train)
    fit, val = inner_split(train)
    model = DecisionTreeClassifier(**EDGE_TREE).fit(fit[feats].to_numpy(np.float32), fit["label"])
    val = val.assign(pred=model.predict(val[feats].to_numpy(np.float32)),
                     pair=[(f,) + tuple(sorted(p)) for f, p in zip(val.source_file, zip(val.src_ip, val.dst_ip))])
    val = val.sort_values(["source_file", "bidirectional_last_seen_ms"])
    att = val[val.label != "Benign"]
    attack_pairs = set(att.pair)
    benign_only = set(val.pair) - attack_pairs
    rows = []
    for ig in (False, True):
        for k in VKS:
            counts, blocked = {}, {}
            for pair, pred, t in zip(val.pair, val.pred, val.bidirectional_last_seen_ms):
                if pred == "Benign" or (ig and pred == "MITM-ARP") or pair in blocked:
                    continue
                counts[pair] = counts.get(pair, 0) + 1
                if counts[pair] >= k:
                    blocked[pair] = t
            after = np.array([p in blocked and s > blocked[p] for p, s in zip(att.pair, att.bidirectional_first_seen_ms)])
            # per-class pair coverage (not used by the rule; shows what it ignores)
            pc = att.groupby("pair").label.first()
            cov = {c: f"{sum(p in blocked for p in g.index)}/{len(g)}" for c, g in pc.groupby(pc)}
            rows.append({"k": k, "ignore MITM-ARP": ig, "attack flows after block (unrounded)": float(after.mean()),
                         "false blocks": len(benign_only & set(blocked)),
                         "attack pairs blocked": f"{len(attack_pairs & set(blocked))}/{len(attack_pairs)}",
                         "attack pairs blocked by class": ", ".join(f"{c} {v}" for c, v in cov.items())})
    t = pd.DataFrame(rows)
    best = t["attack flows after block (unrounded)"].max()
    t["gap to best"] = best - t["attack flows after block (unrounded)"]
    t["within 0.005"] = t["gap to best"] <= 0.005
    ok = t[t["within 0.005"]]
    pick = ok.sort_values(["false blocks", "k"]).iloc[0]
    t["attack flows after block (unrounded)"] = t["attack flows after block (unrounded)"].map(lambda v: f"{v:.6f}")
    t["gap to best"] = t["gap to best"].map(lambda v: f"{v:.6f}")
    return t, pick, bool(t["within 0.005"].all())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows, exp_rows = [], []
    for tag in ("enforce_k1", "enforce_policy"):
        cap_h, wall_h, nw = exposure(tag)
        exp_rows.append({"run": tag, "windows": nw, "capture time (min)": round(cap_h * 60, 2),
                         "wall-clock replay (min)": round(wall_h * 60, 2)})
        pw = []
        for folder, d in windows(tag):
            att_pairs = set(d[d.label != "Benign"].pair)
            blocked = set(d[d.blocked_now == 1].pair)
            pw.append((folder, blocked - att_pairs, len(set(d.pair) - att_pairs)))
        rows.append(summarise(f"{tag} (enforced)", pw, cap_h, wall_h))
        print(rows[-1], flush=True)
    cap_h, wall_h, nw = exposure("run1")
    exp_rows.append({"run": "run1", "windows": nw, "capture time (min)": round(cap_h * 60, 2),
                     "wall-clock replay (min)": round(wall_h * 60, 2)})
    ws = windows("run1")
    for ignore in (False, True):
        for k in KS:
            pw = []
            for folder, d in ws:
                att_pairs = set(d[d.label != "Benign"].pair)
                blocked = simulate(d, k, ignore)
                pw.append((folder, set(blocked) - att_pairs, len(set(d.pair) - att_pairs)))
            rows.append(summarise(f"run1 simulation, k={k}{', MITM-ARP ignored' if ignore else ''}", pw, cap_h, wall_h))
            print(rows[-1], flush=True)
    t, pick, all_ok = policy_check()
    md = ["# False blocks per hour and distinct benign hosts (final review M5)", "",
          "Script: src/analysis/final_blocking_rates.py. Definitions as in src/analysis/blocking_accounting.py. "
          "Per-hour rates extrapolate from about 10 minutes of traffic (ten 60 s windows) and inherit the per-window "
          "reset of block counters; they are exposure-normalised counts, not a measured hourly rate.", "",
          "## Exposure", "", pd.DataFrame(exp_rows).to_markdown(index=False), "",
          "## False blocks", "", pd.DataFrame(rows).to_markdown(index=False), "",
          "Distinct hosts: IPs at either end of a falsely blocked pair. 'Sum over windows' counts an IP once per window "
          "(each window is a separate capture); 'unique' counts each IP once over the run (the captures share one "
          "lab subnet, so the same IP may be a different device in different captures).", "",
          "## Blocking-policy selection rule on validation (tune_block_policy.py), unrounded", "",
          t.to_markdown(index=False), "",
          f"Every policy within 0.005 of the best coverage: **{'yes' if all_ok else 'NO'}**. "
          f"The rule therefore picks the fewest false blocks: k={int(pick.k)}, ignore MITM-ARP={bool(pick['ignore MITM-ARP'])} "
          "(the largest k in the grid [1, 2, 3, 5, 10])."]
    (OUT / "blocking_rates.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
