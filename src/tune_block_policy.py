"""Choose the blocking policy on VALIDATION data (never on the live test windows).

Simulates the gateway's verdict stream on the validation period (last 20% of each pcap's training
flows; tree fit on the first 80%), in flow-end order. Policy: block a host pair once it has
collected k attack verdicts, optionally ignoring MITM-ARP flow verdicts (flow statistics cannot
see ARP spoofing; the ARP watcher covers it).

Per policy: attack pairs blocked (share of pairs that carry attack flows), false blocks (pairs with
only benign flows that got blocked), and the share of attack flows that start after their pair
was blocked (traffic the block would stop). Rule: fewest false blocks among policies whose share
of attack flows arriving after the block is within 0.005 of the best policy. (Blocking a pair only
helps against traffic that comes after the block; one- or two-flow attacks such as a single SQL
injection request are over before any block, so "number of attack pairs blocked" is the wrong
target. An earlier version used ">= 90% of the attack pairs blocked by k=1"; both are in the table.)

Usage: python src/tune_block_policy.py
Output: results/block_policy.md, results/block_policy.json (read by gateway.py)
"""
import json

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from config import EDGE_TREE, PROCESSED, RESULTS, feature_columns
from nsga_select import inner_split
from train_baseline import temporal_split

KS = [1, 2, 3, 5, 10]


def simulate(df, k, ignore_mitm):
    df = df.sort_values("bidirectional_last_seen_ms")
    counts, blocked_at = {}, {}
    for pair, pred, t in zip(df.pair, df.pred, df.bidirectional_last_seen_ms):
        if pred == "Benign" or (ignore_mitm and pred == "MITM-ARP") or pair in blocked_at:
            continue
        counts[pair] = counts.get(pair, 0) + 1
        if counts[pair] >= k:
            blocked_at[pair] = t
    attack_pairs = set(df[df.label != "Benign"].pair)
    benign_only = set(df.pair) - attack_pairs
    att = df[df.label != "Benign"]
    after = [p in blocked_at and s > blocked_at[p] for p, s in zip(att.pair, att.bidirectional_first_seen_ms)]
    return {"k": k, "ignore_mitm_flow_verdicts": ignore_mitm,
            "attack_pairs": len(attack_pairs),
            "attack_pairs_blocked": len(attack_pairs & set(blocked_at)),
            "false_blocks": len(benign_only & set(blocked_at)),
            "attack_flows_after_block": round(float(np.mean(after)), 3) if len(after) else None}


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet")
    train, _ = temporal_split(df)
    feats = feature_columns(train)
    fit, val = inner_split(train)
    model = DecisionTreeClassifier(**EDGE_TREE).fit(fit[feats].to_numpy(np.float32), fit["label"])
    val = val.assign(pred=model.predict(val[feats].to_numpy(np.float32)),
                     pair=[tuple(sorted(p)) for p in zip(val.src_ip, val.dst_ip)])
    rows = [simulate(val, k, ig) for ig in (False, True) for k in KS]
    t = pd.DataFrame(rows)
    ok = t[t.attack_flows_after_block >= t.attack_flows_after_block.max() - 0.005]
    best = ok.sort_values(["false_blocks", "k"]).iloc[0]
    policy = {"min_attack_verdicts": int(best.k),
              "ignore_mitm_flow_verdicts": bool(best.ignore_mitm_flow_verdicts)}
    (RESULTS / "block_policy.json").write_text(json.dumps(policy, indent=2))
    md = ["# Blocking policy tuning (validation = last 20% of the training period)", "",
          t.to_markdown(index=False), "", f"Chosen: `{policy}`"]
    (RESULTS / "block_policy.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
