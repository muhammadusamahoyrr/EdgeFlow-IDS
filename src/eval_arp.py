"""Evaluate the ARP watcher per live window, with fresh state per window.

Each live window comes from a different CIC-IoT2023 capture session (different days, different
DHCP leases), so watcher state must not carry over between windows. This runs arp_watch.py's
rules on every window pcap (the same traffic the gateway saw; packet ratio ~1.0) and counts
alerts by severity. Only the MITM-ArpSpoofing window contains an ARP attack.

Usage: python src/eval_arp.py
Output: results/arp_eval.md
"""
import json
import subprocess
import tempfile
from pathlib import Path

from config import RAW, RESULTS

SRC = Path(__file__).resolve().parent


def main():
    manifest = json.loads((RAW / "live" / "manifest.json").read_text())
    rows = []
    for w in manifest:
        with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as t:
            out = t.name
        subprocess.run(["/opt/edgeflow/bin/python", str(SRC / "arp_watch.py"), "--pcap",
                        str(RAW / "live" / w["pcap"]), "--out", out], check=True)
        alerts = [json.loads(x) for x in Path(out).read_text().splitlines() if x.strip()]
        Path(out).unlink()
        high = [a for a in alerts if a["severity"] == "high"]
        first = (min(a["time_ms"] for a in high) / 1000 - w["start_epoch"]) if high else None
        rows.append((w["folder"], len(high), len([a for a in alerts if a["severity"] == "info"]),
                     f"{first:.1f}" if first is not None else "-",
                     "; ".join(sorted({f"{a['mac']} claims {a['detail'][0]}" for a in high}))))
    md = ["# ARP watcher per live window (fresh state per window)", "",
          "| Window | High alerts | Info alerts | First high alert (s into window) | High alert detail |",
          "|---|---|---|---|---|"]
    md += [f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |" for r in rows]
    md += ["", "Only MITM-ArpSpoofing contains an ARP attack: high alerts elsewhere are false alarms."]
    (RESULTS / "arp_eval.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
