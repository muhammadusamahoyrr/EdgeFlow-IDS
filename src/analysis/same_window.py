"""Same-window baseline for the live CPU-budget comparison (review round 7).

Table V of the paper reports live macro-F1 0.917-0.918 for the half-core runs, which replayed only
three windows (DDoS-SYN_Flood, DoS-HTTP_Flood, Mirai-udpplain), against 0.804 for the no-limit runs,
which replayed all ten windows. The two numbers average over different classes and are not
comparable. Here the no-limit runs (and the one-core run) are re-scored on the same three windows.

Method: exactly src/eval_live.py restricted to those windows: live flows from
results/live/<run>/flows.csv (the gateway's recorded verdict `pred`), assigned to a window by
start time (+-1 s, eval_live.in_window), boundary-spanning training connections removed
(eval_live.drop_continuing), labelled with data/attackers.json (extract_flows.label_flows); the
offline side is NFStream on the same window pcap, classified with the run's model. Macro-F1 over
the classes present on either side (sklearn f1_score, zero_division=0), as in eval_live.
Check: recomputing over ALL windows of each run must reproduce live_vs_offline.json (printed).
Read-only with respect to existing result files.

Usage: python src/analysis/same_window.py
Output: results/live/same_window.md
"""
import json
import pathlib
import pickle
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # import from src

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from nfstream import NFStreamer  # noqa: E402
from sklearn.metrics import precision_recall_fscore_support  # noqa: E402

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RAW, RESULTS, STREAMER_KW  # noqa: E402
from eval_live import drop_continuing, in_window, macro  # noqa: E402
from extract_flows import label_flows  # noqa: E402

RUNS = [("run1", "no limit"), ("run1_r2", "no limit"), ("run1_r3", "no limit"), ("edge100", "one core"),
        ("edge50", "half core"), ("edge50_r2", "half core"), ("edge50_r3", "half core")]
THREE = ["DDoS-SYN_Flood", "DoS-HTTP_Flood", "Mirai-udpplain"]
_off_cache = {}


def score(run_dir):
    meta = json.loads((run_dir / "windows.json").read_text())
    model_path = pathlib.Path(meta["model"])
    if not model_path.exists():
        model_path = RESULTS / "models" / model_path.name
    with open(model_path, "rb") as f:  # trusted local model file (train_edge_model.py)
        bundle = pickle.load(f)
    model, feats = bundle["model"], bundle["features"]
    attackers = json.loads(ATTACKERS_FILE.read_text())
    live = pd.read_csv(run_dir / "flows.csv")
    off_parts, lv_parts = [], []
    for w in meta["windows"]:
        folder = w["folder"]
        cls, info = FOLDER_TO_CLASS[folder], attackers.get(folder, {})
        keys = bundle.get("continuing_connections", {}).get(w["source_file"], [])
        ck = (w["pcap"], str(model_path))
        if ck not in _off_cache:
            off = NFStreamer(source=str(RAW / "live" / w["pcap"]), **STREAMER_KW).to_pandas()
            off, _ = drop_continuing(off, keys)
            off = label_flows(off.copy(), cls, info)
            off["pred"] = model.predict(off[feats].to_numpy(np.float32)) if len(off) else []
            _off_cache[ck] = off[["label", "pred"]].copy()
        lv, _ = drop_continuing(in_window(live, w), keys)
        lv = label_flows(lv.copy(), cls, info)
        off_parts.append(_off_cache[ck].assign(window=folder))
        lv_parts.append(lv[["label", "pred"]].assign(window=folder))
    return meta, pd.concat(off_parts), pd.concat(lv_parts)


def summarise(off, lv):
    classes = sorted(set(off.label) | set(lv.label))
    out = {"classes": classes, "off_flows": len(off), "live_flows": len(lv),
           "off_macro": macro(off.label, off.pred, classes), "live_macro": macro(lv.label, lv.pred, classes)}
    for side, d in (("off", off), ("live", lv)):
        _, _, f1, sup = precision_recall_fscore_support(d.label, d.pred, labels=classes, zero_division=0)
        out[side + "_pc"] = {c: (round(float(a), 3), int(s)) for c, a, s in zip(classes, f1, sup)}
    return out


def main():
    rows, checks, pcs = [], [], []
    for tag, cpu in RUNS:
        run_dir = RESULTS / "live" / tag
        meta, off, lv = score(run_dir)
        j = json.loads((run_dir / "live_vs_offline.json").read_text())
        full = summarise(off, lv)
        checks.append({"run": tag, "live macro-F1 (json)": round(j["live"]["macro_f1"], 4),
                       "live recomputed": round(full["live_macro"], 4),
                       "offline (json)": round(j["offline"]["macro_f1"], 4),
                       "offline recomputed": round(full["off_macro"], 4),
                       "match": abs(j["live"]["macro_f1"] - full["live_macro"]) < 1e-9
                       and abs(j["offline"]["macro_f1"] - full["off_macro"]) < 1e-9})
        print(checks[-1], flush=True)
        windows = sorted(set(lv.window))
        s3 = summarise(off[off.window.isin(THREE)], lv[lv.window.isin(THREE)])
        rows.append({"run": tag, "CPU": cpu, "windows replayed": len(windows),
                     "live macro-F1, own windows": round(full["live_macro"], 4),
                     "live macro-F1, 3 half-core windows": round(s3["live_macro"], 4),
                     "offline macro-F1, 3 windows": round(s3["off_macro"], 4),
                     "live flows, 3 windows": f"{s3['live_flows']:,}",
                     "classes (3 windows)": ", ".join(s3["classes"])})
        print(rows[-1], flush=True)
        for c, (f, n) in s3["live_pc"].items():
            pcs.append({"run": tag, "class": c, "live F1": f, "live support": n,
                        "offline F1": s3["off_pc"][c][0], "offline support": s3["off_pc"][c][1]})
    md = ["# Same-window baseline: live macro-F1 on the three half-core windows (review round 7)", "",
          f"Windows: {', '.join(THREE)} (the only windows replayed in the half-core runs). Method: "
          "src/eval_live.py restricted to these windows (gateway verdicts from flows.csv; offline = NFStream "
          "on the window pcap). Macro-F1 over the classes present on either side.", "",
          "## Check: recomputation over each run's own windows reproduces live_vs_offline.json", "",
          pd.DataFrame(checks).to_markdown(index=False), "",
          "## Macro-F1 on the same three windows", "", pd.DataFrame(rows).to_markdown(index=False), "",
          "## Per-class F1 on the three windows", "", pd.DataFrame(pcs).to_markdown(index=False)]
    (RESULTS / "live" / "same_window.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
