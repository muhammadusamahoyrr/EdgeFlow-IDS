"""Internal (LAN-to-LAN) conversations per pcap, by destination port: helps find low-volume attacks."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # EdgeFlow-IDS: import from src
import sys
from pathlib import Path
from nfstream import NFStreamer
from config import RAW, STREAMER_KW

for p in [Path(a) for a in sys.argv[1:]] or sorted((RAW / "cic-iot2023").rglob("*.pcap")):
    df = NFStreamer(source=str(p), **STREAMER_KW).to_pandas()
    lan = df[df.src_ip.str.startswith("192.168.137.") & df.dst_ip.str.startswith("192.168.137.")
             & ~df.dst_ip.isin(["192.168.137.1", "192.168.137.255"])]
    g = (lan.groupby(["src_ip", "dst_ip", "dst_port"])
            .agg(flows=("id", "size"), pkts=("bidirectional_packets", "sum"),
                 bytes=("bidirectional_bytes", "sum"))
            .sort_values("flows", ascending=False).head(8))
    print(f"\n=== {p.parent.name}  (LAN flows {len(lan):,} of {len(df):,})\n{g.to_string()}")
