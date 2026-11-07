"""Flow-by-flow live/offline match on EVERY live run (final review M6 / B4).

Logic of analysis/match_live_offline.py (5-tuple + order of appearance within the window, training
connections still running after the boundary dropped on both sides, labels from label_flows), applied
to every results/live/<run>/ that has flows.csv and windows.json. Offline flows are re-extracted once
per window pcap with the current (patched) NFStream and the run's model; live verdicts are the ones
the gateway logged (flows.csv 'pred').

Per run and window: offline / live flows, match rate (matched / offline), live-only, identical packet
and byte counts among matched flows, verdict agreement, live/offline flow-count ratio, achieved replay
pps (tcpreplay), original pps (window packets / span of the window's packets, from the offline flows'
first/last packet), and replay rate as a share of the original.

Caveats: enforced runs (enforce_k1, enforce_policy, test_reset) drop packets of blocked pairs, so
packet/byte counts and flow counts are expected to differ after a block; bugcheck_unpatched ran the
unpatched NFStream live (the defect changes export timing, not flow content).

Does not write into results/live/ (the per-run flow_match.md of run1 is left untouched).

Usage: python src/analysis/final_fidelity.py
Output: results/final/fidelity_all_runs.md
"""
import json
import pathlib
import pickle
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from nfstream import NFStreamer  # noqa: E402

from analysis.match_live_offline import KEY, with_occurrence  # noqa: E402
from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RAW, RESULTS, STREAMER_KW  # noqa: E402
from eval_live import drop_continuing, in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402

OUT = RESULTS / "final"
ATT = json.loads(ATTACKERS_FILE.read_text())
_cache = {}


def load_model(meta):
    p = pathlib.Path(meta["model"])
    if not p.exists():
        p = RESULTS / "models" / p.name
    with open(p, "rb") as f:  # trusted: produced locally by train_edge_model.py
        return p.name, pickle.load(f)


def offline(w, mname, bundle):
    key = (w["pcap"], mname)
    if key not in _cache:
        raw = NFStreamer(source=str(RAW / "live" / w["pcap"]), **STREAMER_KW).to_pandas()
        span_s = (raw.bidirectional_last_seen_ms.max() - raw.bidirectional_first_seen_ms.min()) / 1000
        keys = bundle.get("continuing_connections", {}).get(w["source_file"], [])
        off, _ = drop_continuing(raw, keys)
        off = label_flows(off.copy(), FOLDER_TO_CLASS[w["folder"]], ATT.get(w["folder"], {}))
        off["pred"] = bundle["model"].predict(off[bundle["features"]].to_numpy(np.float32))
        _cache[key] = (with_occurrence(off), span_s)
    return _cache[key]


