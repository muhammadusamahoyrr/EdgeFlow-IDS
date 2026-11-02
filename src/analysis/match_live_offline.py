"""Flow-by-flow comparison of a live run with offline extraction (paper revision, item M1).

Equal macro-F1 can hide differences, so every flow is matched: within each window, flows are keyed
by 5-tuple and their order of appearance within that 5-tuple (live timestamps are wall-clock,
offline ones are capture time, so start times cannot be compared directly). For matched pairs we
report how often packet counts, byte counts and verdicts are identical; unmatched flows on either
side are counted separately. Macro-F1 intervals use the host-pair bootstrap (cluster_ci.py).

Usage: python src/analysis/match_live_offline.py --tag run1
Output: results/live/<tag>/flow_match.md
"""
import argparse
import json
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from nfstream import NFStreamer  # noqa: E402

from analysis.cluster_ci import cluster_bootstrap, cluster_ids  # noqa: E402
from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RAW, RESULTS, STREAMER_KW  # noqa: E402
from eval_live import drop_continuing, in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402

KEY = ["src_ip", "src_port", "dst_ip", "dst_port", "protocol"]


def with_occurrence(df):
    df = df.sort_values("bidirectional_first_seen_ms").copy()
    for c in ("src_port", "dst_port", "protocol"):
        df[c] = df[c].astype(int)
    df["occ"] = df.groupby(KEY).cumcount()
    return df


def main(tag):
    run = RESULTS / "live" / tag
    meta = json.loads((run / "windows.json").read_text())
    model_path = pathlib.Path(meta["model"])
    if not model_path.exists():
        model_path = RESULTS / "models" / model_path.name
    # Trusted input: the model file is produced locally by train_edge_model.py.
    with open(model_path, "rb") as f:
        bundle = pickle.load(f)
    model, feats = bundle["model"], bundle["features"]
    attackers = json.loads(ATTACKERS_FILE.read_text())
    live_all = pd.read_csv(run / "flows.csv")

    rows, off_parts, live_parts = [], [], []
    for w in meta["windows"]:
        folder, cls = w["folder"], FOLDER_TO_CLASS[w["folder"]]
        keys = bundle.get("continuing_connections", {}).get(w["source_file"], [])
        off = NFStreamer(source=str(RAW / "live" / w["pcap"]), **STREAMER_KW).to_pandas()
        off, _ = drop_continuing(off, keys)
        off = label_flows(off.copy(), cls, attackers.get(folder, {}))
        off["pred"] = model.predict(off[feats].to_numpy(np.float32))
        lv, _ = drop_continuing(in_window(live_all, w), keys)
        lv = label_flows(lv.copy(), cls, attackers.get(folder, {}))
        off, lv = with_occurrence(off), with_occurrence(lv)
        m = off.merge(lv, on=KEY + ["occ"], how="outer", suffixes=("_off", "_live"), indicator=True)
        both = m[m["_merge"] == "both"]
        rows.append({
            "window": folder,
            "offline flows": len(off), "live flows": len(lv), "matched": len(both),
            "offline only": int((m["_merge"] == "left_only").sum()),
            "live only": int((m["_merge"] == "right_only").sum()),
            "same packets": round(float((both.bidirectional_packets_off == both.bidirectional_packets_live).mean()), 4) if len(both) else None,
            "same bytes": round(float((both.bidirectional_bytes_off == both.bidirectional_bytes_live).mean()), 4) if len(both) else None,
            "same verdict": round(float((both.pred_off == both.pred_live).mean()), 4) if len(both) else None,
        })
        print(rows[-1])
        off_parts.append(off.assign(source_file=w["source_file"]))
        live_parts.append(lv.assign(source_file=w["source_file"]))

    t = pd.DataFrame(rows)
    tot = t[["offline flows", "live flows", "matched", "offline only", "live only"]].sum()
    off, lv = pd.concat(off_parts), pd.concat(live_parts)
    classes = sorted(set(off.label) | set(lv.label))
    ci = {}
    for name, d in (("offline", off), ("live", lv)):
        cl = cluster_ids(d.source_file.to_numpy(), d.src_ip.to_numpy(), d.dst_ip.to_numpy())
        ci[name] = cluster_bootstrap(d.label.to_numpy(), d.pred.to_numpy(), cl, classes)
    md = [f"# Flow-by-flow match, live vs offline ({tag})", "",
          f"Matched {int(tot['matched']):,} flows; offline-only {int(tot['offline only']):,}, "
          f"live-only {int(tot['live only']):,} (of {int(tot['offline flows']):,} offline / "
          f"{int(tot['live flows']):,} live).", "",
          "Macro-F1 with host-pair bootstrap 95% CI: "
          f"offline {ci['offline'][0]:.3f} [{ci['offline'][1]:.3f}, {ci['offline'][2]:.3f}], "
          f"live {ci['live'][0]:.3f} [{ci['live'][1]:.3f}, {ci['live'][2]:.3f}] "
          f"({ci['live'][3]:,} host-pair clusters live).", "",
          t.to_markdown(index=False)]
    (run / "flow_match.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="run1")
    main(ap.parse_args().tag)
