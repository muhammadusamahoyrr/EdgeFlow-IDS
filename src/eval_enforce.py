"""Mitigation results of an --enforce live run.

For every host pair the gateway blocked: was the flow that triggered the block an attack flow
(by the attackers.json rules) or a false block? How many packets did the pair's two OVS drop
rules stop (n_packets from ovs-ofctl dump-flows)? How many packets did the window offer in total?

Usage: python src/eval_enforce.py --tag enforce
Output: results/live/<tag>/enforcement.md
"""
import argparse
import json
import re

import pandas as pd

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RESULTS
from extract_flows import label_flows


def main(tag):
    run = RESULTS / "live" / tag
    attackers = json.loads(ATTACKERS_FILE.read_text())
    meta = json.loads((run / "windows.json").read_text())
    live = pd.read_csv(run / "flows.csv")
    trig = live[live.blocked_now == 1]

    parts = []
    for w in meta["windows"]:
        part = trig[(trig.bidirectional_first_seen_ms >= w["replay_start_ms"] - 1000)
                    & (trig.bidirectional_first_seen_ms <= w["replay_end_ms"] + 1000)].copy()
        if len(part):
            part = label_flows(part, FOLDER_TO_CLASS[w["folder"]], attackers.get(w["folder"], {}))
            parts.append(part.assign(window=w["folder"], window_packets=w["packets"]))
    if not parts:
        print("no blocks recorded")
        return
    trig = pd.concat(parts)

    drops = {}
    for line in (run / "ovs_flows.txt").read_text().splitlines():
        m = re.search(r"n_packets=(\d+).*priority=100,ip,nw_src=([\d.]+),nw_dst=([\d.]+)", line)
        if m:
            pair = tuple(sorted((m.group(2), m.group(3))))
            drops[pair] = drops.get(pair, 0) + int(m.group(1))
    trig["pair"] = [tuple(sorted(p)) for p in zip(trig.src_ip, trig.dst_ip)]
    trig["dropped_packets"] = [drops.get(p, 0) for p in trig.pair]
    trig["correct_block"] = trig.label != "Benign"
    trig["block_after_flow_start_s"] = (trig.verdict_ms - trig.bidirectional_first_seen_ms) / 1000

    by_win = trig.groupby("window").agg(
        blocked_pairs=("pair", "size"), correct=("correct_block", "sum"),
        dropped_packets=("dropped_packets", "sum"), window_packets=("window_packets", "first"),
        median_block_after_flow_start_s=("block_after_flow_start_s", "median"))
    by_win["dropped_share_of_window"] = (by_win.dropped_packets / by_win.window_packets).round(3)
    md = [f"# Enforcement results ({tag})", "",
          f"Blocked host pairs: {len(trig)} · correct (attack) {int(trig.correct_block.sum())} · "
          f"false blocks {int((~trig.correct_block).sum())}",
          f"Packets dropped by the gateway's rules: {int(trig.dropped_packets.sum()):,}",
          "A pair is blocked only after its first flow has ended and been classified "
          "(idle timeout 15 s), so short attacks finish before the block.", "",
          by_win.to_markdown(), "", "False blocks (benign pairs):", "",
          trig[~trig.correct_block][["window", "src_ip", "dst_ip", "dst_port", "pred",
                                     "dropped_packets"]].to_markdown(index=False)]
    (run / "enforcement.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    main(ap.parse_args().tag)
