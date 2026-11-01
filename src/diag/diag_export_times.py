"""When does the live gateway export flows? Export time vs flow end, relative to the replay windows."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # EdgeFlow-IDS: import from src
import json, sys
import pandas as pd
from config import RESULTS
run = RESULTS / "live" / sys.argv[1]
df = pd.read_csv(run / "flows.csv")
w = json.loads((run / "windows.json").read_text())
w = w["windows"] if isinstance(w, dict) else w
t0 = w[0]["replay_start_ms"]
for x in w:
    print(f"{x['folder']}: replay {(x['replay_start_ms']-t0)/1000:.0f}-{(x['replay_end_ms']-t0)/1000:.0f} s")
df["end_s"] = (df.bidirectional_last_seen_ms - t0) / 1000
df["export_s"] = (df.verdict_ms - t0) / 1000
df["wait_s"] = df.export_s - df.end_s
lan = df[~df.src_ip.str.startswith("10.0.")]
print("\nexport time histogram (10 s bins):")
print(lan.export_s.floordiv(10).mul(10).value_counts().sort_index().to_string())
print("\nwait after flow end, quantiles:", lan.wait_s.quantile([.1, .5, .9]).round(1).to_dict())
print("ticker flows:", len(df) - len(lan))
print(df[df.src_ip.str.startswith("10.0.")][["src_ip","dst_ip","protocol","bidirectional_packets","end_s","export_s"]].to_string())
