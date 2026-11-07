"""Late blocks: separate window length from export delay (reviewer round 17, item 1).

Validation (tune_block_policy.py) scores whole capture periods with each verdict stamped at flow
end and gives 0.995 of attack flows starting after their pair is blocked; the run-1 simulation
(block_curve.py) uses 60 s windows and the logged live verdict times and gives 0.111. Here the same
blocking rule is replayed on the SAME run-1 windows and flows, changing only the verdict time:

  (a) flow end            bidirectional_last_seen_ms (the validation stamping)
  (b) flow end + 15 s     the idle timeout, i.e. the earliest an idle flow can be exported
  (c) live verdict time   verdict_ms as logged by the gateway (block_curve.py)

Policy: k verdicts per host pair, MITM-ARP verdicts ignored or not, counts reset per window.
Metric: share of attack flows (flow start) after their pair's block, pooled over the ten windows,
and the same share within the DDoS-SYN and DoS-HTTP windows.

Usage: python src/analysis/block_timing.py [--tag run1]
Output: results/final/block_timing.md
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import pandas as pd  # noqa: E402

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RESULTS  # noqa: E402
from eval_live import in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402

KS = [1, 3, 10]
TIMINGS = [("(a) flow end", "end"), ("(b) flow end + 15 s", "end15"), ("(c) live verdict time", "live")]


def blocks(d, tcol, k, ignore):
    votes, at = {}, {}
    for pair, pred, t in zip(d.pair, d.pred, d[tcol]):
        if pair in at or pred == "Benign" or (ignore and pred == "MITM-ARP"):
            continue
        votes[pair] = votes.get(pair, 0) + 1
        if votes[pair] >= k:
            at[pair] = t
    return at


def main(tag):
    run = RESULTS / "live" / tag
    meta = json.loads((run / "windows.json").read_text())
    attackers = json.loads(ATTACKERS_FILE.read_text())
    live = pd.read_csv(run / "flows.csv")
    wins = []
    for w in meta["windows"]:
        d = label_flows(in_window(live, w).copy(), FOLDER_TO_CLASS[w["folder"]], attackers.get(w["folder"], {}))
        d["pair"] = [tuple(sorted(p)) for p in zip(d.src_ip, d.dst_ip)]
        d["end"] = d.bidirectional_last_seen_ms
        d["end15"] = d.bidirectional_last_seen_ms + 15000
        d["live"] = d.verdict_ms
        wins.append((w["folder"], d))
    rows = []
    for ignore in (False, True):
        for k in KS:
            for tname, tcol in TIMINGS:
                after = total = 0
                sub = {}
                for folder, d in wins:
                    d = d.sort_values(tcol)
                    at = blocks(d, tcol, k, ignore)
                    att = d[d.label != "Benign"]
                    hit = sum(1 for p, s in zip(att.pair, att.bidirectional_first_seen_ms) if p in at and s > at[p])
                    after += hit
                    total += len(att)
                    if folder in ("DDoS-SYN_Flood", "DoS-HTTP_Flood"):
                        sub[folder] = round(hit / len(att), 3) if len(att) else None
                rows.append({"k": k, "MITM-ARP verdicts": "ignored" if ignore else "counted", "verdict time": tname,
                             "attack flows after block (pooled)": round(after / total, 4),
                             "DDoS-SYN window": sub.get("DDoS-SYN_Flood"), "DoS-HTTP window": sub.get("DoS-HTTP_Flood"),
                             "attack flows": total})
                print(rows[-1], flush=True)
    md = ["# Late blocks: window length vs export delay (round 17)", "",
          f"Script: src/analysis/block_timing.py, run {tag}, ten 60 s windows, counts reset per window. "
          "Validation (whole capture periods, flow-end stamps): 0.995 (results/final/blocking_rates.md).", "",
          pd.DataFrame(rows).to_markdown(index=False)]
    (RESULTS / "final" / "block_timing.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="run1")
    main(ap.parse_args().tag)