def sent(w):
    m = re.search(r"Actual: (\d+) packets \((\d+) bytes\) sent in ([\d.]+) seconds", w.get("tcpreplay", ""))
    return (int(m.group(1)), float(m.group(3))) if m else (None, None)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    runs = sorted(p.parent.name for p in (RESULTS / "live").glob("*/flows.csv")
                  if (p.parent / "windows.json").exists())
    all_rows, run_rows = [], []
    for tag in runs:
        meta = json.loads((RESULTS / "live" / tag / "windows.json").read_text())
        mname, bundle = load_model(meta)
        live_all = pd.read_csv(RESULTS / "live" / tag / "flows.csv")
        rows = []
        for w in meta["windows"]:
            off, span_s = offline(w, mname, bundle)
            keys = bundle.get("continuing_connections", {}).get(w["source_file"], [])
            lv, _ = drop_continuing(in_window(live_all, w), keys)
            lv = with_occurrence(label_flows(lv.copy(), FOLDER_TO_CLASS[w["folder"]], ATT.get(w["folder"], {})))
            m = off.merge(lv, on=KEY + ["occ"], how="outer", suffixes=("_off", "_live"), indicator=True)
            both = m[m["_merge"] == "both"]
            n_pk, secs = sent(w)
            orig_pps = w["packets"] / span_s if span_s > 0 else None
            rep_pps = w.get("offered_pps")
            r = {"run": tag, "window": w["folder"], "offline flows": len(off), "live flows": len(lv),
                 "matched": len(both), "match rate": round(len(both) / len(off), 4) if len(off) else None,
                 "live only": int((m["_merge"] == "right_only").sum()),
                 "same packets": round(float((both.bidirectional_packets_off == both.bidirectional_packets_live).mean()), 4) if len(both) else None,
                 "same bytes": round(float((both.bidirectional_bytes_off == both.bidirectional_bytes_live).mean()), 4) if len(both) else None,
                 "same verdict": round(float((both.pred_off == both.pred_live).mean()), 4) if len(both) else None,
                 "live/offline flows": round(len(lv) / len(off), 4) if len(off) else None,
                 "replay pps": rep_pps, "original pps": round(orig_pps, 1) if orig_pps else None,
                 "replay / original rate": round(rep_pps / orig_pps, 3) if (rep_pps and orig_pps) else None,
                 "replay s / original span s": f"{secs} / {span_s:.1f}" if secs else None}
            rows.append(r)
            print(r, flush=True)
        t = pd.DataFrame(rows)
        all_rows += rows
        tot = t[["offline flows", "live flows", "matched", "live only"]].sum()
        both_w = t["matched"]
        run_rows.append({"run": tag, "enforce": meta.get("enforce"), "CPU quota": meta.get("cpu_quota"),
                         "model": mname, "windows": len(t),
                         "offline / live flows": f"{int(tot['offline flows']):,} / {int(tot['live flows']):,}",
                         "matched": f"{int(tot['matched']):,}",
                         "match rate": round(tot["matched"] / tot["offline flows"], 4),
                         "live only": int(tot["live only"]),
                         "same packets (flow-weighted)": round(float((t["same packets"] * both_w).sum() / both_w.sum()), 4),
                         "same verdict (flow-weighted)": round(float((t["same verdict"] * both_w).sum() / both_w.sum()), 4),
                         "min same verdict over windows": t["same verdict"].min(),
                         "live/offline flows": round(tot["live flows"] / tot["offline flows"], 4)})
    allt = pd.DataFrame(all_rows)
    dd = allt[allt.window.isin(["DDoS-SYN_Flood", "DoS-HTTP_Flood", "Mirai-udpplain"])][
        ["run", "window", "replay pps", "original pps", "replay / original rate", "live/offline flows",
         "match rate", "same packets", "same verdict"]].sort_values(["window", "replay / original rate"])
    corr = {}
    enforced = {r["run"] for r in run_rows if r["enforce"]}
    for wname, g in dd[~dd.run.isin(enforced)].groupby("window"):
        g = g.dropna(subset=["replay / original rate", "live/offline flows"])
        if len(g) > 2:
            corr[wname] = round(float(np.corrcoef(g["replay / original rate"], g["live/offline flows"])[0, 1]), 3)
    md = ["# Live/offline flow-by-flow fidelity on every live run (final review M6)", "",
          "Script: src/analysis/final_fidelity.py (logic of src/analysis/match_live_offline.py). Match = same "
          "5-tuple and same order of appearance within the window; match rate = matched / offline flows. Offline: "
          "patched NFStream on data/raw/live/<window pcap>, verdicts of the run's model; live: flows.csv as logged "
          "(verdict = the gateway's 'pred'). Replay pps = tcpreplay's achieved rate (windows.json); original pps = "
          "window packets / span between the first and last packet of the window's offline flows.", "",
          "Caveats: enforce_k1, enforce_policy and test_reset are enforced runs (blocked pairs lose packets, so counts "
          "differ by design after a block); bugcheck_unpatched used the unpatched NFStream live (its XSS window logged "
          "only 118 of 224 flows: flows exported late by the defect are missing from flows.csv); run1 used the old "
          "harness (no quiet wait / reset). Matched flows of split connections: when slow replay splits a connection, "
          "its first piece still matches (same 5-tuple, occurrence 0) but with fewer packets, so 'same packets' drops "
          "and the extra pieces appear as 'live only'.", "",
          "## Per run", "", pd.DataFrame(run_rows).to_markdown(index=False), "",
          "## Flow-count ratio vs achieved replay rate (high-rate windows)", "", dd.to_markdown(index=False), "",
          "Pearson correlation of replay/original rate with live/offline flow ratio, per window, non-enforced "
          "runs only (blocks remove flows in enforced runs): "
          + ", ".join(f"{k} {v}" for k, v in corr.items()) + ".", "",
          "## Per run and window", "", allt.to_markdown(index=False)]
    (OUT / "fidelity_all_runs.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
