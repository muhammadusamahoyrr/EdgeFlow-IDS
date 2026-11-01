"""Why is BruteForce recall low? Compare train vs test BruteForce flows (temporal split)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # EdgeFlow-IDS: import from src
import pandas as pd
from config import PROCESSED
from train_baseline import temporal_split

df = pd.read_parquet(PROCESSED / "flows.parquet")
train, test = temporal_split(df)
for name, part in (("train", train), ("test", test)):
    bf = part[part.label == "BruteForce"]
    t = pd.to_datetime(bf.bidirectional_first_seen_ms, unit="ms")
    print(f"\n{name}: {len(bf)} flows, {t.min()} -> {t.max()}")
    print(bf.groupby(["dst_ip", "dst_port"]).size().sort_values(ascending=False).head(6).to_string())
    print("median pkts", bf.bidirectional_packets.median(), "| median duration ms", bf.bidirectional_duration_ms.median())
f = df[df.source_file.str.startswith("Dictionary")]
t = pd.to_datetime(f.bidirectional_first_seen_ms, unit="ms")
print("\nfile time span:", t.min(), "->", t.max())
print(t.dt.floor("h").value_counts().sort_index().head(10).to_string())
