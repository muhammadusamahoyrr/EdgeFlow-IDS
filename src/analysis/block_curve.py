"""Blocking-policy trade-off on the live verdict stream (paper revision, reviewer item M5).

Replays the policy logic of gateway.py offline on the verdicts that the live detection run
logged (results/live/<tag>/flows.csv), per window (blocks and counts reset per window, as in the
final harness), for k in KS and with/without counting MITM-ARP flow verdicts. This is the
test-period counterpart of tune_block_policy.py (which works on validation data); it is used only
to describe the trade-off, not to choose the policy.

Per policy: pairs blocked, attacker pairs blocked (by class), false blocks (pairs with no attack
flow in that window), share of attack flows that start after their pair was blocked, and the
median time from a pair's first flow to its block.

Usage: python src/analysis/block_curve.py --tag run1
Output: results/live/<tag>/block_curve.md
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RESULTS  # noqa: E402
from eval_live import in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402

KS = [1, 2, 3, 5, 10, 20]


def simulate(df, k, ignore_mitm):
    """df: one window's flows with pair, pred, label, verdict_ms, first_seen. Returns dict."""
    votes, blocked_at = {}, {}
    for pair, pred, t in zip(df.pair, df.pred, df.verdict_ms):
        if pair in blocked_at or pred == "Benign" or (ignore_mitm and pred == "MITM-ARP"):
            continue
        votes[pair] = votes.get(pair, 0) + 1
        if votes[pair] >= k:
            blocked_at[pair] = t
    return blocked_at


def main(tag):
    run = RESULTS / "live" / tag
    meta = json.loads((run / "windows.json").read_text())
    attackers = json.loads(ATTACKERS_FILE.read_text())
    live = pd.read_csv(run / "flows.csv")
    windows = []
    for w in meta["windows"]:
        d = label_flows(in_window(live, w).copy(), FOLDER_TO_CLASS[w["folder"]], attackers.get(w["folder"], {}))
        d["pair"] = [tuple(sorted(p)) for p in zip(d.src_ip, d.dst_ip)]
        windows.append((w["folder"], d.sort_values("verdict_ms")))

    rows = []
    for ignore in (False, True):
        for k in KS:
            n_blocked = n_false = n_att_pairs = n_att_blocked = 0
            after, total_att, delays, per_class = 0, 0, [], {}
            for folder, d in windows:
                blocked = simulate(d, k, ignore)
                att = d[d.label != "Benign"]
                att_pairs = set(att.pair)
                pair_cls = att.groupby("pair").label.first().to_dict()
                first = d.groupby("pair").bidirectional_first_seen_ms.min()
                n_blocked += len(blocked)
                n_false += len(set(blocked) - att_pairs)
                n_att_pairs += len(att_pairs)
                n_att_blocked += len(att_pairs & set(blocked))
                for p in att_pairs:
                    c = pair_cls[p]
                    tot, hit = per_class.get(c, (0, 0))
                    per_class[c] = (tot + 1, hit + (p in blocked))
                total_att += len(att)
                after += sum(1 for p, s in zip(att.pair, att.bidirectional_first_seen_ms)
                             if p in blocked and s > blocked[p])
                delays += [(t - first[p]) / 1000 for p, t in blocked.items() if p in att_pairs]
            rows.append({
                "k": k, "ignore MITM-ARP verdicts": ignore, "pairs blocked": n_blocked,
                "false blocks": n_false, "attacker pairs blocked": f"{n_att_blocked}/{n_att_pairs}",
                "attack flows after block": round(after / total_att, 3) if total_att else None,
                "median time to block (s)": round(float(np.median(delays)), 1) if delays else None,
                "attacker pairs blocked by class": ", ".join(f"{c} {h}/{t}" for c, (t, h) in sorted(per_class.items())),
            })
            print({k2: v for k2, v in rows[-1].items() if k2 != "attacker pairs blocked by class"})
    md = [f"# Blocking-policy trade-off on the live verdict stream ({tag})", "",
          "Simulated per window from the logged verdicts; describes the trade-off only (the policy "
          "itself was chosen on validation data, results/block_policy.md).", "",
          pd.DataFrame(rows).to_markdown(index=False)]
    (run / "block_curve.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="run1")
    main(ap.parse_args().tag)
