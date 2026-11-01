"""Share of attack vs background (Benign) flows inside each attack pcap, after evidence-based labelling.

Usage: python src/label_shares.py
Output: results/label_shares.md
"""
import pandas as pd

from config import PROCESSED, RESULTS


def main():
    df = pd.read_parquet(PROCESSED / "flows.parquet", columns=["source_file", "label"])
    t = (df.assign(is_attack=df.label != "Benign")
           .groupby("source_file")
           .agg(flows=("label", "size"), attack_flows=("is_attack", "sum")))
    t["background_flows"] = t.flows - t.attack_flows
    t["background_share"] = (t.background_flows / t.flows).round(3)
    md = ["# Attack vs background flows per pcap (labels from data/attackers.json)", "",
          t.to_markdown(), "",
          "Large pcaps are trimmed to their first 1M packets (src/trim_pcaps.sh)."]
    (RESULTS / "label_shares.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
