"""Sanity check for block_timing.py: when do the DDoS-SYN window's attack flows start (run1)?"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from config import ATTACKERS_FILE, FOLDER_TO_CLASS, RESULTS  # noqa: E402
from eval_live import in_window  # noqa: E402
from extract_flows import label_flows  # noqa: E402

run = RESULTS / "live" / "run1"
meta = json.loads((run / "windows.json").read_text())
att = json.loads(ATTACKERS_FILE.read_text())
live = pd.read_csv(run / "flows.csv")
for w in meta["windows"]:
    if w["folder"] != "DDoS-SYN_Flood":
        continue
    d = label_flows(in_window(live, w).copy(), FOLDER_TO_CLASS[w["folder"]], att.get(w["folder"], {}))
    a = d[d.label != "Benign"]
    t0 = d.bidirectional_first_seen_ms.min()
    s = (a.bidirectional_first_seen_ms - t0) / 1000
    e = (a.bidirectional_last_seen_ms - t0) / 1000
    v = (a.verdict_ms - t0) / 1000
    print("attack flows", len(a), "span of starts (s): min %.1f max %.1f" % (s.min(), s.max()))
    print("start quantiles 10/50/90 (s):", np.percentile(s, [10, 50, 90]).round(1))
    print("share starting within first 15/20/30 s:", [round(float((s <= x).mean()), 3) for x in (15, 20, 30)])
    print("first flow end (s): %.2f, first verdict (s): %.2f" % (e.min(), v.min()))
    print("duration quantiles 50/90 (s):", np.percentile(e - s, [50, 90]).round(2))
