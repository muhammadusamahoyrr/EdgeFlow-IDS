"""List top talkers in each attack pcap, to identify attacker/victim IPs for labelling.

Usage: python src/diag/find_attackers.py [pcap ...]   (default: every pcap under data/raw/cic-iot2023)
Prints candidates; the confirmed IPs are written by hand into data/attackers.json.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # EdgeFlow-IDS: import from src
import sys
from pathlib import Path

import pandas as pd
from nfstream import NFStreamer

from config import RAW, STREAMER_KW


def top_talkers(pcap, k=5):
    df = NFStreamer(source=str(pcap), **STREAMER_KW).to_pandas()
    print(f"\n=== {pcap.parent.name}/{pcap.name}: {len(df):,} flows")
    by_src = (df.groupby("src_ip")
                .agg(flows=("id", "size"), pkts=("src2dst_packets", "sum"),
                     dsts=("dst_ip", "nunique"), dports=("dst_port", "nunique"))
                .sort_values("pkts", ascending=False).head(k))
    print("top sources:\n", by_src.to_string())
    by_pair = (df.groupby(["src_ip", "dst_ip"])
                 .agg(flows=("id", "size"), pkts=("bidirectional_packets", "sum"))
                 .sort_values("pkts", ascending=False).head(k))
    print("top pairs:\n", by_pair.to_string())


if __name__ == "__main__":
    pcaps = [Path(p) for p in sys.argv[1:]] or sorted((RAW / "cic-iot2023").rglob("*.pcap"))
    for p in pcaps:
        top_talkers(p)
